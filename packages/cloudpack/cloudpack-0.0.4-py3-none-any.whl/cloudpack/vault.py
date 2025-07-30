import os
from configparser import ConfigParser, NoOptionError, NoSectionError
from pathlib import Path
from getpass import getpass
from click import UsageError
import math
import shutil
import json

import cloudpack.config as config
from cloudpack.crypto import encrypt, decrypt, derive_vault_key
from cloudpack.utils import is_password_secure

DEFAULT_CONFIG = """
; This is the configuration file for this cloudpack vault.
; Learn more at https://github.com/atar4xis/cloudpack

[vault]
version = 0.0.1

[provider:google_drive]
enabled = False
client_id =
client_secret =

[provider:dropbox]
enabled = False
client_id =
client_secret =
"""


def init(path) -> None:
    """
    Initialize a new CloudPack vault at the specified path.
    Creates the directory if it doesn't exist, and writes the default config file.
    Warns if the directory is not empty.
    """

    directory = Path(path).resolve()
    print(f"Initializing vault in {directory} ...")

    # create the directory if it doesn't exist
    if not directory.exists():
        directory.mkdir(parents=True)

    # warn if the directory is not empty
    if any(directory.iterdir()):
        print("Warning: Target directory is not empty")
        proceed = input("Proceed anyway? (y/N): ")
        if not proceed.strip().lower().startswith("y"):
            print("Operation aborted")
            return

    # create directory structure
    dir_tree = ["chunks", "files"]
    for dir in dir_tree:
        Path(directory / dir).mkdir(exist_ok=True)

    # write default configuration file
    config_file = directory / "config.ini"
    with open(config_file, "w") as f:
        f.write(DEFAULT_CONFIG)

    # write default meta file
    meta_file = directory / "vault.meta"
    with open(meta_file, "w") as f:
        f.write("{}")

    # === master password ===
    master_password = getpass("Enter master password: ")
    while not is_password_secure(master_password) and not master_password.startswith(
        "INSECURE: "
    ):
        print("""The password you entered is considered insecure.
We recommend using a password that meets the following criteria:
- At least 12 characters long
- Includes uppercase and lowercase letters
- Contains numbers and symbols

If you understand the risks and still wish to proceed,
you can bypass this check by prefixing your password with 'INSECURE: '
""")
        master_password = getpass("Enter master password: ")

    # if the password is insecure, strip the prefix
    if master_password.startswith("INSECURE: "):
        master_password = master_password[10:]

    # derive a vault key, encrypt a static string, store it in the .passwd file
    key_salt = os.urandom(16)
    vault_key = derive_vault_key(master_password, key_salt)
    with open(directory / ".passwd", "wb") as f:
        f.write(key_salt + encrypt(b"CloudPack", vault_key))

    # === initial configuration wizard ===
    config = ConfigParser()
    config.read(config_file)
    # TODO: implement wizard

    print("CloudPack vault initialized.")


def add(file) -> None:
    # TODO: implement
    pass


def upload() -> None:
    # TODO: implement
    pass


def configure(action, *args) -> None:
    """
    Perform configuration actions (get, set, list) on the config file.
    """

    path = Path(".")
    try:
        cfg = config.load(path)
    except FileNotFoundError:
        raise UsageError("Configuration file not found")

    try:
        match action:
            case "get":
                print(config.get(cfg, args[0]))
            case "set":
                key, value = args
                config.get(cfg, key)
                config.set(cfg, key, value)
                config.save(cfg, path)
                print("Configuration updated")
            case "list":
                config.list(cfg)
            case _:
                raise UsageError("Unknown action")
    except (NoSectionError, NoOptionError, ValueError):
        raise UsageError("Unknown configuration key")


def validate_master_password(path) -> None | str:
    """
    Request and validate the master password.
    """
    passwd_file = Path(path).resolve() / ".passwd"
    if not passwd_file.exists():
        print(
            "Error: Missing .passwd file. Make sure you are unlocking a cloudpack vault."
        )
        return None

    master_password = getpass("Enter master password: ")
    data = passwd_file.read_bytes()
    key_salt = data[:16]
    encrypted_blob = data[16:]

    vault_key = derive_vault_key(master_password, key_salt)
    try:
        decrypted = decrypt(encrypted_blob, vault_key)
    except Exception:
        print("Invalid master password provided.")
        return None

    if decrypted != b"CloudPack":
        print("Invalid master password provided.")
        return None

    return master_password


def unlock(path) -> None:
    """
    Unlock the vault using the master password.
    """
    path = Path(path)
    master_password = validate_master_password(path)
    if not master_password:
        return

    with open(path / "vault.meta", "r+b") as f:
        salt = f.read(16)
        encrypted_meta = f.read()
        key = derive_vault_key(master_password, salt)
        metadata = decrypt(encrypted_meta, key)
        f.seek(0)
        f.write(b"{}")
        f.truncate()

    chunks_dir = path / "chunks"
    chunk_metadata = json.loads(metadata)
    chunk_cache = {}

    for relative_path, blocks in chunk_metadata.items():
        output_path = path / "files" / relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as out_file:
            for block in blocks:
                chunk_id = block["chunk"]
                offset = block["offset"]
                size = block["size"]

                if chunk_id not in chunk_cache:
                    with open(chunks_dir / f"{chunk_id}.chunk", "rb") as chunk_file:
                        chunk_cache[chunk_id] = chunk_file.read()

                encrypted_block = chunk_cache[chunk_id][offset : offset + size]
                decrypted_block = decrypt(encrypted_block, key)
                out_file.write(decrypted_block)

    # remove existing chunks
    for chunk_file in chunks_dir.iterdir():
        if chunk_file.is_file():
            chunk_file.unlink()

    print("Vault unlocked.")


def lock(path) -> None:
    """
    Lock the vault using the master password.
    """
    path = Path(path)
    master_password = validate_master_password(path)
    if master_password is None:
        return

    salt = os.urandom(16)
    key = derive_vault_key(master_password, salt)

    num_chunks = 8  # TODO: make this dynamic

    chunks = [
        {"id": os.urandom(8).hex(), "data": b"", "offset": 0} for _ in range(num_chunks)
    ]

    chunk_metadata = {}
    files_root = path / "files"
    chunk_index = 0  # for round-robin distribution

    print("Encrypting files...")
    for file in files_root.rglob("*"):
        if not file.is_file():
            continue

        relative_path = str(file.relative_to(files_root))
        file_metadata = []

        file_size = file.stat().st_size
        if file_size == 0:
            chunk_metadata[relative_path] = []
            continue

        block_size = math.ceil(file_size / num_chunks)

        with open(file, "rb") as f:
            while True:
                block = f.read(block_size)
                if not block:
                    break

                encrypted_block = encrypt(block, key)
                chunk = chunks[chunk_index % num_chunks]
                offset = chunk["offset"]

                chunk["data"] += encrypted_block
                chunk["offset"] += len(encrypted_block)

                file_metadata.append(
                    {
                        "chunk": chunk["id"],
                        "offset": offset,
                        "size": len(encrypted_block),
                    }
                )

                chunk_index += 1

        chunk_metadata[relative_path] = file_metadata

    print("Writing data...")
    chunks_dir = path / "chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)

    # remove existing chunks
    for chunk_file in chunks_dir.iterdir():
        if chunk_file.is_file():
            chunk_file.unlink()

    # write new chunks
    for chunk in chunks:
        with open(chunks_dir / f"{chunk['id']}.chunk", "wb") as f:
            f.write(chunk["data"])

    print("Writing metadata...")
    with open(path / "vault.meta", "r+b") as f:
        f.seek(0)
        f.write(salt + encrypt(json.dumps(chunk_metadata).encode(), key))
        f.truncate()

    # remove files
    shutil.rmtree(files_root, ignore_errors=True)

    print("Vault locked.")

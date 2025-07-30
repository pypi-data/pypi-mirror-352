from pathlib import Path
from click.testing import CliRunner
from unittest.mock import patch

from cloudpack.cli import cli


def test_vault_init(tmp_path):
    master_password = "My$3cureV4ultPa$$w0rd!"
    with patch("cloudpack.vault.getpass", return_value=master_password):
        runner = CliRunner()
        vault_path = tmp_path / "vault"
        result = runner.invoke(cli, ["init", str(vault_path)])

        assert result.exit_code == 0
        assert "vault initialized" in result.output
        assert vault_path.exists() and vault_path.is_dir()
        assert (vault_path / ".passwd").exists()


def test_configure(tmp_path):
    config_file = tmp_path / "config.ini"
    config_file.write_text("""
[section]
key = value
""")

    runner = CliRunner()

    with runner.isolated_filesystem():
        # missing config.ini file
        result = runner.invoke(cli, ["config", "list"])
        assert result.exit_code != 0
        assert "Configuration file not found" in result.output

        (Path.cwd() / "config.ini").write_text(config_file.read_text())

        # config get with valid key
        result = runner.invoke(cli, ["config", "get", "section.key"])
        assert result.exit_code == 0
        assert "value" in result.output

        # config set with valid key
        result = runner.invoke(cli, ["config", "set", "section.key", "newvalue"])
        assert result.exit_code == 0
        assert "Configuration updated" in result.output

        # verify updated value
        result = runner.invoke(cli, ["config", "get", "section.key"])
        assert result.exit_code == 0
        assert "newvalue" in result.output

        # config list
        result = runner.invoke(cli, ["config", "list"])
        assert result.exit_code == 0
        assert "section.key = newvalue" in result.output

        # config get with unknown key
        result = runner.invoke(cli, ["config", "get", "section.unknown"])
        assert result.exit_code != 0
        assert "Unknown configuration key" in result.output

        # config set with unknown key
        result = runner.invoke(cli, ["config", "set", "section.unknown", "val"])
        assert result.exit_code != 0
        assert "Unknown configuration key" in result.output

        # config get with invalid key format
        result = runner.invoke(cli, ["config", "get", "invalidkeyformat"])
        assert result.exit_code != 0
        assert "Unknown configuration key" in result.output

        # config set with invalid key format
        result = runner.invoke(cli, ["config", "set", "invalidkeyformat", "val"])
        assert result.exit_code != 0
        assert "Unknown configuration key" in result.output

        # unknown config action
        result = runner.invoke(cli, ["config", "unknown_action"])
        assert result.exit_code != 0

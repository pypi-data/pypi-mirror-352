# CloudPack

![Project Status](https://img.shields.io/badge/status-pre--alpha-red)
![Tests](https://github.com/atar4xis/cloudpack/actions/workflows/python-app.yml/badge.svg)

**CloudPack** is an open-source, multi-cloud file vault. It encrypts your files, splits them into chunks, and stores those chunks across different cloud providers. You hold the only key - your master password.

> ⚠️ **Project Status: Pre-Alpha**  
> CloudPack is in active early development and is **not ready to use**. Expect incomplete features, placeholder code, and rapid breaking changes. Contributions and feedback are welcome.

## Features

- 🔐 **End-to-End Encryption** - AES-256 encryption before upload
- 🧩 **Chunked Storage** - Files are split and distributed across providers
- ☁️ **Multi-Cloud Support** - Use Google Drive, Dropbox, OneDrive, and more
- 🔄 **Cross-Platform** - Works on macOS, Linux, and Windows
- 🛠 **CLI and API** - Full control for power users and integrations

## Installation

**Requirements:**

- Python 3.10 or higher
- pip (Python package installer)

**Install from PyPI:**

```bash
pip install cloudpack
```

**Install from source (for development):**

```bash
git clone https://github.com/atar4xis/cloudpack.git
cd cloudpack
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

## Usage/Examples

After installation, you can access the CLI with:

```bash
cloudpack --help
```

To create a new vault in the current directory:

```bash
cloudpack init
```

To specify a custom location:

```bash
cloudpack init /path/to/vault
```

## Supported Providers

⚠️ This section is under development.

## License

CloudPack is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome!

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines and setup instructions.

## Roadmap

- [x] Command-Line Interface
- [x] Core Encryption & Chunking
- [x] Basic Vault Operations
- [ ] Configuration Management
- [ ] Google Drive Support
- [ ] Dropbox Support
- [ ] Documentation & Tutorials
- [ ] API Development
- [ ] Desktop GUI

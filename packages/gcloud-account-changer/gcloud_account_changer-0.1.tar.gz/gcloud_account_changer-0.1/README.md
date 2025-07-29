# gcloud-account-changer

Google Cloud CLI Account & Project Selector - A terminal-based interactive tool for managing multiple Google Cloud accounts and projects.

## Features

- 🔄 Easy switching between multiple Google Cloud accounts
- 📋 Interactive project selection for each account
- 🎨 Terminal-based user interface using urwid
- ⚡ Quick account and project configuration
- 💾 Remember your preferred settings

## Installation

### Using pipx (Recommended)

```bash
pipx install gcloud-account-changer
```

### Using uv

```bash
uv tool install gcloud-account-changer
```

### Using pip

```bash
pip install gcloud-account-changer
```

## Prerequisites

- Google Cloud CLI (`gcloud`) must be installed and configured
- Python 3.7 or higher
- At least one Google Cloud account authenticated with `gcloud auth login`

## Usage

After installation, run the tool using:

```bash
gcloud-account-changer
```

The interactive interface will guide you through:

1. **Account Selection**: Choose from your authenticated Google Cloud accounts
2. **Project Selection**: Select a project from the chosen account
3. **Configuration**: Apply the selected account and project to your gcloud CLI

### Keyboard Navigation

- **Arrow Keys**: Navigate through options
- **Enter**: Select an option
- **Esc/Q**: Quit the application

## Getting Started

1. First, authenticate your Google Cloud accounts:
   ```bash
   gcloud auth login
   ```

2. Install gcloud-account-changer:
   ```bash
   pipx install gcloud-account-changer
   ```

3. Run the tool:
   ```bash
   gcloud-account-changer
   ```

4. Select your desired account and project from the interactive interface

## Requirements

- `urwid` - Terminal user interface library
- `gcloud` CLI tool (must be installed separately)

## Development

To contribute to this project:

1. Clone the repository:
   ```bash
   git clone https://github.com/search5/gcloud-account-changer.git
   cd gcloud-account-changer
   ```

2. Install in development mode:
   ```bash
   uv sync
   ```

## License

This project is licensed under the BSD License.

## Author

**Lee Ji-Ho** - [search5@gmail.com](mailto:search5@gmail.com)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Issues

If you encounter any problems or have feature requests, please create an issue on the [GitHub repository](https://github.com/search5/gcloud-account-changer/issues).

## Changelog

### v0.1
- Initial release
- Basic account and project switching functionality
- Terminal-based user interface
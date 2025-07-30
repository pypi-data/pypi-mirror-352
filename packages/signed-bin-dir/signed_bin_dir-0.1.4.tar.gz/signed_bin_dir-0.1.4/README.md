# Signed Binary Directory

A secure tool signing system that automatically adds project-specific tools to your PATH when you navigate into directories. This ensures that only cryptographically signed and verified tools are executed, providing security against malicious scripts while maintaining convenience.

## Features

- 🔐 **Cryptographic Signing**: Uses your SSH private key to sign executable files
- 🛡️ **Automatic Verification**: Verifies signatures before adding directories to PATH
- 🐚 **Shell Integration**: Works with both Fish and Bash shells
- 📁 **Hierarchical Discovery**: Finds signed bin directories in current and parent directories
- ⚡ **Fast**: Minimal overhead when changing directories
- 🔍 **Transparent**: Optional notifications when signed tools are discovered
- 🛠️ **Easy Setup**: Automatic shell integration installer

## Security Model

This tool uses your existing SSH key pair for signing and verification:

- **Signing**: Uses your SSH private key (`~/.ssh/id_rsa` by default) to create cryptographic signatures
- **Verification**: Uses the corresponding public key to verify signatures before trusting executables
- **Manifest**: Creates a `.signed-manifest.json` file containing hashes and signatures of all executables
- **Trust**: Only directories with valid signatures from your key are added to PATH

## Installation

### Install from PyPI

```bash
# Install the latest version from PyPI
pip install signed-bin-dir

# Or install in development mode from source
git clone https://github.com/igutekunst/signed-bin-dir.git
cd signed-bin-dir
pip install -e .
```

### Shell Integration (Automatic)

The easiest way to set up shell integration:

```bash
# Auto-detect and install for all available shells
sign-bin-dir install

# Install for a specific shell
sign-bin-dir install --shell fish
sign-bin-dir install --shell bash

# Check installation status
sign-bin-dir status

# Uninstall if needed
sign-bin-dir uninstall --all
```

The shell integration files are automatically included with the pip package, so no additional setup is required.

### Shell Integration (Manual)

If you prefer manual setup, you can find the integration files in your Python environment after installation:

```bash
# Find the integration files
python3 -c "import signed_bin_dir; from pathlib import Path; print(Path(signed_bin_dir.__file__).parent.parent / 'share' / 'signed-bin-dir' / 'shell_integrations')"
```

#### Fish Shell

Add to your `~/.config/fish/config.fish`:

```fish
# Source the signed-bin-dir integration (adjust path as needed)
source /path/to/shell_integrations/signed_bin_dir.fish
```

#### Bash Shell

Add to your `~/.bashrc`:

```bash
# Source the signed-bin-dir integration (adjust path as needed)
source /path/to/shell_integrations/signed_bin_dir.bash
```

## Usage

### Basic Workflow

1. **Create a bin directory** in your project with executable tools
2. **Sign the directory** using `sign-bin-dir`
3. **Navigate into the project** - tools are automatically added to PATH
4. **Navigate away** - tools are automatically removed from PATH

### Command Line Interface

#### Shell Integration Management

```bash
# Check which shells are available and integration status
sign-bin-dir status

# Install integration for all detected shells
sign-bin-dir install

# Install for specific shell
sign-bin-dir install --shell fish

# Uninstall integration
sign-bin-dir uninstall --shell fish
sign-bin-dir uninstall --all
```

#### Sign a bin directory

```bash
# Sign all executables in a bin directory
sign-bin-dir sign ./bin

# Use a specific private key
sign-bin-dir sign ./bin --private-key ~/.ssh/my_key

# Verbose output
sign-bin-dir sign ./bin --verbose
```

#### Verify signatures

```bash
# Verify all signatures in a bin directory
sign-bin-dir verify ./bin

# Verify with verbose output
sign-bin-dir verify ./bin --verbose
```

#### List signed files

```bash
# List all signed files in a bin directory
sign-bin-dir list-files ./bin
```

### Convenience Functions

The shell integrations provide helpful functions:

```bash
# Sign the bin directory in current project
sign-current-bin

# Verify the bin directory in current project
verify-current-bin
```

## Example Project Structure

```
my-project/
├── bin/
│   ├── my-tool
│   ├── deploy-script
│   └── .signed-manifest.json  # Created by sign-bin-dir
├── src/
└── README.md
```

## Quick Start

1. **Install the package**:
   ```bash
   pip install signed-bin-dir
   ```

2. **Set up shell integration**:
   ```bash
   sign-bin-dir install
   ```

3. **Restart your shell** or source your config file

4. **Try with a project**:
   ```bash
   mkdir my-project && cd my-project
   mkdir bin
   echo '#!/bin/bash\necho "Hello from my tool!"' > bin/my-tool
   chmod +x bin/my-tool
   sign-bin-dir sign bin
   my-tool    # Works!
   cd ..
   my-tool    # Command not found (removed from PATH)
   ```

## How It Works

1. **Directory Change Detection**: Shell hooks detect when you change directories
2. **Discovery**: Searches current and parent directories for `bin/` folders with `.signed-manifest.json`
3. **Verification**: Validates signatures against your SSH public key
4. **PATH Management**: Adds verified directories to PATH, removes them when you leave

## Security Considerations

- **Key Security**: Protect your SSH private key as it's used for signing
- **Trust Model**: Only trust signatures from keys you control
- **Verification**: Always verify signatures before executing tools
- **Isolation**: Each project's tools are isolated and only available in that context

## Configuration

### Custom SSH Key

By default, the tool uses `~/.ssh/id_rsa`. To use a different key:

```bash
sign-bin-dir sign ./bin --private-key ~/.ssh/my_project_key
```

### Shell Integration Options

You can customize the shell integration behavior:

```fish
# In your Fish config, uncomment this line to show notifications
__signed_bin_dir_check_current
```

## Development

### Setup Development Environment

```bash
# Clone and install in development mode
git clone https://github.com/igutekunst/signed-bin-dir.git
cd signed-bin-dir
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black signed_bin_dir/
isort signed_bin_dir/

# Type checking
mypy signed_bin_dir/
```

### Project Structure

```
signed-bin-dir/
├── signed_bin_dir/
│   ├── __init__.py
│   ├── cli.py              # Command-line interface
│   ├── signer.py           # Core signing/verification logic
│   ├── path_manager.py     # PATH management functionality
│   └── installer.py        # Shell integration installer
├── shell_integrations/
│   ├── signed_bin_dir.fish # Fish shell integration
│   └── signed_bin_dir.bash # Bash shell integration
├── tests/
├── pyproject.toml
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Author

Isaac Harrison Gutekunst <isaac@supercortex.io>

## Troubleshooting

### Common Issues

**"Private key not found"**
- Ensure you have an SSH key pair generated: `ssh-keygen -t rsa`
- Check the key path: `ls -la ~/.ssh/`

**"Signature verification failed"**
- Re-sign the directory: `sign-bin-dir sign ./bin`
- Check file permissions: `ls -la bin/`

**"Command not found: sign-bin-dir"**
- Ensure the package is installed: `pip list | grep signed-bin-dir`
- Check your PATH includes pip's bin directory

**Shell integration not working**
- Check installation status: `sign-bin-dir status`
- Reinstall integration: `sign-bin-dir install`
- Restart your shell or source the config file

**Integration installer issues**
- Make sure you have write permissions to your shell config files
- Check if your shell config directory exists (e.g., `~/.config/fish/`)
- Use manual installation if automatic installation fails 
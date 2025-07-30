"""Command-line interface for signed-bin-dir."""

import sys
from pathlib import Path
from typing import Optional

import click

from .installer import ShellIntegrationInstaller
from .signer import BinDirSigner


@click.group()
@click.version_option()
def cli() -> None:
    """Secure tool signing system for automatically adding project-specific tools to PATH."""
    pass


@cli.command()
@click.argument("bin_directory", type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
@click.option("--private-key", "-k", type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
              help="Path to SSH private key (defaults to ~/.ssh/id_rsa)")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--debug", "-d", is_flag=True, help="Debug output")
def sign(bin_directory: Path, private_key: Optional[Path], verbose: bool, debug: bool) -> None:
    """Sign all executable files in a bin directory."""
    try:
        signer = BinDirSigner(private_key, debug=debug)
        manifest = signer.sign_bin_directory(bin_directory)
        
        if verbose:
            click.echo(f"Signed {len(manifest['files'])} files in {bin_directory}")
            for filename in manifest['files']:
                click.echo(f"  - {filename}")
        else:
            click.echo(f"Successfully signed {len(manifest['files'])} files in {bin_directory}")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("bin_directory", type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
@click.option("--private-key", "-k", type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
              help="Path to SSH private key (defaults to ~/.ssh/id_rsa)")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--debug", "-d", is_flag=True, help="Debug output")
def verify(bin_directory: Path, private_key: Optional[Path], verbose: bool, debug: bool) -> None:
    """Verify signatures of all files in a bin directory."""
    try:
        signer = BinDirSigner(private_key, debug=debug)
        is_valid = signer.verify_bin_directory(bin_directory)
        
        if is_valid:
            signed_files = signer.get_signed_files(bin_directory)
            if verbose:
                click.echo(f"✓ All signatures valid for {len(signed_files)} files in {bin_directory}")
                for filename in signed_files:
                    click.echo(f"  ✓ {filename}")
            else:
                click.echo(f"✓ All signatures valid ({len(signed_files)} files)")
        else:
            click.echo("✗ Signature verification failed", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("bin_directory", type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
@click.option("--private-key", "-k", type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
              help="Path to SSH private key (defaults to ~/.ssh/id_rsa)")
@click.option("--debug", "-d", is_flag=True, help="Debug output")
def list_files(bin_directory: Path, private_key: Optional[Path], debug: bool) -> None:
    """List all signed files in a bin directory."""
    try:
        signer = BinDirSigner(private_key, debug=debug)
        signed_files = signer.get_signed_files(bin_directory)
        
        if signed_files:
            click.echo(f"Signed files in {bin_directory}:")
            for filename in signed_files:
                click.echo(f"  {filename}")
        else:
            click.echo(f"No signed files found in {bin_directory}")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--shell", "-s", type=click.Choice(["fish", "bash", "zsh"]), 
              help="Install for specific shell (default: auto-detect)")
@click.option("--all", "-a", is_flag=True, help="Install for all detected shells")
def install(shell: Optional[str], all: bool) -> None:
    """Install shell integration for automatic PATH management."""
    try:
        installer = ShellIntegrationInstaller()
        
        if all:
            results = installer.install_all()
            for shell_name, (success, message) in results.items():
                status = "✓" if success else "✗"
                click.echo(f"{status} {shell_name}: {message}")
        elif shell:
            success, message = installer.install_for_shell(shell)
            status = "✓" if success else "✗"
            click.echo(f"{status} {shell}: {message}")
            if not success:
                sys.exit(1)
        else:
            # Auto-detect and install for all available shells
            detected_shells = installer.detect_shells()
            if not detected_shells:
                click.echo("No supported shells with config files detected.")
                click.echo("Supported shells: fish, bash, zsh")
                sys.exit(1)
            
            click.echo(f"Detected shells: {', '.join(detected_shells)}")
            for shell_name in detected_shells:
                success, message = installer.install_for_shell(shell_name)
                status = "✓" if success else "✗"
                click.echo(f"{status} {shell_name}: {message}")
                
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--shell", "-s", type=click.Choice(["fish", "bash", "zsh"]), 
              help="Uninstall for specific shell")
@click.option("--all", "-a", is_flag=True, help="Uninstall for all shells")
def uninstall(shell: Optional[str], all: bool) -> None:
    """Uninstall shell integration."""
    try:
        installer = ShellIntegrationInstaller()
        
        if all:
            results = installer.uninstall_all()
            for shell_name, (success, message) in results.items():
                status = "✓" if success else "✗"
                click.echo(f"{status} {shell_name}: {message}")
        elif shell:
            success, message = installer.uninstall_for_shell(shell)
            status = "✓" if success else "✗"
            click.echo(f"{status} {shell}: {message}")
            if not success:
                sys.exit(1)
        else:
            click.echo("Please specify --shell or --all")
            sys.exit(1)
                
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def status() -> None:
    """Show shell integration installation status."""
    try:
        installer = ShellIntegrationInstaller()
        status_info = installer.status()
        
        click.echo("Shell Integration Status:")
        click.echo("=" * 50)
        
        for shell, info in status_info.items():
            shell_available = "✓" if info["shell_available"] else "✗"
            config_exists = "✓" if info["config_exists"] else "✗"
            integration_installed = "✓" if info["integration_installed"] else "✗"
            
            click.echo(f"\n{shell.upper()}:")
            click.echo(f"  Shell available:        {shell_available}")
            click.echo(f"  Config file exists:     {config_exists}")
            click.echo(f"  Integration installed:  {integration_installed}")
            
            if info["shell_available"] and info["config_exists"] and not info["integration_installed"]:
                click.echo(f"  → Run: sign-bin-dir install --shell {shell}")
                
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def main() -> None:
    """Main entry point for sign-bin-dir command."""
    cli()


if __name__ == "__main__":
    main() 
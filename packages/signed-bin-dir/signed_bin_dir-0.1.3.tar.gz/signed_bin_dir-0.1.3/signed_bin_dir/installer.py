"""Shell integration installer for signed-bin-dir."""

import os
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ShellIntegrationInstaller:
    """Installs shell integration for signed-bin-dir."""
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize with project root path."""
        if project_root is None:
            # Try to find shell integrations in installed package first
            try:
                import signed_bin_dir
                package_path = Path(signed_bin_dir.__file__).parent
                
                # For pip-installed packages, look in multiple possible locations
                possible_locations = [
                    # Standard pip install location (site-packages/../share)
                    package_path.parent.parent / "share" / "signed-bin-dir" / "shell_integrations",
                    # Alternative pip install location (venv/share)
                    package_path.parent.parent.parent / "share" / "signed-bin-dir" / "shell_integrations",
                    # Development install location (project root)
                    package_path.parent / "shell_integrations",
                    # Legacy location (site-packages/shell_integrations)
                    package_path.parent / "shell_integrations",
                ]
                
                # Find the first location that exists
                for location in possible_locations:
                    if location.exists() and (location / "signed_bin_dir.fish").exists():
                        self.shell_integrations_dir = location
                        self.project_root = location.parent.parent if "share" in str(location) else location.parent
                        break
                else:
                    # Fallback: try to find project root by looking for pyproject.toml
                    current = package_path
                    while current != current.parent:
                        if (current / "pyproject.toml").exists():
                            self.project_root = current
                            self.shell_integrations_dir = current / "shell_integrations"
                            break
                        current = current.parent
                    else:
                        # Last resort: use package directory
                        self.project_root = package_path.parent
                        self.shell_integrations_dir = package_path.parent / "shell_integrations"
                        
            except ImportError:
                # Package not installed, try to find project root
                current = Path(__file__).parent
                while current != current.parent:
                    if (current / "pyproject.toml").exists():
                        project_root = current
                        break
                    current = current.parent
                else:
                    # Fallback to parent of this file
                    project_root = Path(__file__).parent.parent
                
                self.project_root = project_root
                self.shell_integrations_dir = project_root / "shell_integrations"
        else:
            self.project_root = project_root
            self.shell_integrations_dir = project_root / "shell_integrations"
    
    def get_shell_configs(self) -> Dict[str, List[Path]]:
        """Get shell configuration file paths for different shells."""
        home = Path.home()
        
        configs = {
            "fish": [
                home / ".config" / "fish" / "config.fish",
            ],
            "bash": [
                home / ".bashrc",
                home / ".bash_profile",
            ],
            "zsh": [
                home / ".zshrc",
            ]
        }
        
        return configs
    
    def detect_shells(self) -> List[str]:
        """Detect which shells are available and have config files."""
        available_shells = []
        configs = self.get_shell_configs()
        
        for shell, config_paths in configs.items():
            # Check if shell is installed
            if shutil.which(shell):
                # Check if any config file exists
                for config_path in config_paths:
                    if config_path.exists():
                        available_shells.append(shell)
                        break
        
        return available_shells
    
    def get_integration_file(self, shell: str) -> Path:
        """Get the integration file path for a shell."""
        if shell == "fish":
            return self.shell_integrations_dir / "signed_bin_dir.fish"
        elif shell in ["bash", "zsh"]:
            return self.shell_integrations_dir / "signed_bin_dir.bash"
        else:
            raise ValueError(f"Unsupported shell: {shell}")
    
    def get_source_line(self, shell: str) -> str:
        """Get the source line to add to shell config."""
        integration_file = self.get_integration_file(shell)
        
        if shell == "fish":
            return f"source {integration_file}"
        else:  # bash, zsh
            return f"source {integration_file}"
    
    def is_already_installed(self, config_path: Path, shell: str) -> bool:
        """Check if integration is already installed in config file."""
        if not config_path.exists():
            return False
        
        source_line = self.get_source_line(shell)
        integration_file = self.get_integration_file(shell)
        
        try:
            with open(config_path, 'r') as f:
                content = f.read()
                
            # Check for exact source line or reference to integration file
            return (
                source_line in content or
                str(integration_file) in content or
                "signed_bin_dir" in content
            )
        except Exception:
            return False
    
    def install_for_shell(self, shell: str, config_path: Optional[Path] = None) -> Tuple[bool, str]:
        """Install integration for a specific shell."""
        configs = self.get_shell_configs()
        
        if shell not in configs:
            return False, f"Unsupported shell: {shell}"
        
        # Choose config file
        if config_path is None:
            # Find the first existing config file
            for path in configs[shell]:
                if path.exists():
                    config_path = path
                    break
            else:
                # Create the default config file
                config_path = configs[shell][0]
                config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if already installed
        if self.is_already_installed(config_path, shell):
            return True, f"Integration already installed in {config_path}"
        
        # Check if integration file exists
        integration_file = self.get_integration_file(shell)
        if not integration_file.exists():
            return False, f"Integration file not found: {integration_file}"
        
        # Add source line to config
        source_line = self.get_source_line(shell)
        comment = f"# Added by signed-bin-dir installer"
        
        try:
            with open(config_path, 'a') as f:
                f.write(f"\n{comment}\n{source_line}\n")
            
            return True, f"Integration installed in {config_path}"
        except Exception as e:
            return False, f"Failed to write to {config_path}: {e}"
    
    def uninstall_for_shell(self, shell: str, config_path: Optional[Path] = None) -> Tuple[bool, str]:
        """Uninstall integration for a specific shell."""
        configs = self.get_shell_configs()
        
        if shell not in configs:
            return False, f"Unsupported shell: {shell}"
        
        # Choose config file
        if config_path is None:
            # Find the first existing config file that has the integration
            for path in configs[shell]:
                if path.exists() and self.is_already_installed(path, shell):
                    config_path = path
                    break
            else:
                return True, f"Integration not found in any {shell} config files"
        
        if not config_path.exists():
            return True, f"Config file does not exist: {config_path}"
        
        try:
            with open(config_path, 'r') as f:
                lines = f.readlines()
            
            # Remove lines related to signed-bin-dir
            filtered_lines = []
            skip_next = False
            
            for line in lines:
                if skip_next:
                    skip_next = False
                    continue
                
                if "signed-bin-dir" in line.lower() or "signed_bin_dir" in line:
                    # Skip this line and potentially the next one if it's a source line
                    if line.strip().startswith("#"):
                        skip_next = True
                    continue
                
                filtered_lines.append(line)
            
            # Write back the filtered content
            with open(config_path, 'w') as f:
                f.writelines(filtered_lines)
            
            return True, f"Integration removed from {config_path}"
        except Exception as e:
            return False, f"Failed to modify {config_path}: {e}"
    
    def install_all(self) -> Dict[str, Tuple[bool, str]]:
        """Install integration for all detected shells."""
        results = {}
        detected_shells = self.detect_shells()
        
        for shell in detected_shells:
            results[shell] = self.install_for_shell(shell)
        
        return results
    
    def uninstall_all(self) -> Dict[str, Tuple[bool, str]]:
        """Uninstall integration for all shells."""
        results = {}
        configs = self.get_shell_configs()
        
        for shell in configs.keys():
            results[shell] = self.uninstall_for_shell(shell)
        
        return results
    
    def status(self) -> Dict[str, Dict[str, bool]]:
        """Get installation status for all shells."""
        status_info = {}
        configs = self.get_shell_configs()
        
        for shell, config_paths in configs.items():
            shell_installed = shutil.which(shell) is not None
            config_exists = any(path.exists() for path in config_paths)
            integration_installed = any(
                self.is_already_installed(path, shell) 
                for path in config_paths 
                if path.exists()
            )
            
            status_info[shell] = {
                "shell_available": shell_installed,
                "config_exists": config_exists,
                "integration_installed": integration_installed,
            }
        
        return status_info 
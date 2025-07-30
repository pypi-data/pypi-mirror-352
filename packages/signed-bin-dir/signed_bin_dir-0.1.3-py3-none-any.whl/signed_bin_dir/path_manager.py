"""PATH management functionality for shell integrations."""

import os
from pathlib import Path
from typing import List, Optional, Set

from .signer import BinDirSigner


class PathManager:
    """Manages PATH modifications for signed bin directories."""
    
    def __init__(self, private_key_path: Optional[Path] = None):
        """Initialize with SSH private key path."""
        self.signer = BinDirSigner(private_key_path)
        self._managed_paths: Set[str] = set()
    
    def find_bin_directories(self, start_path: Path) -> List[Path]:
        """Find all bin directories from current path up to root."""
        bin_dirs = []
        current_path = start_path.resolve()
        
        # Check current directory and all parent directories
        while current_path != current_path.parent:
            bin_dir = current_path / "bin"
            if bin_dir.exists() and bin_dir.is_dir():
                manifest_path = bin_dir / ".signed-manifest.json"
                if manifest_path.exists():
                    bin_dirs.append(bin_dir)
            current_path = current_path.parent
            
        return bin_dirs
    
    def get_verified_bin_directories(self, start_path: Path) -> List[Path]:
        """Get all verified bin directories from current path up to root."""
        bin_dirs = self.find_bin_directories(start_path)
        verified_dirs = []
        
        for bin_dir in bin_dirs:
            try:
                if self.signer.verify_bin_directory(bin_dir):
                    verified_dirs.append(bin_dir)
            except Exception:
                # Skip directories that can't be verified
                continue
                
        return verified_dirs
    
    def should_add_to_path(self, bin_dir: Path) -> bool:
        """Check if a bin directory should be added to PATH."""
        return (
            bin_dir.exists() and 
            bin_dir.is_dir() and
            self.signer.verify_bin_directory(bin_dir)
        )
    
    def get_path_additions(self, current_dir: Path) -> List[str]:
        """Get list of directories that should be added to PATH."""
        verified_dirs = self.get_verified_bin_directories(current_dir)
        return [str(bin_dir.absolute()) for bin_dir in verified_dirs]
    
    def generate_path_string(self, current_dir: Path, existing_path: Optional[str] = None) -> str:
        """Generate new PATH string with verified bin directories."""
        if existing_path is None:
            existing_path = os.environ.get("PATH", "")
            
        path_additions = self.get_path_additions(current_dir)
        
        # Remove any previously managed paths to avoid duplicates
        path_parts = existing_path.split(os.pathsep) if existing_path else []
        cleaned_parts = [p for p in path_parts if p not in self._managed_paths]
        
        # Update managed paths
        self._managed_paths = set(path_additions)
        
        # Prepend new verified directories
        new_path_parts = path_additions + cleaned_parts
        
        return os.pathsep.join(new_path_parts)
    
    def get_shell_export_command(self, current_dir: Path, shell: str = "bash") -> str:
        """Get shell command to export updated PATH."""
        new_path = self.generate_path_string(current_dir)
        
        if shell.lower() in ["fish"]:
            return f'set -gx PATH "{new_path}"'
        else:  # bash, zsh, etc.
            return f'export PATH="{new_path}"' 
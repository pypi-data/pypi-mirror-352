"""Core signing and verification functionality."""

import getpass
import hashlib
import json
import os
import stat
from pathlib import Path
from typing import Dict, List, Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.exceptions import InvalidSignature


class BinDirSigner:
    """Signs and verifies binary directories using SSH private keys."""
    
    def __init__(self, private_key_path: Optional[Path] = None, debug: bool = False):
        """Initialize with SSH private key path."""
        if private_key_path is None:
            private_key_path = Path.home() / ".ssh" / "id_rsa"
        
        self.private_key_path = private_key_path
        self.public_key_path = private_key_path.with_suffix(".pub")
        self.debug = debug
        
    def _debug_print(self, message: str) -> None:
        """Print debug message if debug mode is enabled."""
        if self.debug:
            print(f"DEBUG: {message}")
        
    def _load_private_key(self) -> rsa.RSAPrivateKey:
        """Load the SSH private key."""
        if not self.private_key_path.exists():
            raise FileNotFoundError(f"Private key not found: {self.private_key_path}")
        
        self._debug_print(f"Attempting to load private key from: {self.private_key_path}")
        
        try:
            with open(self.private_key_path, "rb") as key_file:
                key_data = key_file.read()
                self._debug_print(f"Key file size: {len(key_data)} bytes")
                self._debug_print(f"Key starts with: {key_data[:50]}")
                
                # Try to load without password first
                password = None
                for attempt in range(3):  # Allow up to 3 password attempts
                    try:
                        # Try to load as PEM first
                        try:
                            private_key = serialization.load_pem_private_key(
                                key_data,
                                password=password,
                            )
                            self._debug_print("Successfully loaded as PEM format")
                            break
                        except Exception as pem_error:
                            self._debug_print(f"PEM loading failed: {pem_error}")
                            
                            # Try to load as OpenSSH format
                            try:
                                private_key = serialization.load_ssh_private_key(
                                    key_data,
                                    password=password,
                                )
                                self._debug_print("Successfully loaded as OpenSSH format")
                                break
                            except Exception as ssh_error:
                                self._debug_print(f"OpenSSH loading failed: {ssh_error}")
                                
                                # Check if it's a password issue
                                if "password" in str(ssh_error).lower() or "passphrase" in str(ssh_error).lower():
                                    if password is None:
                                        self._debug_print("Key appears to be password-protected, prompting for passphrase")
                                        try:
                                            password_str = getpass.getpass("Enter passphrase for SSH key: ")
                                            password = password_str.encode() if password_str else None
                                            continue  # Try again with password
                                        except KeyboardInterrupt:
                                            raise ValueError("Password entry cancelled")
                                    else:
                                        self._debug_print("Invalid password provided")
                                        if attempt < 2:  # Not the last attempt
                                            print("Invalid passphrase. Please try again.")
                                            try:
                                                password_str = getpass.getpass("Enter passphrase for SSH key: ")
                                                password = password_str.encode() if password_str else None
                                                continue
                                            except KeyboardInterrupt:
                                                raise ValueError("Password entry cancelled")
                                
                                # If we get here on the last attempt, raise the error
                                if attempt == 2:
                                    raise ValueError(f"Could not load private key after {attempt + 1} attempts. PEM error: {pem_error}, SSH error: {ssh_error}")
                    except Exception as load_error:
                        if "password" not in str(load_error).lower() and "passphrase" not in str(load_error).lower():
                            # Not a password issue, re-raise immediately
                            raise
                        # Password issue, continue to next attempt
                        continue
                else:
                    # This shouldn't happen due to the break statements, but just in case
                    raise ValueError("Failed to load private key after maximum attempts")
                
        except Exception as e:
            self._debug_print(f"Failed to read key file: {e}")
            raise
            
        if not isinstance(private_key, rsa.RSAPrivateKey):
            raise ValueError(f"Only RSA keys are supported, got {type(private_key)}")
            
        self._debug_print("Private key loaded successfully")
        return private_key
    
    def _load_public_key(self) -> rsa.RSAPublicKey:
        """Load the SSH public key."""
        if not self.public_key_path.exists():
            raise FileNotFoundError(f"Public key not found: {self.public_key_path}")
        
        self._debug_print(f"Attempting to load public key from: {self.public_key_path}")
        
        try:
            with open(self.public_key_path, "r") as key_file:
                public_key_data = key_file.read().strip()
                self._debug_print(f"Public key data length: {len(public_key_data)}")
                self._debug_print(f"Public key starts with: {public_key_data[:50]}")
                
            # Parse SSH public key format
            parts = public_key_data.split()
            if len(parts) < 2:
                raise ValueError("Invalid SSH public key format - not enough parts")
            
            key_type = parts[0]
            self._debug_print(f"Key type: {key_type}")
            
            if key_type not in ["ssh-rsa", "rsa-sha2-256", "rsa-sha2-512"]:
                raise ValueError(f"Unsupported key type: {key_type}. Only RSA keys are supported.")
            
            # Use cryptography's SSH public key loader
            public_key = serialization.load_ssh_public_key(public_key_data.encode())
            self._debug_print("Successfully loaded SSH public key")
            
        except Exception as e:
            self._debug_print(f"Failed to load public key: {e}")
            raise
        
        if not isinstance(public_key, rsa.RSAPublicKey):
            raise ValueError(f"Only RSA keys are supported, got {type(public_key)}")
            
        self._debug_print("Public key loaded successfully")
        return public_key
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def _is_executable(self, file_path: Path) -> bool:
        """Check if a file is executable."""
        return os.access(file_path, os.X_OK)
    
    def sign_bin_directory(self, bin_dir: Path) -> Dict:
        """Sign all executable files in a bin directory and create manifest."""
        if not bin_dir.exists() or not bin_dir.is_dir():
            raise ValueError(f"Directory does not exist: {bin_dir}")
            
        private_key = self._load_private_key()
        
        manifest = {
            "version": "1.0",
            "signer": str(self.public_key_path),
            "bin_directory": str(bin_dir.absolute()),
            "files": {}
        }
        
        # Find all executable files
        for file_path in bin_dir.iterdir():
            if file_path.is_file() and self._is_executable(file_path):
                file_hash = self._calculate_file_hash(file_path)
                
                # Sign the hash
                signature = private_key.sign(
                    file_hash.encode(),
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                
                manifest["files"][file_path.name] = {
                    "hash": file_hash,
                    "signature": signature.hex(),
                    "size": file_path.stat().st_size,
                    "mode": oct(file_path.stat().st_mode)
                }
        
        # Save manifest
        manifest_path = bin_dir / ".signed-manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
            
        return manifest
    
    def verify_bin_directory(self, bin_dir: Path) -> bool:
        """Verify the signatures of all files in a bin directory."""
        manifest_path = bin_dir / ".signed-manifest.json"
        
        if not manifest_path.exists():
            return False
            
        try:
            with open(manifest_path, "r") as f:
                manifest = json.load(f)
                
            public_key = self._load_public_key()
            
            # Verify each file
            for filename, file_info in manifest["files"].items():
                file_path = bin_dir / filename
                
                if not file_path.exists():
                    return False
                    
                # Check if file has been modified
                current_hash = self._calculate_file_hash(file_path)
                if current_hash != file_info["hash"]:
                    return False
                    
                # Verify signature
                signature = bytes.fromhex(file_info["signature"])
                try:
                    public_key.verify(
                        signature,
                        current_hash.encode(),
                        padding.PSS(
                            mgf=padding.MGF1(hashes.SHA256()),
                            salt_length=padding.PSS.MAX_LENGTH
                        ),
                        hashes.SHA256()
                    )
                except InvalidSignature:
                    return False
                    
            return True
            
        except (json.JSONDecodeError, KeyError, ValueError):
            return False
    
    def get_signed_files(self, bin_dir: Path) -> List[str]:
        """Get list of signed executable files in a directory."""
        manifest_path = bin_dir / ".signed-manifest.json"
        
        if not manifest_path.exists():
            return []
            
        try:
            with open(manifest_path, "r") as f:
                manifest = json.load(f)
            return list(manifest["files"].keys())
        except (json.JSONDecodeError, KeyError):
            return [] 
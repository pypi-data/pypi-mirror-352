"""Tests for the signer module."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from signed_bin_dir.signer import BinDirSigner


class TestBinDirSigner:
    """Test cases for BinDirSigner class."""
    
    def test_init_default_key_path(self):
        """Test initialization with default SSH key path."""
        signer = BinDirSigner()
        expected_path = Path.home() / ".ssh" / "id_rsa"
        assert signer.private_key_path == expected_path
        assert signer.public_key_path == expected_path.with_suffix(".pub")
    
    def test_init_custom_key_path(self):
        """Test initialization with custom SSH key path."""
        custom_path = Path("/custom/path/key")
        signer = BinDirSigner(custom_path)
        assert signer.private_key_path == custom_path
        assert signer.public_key_path == custom_path.with_suffix(".pub")
    
    def test_calculate_file_hash(self):
        """Test file hash calculation."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_path = Path(f.name)
        
        try:
            signer = BinDirSigner()
            hash_value = signer._calculate_file_hash(temp_path)
            # SHA-256 of "test content"
            expected = "1eebdf4fdc9fc7bf283031b93f9aef3338de9052f584b10f4e8c59d6b3c9b1e8"
            assert hash_value == expected
        finally:
            temp_path.unlink()
    
    def test_is_executable(self):
        """Test executable file detection."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            signer = BinDirSigner()
            
            # File should not be executable initially
            assert not signer._is_executable(temp_path)
            
            # Make file executable
            temp_path.chmod(0o755)
            assert signer._is_executable(temp_path)
        finally:
            temp_path.unlink()
    
    def test_get_signed_files_no_manifest(self):
        """Test getting signed files when no manifest exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            bin_dir = Path(temp_dir)
            signer = BinDirSigner()
            
            signed_files = signer.get_signed_files(bin_dir)
            assert signed_files == []
    
    def test_get_signed_files_with_manifest(self):
        """Test getting signed files when manifest exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            bin_dir = Path(temp_dir)
            manifest_path = bin_dir / ".signed-manifest.json"
            
            # Create a mock manifest
            manifest = {
                "version": "1.0",
                "files": {
                    "tool1": {"hash": "abc123", "signature": "def456"},
                    "tool2": {"hash": "ghi789", "signature": "jkl012"}
                }
            }
            
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f)
            
            signer = BinDirSigner()
            signed_files = signer.get_signed_files(bin_dir)
            
            assert set(signed_files) == {"tool1", "tool2"}
    
    @patch('signed_bin_dir.signer.BinDirSigner._load_private_key')
    def test_sign_bin_directory_empty(self, mock_load_key):
        """Test signing an empty bin directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            bin_dir = Path(temp_dir)
            
            # Mock the private key
            mock_key = Mock()
            mock_load_key.return_value = mock_key
            
            signer = BinDirSigner()
            manifest = signer.sign_bin_directory(bin_dir)
            
            assert manifest["version"] == "1.0"
            assert manifest["files"] == {}
            
            # Check that manifest file was created
            manifest_path = bin_dir / ".signed-manifest.json"
            assert manifest_path.exists()
    
    def test_sign_bin_directory_nonexistent(self):
        """Test signing a non-existent directory raises error."""
        signer = BinDirSigner()
        nonexistent_dir = Path("/nonexistent/directory")
        
        with pytest.raises(ValueError, match="Directory does not exist"):
            signer.sign_bin_directory(nonexistent_dir) 
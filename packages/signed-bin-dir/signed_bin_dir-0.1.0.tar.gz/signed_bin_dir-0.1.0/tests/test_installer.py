"""Tests for the installer module."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from signed_bin_dir.installer import ShellIntegrationInstaller


class TestShellIntegrationInstaller:
    """Test cases for ShellIntegrationInstaller class."""
    
    def test_init_with_project_root(self):
        """Test initialization with explicit project root."""
        project_root = Path("/test/project")
        installer = ShellIntegrationInstaller(project_root)
        
        assert installer.project_root == project_root
        assert installer.shell_integrations_dir == project_root / "shell_integrations"
    
    def test_get_shell_configs(self):
        """Test getting shell configuration paths."""
        installer = ShellIntegrationInstaller()
        configs = installer.get_shell_configs()
        
        assert "fish" in configs
        assert "bash" in configs
        assert "zsh" in configs
        
        # Check that fish config includes the expected path
        fish_configs = configs["fish"]
        assert any("config.fish" in str(path) for path in fish_configs)
        
        # Check that bash configs include expected paths
        bash_configs = configs["bash"]
        assert any(".bashrc" in str(path) for path in bash_configs)
    
    @patch('shutil.which')
    def test_detect_shells(self, mock_which):
        """Test shell detection."""
        # Mock shell availability
        def which_side_effect(shell):
            return "/usr/bin/" + shell if shell in ["fish", "bash"] else None
        
        mock_which.side_effect = which_side_effect
        
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            
            # Create mock config files
            fish_config = home / ".config" / "fish" / "config.fish"
            fish_config.parent.mkdir(parents=True)
            fish_config.touch()
            
            bash_config = home / ".bashrc"
            bash_config.touch()
            
            installer = ShellIntegrationInstaller()
            
            # Mock the home directory
            with patch.object(Path, 'home', return_value=home):
                detected = installer.detect_shells()
                
            assert "fish" in detected
            assert "bash" in detected
            assert "zsh" not in detected  # No config file created
    
    def test_get_integration_file(self):
        """Test getting integration file paths."""
        project_root = Path("/test/project")
        installer = ShellIntegrationInstaller(project_root)
        
        fish_file = installer.get_integration_file("fish")
        assert fish_file == project_root / "shell_integrations" / "signed_bin_dir.fish"
        
        bash_file = installer.get_integration_file("bash")
        assert bash_file == project_root / "shell_integrations" / "signed_bin_dir.bash"
        
        zsh_file = installer.get_integration_file("zsh")
        assert zsh_file == project_root / "shell_integrations" / "signed_bin_dir.bash"
        
        with pytest.raises(ValueError, match="Unsupported shell"):
            installer.get_integration_file("unsupported")
    
    def test_get_source_line(self):
        """Test generating source lines for different shells."""
        project_root = Path("/test/project")
        installer = ShellIntegrationInstaller(project_root)
        
        fish_line = installer.get_source_line("fish")
        expected_fish = f"source {project_root}/shell_integrations/signed_bin_dir.fish"
        assert fish_line == expected_fish
        
        bash_line = installer.get_source_line("bash")
        expected_bash = f"source {project_root}/shell_integrations/signed_bin_dir.bash"
        assert bash_line == expected_bash
    
    def test_is_already_installed(self):
        """Test checking if integration is already installed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.fish"
            installer = ShellIntegrationInstaller()
            
            # Test with non-existent file
            assert not installer.is_already_installed(config_path, "fish")
            
            # Test with file that doesn't contain integration
            config_path.write_text("# Some other config\nset -x PATH /usr/bin\n")
            assert not installer.is_already_installed(config_path, "fish")
            
            # Test with file that contains integration
            config_path.write_text("# Some config\nsource /path/to/signed_bin_dir.fish\n")
            assert installer.is_already_installed(config_path, "fish")
    
    def test_install_for_shell(self):
        """Test installing integration for a specific shell."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "project"
            project_root.mkdir()
            
            # Create integration file
            integrations_dir = project_root / "shell_integrations"
            integrations_dir.mkdir()
            fish_integration = integrations_dir / "signed_bin_dir.fish"
            fish_integration.write_text("# Fish integration content")
            
            # Create config file
            config_path = Path(temp_dir) / "config.fish"
            config_path.write_text("# Existing config\n")
            
            installer = ShellIntegrationInstaller(project_root)
            success, message = installer.install_for_shell("fish", config_path)
            
            assert success
            assert "Integration installed" in message
            
            # Check that the source line was added
            content = config_path.read_text()
            assert "signed-bin-dir installer" in content
            assert str(fish_integration) in content
    
    def test_install_already_installed(self):
        """Test installing when integration is already present."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "project"
            project_root.mkdir()
            
            # Create integration file
            integrations_dir = project_root / "shell_integrations"
            integrations_dir.mkdir()
            fish_integration = integrations_dir / "signed_bin_dir.fish"
            fish_integration.write_text("# Fish integration content")
            
            # Create config file with existing integration
            config_path = Path(temp_dir) / "config.fish"
            config_path.write_text(f"source {fish_integration}\n")
            
            installer = ShellIntegrationInstaller(project_root)
            success, message = installer.install_for_shell("fish", config_path)
            
            assert success
            assert "already installed" in message
    
    def test_uninstall_for_shell(self):
        """Test uninstalling integration for a specific shell."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "project"
            installer = ShellIntegrationInstaller(project_root)
            
            # Create config file with integration
            config_path = Path(temp_dir) / "config.fish"
            config_content = """# Existing config
# Added by signed-bin-dir installer
source /path/to/signed_bin_dir.fish
# More config
"""
            config_path.write_text(config_content)
            
            success, message = installer.uninstall_for_shell("fish", config_path)
            
            assert success
            assert "removed" in message
            
            # Check that integration lines were removed
            content = config_path.read_text()
            assert "signed-bin-dir" not in content
            assert "signed_bin_dir" not in content
            assert "# Existing config" in content  # Other content preserved
            assert "# More config" in content
    
    def test_status(self):
        """Test getting installation status."""
        with patch('shutil.which') as mock_which:
            mock_which.return_value = "/usr/bin/fish"  # Fish is available
            
            with tempfile.TemporaryDirectory() as temp_dir:
                home = Path(temp_dir)
                
                # Create fish config with integration
                fish_config = home / ".config" / "fish" / "config.fish"
                fish_config.parent.mkdir(parents=True)
                fish_config.write_text("source /path/to/signed_bin_dir.fish")
                
                installer = ShellIntegrationInstaller()
                
                with patch.object(Path, 'home', return_value=home):
                    status = installer.status()
                
                assert "fish" in status
                fish_status = status["fish"]
                assert fish_status["shell_available"] is True
                assert fish_status["config_exists"] is True
                assert fish_status["integration_installed"] is True 
"""
Installation utilities for Ollama.
"""
import os
import sys
import logging
import subprocess
from typing import Optional, Tuple

from .exceptions import InstallationError
from . import utils

logger = logging.getLogger('getllm.ollama.install')

class OllamaInstaller:
    """Handles installation of Ollama and its dependencies."""
    
    def __init__(self, ollama_path: str = None):
        """Initialize the installer.
        
        Args:
            ollama_path: Path to the Ollama executable
        """
        self.ollama_path = ollama_path or os.getenv('OLLAMA_PATH', 'ollama')
    
    def is_installed(self) -> bool:
        """Check if Ollama is installed."""
        try:
            result = subprocess.run(
                [self.ollama_path, '--version'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def install(self, method: str = 'auto') -> bool:
        """Install Ollama using the specified method.
        
        Args:
            method: Installation method ('auto', 'direct', 'docker', 'bexy')
            
        Returns:
            bool: True if installation was successful
            
        Raises:
            InstallationError: If installation fails
        """
        if method == 'auto':
            if utils.is_linux():
                return self.install_linux()
            elif utils.is_macos():
                return self.install_macos()
            elif utils.is_windows():
                return self.install_windows()
            else:
                return self.install_docker()
        elif method == 'direct':
            if utils.is_linux():
                return self.install_linux()
            elif utils.is_macos():
                return self.install_macos()
            elif utils.is_windows():
                return self.install_windows()
            else:
                raise InstallationError("Direct installation not supported on this platform")
        elif method == 'docker':
            return self.install_docker()
        elif method == 'bexy':
            return self.install_bexy()
        else:
            raise ValueError(f"Unknown installation method: {method}")
    
    def install_linux(self) -> bool:
        """Install Ollama on Linux."""
        logger.info("Installing Ollama on Linux...")
        
        # Check for curl
        if not shutil.which('curl'):
            # Try to install curl
            success, _ = utils.run_command('apt-get update && apt-get install -y curl')
            if not success:
                raise InstallationError("curl is required but could not be installed")
        
        # Download and run the install script
        install_cmd = "curl -fsSL https://ollama.com/install.sh | sh"
        success, output = utils.run_command(install_cmd, use_sudo=True)
        
        if not success:
            raise InstallationError(f"Failed to install Ollama: {output}")
        
        # Add user to the ollama group if not already a member
        current_user = os.getenv('USER')
        if current_user:
            utils.run_command(f"usermod -aG ollama {current_user}", use_sudo=True)
            logger.info(f"Added user {current_user} to the ollama group")
        
        logger.info("Ollama installed successfully on Linux")
        return True
    
    def install_macos(self) -> bool:
        """Install Ollama on macOS."""
        logger.info("Installing Ollama on macOS...")
        
        # Check for Homebrew
        if not shutil.which('brew'):
            # Install Homebrew if not present
            install_brew = "/bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            success, output = utils.run_command(install_brew)
            if not success:
                raise InstallationError(f"Failed to install Homebrew: {output}")
        
        # Install Ollama using Homebrew
        install_cmd = "brew install ollama"
        success, output = utils.run_command(install_cmd)
        
        if not success:
            raise InstallationError(f"Failed to install Ollama: {output}")
        
        logger.info("Ollama installed successfully on macOS")
        return True
    
    def install_windows(self) -> bool:
        """Install Ollama on Windows."""
        logger.info("Installing Ollama on Windows...")
        
        # Check for winget
        try:
            subprocess.run(
                ["winget", "--version"],
                capture_output=True,
                check=True,
                shell=True
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            raise InstallationError(
                "winget is required but not found. "
                "Please install it from the Microsoft Store."
            )
        
        # Install Ollama using winget
        install_cmd = "winget install ollama.ollama"
        success, output = utils.run_command(install_cmd, shell=True)
        
        if not success:
            raise InstallationError(f"Failed to install Ollama: {output}")
        
        logger.info("Ollama installed successfully on Windows")
        return True
    
    def install_docker(self) -> bool:
        """Install and run Ollama using Docker."""
        logger.info("Installing Ollama using Docker...")
        
        # Check if Docker is installed
        docker_check = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True
        )
        
        if docker_check.returncode != 0:
            raise InstallationError(
                "Docker is not installed. Please install Docker first."
            )
        
        # Pull the Ollama Docker image
        pull_cmd = "docker pull ollama/ollama"
        success, output = utils.run_command(pull_cmd)
        if not success:
            raise InstallationError(f"Failed to pull Ollama Docker image: {output}")
        
        # Create a Docker volume for persistent storage
        volume_cmd = "docker volume create ollama_data"
        success, output = utils.run_command(volume_cmd)
        if not success and "already exists" not in output:
            logger.warning(f"Failed to create Docker volume (may already exist): {output}")
        
        # Run the Ollama container
        run_cmd = (
            "docker run -d "
            "--name ollama "
            "-p 11434:11434 "
            "-v ollama_data:/root/.ollama "
            "--restart unless-stopped "
            "ollama/ollama"
        )
        
        success, output = utils.run_command(run_cmd)
        if not success:
            raise InstallationError(f"Failed to start Ollama container: {output}")
        
        logger.info("Ollama is running in a Docker container")
        return True
    
    def install_bexy(self) -> bool:
        """Set up Ollama in a bexy sandbox environment."""
        logger.warning("Bexy sandbox installation is not fully implemented")
        return False

def ensure_ollama_installed(ollama_path: str = None) -> bool:
    """Ensure Ollama is installed, installing it if necessary.
    
    Args:
        ollama_path: Path to the Ollama executable
        
    Returns:
        bool: True if Ollama is installed, False otherwise
    """
    installer = OllamaInstaller(ollama_path)
    
    if installer.is_installed():
        return True
    
    logger.info("Ollama is not installed. Attempting to install...")
    try:
        return installer.install()
    except Exception as e:
        logger.error(f"Failed to install Ollama: {e}")
        return False

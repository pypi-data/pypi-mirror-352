"""
Utility functions for the Ollama integration.
"""
import os
import logging
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import shutil
import subprocess
import platform
import re

logger = logging.getLogger('getllm.ollama.utils')

def get_package_dir() -> Path:
    """Get the .getllm package directory."""
    package_dir = Path.home() / '.getllm'
    package_dir.mkdir(exist_ok=True)
    return package_dir

def check_disk_space(required_space_gb: float = None, 
                    model_name: str = None) -> Tuple[bool, float, float]:
    """
    Check if there is enough disk space available.
    
    Args:
        required_space_gb: Required space in GB, if known
        model_name: Name of the model to check space for
        
    Returns:
        Tuple of (has_enough_space, available_gb, required_gb)
    """
    if required_space_gb is None:
        # Default required space if not specified (in GB)
        required_space_gb = 20.0  # Default to 20GB if not specified
        logger.warning(f"No required space specified, using default: {required_space_gb}GB")
    
    # Get disk usage statistics
    total, used, free = shutil.disk_usage("/")
    
    # Convert bytes to GB
    available_gb = free / (1024 ** 3)
    
    has_enough = available_gb >= required_space_gb
    
    if not has_enough:
        logger.warning(
            f"Insufficient disk space for model {model_name or 'unknown'}. "
            f"Required: {required_space_gb:.2f}GB, Available: {available_gb:.2f}GB"
        )
    
    return has_enough, available_gb, required_space_gb

def run_command(cmd: str, cwd: Optional[str] = None) -> Tuple[bool, str]:
    """
    Run a shell command and return (success, output).
    
    Args:
        cmd: The command to run
        cwd: Working directory for the command
        
    Returns:
        Tuple of (success, output)
    """
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, f"{e.stderr}\n{e.stdout}"

def is_linux() -> bool:
    """Check if the current OS is Linux."""
    return platform.system().lower() == 'linux'

def is_macos() -> bool:
    """Check if the current OS is macOS."""
    return platform.system().lower() == 'darwin'

def is_windows() -> bool:
    """Check if the current OS is Windows."""
    return platform.system().lower() == 'windows'

def extract_python_code(text: str) -> str:
    """
    Extract Python code blocks from markdown or plain text.
    
    Args:
        text: The text to extract code from
        
    Returns:
        The extracted Python code
    """
    # Try to extract from markdown code blocks first
    code_blocks = re.findall(r'```(?:python)?\n(.*?)\n```', text, re.DOTALL)
    if code_blocks:
        return '\n'.join(code_blocks)
    
    # If no code blocks found, try to extract indented code
    lines = text.split('\n')
    code_lines = []
    in_code = False
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
            
        if any(stripped.startswith(s) for s in ('def ', 'class ', 'import ', 'from ')):
            in_code = True
            
        if in_code:
            # Remove any leading Python prompt (>>> or ...)
            line = re.sub(r'^\s*(>>>|\.\.\.)\s*', '', line)
            code_lines.append(line)
    
    return '\n'.join(code_lines) if code_lines else text

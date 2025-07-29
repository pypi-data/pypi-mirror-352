# utils.py:
import os
import shutil
import json
from pathlib import Path
from typing import Dict, Optional, List # Added List

def generate_folder(folder_path: str, clean: bool = False) -> None: # Changed clean default to False
    """Create a directory if it doesn't exist.
    Optionally clean if it exists and clean is True (use with caution).
    
    Args:
        folder_path: Path to the directory
        clean: If True AND directory exists, removes existing directory contents.
               Defaults to False to prevent accidental data loss.
    """
    if os.path.exists(folder_path):
        if clean:
            print(f"Cleaning existing directory: {folder_path}")
            shutil.rmtree(folder_path)
            os.makedirs(folder_path)
        # else: directory exists, do nothing
    else:
        os.makedirs(folder_path, exist_ok=True) # exist_ok=True is good practice

def write_file(file_path: str, content: str) -> None:
    """Write content to a file, creating parent directories if needed.
    
    Args:
        file_path: Path to the file
        content: Content to write
    """
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True) # Ensure parent directories are created
    with open(file_path, "w", encoding='utf-8') as f: # Added encoding
        f.write(content)

def read_file(file_path: str) -> Optional[str]:
    """Read content from a file.
    
    Args:
        file_path: Path to the file
    
    Returns:
        File content or None if file doesn't exist
    """
    try:
        with open(file_path, "r", encoding='utf-8') as f: # Added encoding
            return f.read()
    except FileNotFoundError:
        return None
    except Exception as e: # Catch other potential read errors
        print(f"Error reading file {file_path}: {e}")
        return None


def load_codebase(directory: str) -> Dict[str, str]:
    """Load all files in a directory into a dictionary.
    Excludes files in .VIGI_dev_meta or other dot-prefixed directories.
    
    Args:
        directory: Path to the directory
    
    Returns:
        Dictionary mapping relative file paths to their content
    """
    codebase = {}
    if not os.path.isdir(directory):
        return codebase
        
    for root, dirs, files in os.walk(directory):
        # Exclude dot-prefixed directories (like .git, .VIGI_dev_meta)
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file.startswith('.'): # Exclude dot-prefixed files
                continue
            
            full_file_path = os.path.join(root, file)
            relative_file_path = os.path.relpath(full_file_path, directory)
            content = read_file(full_file_path)
            if content is not None:
                codebase[relative_file_path] = content
    return codebase

def save_codebase(directory: str, codebase: Dict[str, str]) -> None:
    """Save a codebase dictionary to files.
    
    Args:
        directory: Root directory to save files in
        codebase: Dictionary mapping relative file paths to content
    """
    for file_path, content in codebase.items():
        # file_path is relative to 'directory'
        full_target_path = os.path.join(directory, file_path)
        write_file(full_target_path, content)

def validate_json(json_str: str) -> bool:
    """Check if a string is valid JSON.
    
    Args:
        json_str: String to validate
    
    Returns:
        True if valid JSON, False otherwise
    """
    try:
        json.loads(json_str)
        return True
    except json.JSONDecodeError:
        return False

def find_files_by_extension(directory: str, extensions: List[str]) -> List[str]: # Used List from typing
    """Find all files with specific extensions in a directory.
    
    Args:
        directory: Directory to search
        extensions: List of file extensions (e.g., ['.js', '.html'])
    
    Returns:
        List of matching absolute file paths
    """
    matching_files = []
    if not os.path.isdir(directory):
        return matching_files

    for root, _, files in os.walk(directory):
        # Exclude dot-prefixed directories
        if any(part.startswith('.') for part in Path(root).parts):
            continue
        for file in files:
            if not file.startswith('.') and any(file.endswith(ext) for ext in extensions):
                matching_files.append(os.path.join(root, file))
    return matching_files

def get_file_tree(directory: str) -> str:
    """Generate a string representation of a directory's file tree.
    Excludes dot-prefixed files/directories.
    
    Args:
        directory: Directory to scan
    
    Returns:
        String representation of the file tree
    """
    file_tree = []
    if not os.path.isdir(directory):
        return "Directory not found."

    for root, dirs, files in os.walk(directory, topdown=True):
        # Filter out dot-prefixed directories from further traversal
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        # For display, only process if current root is not itself dot-prefixed (relative to initial directory)
        relative_root = os.path.relpath(root, directory)
        if relative_root == '.': # Root of the scan
            level = 0
            file_tree.append(f"{os.path.basename(directory)}/")
        elif not relative_root.startswith('.'): # Check parts of the path for dot-prefix
            level = relative_root.count(os.sep) + 1
            indent = '  ' * level
            file_tree.append(f"{indent}|-- {os.path.basename(root)}/")
        else: # Skip processing display for this dot-prefixed directory
            continue 
            
        subindent = '  ' * (level + 1)
        for f_name in sorted(files):
            if not f_name.startswith('.'):
                file_tree.append(f"{subindent}|-- {f_name}")
    return "\n".join(file_tree)
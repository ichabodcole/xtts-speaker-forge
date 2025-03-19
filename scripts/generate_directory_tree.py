#!/usr/bin/env python3
import os
import argparse
from pathlib import Path

def generate_tree(directory, output_file, exclude_dirs=None, exclude_files=None, max_depth=None, indent='  '):
    """
    Generate a markdown file with the directory structure
    
    Args:
        directory (str): Root directory to map
        output_file (str): Path to output markdown file
        exclude_dirs (list): List of directory names to exclude
        exclude_files (list): List of file names to exclude
        max_depth (int): Maximum depth to traverse
        indent (str): Indentation string
    """
    if exclude_dirs is None:
        exclude_dirs = ['.git', '__pycache__', 'node_modules', '.venv', '.env']
    
    if exclude_files is None:
        exclude_files = ['.DS_Store', '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll', '*.class']
    
    root_path = Path(directory).resolve()
    
    with open(output_file, 'w') as f:
        f.write(f"# Directory Structure for {root_path.name}\n\n")
        f.write("```\n")
        f.write(f"{root_path.name}/\n")
        
        def should_exclude(path, is_dir=False):
            """Check if path should be excluded"""
            name = path.name
            
            if is_dir:
                return name in exclude_dirs
            else:
                # Check for exact match
                if name in exclude_files:
                    return True
                
                # Check for wildcard patterns
                for pattern in exclude_files:
                    if '*' in pattern and name.endswith(pattern.replace('*', '')):
                        return True
            
            return False
        
        def write_directory(path, current_depth=1):
            """Recursively write directory structure"""
            if max_depth is not None and current_depth > max_depth:
                return
            
            # Get all directories and files, sorted
            dirs = []
            files = []
            
            try:
                for item in sorted(path.iterdir()):
                    if item.is_dir() and not should_exclude(item, is_dir=True):
                        dirs.append(item)
                    elif item.is_file() and not should_exclude(item):
                        files.append(item)
            except PermissionError:
                f.write(f"{indent * current_depth}[Permission Denied]\n")
                return
            
            # Write directories first
            for dir_path in dirs:
                f.write(f"{indent * current_depth}{dir_path.name}/\n")
                write_directory(dir_path, current_depth + 1)
            
            # Then write files
            for file_path in files:
                f.write(f"{indent * current_depth}{file_path.name}\n")
        
        write_directory(root_path)
        f.write("```\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate directory structure as markdown')
    parser.add_argument('-d', '--directory', default='.', help='Directory to map (default: current directory)')
    parser.add_argument('-o', '--output', default='directory_structure.md', help='Output markdown file (default: directory_structure.md)')
    parser.add_argument('-x', '--exclude-dirs', nargs='+', help='Directories to exclude')
    parser.add_argument('-f', '--exclude-files', nargs='+', help='Files to exclude')
    parser.add_argument('-m', '--max-depth', type=int, help='Maximum depth to traverse')
    
    args = parser.parse_args()
    
    # Add any custom excludes to the default ones
    exclude_dirs = ['.git', '__pycache__', 'node_modules', '.venv', '.env']
    if args.exclude_dirs:
        exclude_dirs.extend(args.exclude_dirs)
    
    exclude_files = ['.DS_Store', '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll', '*.class']
    if args.exclude_files:
        exclude_files.extend(args.exclude_files)
    
    generate_tree(
        args.directory,
        args.output,
        exclude_dirs=exclude_dirs,
        exclude_files=exclude_files,
        max_depth=args.max_depth
    )
    
    print(f"Directory structure has been written to {args.output}") 
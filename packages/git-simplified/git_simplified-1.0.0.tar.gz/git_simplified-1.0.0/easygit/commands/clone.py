"""
Clone command module for the EasyGit CLI
"""

import os
import re
import argparse
from typing import Any

from easygit.core.color import print_header, print_success, print_error, print_info, print_warning
from easygit.core.git import run_git_command
from easygit.core.utils import get_command_name, extract_repo_name_from_url
from easygit.core.config import get_config_value

def setup_parser(subparsers: Any) -> None:
    """Set up the parser for the clone command."""
    clone_parser = subparsers.add_parser("clone", help="Clone a repository into a new directory")
    clone_parser.add_argument("url", nargs="?", help="Repository URL to clone")
    clone_parser.add_argument("directory", nargs="?", help="Directory to clone into")
    clone_parser.add_argument("--depth", type=int, help="Create a shallow clone with specified depth")
    clone_parser.add_argument("--branch", "-b", help="Clone a specific branch")
    clone_parser.add_argument("--recursive", action="store_true", help="Initialize all submodules")
    clone_parser.add_argument("--shallow-submodules", action="store_true", help="Clone submodules with --depth=1")

def execute(args: argparse.Namespace) -> None:
    """Execute the clone command."""
    command_name = get_command_name()
    verbose = get_config_value("verbose", False)
    
    if not args.url:
        print_error("Repository URL is required.")
        print_info(f"Usage: {command_name} clone <repository-url> [directory]")
        return
    
    # Validate URL format
    if not (args.url.startswith("http://") or args.url.startswith("https://") or 
            args.url.startswith("git@") or args.url.startswith("ssh://")):
        print_warning(f"URL '{args.url}' doesn't look like a standard Git repository URL.")
        print_info("Standard formats: https://github.com/user/repo.git or git@github.com:user/repo.git")
        
        from easygit.core.utils import confirm_action
        if not confirm_action("Do you want to continue anyway?"):
            print_info("Clone operation cancelled.")
            return
    
    # Determine target directory
    if args.directory:
        target_dir = args.directory
    else:
        # Extract repo name from URL
        target_dir = extract_repo_name_from_url(args.url)
    
    print_header(f"Cloning repository {args.url} into ./{target_dir}")
    
    # Check if target directory already exists
    if os.path.exists(target_dir):
        print_error(f"Directory '{target_dir}' already exists.")
        print_info("Choose a different directory name or remove the existing one.")
        return
    
    clone_args = ["clone", args.url]
    if args.directory:
        clone_args.append(args.directory)
    
    if args.depth:
        clone_args.extend(["--depth", str(args.depth)])
        print_info(f"Creating a shallow clone with depth {args.depth}.")
    
    if args.branch:
        clone_args.extend(["--branch", args.branch])
        print_info(f"Cloning branch: {args.branch}")
    
    if args.recursive:
        clone_args.append("--recursive")
        print_info("Initializing all submodules.")
        
    if args.shallow_submodules:
        clone_args.append("--shallow-submodules")
        print_info("Cloning submodules with --depth=1.")
    
    # Show progress
    print_info("Cloning in progress. This may take a while depending on repository size...")
    
    return_code, _, _ = run_git_command(clone_args, verbose=verbose)
    
    if return_code == 0:
        print_success(f"Repository cloned successfully into {target_dir}!")
        
        # Show clone stats
        if os.path.exists(target_dir):
            # Get number of files
            try:
                file_count = sum(len(files) for _, _, files in os.walk(target_dir))
                print_info(f"Cloned {file_count} files.")
            except Exception:
                pass
                
            # Get latest commit
            os.chdir(target_dir)
            return_code, output, _ = run_git_command(["log", "-1", "--oneline"], capture_output=True, verbose=False)
            if return_code == 0 and output:
                print_info(f"Latest commit: {output.strip()}")
                
            # Get current branch
            return_code, output, _ = run_git_command(["branch", "--show-current"], capture_output=True, verbose=False)
            if return_code == 0 and output:
                print_info(f"Current branch: {output.strip()}")
            
            print_info(f"To start working with the repository: cd {target_dir}")
    else:
        print_error("Failed to clone repository.")
        print_info("Check that the URL is correct and you have permission to access it.")
        print_info("For private repositories, ensure you have the necessary authentication set up.")

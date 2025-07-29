"""
Add command module for the EasyGit CLI
"""

import os
import argparse
from typing import Any

from easygit.core.color import print_header, print_success, print_warning, print_info, print_error
from easygit.core.git import run_git_command, is_git_repository
from easygit.core.utils import get_command_name

def setup_parser(subparsers: Any) -> None:
    """Set up the parser for the add command."""
    add_parser = subparsers.add_parser("add", help="Add file contents to the index")
    add_parser.add_argument("files", nargs="*", help="Files to add")
    add_parser.add_argument("--all", "-a", action="store_true", help="Add all files")
    add_parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")

def execute(args: argparse.Namespace) -> None:
    """Execute the add command."""
    command_name = get_command_name()
    
    if not is_git_repository():
        print_error(f"Not a Git repository. Run '{command_name} init' first.")
        return
    
    if args.all:
        print_header("Adding all changes to staging area")
        return_code, _, _ = run_git_command(["add", "--all"])
    elif args.interactive:
        print_header("Interactive add mode")
        run_git_command(["add", "--interactive"])
        return
    elif not args.files:
        print_warning("No files specified. Use --all to add all files or specify files.")
        print_info(f"Usage: {command_name} add <file1> <file2> ... or {command_name} add --all")
        return
    else:
        # Check if files exist before adding
        missing_files = [f for f in args.files if not os.path.exists(f)]
        if missing_files:
            print_warning(f"The following files don't exist: {', '.join(missing_files)}")
            print_info("Did you make a typo? Please check the filenames.")
            
            # Continue with existing files
            existing_files = [f for f in args.files if os.path.exists(f)]
            if not existing_files:
                return
            args.files = existing_files
        
        print_header(f"Adding {', '.join(args.files)} to staging area")
        return_code, _, _ = run_git_command(["add"] + args.files)
    
    if return_code == 0:
        # Check what was actually added
        return_code, output, _ = run_git_command(["diff", "--cached", "--name-only"], capture_output=True)
        if return_code == 0 and output and output.strip():
            files = output.strip().split('\n')
            print_success(f"Added {len(files)} file(s) to staging area.")
            print_info(f"Use '{command_name} status' to see what files are staged.")
            print_info(f"Use '{command_name} commit -m \"Your message\"' to commit changes.")
        else:
            print_success("Files added to staging area.")
            print_info(f"Use '{command_name} commit' to commit your changes.")
    else:
        print_error("Failed to add files to staging area.")
        print_info("Check that the files exist and you have permission to access them.")

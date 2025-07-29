"""
Init command module for the EasyGit CLI
"""

import os
import argparse
from typing import Any

from easygit.core.color import print_header, print_success, print_warning, print_info, print_error
from easygit.core.git import run_git_command, is_git_repository
from easygit.core.utils import get_command_name

def setup_parser(subparsers: Any) -> None:
    """Set up the parser for the init command."""
    init_parser = subparsers.add_parser("init", help="Initialize a new Git repository")
    init_parser.add_argument("--branch", "-b", help="Name for the initial branch")
    init_parser.add_argument("--name", help="Set the Git user name")
    init_parser.add_argument("--email", help="Set the Git user email")

def execute(args: argparse.Namespace) -> None:
    """Execute the init command."""
    if is_git_repository():
        print_warning("This directory is already a Git repository.")
        return
    
    print_header("Initializing a new Git repository")
    
    init_args = ["init"]
    if args.branch:
        init_args.extend(["--initial-branch", args.branch])
        print_info(f"Setting initial branch name to: {args.branch}")
    
    return_code, _, _ = run_git_command(init_args)
    
    command_name = get_command_name()
    
    if return_code == 0:
        print_success("Git repository initialized successfully!")
        
        # Setup user name and email if requested
        if args.name or args.email:
            print_header("Setting up Git identity")
            
            if args.name:
                run_git_command(["config", "user.name", args.name])
                print_success(f"Set user name to: {args.name}")
            
            if args.email:
                run_git_command(["config", "user.email", args.email])
                print_success(f"Set user email to: {args.email}")
        
        current_dir = os.path.basename(os.getcwd())
        print_info(f"Repository '{current_dir}' is ready to use!")
        print_info(f"Use '{command_name} add' to stage files for commit.")
    else:
        print_error("Failed to initialize Git repository.")

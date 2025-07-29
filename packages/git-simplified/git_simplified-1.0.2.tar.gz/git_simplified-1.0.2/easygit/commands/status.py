"""
Status command module for the EasyGit CLI
"""

import argparse
from typing import Any

from easygit.core.color import print_header, print_success, print_error, print_info, BRIGHT, RESET
from easygit.core.git import run_git_command, is_git_repository, get_current_branch, get_remote_url
from easygit.core.utils import get_command_name

def setup_parser(subparsers: Any) -> None:
    """Set up the parser for the status command."""
    status_parser = subparsers.add_parser("status", help="Show the working tree status")

def execute(args: argparse.Namespace) -> None:
    """Execute the status command."""
    command_name = get_command_name()
    
    if not is_git_repository():
        print_error(f"Not a Git repository. Run '{command_name} init' first.")
        return
    
    print_header("Checking repository status")
    
    # Get current branch
    branch = get_current_branch()
    if branch:
        print_info(f"Current branch: {BRIGHT}{branch}{RESET}")
    
    # Get remote info
    remote_url = get_remote_url()
    if remote_url:
        print_info(f"Remote: {remote_url}")
    
    # Get status
    return_code, output, _ = run_git_command(["status", "--porcelain"], capture_output=True)
    
    if return_code != 0:
        print_error("Failed to get repository status.")
        return
    
    # Run detailed status
    run_git_command(["status"])
    
    if not output or not output.strip():
        print_success("Working tree is clean! No changes to commit.")
    else:
        # Count changes
        staged = 0
        modified = 0
        untracked = 0
        
        for line in output.splitlines():
            if line.startswith("??"):
                untracked += 1
            elif line[0] != " ":
                staged += 1
            if line[1] != " ":
                modified += 1
        
        if staged > 0:
            print_info(f"You have {staged} staged file(s) ready to commit.")
            print_info(f"Use '{command_name} commit -m \"Your message\"' to commit changes.")
        
        if modified > 0:
            print_info(f"You have {modified} modified file(s) not staged for commit.")
            print_info(f"Use '{command_name} add <file>' to stage specific files.")
            print_info(f"Use '{command_name} add --all' to stage all changes.")
        
        if untracked > 0:
            print_info(f"You have {untracked} untracked file(s).")
            print_info(f"Use '{command_name} add <file>' to start tracking specific files.")

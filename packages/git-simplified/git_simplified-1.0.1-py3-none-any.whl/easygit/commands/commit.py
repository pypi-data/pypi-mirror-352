"""
Commit command module for the EasyGit CLI
"""

import os
import argparse
from datetime import datetime
from typing import Any

from easygit.core.color import print_header, print_success, print_warning, print_info, print_error
from easygit.core.git import run_git_command, is_git_repository, get_current_user, get_current_branch
from easygit.core.utils import get_command_name

def setup_parser(subparsers: Any) -> None:
    """Set up the parser for the commit command."""
    commit_parser = subparsers.add_parser("commit", help="Record changes to the repository")
    commit_parser.add_argument("--message", "-m", help="Commit message")
    commit_parser.add_argument("--amend", action="store_true", help="Amend the previous commit")

def execute(args: argparse.Namespace) -> None:
    """Execute the commit command."""
    command_name = get_command_name()
    
    if not is_git_repository():
        print_error(f"Not a Git repository. Run '{command_name} init' first.")
        return
    
    # Check if git user is configured
    name, email = get_current_user()
    if not name or not email:
        print_warning("Git user identity is not configured.")
        if not name:
            print_error("User name is not set.")
            print_info(f"Set your name with: git config user.name \"Your Name\"")
        if not email:
            print_error("User email is not set.")
            print_info(f"Set your email with: git config user.email \"your.email@example.com\"")
        print_info("Your commits need a valid identity.")
        return
    
    # Check if there are staged changes
    return_code, output, _ = run_git_command(["diff", "--cached", "--name-only"], capture_output=True)
    
    if return_code != 0:
        print_error("Failed to check staged changes.")
        return
    
    if not output or not output.strip():
        print_warning("No changes staged for commit.")
        
        # Check if there are unstaged changes
        return_code, output, _ = run_git_command(["diff", "--name-only"], capture_output=True)
        if return_code == 0 and output and output.strip():
            print_info("You have unstaged changes.")
            print_info(f"Use '{command_name} add --all' to stage all changes.")
            print_info(f"Use '{command_name} add <file>' to stage specific files.")
        
        return
    
    if args.amend:
        print_header("Amending the previous commit")
        
        commit_cmd = ["commit", "--amend"]
        if args.message:
            commit_cmd.extend(["-m", args.message])
        
        return_code, _, _ = run_git_command(commit_cmd)
    else:
        print_header("Committing changes")
        
        if not args.message:
            # Check if we can use the editor
            editor = os.environ.get("EDITOR", "")
            if editor:
                print_info(f"Opening editor ({editor}) for commit message...")
                return_code, _, _ = run_git_command(["commit"])
            else:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                default_message = f"Update {timestamp}"
                print_warning(f"No commit message provided. Using: \"{default_message}\"")
                print_info("For better commit messages, use: -m \"Your descriptive message\"")
                return_code, _, _ = run_git_command(["commit", "-m", default_message])
        else:
            return_code, _, _ = run_git_command(["commit", "-m", args.message])
    
    if return_code == 0:
        print_success("Changes committed successfully!")
        
        # Get the latest commit message for confirmation
        return_code, output, _ = run_git_command(["log", "-1", "--pretty=%B"], capture_output=True)
        if return_code == 0 and output:
            print_info(f"Commit message: \"{output.strip()}\"")
        
        # Get the current branch
        branch = get_current_branch()
        if branch:
            print_info(f"Committed to branch: {branch}")
            print_info(f"Use '{command_name} push' to push your changes to remote.")
    else:
        print_error("Failed to commit changes.")

"""
Checkout command module for the EasyGit CLI
"""

import argparse
from typing import Any

from easygit.core.color import print_header, print_success, print_error, print_info
from easygit.core.git import run_git_command, is_git_repository, get_current_branch, get_local_branches, get_remote_branches
from easygit.core.utils import get_command_name
from easygit.core.config import get_config_value

def setup_parser(subparsers: Any) -> None:
    """Set up the parser for the checkout command."""
    checkout_parser = subparsers.add_parser("checkout", help="Switch branches or restore working tree files")
    checkout_parser.add_argument("branch", nargs="?", help="Branch to checkout")
    checkout_parser.add_argument("--new", "-b", help="Create and checkout a new branch")
    checkout_parser.add_argument("--force", "-f", action="store_true", help="Force checkout even with local changes")

def execute(args: argparse.Namespace) -> None:
    """Execute the checkout command."""
    command_name = get_command_name()
    verbose = get_config_value("verbose", False)
    
    if not is_git_repository():
        print_error(f"Not a Git repository. Run '{command_name} init' first.")
        return
    
    if args.new:
        # Create and checkout a new branch
        print_header(f"Creating and switching to new branch: {args.new}")
        
        checkout_args = ["checkout", "-b", args.new]
        if args.force:
            checkout_args.append("--force")
        
        return_code, _, _ = run_git_command(checkout_args, verbose=verbose)
        
        if return_code == 0:
            print_success(f"Created and switched to branch '{args.new}'!")
        else:
            print_error(f"Failed to create and switch to branch '{args.new}'.")
            return
    elif not args.branch:
        print_error("Branch name is required.")
        print_info(f"Usage: {command_name} checkout <branch-name>")
        print_info(f"To create and checkout a new branch: {command_name} checkout --new <branch-name>")
        return
    else:
        # Check if the branch exists
        local_branches = get_local_branches()
        remote_branches = get_remote_branches()
        
        if args.branch not in local_branches and args.branch in remote_branches:
            print_info(f"Branch '{args.branch}' exists on remote but not locally.")
            print_header(f"Creating local branch '{args.branch}' tracking remote branch")
            
            return_code, _, _ = run_git_command(["checkout", "--track", f"origin/{args.branch}"], verbose=verbose)
            
            if return_code == 0:
                print_success(f"Successfully created and switched to branch '{args.branch}'!")
                return
            else:
                print_error(f"Failed to create tracking branch '{args.branch}'.")
                return
        elif args.branch not in local_branches:
            print_error(f"Branch '{args.branch}' doesn't exist.")
            print_info(f"Available branches: {', '.join(local_branches)}")
            print_info(f"Create a new branch with: {command_name} checkout --new {args.branch}")
            return
        
        print_header(f"Switching to branch: {args.branch}")
        
        checkout_args = ["checkout"]
        if args.force:
            checkout_args.append("--force")
        checkout_args.append(args.branch)
        
        return_code, _, _ = run_git_command(checkout_args, verbose=verbose)
        
        if return_code == 0:
            print_success(f"Switched to branch '{args.branch}'!")
        else:
            print_error(f"Failed to switch to branch '{args.branch}'.")
            print_info("You might have uncommitted changes that conflict with the branch.")
            print_info(f"Commit your changes first with: {command_name} commit")
            print_info(f"Or use --force to force checkout (may discard changes): {command_name} checkout --force {args.branch}")

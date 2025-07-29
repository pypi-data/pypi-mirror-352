"""
Branch command module for the EasyGit CLI
Created by: QinCai-rui
Date: 2025-06-01 23:57:19
"""

import argparse
from typing import Any

from easygit.core.color import print_header, print_success, print_error, print_info, print_warning
from easygit.core.git import run_git_command, is_git_repository, get_current_branch, get_local_branches
from easygit.core.utils import get_command_name
from easygit.core.config import get_config_value

def setup_parser(subparsers: Any) -> None:
    """Set up the parser for the branch command."""
    branch_parser = subparsers.add_parser("branch", help="List, create, or delete branches")
    branch_parser.add_argument("--new", "-n", help="Create a new branch")
    branch_parser.add_argument("--base", help="Base branch for the new branch")
    branch_parser.add_argument("--delete", "-d", help="Delete a branch")
    branch_parser.add_argument("--force", "-f", action="store_true", help="Force operation")
    branch_parser.add_argument("--all", "-a", action="store_true", help="List all branches (local and remote)")
    branch_parser.add_argument("--remote", "-r", action="store_true", help="List remote branches")
    branch_parser.add_argument("--checkout", "-c", action="store_true", help="Checkout after creating")

def execute(args: argparse.Namespace) -> None:
    """Execute the branch command."""
    command_name = get_command_name()
    verbose = get_config_value("verbose", False)
    
    if not is_git_repository():
        print_error(f"Not a Git repository. Run '{command_name} init' first.")
        return
    
    if args.new:
        # Check if the branch already exists
        local_branches = get_local_branches()
        if args.new in local_branches:
            print_error(f"Branch '{args.new}' already exists.")
            print_info(f"Use '{command_name} checkout {args.new}' to switch to it.")
            return
        
        print_header(f"Creating new branch: {args.new}")
        
        # Determine base branch
        base = args.base if args.base else get_current_branch()
        if base:
            print_info(f"Creating from branch: {base}")
        
        branch_args = ["branch", args.new]
        if args.base:
            branch_args.append(args.base)
        
        return_code, _, _ = run_git_command(branch_args, verbose=verbose)
        
        if return_code == 0:
            print_success(f"Branch '{args.new}' created successfully!")
            print_info(f"Switch to the new branch with: {command_name} checkout {args.new}")
            
            if args.checkout:
                print_header(f"Switching to branch: {args.new}")
                return_code, _, _ = run_git_command(["checkout", args.new], verbose=verbose)
                if return_code == 0:
                    print_success(f"Switched to branch '{args.new}'!")
                else:
                    print_error(f"Failed to switch to branch '{args.new}'.")
        else:
            print_error(f"Failed to create branch '{args.new}'.")
    elif args.delete:
        # Check if the branch exists
        local_branches = get_local_branches()
        if args.delete not in local_branches:
            print_error(f"Branch '{args.delete}' doesn't exist.")
            print_info(f"Available branches: {', '.join(local_branches)}")
            return
        
        # Check if it's the current branch
        current_branch = get_current_branch()
        if args.delete == current_branch:
            print_error(f"Cannot delete the current branch '{args.delete}'.")
            print_info(f"Switch to another branch first with: {command_name} checkout <branch>")
            return
        
        print_header(f"Deleting branch: {args.delete}")
        
        delete_args = ["branch"]
        if args.force:
            delete_args.append("-D")
            print_warning("Using force delete. This will delete the branch even if it has unmerged changes!")
        else:
            delete_args.append("-d")
        delete_args.append(args.delete)
        
        return_code, _, _ = run_git_command(delete_args, verbose=verbose)
        
        if return_code == 0:
            print_success(f"Branch '{args.delete}' deleted successfully!")
        else:
            print_error(f"Failed to delete branch '{args.delete}'.")
            print_info("The branch might not be fully merged. Use --force to force delete.")
    else:
        print_header("Listing branches")
        
        if args.all:
            run_git_command(["branch", "--all"], verbose=verbose)
        elif args.remote:
            run_git_command(["branch", "--remote"], verbose=verbose)
        else:
            run_git_command(["branch"], verbose=verbose)
        
        current_branch = get_current_branch()
        if current_branch:
            print_info(f"Current branch: {current_branch}")
        
        print_info(f"Create a new branch with: {command_name} branch --new <branch-name>")
        print_info(f"Delete a branch with: {command_name} branch --delete <branch-name>")
        print_info(f"Switch branches with: {command_name} checkout <branch-name>")

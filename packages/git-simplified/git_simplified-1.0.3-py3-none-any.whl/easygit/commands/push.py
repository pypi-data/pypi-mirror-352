"""
Push command module for the EasyGit CLI
"""

import argparse
from typing import Any

from easygit.core.color import print_header, print_success, print_error, print_info, print_warning
from easygit.core.git import run_git_command, is_git_repository, get_current_branch, get_remote_branches
from easygit.core.utils import get_command_name

def setup_parser(subparsers: Any) -> None:
    """Set up the parser for the push command."""
    push_parser = subparsers.add_parser("push", help="Push changes to remote repository")
    push_parser.add_argument("--branch", "-b", help="Branch to push")
    push_parser.add_argument("--force", "-f", action="store_true", help="Force push (use with caution)")

def execute(args: argparse.Namespace) -> None:
    """Execute the push command."""
    command_name = get_command_name()
    
    if not is_git_repository():
        print_error(f"Not a Git repository. Run '{command_name} init' first.")
        return
    
    # Get current branch
    current_branch = get_current_branch()
    if not current_branch:
        print_error("Failed to determine current branch.")
        return
    
    # Check if a remote repository is configured
    return_code, output, _ = run_git_command(["remote"], capture_output=True)
    
    if not output or not output.strip():
        print_error("No remote repository configured.")
        print_info("Add a remote with: git remote add origin <repository-url>")
        return
    
    # Determine the branch to push
    branch_to_push = args.branch if args.branch else current_branch
    
    print_header(f"Pushing branch '{branch_to_push}' to remote repository")
    
    # Check if branch exists on remote
    remote_branches = get_remote_branches()
    is_new_branch = branch_to_push not in remote_branches
    
    push_args = ["push"]
    if args.force:
        push_args.append("--force")
        print_warning("Using --force. This will overwrite remote changes!")
    
    if is_new_branch:
        push_args.extend(["--set-upstream", "origin", branch_to_push])
        print_info(f"Setting up new remote branch: {branch_to_push}")
    else:
        push_args.extend(["origin", branch_to_push])
    
    return_code, _, _ = run_git_command(push_args)
    
    if return_code == 0:
        print_success(f"Successfully pushed branch '{branch_to_push}' to remote repository!")
        
        if is_new_branch:
            print_info(f"Created new remote branch: origin/{branch_to_push}")
    else:
        print_error(f"Failed to push branch '{branch_to_push}'.")
        print_info("The remote repository might not exist or you might not have permission.")
        print_info("For force push (caution!), use: --force")

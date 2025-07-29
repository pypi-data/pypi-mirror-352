"""
Pull command module for the EasyGit CLI
"""

import argparse
from typing import Any

from easygit.core.color import print_header, print_success, print_error, print_info, print_warning
from easygit.core.git import run_git_command, is_git_repository, get_current_branch
from easygit.core.utils import get_command_name, confirm_action
from easygit.core.config import get_config_value

def setup_parser(subparsers: Any) -> None:
    """Set up the parser for the pull command."""
    pull_parser = subparsers.add_parser("pull", help="Fetch from and integrate with another repository or a local branch")
    pull_parser.add_argument("--rebase", action="store_true", help="Rebase instead of merge")
    pull_parser.add_argument("--force", "-f", action="store_true", help="Force pull even with uncommitted changes")
    pull_parser.add_argument("--remote", help="Remote to pull from (defaults to 'origin')")
    pull_parser.add_argument("--branch", help="Remote branch to pull (defaults to current branch tracking branch)")

def execute(args: argparse.Namespace) -> None:
    """Execute the pull command."""
    command_name = get_command_name()
    verbose = get_config_value("verbose", False)
    
    if not is_git_repository():
        print_error(f"Not a Git repository. Run '{command_name} init' first.")
        return
    
    # Get current branch
    current_branch = get_current_branch()
    if not current_branch:
        print_error("Failed to determine current branch.")
        return
    
    print_header(f"Pulling changes into branch '{current_branch}'")
    
    # Check for uncommitted changes
    return_code, output, _ = run_git_command(["status", "--porcelain"], capture_output=True, verbose=verbose)
    if return_code == 0 and output and output.strip():
        print_warning("You have uncommitted changes that might be overwritten by pull.")
        print_info(f"Consider committing your changes first with '{command_name} commit'.")
        
        if not args.force:
            if not confirm_action("Do you want to continue anyway?"):
                print_info("Pull operation cancelled.")
                return
    
    # Construct pull command
    pull_args = ["pull"]
    
    if args.remote:
        pull_args.append(args.remote)
        if args.branch:
            pull_args.append(args.branch)
    
    if args.rebase:
        pull_args.append("--rebase")
        print_info("Using rebase strategy to integrate changes.")
    
    # Execute pull command
    return_code, _, _ = run_git_command(pull_args, verbose=verbose)
    
    if return_code == 0:
        print_success("Successfully pulled changes from remote repository!")
        
        # Show updated status
        return_code, output, _ = run_git_command(["status", "--short"], capture_output=True, verbose=verbose)
        if return_code == 0 and output and output.strip():
            print_info("Files updated by pull:")
            for line in output.strip().splitlines():
                print(f"  {line}")
    else:
        print_error("Failed to pull changes.")
        print_info("There might be conflicts that need to be resolved manually.")
        
        # Check for merge conflicts
        return_code, output, _ = run_git_command(["diff", "--name-only", "--diff-filter=U"], capture_output=True, verbose=verbose)
        if return_code == 0 and output and output.strip():
            conflict_files = output.strip().splitlines()
            print_warning(f"Merge conflicts detected in {len(conflict_files)} file(s):")
            for file in conflict_files:
                print(f"  {file}")
            print_info("Resolve conflicts and then commit the result.")

"""
Remote command module for the EasyGit CLI
Created by: QinCai-rui
Date: 2025-06-01 23:57:19
"""

import argparse
from typing import Any

from easygit.core.color import print_header, print_success, print_error, print_info
from easygit.core.git import run_git_command, is_git_repository
from easygit.core.utils import get_command_name
from easygit.core.config import get_config_value

def setup_parser(subparsers: Any) -> None:
    """Set up the parser for the remote command."""
    remote_parser = subparsers.add_parser("remote", help="Manage remote repositories")
    remote_parser.add_argument("--add", help="Add a new remote")
    remote_parser.add_argument("--url", help="URL for the remote")
    remote_parser.add_argument("--remove", help="Remove a remote")
    remote_parser.add_argument("--show", help="Show details of a remote")
    remote_parser.add_argument("--verbose", "-v", action="store_true", help="Be verbose")

def execute(args: argparse.Namespace) -> None:
    """Execute the remote command."""
    command_name = get_command_name()
    verbose = get_config_value("verbose", False)
    
    if not is_git_repository():
        print_error(f"Not a Git repository. Run '{command_name} init' first.")
        return
    
    if args.add and args.url:
        print_header(f"Adding remote '{args.add}' with URL: {args.url}")
        return_code, _, _ = run_git_command(["remote", "add", args.add, args.url], verbose=verbose)
        
        if return_code == 0:
            print_success(f"Remote '{args.add}' added successfully!")
            print_info(f"You can now push to this remote with: {command_name} push")
        else:
            print_error(f"Failed to add remote '{args.add}'.")
    elif args.remove:
        print_header(f"Removing remote: {args.remove}")
        return_code, _, _ = run_git_command(["remote", "remove", args.remove], verbose=verbose)
        
        if return_code == 0:
            print_success(f"Remote '{args.remove}' removed successfully!")
        else:
            print_error(f"Failed to remove remote '{args.remove}'.")
    elif args.show:
        print_header(f"Showing details for remote: {args.show}")
        run_git_command(["remote", "show", args.show], verbose=verbose)
    else:
        print_header("Listing remotes")
        
        if args.verbose:
            run_git_command(["remote", "-v"], verbose=verbose)
        else:
            run_git_command(["remote"], verbose=verbose)
        
        print_info(f"Add a remote with: {command_name} remote --add <name> --url <url>")
        print_info(f"Remove a remote with: {command_name} remote --remove <name>")
        print_info(f"Show remote details with: {command_name} remote --show <name>")

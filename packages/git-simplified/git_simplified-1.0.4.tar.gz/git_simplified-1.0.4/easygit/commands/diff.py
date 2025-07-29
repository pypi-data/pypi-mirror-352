"""
Diff command module for the EasyGit CLI
"""

import argparse
from typing import Any

from easygit.core.color import print_header, print_info, print_error
from easygit.core.git import run_git_command, is_git_repository
from easygit.core.utils import get_command_name
from easygit.core.config import get_config_value

def setup_parser(subparsers: Any) -> None:
    """Set up the parser for the diff command."""
    diff_parser = subparsers.add_parser("diff", help="Show changes between commits, commit and working tree, etc")
    diff_parser.add_argument("--staged", "--cached", action="store_true", help="Show staged changes")
    diff_parser.add_argument("--name-only", action="store_true", help="Show only names of changed files")
    diff_parser.add_argument("--color", action="store_true", help="Show colored diff")
    diff_parser.add_argument("--stat", action="store_true", help="Show diffstat instead of patch")
    diff_parser.add_argument("commits", nargs="*", help="Commits to compare")
    diff_parser.add_argument("path", nargs="*", help="Filter by path")

def execute(args: argparse.Namespace) -> None:
    """Execute the diff command."""
    command_name = get_command_name()
    verbose = get_config_value("verbose", False)
    
    if not is_git_repository():
        print_error(f"Not a Git repository. Run '{command_name} init' first.")
        return
    
    diff_args = ["diff"]
    
    if args.staged:
        diff_args.append("--staged")
        print_header("Showing changes staged for commit")
    elif args.commits:
        if len(args.commits) == 1:
            diff_args.append(args.commits[0])
            print_header(f"Showing changes in commit {args.commits[0]}")
        elif len(args.commits) == 2:
            diff_args.extend([args.commits[0], args.commits[1]])
            print_header(f"Showing changes between {args.commits[0]} and {args.commits[1]}")
        else:
            print_error("Too many commit references. Use at most two.")
            return
    else:
        print_header("Showing unstaged changes")
    
    if args.name_only:
        diff_args.append("--name-only")
    
    if args.color:
        diff_args.append("--color")
        
    if args.stat:
        diff_args.append("--stat")
    
    if args.path:
        diff_args.append("--")
        diff_args.extend(args.path)
    
    run_git_command(diff_args, verbose=verbose)
    
    if not args.staged:
        print_info(f"To see staged changes, use: {command_name} diff --staged")

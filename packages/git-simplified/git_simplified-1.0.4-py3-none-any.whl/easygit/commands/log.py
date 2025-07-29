"""
Log command module for the EasyGit CLI
"""

import argparse
from typing import Any

from easygit.core.color import print_header, print_info, print_error
from easygit.core.git import run_git_command, is_git_repository
from easygit.core.utils import get_command_name
from easygit.core.config import get_config_value

def setup_parser(subparsers: Any) -> None:
    """Set up the parser for the log command."""
    log_parser = subparsers.add_parser("log", help="Show commit logs")
    log_parser.add_argument("--oneline", action="store_true", help="Show one commit per line")
    log_parser.add_argument("--graph", action="store_true", help="Show ASCII graph of branch and merge history")
    log_parser.add_argument("--all", action="store_true", help="Show all commits")
    log_parser.add_argument("--number", "-n", type=int, help="Limit number of commits")
    log_parser.add_argument("--pretty", action="store_true", help="Use a prettier format")
    log_parser.add_argument("--author", help="Filter by author")
    log_parser.add_argument("--since", help="Show commits more recent than a date")
    log_parser.add_argument("--until", help="Show commits older than a date")
    log_parser.add_argument("path", nargs="*", help="Filter by path")

def execute(args: argparse.Namespace) -> None:
    """Execute the log command."""
    command_name = get_command_name()
    verbose = get_config_value("verbose", False)
    
    if not is_git_repository():
        print_error(f"Not a Git repository. Run '{command_name} init' first.")
        return
    
    print_header("Commit History")
    
    log_args = ["log"]
    
    if args.oneline:
        log_args.append("--oneline")
    
    if args.graph:
        log_args.append("--graph")
    
    if args.all:
        log_args.append("--all")
    
    if args.number:
        log_args.extend(["-n", str(args.number)])
    elif not args.all:
        # Default to 10 commits if not specified
        log_args.extend(["-n", "10"])
        print_info("Showing last 10 commits. Use --all to see all commits.")
    
    if args.pretty:
        log_args.extend(["--pretty=format:%C(bold blue)%h%C(reset) - %C(bold green)(%ar)%C(reset) %C(white)%s%C(reset) %C(dim white)- %an%C(reset)%C(bold yellow)%d%C(reset)"])
    
    if args.author:
        log_args.extend([f"--author={args.author}"])
    
    if args.since:
        log_args.extend([f"--since={args.since}"])
    
    if args.until:
        log_args.extend([f"--until={args.until}"])
    
    if args.path:
        log_args.append("--")
        log_args.extend(args.path)
    
    run_git_command(log_args, verbose=verbose)
    
    print_info(f"For more details, use: {command_name} log --all")
    print_info(f"For a graph view, use: {command_name} log --graph")
    print_info(f"For a compact view, use: {command_name} log --oneline")

"""
Command handling module for the EasyGit CLI
Created by: QinCai-rui
Date: 2025-06-02 00:25:31
"""

import sys
import argparse
from typing import Dict, Callable, Any

from easygit.core.color import BRIGHT, YELLOW, CYAN, RESET
from easygit.core.utils import get_command_name, print_welcome_message
from easygit.core.config import set_config_value

# Import all command modules
from easygit.commands.init import setup_parser as setup_init_parser, execute as execute_init
from easygit.commands.status import setup_parser as setup_status_parser, execute as execute_status
from easygit.commands.add import setup_parser as setup_add_parser, execute as execute_add
from easygit.commands.commit import setup_parser as setup_commit_parser, execute as execute_commit
from easygit.commands.push import setup_parser as setup_push_parser, execute as execute_push
from easygit.commands.pull import setup_parser as setup_pull_parser, execute as execute_pull
from easygit.commands.clone import setup_parser as setup_clone_parser, execute as execute_clone
from easygit.commands.branch import setup_parser as setup_branch_parser, execute as execute_branch
from easygit.commands.checkout import setup_parser as setup_checkout_parser, execute as execute_checkout
from easygit.commands.log import setup_parser as setup_log_parser, execute as execute_log
from easygit.commands.diff import setup_parser as setup_diff_parser, execute as execute_diff
from easygit.commands.remote import setup_parser as setup_remote_parser, execute as execute_remote

# Dictionary mapping command names to their execution functions
COMMANDS: Dict[str, Callable[[argparse.Namespace], None]] = {
    "init": execute_init,
    "status": execute_status,
    "add": execute_add,
    "commit": execute_commit,
    "push": execute_push,
    "pull": execute_pull,
    "clone": execute_clone,
    "branch": execute_branch,
    "checkout": execute_checkout,
    "log": execute_log,
    "diff": execute_diff,
    "remote": execute_remote,
}

def create_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    command_name = get_command_name()
    
    parser = argparse.ArgumentParser(
        description=f"{BRIGHT}{YELLOW}EasyGit{RESET}: A beginner-friendly Git CLI with colorful output",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"{CYAN}For command-specific help, use: {command_name} <command> --help{RESET}"
    )
    
    # Add global verbose and debug options
    verbosity_group = parser.add_argument_group('Verbosity Options')
    verbosity_group.add_argument("--verbose", "-v", action="store_true", help="Show Git commands being executed")
    verbosity_group.add_argument("--debug", action="store_true", help="Show additional debug information (includes verbose)")
    verbosity_group.add_argument("--quiet", "-q", action="store_true", help="Suppress all non-essential output")
    
    subparsers = parser.add_subparsers(dest="command", help="Git command to execute")
    
    # Set up parsers for all commands
    setup_init_parser(subparsers)
    setup_status_parser(subparsers)
    setup_add_parser(subparsers)
    setup_commit_parser(subparsers)
    setup_push_parser(subparsers)
    setup_pull_parser(subparsers)
    setup_clone_parser(subparsers)
    setup_branch_parser(subparsers)
    setup_checkout_parser(subparsers)
    setup_log_parser(subparsers)
    setup_diff_parser(subparsers)
    setup_remote_parser(subparsers)
    
    return parser

def main() -> int:
    """Main function to parse arguments and execute commands."""
    parser = create_parser()
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set verbosity flags in config
    if hasattr(args, 'quiet') and args.quiet:
        set_config_value("quiet", True)
        set_config_value("verbose", False)
        set_config_value("debug", False)
    else:
        set_config_value("quiet", False)
        
        if hasattr(args, 'verbose') and args.verbose:
            set_config_value("verbose", True)
        else:
            set_config_value("verbose", False)
            
        if hasattr(args, 'debug') and args.debug:
            set_config_value("debug", True)
            set_config_value("verbose", True)  # Debug implies verbose
        else:
            set_config_value("debug", False)
    
    # Print welcome message if no command is specified
    if len(sys.argv) == 1:
        print_welcome_message()
        return 0
    
    # Execute the command
    if args.command in COMMANDS:
        try:
            COMMANDS[args.command](args)
            return 0
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            return 1
    else:
        parser.print_help()
        return 1

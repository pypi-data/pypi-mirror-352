"""
Utility functions for the EasyGit CLI
"""

import os
import re
import sys
from typing import List

from easygit.core.color import BRIGHT, YELLOW, CYAN, GREEN, RESET, COLORS_ENABLED

def get_command_name() -> str:
    """Get the command name based on how the script was invoked."""
    return os.path.basename(sys.argv[0])

def print_welcome_message() -> None:
    """Print the welcome message for the CLI."""
    user = os.environ.get("USER", "User")
    command_name = get_command_name()
    
    print(f"{BRIGHT}{YELLOW}EasyGit{RESET}: A beginner-friendly Git CLI with colorful output")
    print(f"{CYAN}Hello, {user}!{RESET}")
    
    if not COLORS_ENABLED:
        print("Note: Running without colors. Install colorama for colored output:")
        print("  sudo apt install python3-colorama")
    
    print(f"\n{GREEN}Usage:{RESET} {command_name} <command> [options]")
    
    print(f"\n{GREEN}Basic commands:{RESET}")
    print(f"  {CYAN}init{RESET}      - Initialize a new Git repository")
    print(f"  {CYAN}clone{RESET}     - Clone a repository")
    print(f"  {CYAN}status{RESET}    - Show repository status")
    print(f"  {CYAN}add{RESET}       - Add files to staging area")
    print(f"  {CYAN}commit{RESET}    - Record changes to the repository")
    
    print(f"\n{GREEN}Branch commands:{RESET}")
    print(f"  {CYAN}branch{RESET}    - List, create, or delete branches")
    print(f"  {CYAN}checkout{RESET}  - Switch branches")
    
    print(f"\n{GREEN}Remote commands:{RESET}")
    print(f"  {CYAN}remote{RESET}    - Manage remote repositories")
    print(f"  {CYAN}push{RESET}      - Push changes to remote")
    print(f"  {CYAN}pull{RESET}      - Pull changes from remote")
    
    print(f"\n{GREEN}Inspection commands:{RESET}")
    print(f"  {CYAN}log{RESET}       - Show commit history")
    print(f"  {CYAN}diff{RESET}      - Show changes between commits")
    
    print(f"\n{GREEN}Verbosity options:{RESET}")
    print(f"  {CYAN}--verbose, -v{RESET} - Show Git commands being executed")
    print(f"  {CYAN}--debug{RESET}       - Show additional debug information")
    print(f"  {CYAN}--quiet, -q{RESET}   - Suppress all non-essential output")
    
    print(f"\n{GREEN}For help:{RESET} {command_name} <command> --help")

def extract_repo_name_from_url(url: str) -> str:
    """Extract repository name from a Git URL."""
    match = re.search(r'([^/]+?)(?:\.git)?$', url)
    if match:
        return match.group(1)
    return "repository"

def confirm_action(message: str) -> bool:
    """Ask for user confirmation before proceeding with an action."""
    from easygit.core.color import YELLOW, RESET
    from easygit.core.config import get_config_value
    
    # If in quiet mode, assume yes
    if get_config_value("quiet", False):
        return True
        
    user_input = input(f"{YELLOW}{message} [y/N]: {RESET}").lower()
    return user_input in ('y', 'yes')

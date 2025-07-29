"""
Color handling module for the EasyGit CLI
"""

import os

# Try to import colorama, but provide fallback if not available
try:
    from colorama import init, Fore, Back, Style
    # Initialize colorama
    init(autoreset=True)
    COLORS_ENABLED = True
except ImportError:
    # Define fallback color constants that do nothing
    class DummyColor:
        def __getattr__(self, name):
            return ""
    
    Fore = DummyColor()
    Back = DummyColor()
    Style = DummyColor()
    COLORS_ENABLED = False
    print("Colorama not found. Running without colors.")
    print("To enable colors, install colorama using:")
    print("  sudo apt install python3-colorama")
    print("")

# Define color constants for better readability
GREEN = Fore.GREEN
RED = Fore.RED
YELLOW = Fore.YELLOW
BLUE = Fore.BLUE
MAGENTA = Fore.MAGENTA
CYAN = Fore.CYAN
BRIGHT = Style.BRIGHT
RESET = Style.RESET_ALL

def print_header(text: str) -> None:
    """Print a colorful header."""
    print(f"\n{BRIGHT}{BLUE}{'=' * 60}")
    print(f"{BRIGHT}{BLUE}= {YELLOW}{text}")
    print(f"{BRIGHT}{BLUE}{'=' * 60}{RESET}\n")

def print_success(text: str) -> None:
    """Print a success message."""
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text: str) -> None:
    """Print an error message."""
    print(f"{RED}✗ {text}{RESET}")

def print_warning(text: str) -> None:
    """Print a warning message."""
    print(f"{YELLOW}! {text}{RESET}")

def print_info(text: str) -> None:
    """Print an info message."""
    print(f"{CYAN}ℹ {text}{RESET}")

def print_command(text: str) -> None:
    """Print the command being executed."""
    print(f"{MAGENTA}$ {text}{RESET}")

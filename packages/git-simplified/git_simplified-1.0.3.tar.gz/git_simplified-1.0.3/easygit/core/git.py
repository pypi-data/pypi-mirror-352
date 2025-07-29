"""
Git operations module for the EasyGit CLI
Created by: QinCai-rui
Date: 2025-06-02 00:02:01
"""

import subprocess
import os
import sys
import time
from typing import List, Optional, Tuple, Dict, Any

from easygit.core.color import print_command, print_error, print_info, print_warning, YELLOW, RESET
from easygit.core.config import get_config_value

def run_git_command(args: List[str], capture_output: bool = False, verbose: bool = None) -> Tuple[int, Optional[str], Optional[str]]:
    """Run a git command and return the result.
    
    Args:
        args: The git command arguments
        capture_output: Whether to capture the output
        verbose: Whether to show the command being executed (overrides global setting)
    """
    command = ["git"] + args
    
    # Check if we should show commands
    if verbose is None:
        # Use global config if not specified for this command
        verbose = get_config_value("verbose", False) or get_config_value("debug", False)
    
    debug = get_config_value("debug", False)
    quiet = get_config_value("quiet", False)
    
    if verbose and not quiet:
        print_command(" ".join(command))
    
    if debug and not quiet:
        # Show Git environment variables
        env_vars = {key: os.environ.get(key) for key in [
            "GIT_DIR", "GIT_WORK_TREE", "GIT_CONFIG", "GIT_AUTHOR_NAME", 
            "GIT_AUTHOR_EMAIL", "GIT_COMMITTER_NAME", "GIT_COMMITTER_EMAIL"
        ]}
        filtered_env = {k: v for k, v in env_vars.items() if v is not None}
        if filtered_env:
            print_info(f"Git environment variables: {filtered_env}")
        
        # Show current working directory
        print_info(f"Current working directory: {os.getcwd()}")
        
        # Show command timing
        start_time = time.time()
    
    try:
        if capture_output:
            result = subprocess.run(
                command, 
                check=False, 
                capture_output=True, 
                text=True,
                env=os.environ.copy()  # Ensure environment variables are passed
            )
            return_code, stdout, stderr = result.returncode, result.stdout, result.stderr
            
            if debug and not quiet:
                end_time = time.time()
                print_info(f"Command execution time: {end_time - start_time:.3f} seconds")
                
                if stderr:
                    print_warning(f"Git stderr: {stderr}")
                
                if verbose and stdout and not stdout.isspace():
                    print_info(f"Command output ({len(stdout.splitlines())} lines):")
                
            return return_code, stdout, stderr
        else:
            result = subprocess.run(
                command, 
                check=False,
                env=os.environ.copy()  # Ensure environment variables are passed
            )
            
            if debug and not quiet:
                end_time = time.time()
                print_info(f"Command execution time: {end_time - start_time:.3f} seconds")
                
            return result.returncode, None, None
    except Exception as e:
        if (verbose or debug) and not quiet:
            print_error(f"Failed to execute command: {e}")
            
            # Print traceback in debug mode
            if debug:
                import traceback
                traceback.print_exc()
                
        return 1, None, str(e)

def is_git_repository() -> bool:
    """Check if the current directory is a git repository."""
    return_code, _, _ = run_git_command(["rev-parse", "--is-inside-work-tree"], capture_output=True, verbose=False)
    return return_code == 0

def get_current_branch() -> Optional[str]:
    """Get the name of the current branch."""
    if not is_git_repository():
        return None
    return_code, output, _ = run_git_command(["branch", "--show-current"], capture_output=True, verbose=False)
    if return_code == 0 and output and output.strip():
        return output.strip()
    return None

def get_remote_branches() -> List[str]:
    """Get a list of remote branches."""
    if not is_git_repository():
        return []
    return_code, output, _ = run_git_command(["branch", "-r"], capture_output=True, verbose=False)
    if return_code == 0 and output:
        # Parse branch names and clean them up
        branches = []
        for line in output.splitlines():
            branch = line.strip()
            if branch and not branch.startswith('*'):
                # Remove "origin/" prefix if present
                if branch.startswith('origin/'):
                    branch = branch[7:]
                branches.append(branch)
        return branches
    return []

def get_local_branches() -> List[str]:
    """Get a list of local branches."""
    if not is_git_repository():
        return []
    return_code, output, _ = run_git_command(["branch"], capture_output=True, verbose=False)
    if return_code == 0 and output:
        # Parse branch names and clean them up
        branches = []
        for line in output.splitlines():
            branch = line.strip()
            if branch:
                # Remove "* " prefix from current branch
                if branch.startswith('* '):
                    branch = branch[2:]
                branches.append(branch)
        return branches
    return []

def get_current_user() -> Tuple[Optional[str], Optional[str]]:
    """Get the current Git user name and email."""
    if not is_git_repository():
        return None, None
    
    return_code, name, _ = run_git_command(["config", "user.name"], capture_output=True, verbose=False)
    if return_code != 0 or not name:
        name = None
    else:
        name = name.strip()
    
    return_code, email, _ = run_git_command(["config", "user.email"], capture_output=True, verbose=False)
    if return_code != 0 or not email:
        email = None
    else:
        email = email.strip()
    
    return name, email

def get_remote_url(remote: str = "origin") -> Optional[str]:
    """Get the URL of the remote repository."""
    if not is_git_repository():
        return None
    
    return_code, output, _ = run_git_command(["remote", "get-url", remote], capture_output=True, verbose=False)
    if return_code == 0 and output and output.strip():
        return output.strip()
    return None

def get_remotes() -> List[str]:
    """Get a list of remotes."""
    if not is_git_repository():
        return []
    
    return_code, output, _ = run_git_command(["remote"], capture_output=True, verbose=False)
    if return_code == 0 and output and output.strip():
        return output.strip().splitlines()
    return []

def get_staged_files() -> List[str]:
    """Get a list of staged files."""
    if not is_git_repository():
        return []
    
    return_code, output, _ = run_git_command(["diff", "--cached", "--name-only"], capture_output=True, verbose=False)
    if return_code == 0 and output and output.strip():
        return output.strip().splitlines()
    return []

def get_modified_files() -> List[str]:
    """Get a list of modified files."""
    if not is_git_repository():
        return []
    
    return_code, output, _ = run_git_command(["diff", "--name-only"], capture_output=True, verbose=False)
    if return_code == 0 and output and output.strip():
        return output.strip().splitlines()
    return []

def get_untracked_files() -> List[str]:
    """Get a list of untracked files."""
    if not is_git_repository():
        return []
    
    return_code, output, _ = run_git_command(["ls-files", "--others", "--exclude-standard"], capture_output=True, verbose=False)
    if return_code == 0 and output and output.strip():
        return output.strip().splitlines()
    return []

def get_repo_info() -> Dict[str, Any]:
    """Get repository information."""
    if not is_git_repository():
        return {}
    
    info = {}
    
    # Get current branch
    info["branch"] = get_current_branch()
    
    # Get remotes
    info["remotes"] = get_remotes()
    
    # Get remote URL
    if "origin" in info["remotes"]:
        info["remote_url"] = get_remote_url("origin")
    
    # Get user information
    info["user_name"], info["user_email"] = get_current_user()
    
    # Get status counts
    info["staged_files"] = get_staged_files()
    info["modified_files"] = get_modified_files()
    info["untracked_files"] = get_untracked_files()
    
    # Get commit count
    return_code, output, _ = run_git_command(["rev-list", "--count", "HEAD"], capture_output=True, verbose=False)
    if return_code == 0 and output and output.strip():
        info["commit_count"] = int(output.strip())
    
    # Get last commit
    return_code, output, _ = run_git_command(["log", "-1", "--pretty=%H|%an|%ae|%at|%s"], capture_output=True, verbose=False)
    if return_code == 0 and output and output.strip():
        parts = output.strip().split("|")
        if len(parts) >= 5:
            info["last_commit"] = {
                "hash": parts[0],
                "author_name": parts[1],
                "author_email": parts[2],
                "timestamp": int(parts[3]),
                "message": parts[4]
            }
    
    return info

def is_working_tree_clean() -> bool:
    """Check if the working tree is clean."""
    if not is_git_repository():
        return False
    
    return_code, output, _ = run_git_command(["status", "--porcelain"], capture_output=True, verbose=False)
    return return_code == 0 and (not output or not output.strip())

def has_commits() -> bool:
    """Check if the repository has any commits."""
    if not is_git_repository():
        return False
    
    return_code, _, _ = run_git_command(["rev-parse", "HEAD"], capture_output=True, verbose=False)
    return return_code == 0

def get_git_version() -> Optional[str]:
    """Get the Git version."""
    return_code, output, _ = run_git_command(["--version"], capture_output=True, verbose=False)
    if return_code == 0 and output and output.strip():
        # Parse the version from "git version 2.30.1"
        parts = output.strip().split()
        if len(parts) >= 3:
            return parts[2]
    return None

def has_conflicts() -> bool:
    """Check if there are merge conflicts."""
    if not is_git_repository():
        return False
    
    return_code, output, _ = run_git_command(["diff", "--name-only", "--diff-filter=U"], capture_output=True, verbose=False)
    return return_code == 0 and output and output.strip()

def get_conflict_files() -> List[str]:
    """Get a list of files with merge conflicts."""
    if not is_git_repository():
        return []
    
    return_code, output, _ = run_git_command(["diff", "--name-only", "--diff-filter=U"], capture_output=True, verbose=False)
    if return_code == 0 and output and output.strip():
        return output.strip().splitlines()
    return []

def prompt_for_input(prompt: str, default: str = "") -> str:
    """Prompt for input with a default value."""
    from easygit.core.color import CYAN, RESET
    from easygit.core.config import get_config_value
    
    # If in quiet mode, use default
    if get_config_value("quiet", False):
        return default
    
    if default:
        result = input(f"{CYAN}{prompt} [{default}]: {RESET}")
        return result.strip() or default
    else:
        return input(f"{CYAN}{prompt}: {RESET}").strip()

def is_valid_ref(ref: str) -> bool:
    """Check if a reference (branch, tag, commit) is valid."""
    if not is_git_repository():
        return False
    
    return_code, _, _ = run_git_command(["rev-parse", "--verify", ref], capture_output=True, verbose=False)
    return return_code == 0

def get_tracking_branch() -> Optional[str]:
    """Get the tracking branch for the current branch."""
    if not is_git_repository():
        return None
    
    current_branch = get_current_branch()
    if not current_branch:
        return None
    
    return_code, output, _ = run_git_command(["rev-parse", "--abbrev-ref", f"{current_branch}@{{upstream}}"], capture_output=True, verbose=False)
    if return_code == 0 and output and output.strip():
        return output.strip()
    return None

def has_upstream_changes() -> bool:
    """Check if there are upstream changes that haven't been pulled."""
    if not is_git_repository():
        return False
    
    tracking_branch = get_tracking_branch()
    if not tracking_branch:
        return False
    
    # Fetch from remote to get latest changes
    run_git_command(["fetch"], verbose=False)
    
    # Check if local branch is behind remote
    return_code, output, _ = run_git_command(["rev-list", "--count", f"HEAD..{tracking_branch}"], capture_output=True, verbose=False)
    if return_code == 0 and output and output.strip():
        return int(output.strip()) > 0
    return False

def get_file_status(file_path: str) -> str:
    """Get the status of a file in the repository."""
    if not is_git_repository() or not os.path.exists(file_path):
        return "unknown"
    
    # Check if the file is tracked
    return_code, output, _ = run_git_command(["ls-files", "--error-unmatch", file_path], capture_output=True, verbose=False)
    if return_code != 0:
        return "untracked"
    
    # Check if the file is modified
    return_code, output, _ = run_git_command(["diff", "--name-only", file_path], capture_output=True, verbose=False)
    if return_code == 0 and output and output.strip():
        return "modified"
    
    # Check if the file is staged
    return_code, output, _ = run_git_command(["diff", "--cached", "--name-only", file_path], capture_output=True, verbose=False)
    if return_code == 0 and output and output.strip():
        return "staged"
    
    return "committed"

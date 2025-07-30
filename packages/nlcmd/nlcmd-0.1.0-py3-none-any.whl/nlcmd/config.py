# nlcmd/config.py

import os
import json
import yaml
import glob
from pathlib import Path
from typing import List, Dict, Any, Optional

import typer # For typer.get_app_dir()

# Assuming utils.py and its LOGGER_NAME are correctly set up
import nlcmd.utils as utils

# --- Constants ---
APP_NAME = "nlcmd" # Used for typer.get_app_dir() and logger
DEFAULT_COMMANDS_SUBDIR = "commands" # Subdirectory within the package for built-in commands
USER_CONFIG_FILENAME = "commands.yaml" # User's custom command definitions

# Initialize logger for this module
logger = utils.setup_logger(logger_name=utils.LOGGER_NAME)

# --- Helper Functions ---

def _get_user_config_path() -> Path:
    """
    Determines the path to the user's custom command configuration file.
    Priority:
    1. NLC_CONFIG_PATH environment variable.
    2. Default application config directory (OS-dependent).
    """
    env_path_str = os.environ.get("NLC_CONFIG_PATH")
    if env_path_str:
        logger.info(f"Using user config path from NLC_CONFIG_PATH: {env_path_str}")
        return Path(env_path_str)

    # Default path using typer's recommended app directory
    app_dir = Path(typer.get_app_dir(APP_NAME, force_posix=False)) # force_posix=False for OS native paths
    user_config_path = app_dir / USER_CONFIG_FILENAME
    logger.info(f"Default user config path: {user_config_path}")
    return user_config_path

def _validate_command_entry(entry: Dict[str, Any], source_file: str) -> bool:
    """
    Validates a single command entry for required keys and basic types.
    Logs a warning if validation fails.
    """
    required_keys = {
        "intent": str,
        "tags": list, # Further check: list of strings
        "command": str,
    }
    is_valid = True
    for key, expected_type in required_keys.items():
        if key not in entry:
            logger.warning(f"Validation failed for entry in '{source_file}': Missing key '{key}'. Entry: {entry}")
            is_valid = False
            continue # Skip further checks for this key
        if not isinstance(entry[key], expected_type):
            logger.warning(
                f"Validation failed for entry in '{source_file}': Key '{key}' has incorrect type "
                f"(expected {expected_type.__name__}, got {type(entry[key]).__name__}). Entry: {entry}"
            )
            is_valid = False
        elif key == "tags" and not all(isinstance(tag, str) for tag in entry[key]):
            logger.warning(
                f"Validation failed for entry in '{source_file}': Not all items in 'tags' are strings. Entry: {entry}"
            )
            is_valid = False
    return is_valid

# --- Core Loading Functions ---

def load_builtin_commands() -> List[Dict[str, Any]]:
    """
    Load all built-in command definition JSON files from the package's 'commands' directory.
    """
    builtin_cmds_dir = Path(__file__).resolve().parent / DEFAULT_COMMANDS_SUBDIR
    all_cmds: List[Dict[str, Any]] = []

    logger.info(f"Loading built-in commands from: {builtin_cmds_dir}")
    if not builtin_cmds_dir.is_dir():
        logger.warning(f"Built-in commands directory not found: {builtin_cmds_dir}")
        return []

    for filepath in builtin_cmds_dir.glob("*.json"):
        logger.debug(f"Attempting to load built-in commands from: {filepath.name}")
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list): # Expecting a list of command entries
                    valid_entries = [
                        entry for entry in data if isinstance(entry, dict) and _validate_command_entry(entry, str(filepath))
                    ]
                    all_cmds.extend(valid_entries)
                    logger.info(f"Successfully loaded {len(valid_entries)} valid command(s) from {filepath.name}.")
                else:
                    logger.warning(f"Skipping '{filepath.name}': Expected a list of commands, got {type(data).__name__}.")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from '{filepath.name}': {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading '{filepath.name}': {e}", exc_info=True)
            
    logger.info(f"Total built-in commands loaded: {len(all_cmds)}")
    return all_cmds

def load_user_commands() -> List[Dict[str, Any]]:
    """
    Load user-defined commands from their configuration file (e.g., commands.yaml).
    """
    user_config_path = _get_user_config_path()
    user_cmds: List[Dict[str, Any]] = []

    if not user_config_path.exists():
        logger.info(f"User commands file not found at '{user_config_path}'. No user commands loaded.")
        # Optionally, create the directory or a default config file here if desired
        # For example: user_config_path.parent.mkdir(parents=True, exist_ok=True)
        return []

    logger.info(f"Loading user commands from: {user_config_path}")
    try:
        with open(user_config_path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)
        
        if not config_data: # Handles empty YAML file
            logger.info(f"User config file '{user_config_path}' is empty.")
            return []

        # Assuming the YAML contains a top-level key 'commands' which is a list
        raw_command_list = config_data.get("commands", [])
        if not isinstance(raw_command_list, list):
            logger.warning(
                f"User commands in '{user_config_path}' are not under a 'commands' list or "
                f"the value is not a list. Found type: {type(raw_command_list).__name__}."
            )
            return []

        valid_entries = [
            entry for entry in raw_command_list if isinstance(entry, dict) and _validate_command_entry(entry, str(user_config_path))
        ]
        user_cmds.extend(valid_entries)
        logger.info(f"Successfully loaded {len(user_cmds)} valid user command(s) from {user_config_path}.")

    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML from '{user_config_path}': {e}")
    except Exception as e:
        logger.error(f"Unexpected error loading user commands from '{user_config_path}': {e}", exc_info=True)
        
    return user_cmds

def merge_commands(
    default_commands: List[Dict[str, Any]],
    user_commands: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Merge built-in and user commands. User commands override defaults if they share the same 'intent'.
    """
    logger.debug(f"Starting merge. Defaults: {len(default_commands)}, User: {len(user_commands)}")
    # Create a dictionary of default commands keyed by intent for efficient lookup and override
    merged_by_intent: Dict[str, Dict[str, Any]] = {
        entry["intent"]: entry for entry in default_commands if "intent" in entry
    }
    
    overridden_count = 0
    added_count = 0

    for user_cmd_entry in user_commands:
        intent = user_cmd_entry.get("intent")
        if not intent: # Should have been caught by validation, but good to double check
            logger.warning(f"User command entry missing 'intent', skipping: {user_cmd_entry}")
            continue
        
        if intent in merged_by_intent:
            logger.info(f"User command for intent '{intent}' is overriding the default.")
            overridden_count +=1
        else:
            logger.info(f"Adding new user-defined command for intent '{intent}'.")
            added_count +=1
        merged_by_intent[intent] = user_cmd_entry
            
    final_command_list = list(merged_by_intent.values())
    logger.info(
        f"Command merging complete. Total commands: {len(final_command_list)}. "
        f"User commands added: {added_count}, User commands overridden: {overridden_count}."
    )
    return final_command_list

def load_commands() -> List[Dict[str, Any]]:
    """
    Load and merge all command definitions (built-in and user-defined).
    This is the main entry point for retrieving all available commands.
    """
    logger.info("Starting to load all command definitions.")
    
    # Ensure user config directory exists, useful if we want to write a default config later
    # or if the user expects the directory to be present.
    user_config_dir = _get_user_config_path().parent
    try:
        user_config_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        logger.warning(f"Could not create user config directory '{user_config_dir}': {e}")

    defaults = load_builtin_commands()
    user_cmds = load_user_commands()
    
    merged_commands = merge_commands(defaults, user_cmds)
    logger.info(f"Total {len(merged_commands)} commands available after merging.")
    return merged_commands
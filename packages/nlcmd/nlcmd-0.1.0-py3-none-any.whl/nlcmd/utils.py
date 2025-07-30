# nlcmd/utils.py

import re
import logging
import os
import sys

# Define a logger name, typically the package name
LOGGER_NAME = "nlcmd" # Or "nlc" if you've standardized on that for the project internals

def normalize_text(text: str) -> str:
    """
    Lowercase, remove punctuation, and strip leading/trailing whitespace.
    """
    if not isinstance(text, str):
        # Handle cases where text might not be a string, e.g., if parsing None
        return ""
    text = text.lower()
    # Removes characters that are not alphanumeric or whitespace
    text = re.sub(r"[^\w\s]", "", text)
    # Replace multiple whitespace characters with a single space
    text = re.sub(r"\s+", " ", text).strip()
    return text

def setup_logger(
    log_level: str = "INFO",
    log_file: str = None,
    logger_name: str = LOGGER_NAME
) -> logging.Logger:
    """
    Configure and return a logger.

    The log level can be overridden by the NLC_LOG_LEVEL environment variable.
    If log_file is provided, output will also be sent to that file.

    Args:
        log_level (str): Default log level (e.g., "INFO", "DEBUG").
        log_file (str, optional): Path to a file for logging. Defaults to None.
        logger_name (str): The name for the logger.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(logger_name)

    # Determine the effective log level
    # Environment variable > function argument > default ("INFO")
    effective_log_level_str = os.environ.get(
        "NLC_LOG_LEVEL", log_level
    ).upper()
    
    # Ensure the log level string is valid
    if not hasattr(logging, effective_log_level_str):
        # Fallback to INFO if the level string is invalid
        logging.warning(
            f"Invalid log level '{effective_log_level_str}' provided or in NLC_LOG_LEVEL. "
            f"Defaulting to INFO."
        )
        effective_log_level_str = "INFO"
        
    effective_log_level = getattr(logging, effective_log_level_str)
    logger.setLevel(effective_log_level)

    # Configure handlers only if they haven't been added already
    # This prevents duplicate log messages if setup_logger is called multiple times
    if not logger.handlers:
        # Common formatter
        fmt_string = "%(asctime)s [%(name)s] [%(levelname)s] %(message)s"
        date_fmt_string = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(fmt_string, datefmt=date_fmt_string)

        # Console Handler (StreamHandler)
        console_handler = logging.StreamHandler(sys.stdout) # Use stdout for info/debug
        console_handler.setFormatter(formatter)
        # Allow console handler to respect the logger's level, or set its own
        # console_handler.setLevel(effective_log_level)
        logger.addHandler(console_handler)

        # File Handler (if specified)
        if log_file:
            try:
                # Ensure the directory for the log file exists
                log_dir = os.path.dirname(os.path.abspath(log_file))
                if log_dir and not os.path.exists(log_dir):
                    os.makedirs(log_dir, exist_ok=True)
                
                file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
                file_handler.setFormatter(formatter)
                # Allow file handler to respect the logger's level, or set its own
                # file_handler.setLevel(effective_log_level)
                logger.addHandler(file_handler)
                logger.info(f"Logging to console and file: {log_file}")
            except Exception as e:
                logger.error(f"Failed to configure file logging for {log_file}: {e}", exc_info=True)
                logger.info("Logging to console only.")
        else:
            logger.info("Logging to console only.")
            
    # If handlers are already present, just update the level if necessary
    # This can be useful if setup_logger is called again to change verbosity dynamically
    # though typically Typer callback handles verbosity change before first log.
    elif logger.level != effective_log_level:
        logger.setLevel(effective_log_level)
        logger.debug(f"Logger level updated to {effective_log_level_str}")


    return logger

# Example of how it might be used in other modules:
# from .utils import setup_logger
# logger = setup_logger() # Or setup_logger(__name__) for module-specific loggers
# logger.debug("This is a debug message.")
# logger.info("This is an info message.")
# nlcmd/executor.py

import subprocess
import sys
import os # For handling custom environment variables
from typing import Dict, Optional, Union, Tuple # For type hinting

import nlcmd.utils as utils # Assuming utils.py is in the same directory/package

class CommandExecutor:
    def __init__(self):
        self.logger = utils.setup_logger(logger_name=utils.LOGGER_NAME)

    def run(
        self,
        command: str,
        dry_run: bool = False,
        capture_streams: bool = True,
        timeout: Optional[float] = None, # Timeout in seconds
        custom_env: Optional[Dict[str, str]] = None
    ) -> Dict[str, Union[int, Optional[str]]]:
        """
        Execute the provided shell command.

        Args:
            command (str): The shell command to execute.
            dry_run (bool): If True, print the command instead of executing.
            capture_streams (bool): If True, capture stdout/stderr; otherwise,
                                   they go to the console directly.
            timeout (Optional[float]): Max seconds to wait for the command to complete.
            custom_env (Optional[Dict[str, str]]): Custom environment variables
                                                  for the subprocess.

        Returns:
            Dict[str, Union[int, Optional[str]]]: A dictionary containing:
                - 'return_code' (int): The exit code of the command.
                - 'stdout' (Optional[str]): Captured standard output, if capture_streams=True.
                - 'stderr' (Optional[str]): Captured standard error, if capture_streams=True.
                - 'error_message' (Optional[str]): An error message if an exception
                                                  (e.g., TimeoutExpired) occurred.
        """
        self.logger.info(f"Preparing to execute command: {command}")
        if custom_env:
            self.logger.debug(f"Using custom environment variables: {list(custom_env.keys())}")
        if timeout:
            self.logger.debug(f"Command timeout set to: {timeout}s")

        result = {
            "return_code": -1, # Default to -1 for unexecuted/problematic cases
            "stdout": None,
            "stderr": None,
            "error_message": None,
        }

        if dry_run:
            print(f"[DRY-RUN] {command}")
            self.logger.info(f"[DRY-RUN] Command not executed: {command}")
            result["return_code"] = 0 # Dry run is considered successful in terms of execution flow
            return result

        # Prepare environment: start with current environment and overlay custom_env
        env = os.environ.copy()
        if custom_env:
            env.update(custom_env)

        try:
            if capture_streams:
                # NOTE: Using shell=True can be a security hazard if the command string
                # is constructed from untrusted external input without sanitization.
                # Since commands here are from templates, the risk is somewhat mitigated
                # but always be cautious about argument injection.
                process = subprocess.run(
                    command,
                    shell=True,
                    check=False,  # Set to False to handle non-zero exit codes manually via return_code
                    capture_output=True,
                    text=True,    # Decodes stdout/stderr to strings
                    timeout=timeout,
                    env=env
                )
                result["return_code"] = process.returncode
                result["stdout"] = process.stdout.strip() if process.stdout else ""
                result["stderr"] = process.stderr.strip() if process.stderr else ""

                if process.returncode == 0:
                    self.logger.info(f"Command executed successfully: {command}")
                    if result["stdout"]:
                        self.logger.debug(f"STDOUT:\n{result['stdout']}")
                    if result["stderr"]: # Some successful commands still output to stderr
                        self.logger.debug(f"STDERR (non-fatal):\n{result['stderr']}")
                else:
                    self.logger.error(
                        f"Command failed with exit code {process.returncode}: {command}"
                    )
                    if result["stdout"]:
                        self.logger.error(f"Failed command STDOUT:\n{result['stdout']}")
                    if result["stderr"]:
                        self.logger.error(f"Failed command STDERR:\n{result['stderr']}")
            else:
                # Execute and let output flow to console
                # `check=True` was in the original code, meaning it would raise an error.
                # To be consistent with the detailed dict return, we set check=False
                # and will report the return code.
                process = subprocess.run(
                    command,
                    shell=True,
                    check=False, # If True, it raises CalledProcessError on non-zero exit
                    stdout=sys.stdout, # Directly pipe to console
                    stderr=sys.stderr, # Directly pipe to console
                    timeout=timeout,
                    env=env
                )
                result["return_code"] = process.returncode
                if process.returncode == 0:
                    self.logger.info(f"Command executed successfully (output to console): {command}")
                else:
                    self.logger.error(
                        f"Command failed with exit code {process.returncode} (output to console): {command}"
                    )

        except subprocess.CalledProcessError as e:
            # This block would be hit if check=True was used and command returned non-zero.
            # With check=False, we rely on process.returncode directly.
            # However, keeping it for robustness or if check=True is re-enabled for some path.
            self.logger.error(f"Command failed with CalledProcessError (exit code {e.returncode}): {command}")
            result["return_code"] = e.returncode
            result["stdout"] = e.stdout.strip() if e.stdout else ""
            result["stderr"] = e.stderr.strip() if e.stderr else ""
            result["error_message"] = str(e)
            if result["stdout"]:
                 self.logger.error(f"Failed command STDOUT:\n{result['stdout']}")
            if result["stderr"]:
                self.logger.error(f"Failed command STDERR:\n{result['stderr']}")

        except subprocess.TimeoutExpired as e:
            self.logger.error(f"Command timed out after {timeout}s: {command}")
            result["return_code"] = -2 # Custom code for timeout
            result["stdout"] = e.stdout.decode(errors='ignore').strip() if e.stdout else ""
            result["stderr"] = e.stderr.decode(errors='ignore').strip() if e.stderr else ""
            result["error_message"] = f"Command timed out after {timeout} seconds."
            self.logger.error(f"Timeout details: {e}")

        except FileNotFoundError as e:
            self.logger.error(f"Command not found: {command}. Details: {e}")
            result["return_code"] = -3 # Custom code for FileNotFoundError
            result["error_message"] = f"Command or executable not found: {e.filename}."
            self.logger.error(f"FileNotFoundError details: {e}")

        except Exception as e:
            self.logger.error(f"An unexpected error occurred while executing command '{command}': {e}", exc_info=True)
            result["return_code"] = -4 # Custom code for other exceptions
            result["error_message"] = f"An unexpected error occurred: {str(e)}."

        return result
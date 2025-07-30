# nlcmd/cli.py

import typer
from typing import Optional
import nlcmd.config as config_module
from nlcmd.parser import CommandParser
from nlcmd.executor import CommandExecutor
from nlcmd.utils import setup_logger, LOGGER_NAME # Use LOGGER_NAME from utils
from nlcmd.version import __version__

app = typer.Typer(
    help="nlcmd: Offline Natural Language Command Runner.",
    rich_markup_mode="markdown" # Allows markdown in help text
)
# Initialize logger at the module level, will be configured by main
logger = setup_logger(logger_name=LOGGER_NAME)

# --- Helper function to display execution results ---
def _display_execution_result(result: dict):
    """Helper to display stdout/stderr from command execution."""
    if result.get("stdout"):
        typer.echo("\n--- Output (stdout) ---")
        typer.secho(result["stdout"])
        typer.echo("--- End of Output ---")
    
    if result.get("stderr"):
        # Display stderr even if return code is 0, as it might contain warnings
        typer.echo("\n--- Error Output (stderr) ---")
        typer.secho(result["stderr"], fg=typer.colors.YELLOW if result["return_code"] == 0 else typer.colors.RED)
        typer.echo("--- End of Error Output ---")

    if result["return_code"] != 0:
        if result.get("error_message"):
             typer.secho(f"\n❌ Command execution failed. Error: {result['error_message']}", fg=typer.colors.RED)
        else:
            typer.secho(f"\n❌ Command execution failed with exit code: {result['return_code']}", fg=typer.colors.RED)
    else:
        typer.secho("\n✅ Command executed successfully.", fg=typer.colors.GREEN)
    typer.echo("") # Newline for spacing

# --- Typer App Configuration ---
@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable DEBUG logging. Use -vv for TRACE (if supported)."),
    # config_file: Optional[Path] = typer.Option(None, "--config", help="Path to custom config file."), # Future: pass to config_module
):
    """
    nlcmd: Understands natural language and translates it into shell commands.

    If no subcommand is given, it opens an interactive REPL.
    """
    log_level = "INFO"
    if verbose:
        log_level = "DEBUG"
    
    # Re-initialize logger with potentially new level (setup_logger is idempotent)
    # The global 'logger' instance is updated by this call.
    setup_logger(log_level=log_level, logger_name=LOGGER_NAME)
    logger.debug(f"Logger initialized with level: {log_level}")

    if ctx.invoked_subcommand is None:
        typer.secho("🧠 nlcmd REPL (type 'help', 'list-intents', or 'exit')", fg=typer.colors.BRIGHT_BLUE)
        typer.echo("--------------------------------------------------")
        repl()

def repl():
    """Interactive Read-Eval-Print Loop for nlcmd."""
    cmder = CommandExecutor()
    # It's important that config_module.load_commands() also initializes its own logger
    # if it needs to log during loading, or uses the global one after main sets it up.
    commands = config_module.load_commands()
    parser = CommandParser(commands)

    if not commands:
        typer.secho("⚠️ No commands loaded. Check your configuration and command definition files.", fg=typer.colors.RED)
        typer.echo("   Default commands should be in a 'commands' subdirectory next to 'config.py'.")
        typer.echo(f"   User commands are typically in: {config_module._get_user_config_path()}") # Use the helper
        raise typer.Exit(code=1)

    while True:
        try:
            user_input = typer.prompt(">>", prompt_suffix=" ")
        except (EOFError, KeyboardInterrupt):
            typer.echo("\nGoodbye 👋")
            raise typer.Exit()

        if not user_input.strip():
            continue

        lowered_input = user_input.lower()
        if lowered_input in ("exit", "quit", "q"):
            typer.echo("Goodbye 👋")
            raise typer.Exit()

        if lowered_input == "help":
            typer.echo("\nAvailable commands: 'exit', 'quit', 'q', 'list-intents', 'help'.")
            typer.echo("Type any natural language command you want to execute.")
            typer.echo("\nExamples:")
            typer.echo("  create a python virtual environment")
            typer.echo("  list all files in current directory")
            typer.echo("  install flask with pip")
            typer.echo("  initialize a git repository here")
            typer.echo("  show me the python version")
            typer.echo("  activate virtual environment on linux")
            typer.echo("  find text \"my_pattern\" in file myfile.txt")
            typer.echo("  replace \"old text\" with \"new text\" in config.ini")
            typer.echo("")
            continue
        
        if lowered_input == "list-intents":
            list_intents_logic() # Call the logic directly
            continue

        parse_result = parser.parse(user_input)
        status = parse_result.get("status", "failure")

        if status == "failure":
            error_msg = parse_result.get("error_message", "Could not understand the command.")
            typer.secho(f"🤷 {error_msg} Try rephrasing or type 'help'.\n", fg=typer.colors.YELLOW)
            continue

        filled_command = parse_result["filled_command"]
        
        if status == "needs_arguments":
            missing_args_str = ", ".join(parse_result.get("missing_args", []))
            typer.secho(f"\n🤔 Some arguments seem to be missing: {missing_args_str}", fg=typer.colors.YELLOW)
            typer.echo("   The command template looks like this with current information:")
            typer.secho(f"     {filled_command}", fg=typer.colors.CYAN)
            typer.echo("   You can refine your input, use 'edit' to complete it, or 'n' to cancel.")
        else: # success
             typer.echo(f"\n💡 Suggested command:")
             typer.secho(f"  {filled_command}", fg=typer.colors.BRIGHT_GREEN)
        
        typer.echo("") # Spacing before prompt

        try:
            choice = typer.prompt(
                "Run this? [Y/yes = run, N/no = cancel, E/edit = modify command]",
                default="y",
                show_choices=False # Keep prompt clean
            ).lower()
        except (EOFError, KeyboardInterrupt):
            typer.echo("\n❌ Cancelled by user.\n")
            continue


        if choice in ("y", "yes"):
            # For most commands, capturing streams is useful.
            # For highly interactive commands (e.g. `top`, editors), one might pass capture_streams=False
            # This could be based on a flag in the intent_entry in the future.
            execution_result = cmder.run(filled_command, capture_streams=True)
            _display_execution_result(execution_result)
        elif choice in ("e", "edit"):
            try:
                edited_command = typer.prompt("✏️  Enter edited command", default=filled_command).strip()
                if edited_command:
                    execution_result = cmder.run(edited_command, capture_streams=True)
                    _display_execution_result(execution_result)
                else:
                    typer.secho("❌ No command entered. Cancelled.\n", fg=typer.colors.RED)
            except (EOFError, KeyboardInterrupt):
                typer.echo("\n❌ Edit cancelled by user.\n")
                continue
        else: # n, no, or anything else
            typer.secho("❌ Cancelled by user.\n", fg=typer.colors.RED)


@app.command("run")
def run_once(
    instruction: str = typer.Argument(..., help="Natural language instruction to execute."),
    dry_run: bool = typer.Option(False, "--dry-run", "-d", help="Show the command but do not execute."),
    # yes: bool = typer.Option(False, "--yes", "-y", help="Assume 'yes' to prompts (not implemented for this command yet).")
):
    """
    Parse a single instruction, show the suggested command, and run it (unless --dry-run).
    """
    cmder = CommandExecutor()
    commands = config_module.load_commands()
    parser = CommandParser(commands)

    if not commands:
        typer.secho("⚠️ No commands loaded. Cannot execute instruction.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    parse_result = parser.parse(instruction)
    status = parse_result.get("status", "failure")

    if status == "failure":
        error_msg = parse_result.get("error_message", "Could not understand the command.")
        typer.secho(f"🤷 {error_msg}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    filled_command = parse_result["filled_command"]

    if status == "needs_arguments":
        missing_args_str = ", ".join(parse_result.get("missing_args", []))
        typer.secho(f"🤔 The instruction is missing arguments: {missing_args_str}", fg=typer.colors.YELLOW)
        typer.echo("   The command template with current information:")
        typer.secho(f"     {filled_command}", fg=typer.colors.CYAN)
        typer.echo("   Please provide a more complete instruction.")
        raise typer.Exit(code=1)
    
    typer.echo("💡 Command to run:")
    typer.secho(f"  {filled_command}", fg=typer.colors.BRIGHT_GREEN)
    typer.echo("")

    if dry_run:
        typer.echo("[DRY-RUN] Skipping execution.")
        raise typer.Exit(code=0)

    # Confirmation for run_once might be good, unless a --yes flag is added
    # For now, proceed directly.
    execution_result = cmder.run(filled_command, capture_streams=True)
    _display_execution_result(execution_result)
    
    if execution_result["return_code"] != 0:
        raise typer.Exit(code=execution_result["return_code"])


def list_intents_logic():
    """Logic to show all known intents with their tags."""
    commands = config_module.load_commands()
    if not commands:
        typer.secho("No commands or intents found. Check configuration.", fg=typer.colors.YELLOW)
        return

    typer.echo("\n📚 Known intents and their primary tags:\n")
    lines = []
    for entry in sorted(commands, key=lambda x: x.get("intent", "")): # Sort for consistency
        intent = entry.get("intent", "Unknown Intent")
        tags_preview = ", ".join(entry.get("tags", [])[:5]) # Show first 5 tags
        if len(entry.get("tags", [])) > 5:
            tags_preview += ", ..."
        lines.append(f"- **{intent}**: tags=[{tags_preview}]")
        lines.append(f"  `Command: {entry.get('command', 'N/A')}`")
    typer.echo("\n".join(lines))
    typer.echo("")

@app.command("list-intents")
def list_intents_command():
    """
    Show all known command intents and their associated tags.
    """
    list_intents_logic()

@app.command("version")
def version():
    """
    Print nlcmd version.
    """
    typer.echo(f"nlcmd version {__version__}")

def main_app():
    """Main entry point for the Typer application."""
    app(prog_name="nlcmd") # or "nlc" if you prefer that as the command name

if __name__ == "__main__":
    main_app()
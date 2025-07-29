import os
import sys
import subprocess # For setting env vars
from pathlib import Path # For home directory

# readline import for interactive experience (platform-dependent)
if sys.platform == "win32":
    import pyreadline3 as readline  # noqa: F401
else:
    import readline  # noqa: F401

import typer
from click import BadArgumentUsage
# Import click.Context and click.HelpFormatter for type hinting in custom Typer class
import click # Keep for Context, HelpFormatter, BadArgumentUsage
from typing_extensions import Annotated
from typing import Optional, List, TYPE_CHECKING

# --- Rich and Questionary for beautiful prompts ---
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.padding import Padding
    from rich.rule import Rule
    from rich.prompt import Confirm as RichConfirm # For a simple yes/no if Questionary fails
    import questionary
    from questionary import Style as QuestionaryStyle
except ImportError:
    print("Missing 'rich' or 'questionary'. Please install them: pip install rich questionary")
    sys.exit(1)

# Initialize Rich console
# Define console at the global level so it's available everywhere
console = Console(highlight=False)


# Configuration is likely used for option defaults, keep at top
# Make sure the relative import for config is correct for your project structure
# If 'start.py' is at the root of 'vigi' package, 'from .config import cfg' is fine.
# If 'start.py' is a script OUTSIDE 'vigi' package, you might need to adjust sys.path or use absolute imports.
try:
    from .config import cfg , DESKTOP_VIGI_PATH
except ImportError:
    # Fallback for running script directly if it's not part of a package structure properly recognized
    # This is a common issue if you run `python vigi/start.py` vs `python -m vigi.start`
    # For robust solution, ensure your project is installed (e.g., pip install -e .) or PYTHONPATH is set
    current_script_dir = Path(__file__).parent
    sys.path.insert(0, str(current_script_dir.parent)) # Add parent of 'vigi' package if start.py is vigi/start.py
    


# Forward declaration for type hinting if DigitalPersona is imported late
if TYPE_CHECKING:
    from .tools_and_personas import DigitalPersona # Adjusted for direct call below


# --- API Key Management ---
API_KEY_ENV_VAR = "GEMINI_API_KEY"

def _prompt_for_api_key() -> Optional[str]:
    """Prompts the user for their API key using questionary."""
    console.line()
    console.print(Panel(
        Padding(
            Text.assemble(
                ("🔑 ", "yellow"),
                ("GEMINI_API_KEY Setup", "bold yellow")
            ),
            (1,2)
        ),
        subtitle="This key is required for AI interactions.",
        border_style="yellow",
        expand=False
    ))
    console.line()
    try:
        custom_style = QuestionaryStyle([
            ('qmark', 'fg:#FF9D00 bold'),
            ('question', 'bold'),
            ('answer', 'fg:#f44336 bold'), # Example answer color
        ])
        api_key = questionary.text(
            "Please enter your Gemini API Key:",
            validate=lambda text: True if len(text.strip()) > 10 else "API key seems too short.",
            style=custom_style,
            qmark="🔑"
        ).ask()
        console.line()
        return api_key.strip() if api_key else None
    except Exception as e:
        console.print(f"[bold red]Error during API key prompt: {e}. Please set the {API_KEY_ENV_VAR} environment variable manually.[/bold red]")
        console.line()
        return None

def _set_env_var_permanently_windows(key: str, value: str) -> bool:
    """Attempts to set an environment variable permanently for the current user on Windows."""
    try:
        # Use setx. It modifies the user environment variables.
        # /M would modify system, but requires admin.
        subprocess.check_call(['setx', key, value], shell=False) # shell=False is safer
        console.print(f"✅ [green]Set {key} in your user environment variables. You may need to open a new terminal for it to take effect.[/green]")
        return True
    except subprocess.CalledProcessError as e:
        console.print(f"⚠️ [yellow]Failed to set {key} permanently using 'setx': {e}. Try manually.[/yellow]")
        console.print(f"[yellow]   You can set it temporarily in this session by running: set {key}={value}[/yellow]")
    except FileNotFoundError:
        console.print(f"⚠️ [yellow]'setx' command not found. Cannot set {key} permanently. Try manually.[/yellow]")
    return False

def _add_to_shell_profile(profile_path: Path, line_to_add: str) -> bool:
    """Adds a line to a shell profile file if it's not already there."""
    try:
        # Ensure parent directory exists (mostly for testing/unusual setups)
        profile_path.parent.mkdir(parents=True, exist_ok=True)
        
        if profile_path.exists():
            with open(profile_path, 'r') as f:
                content = f.read()
            if line_to_add in content:
                # console.print(f"ℹ️ [dim cyan]{line_to_add.split('=')[0]} already set in {profile_path.name}.[/dim cyan]")
                return True # Already there or handled

        with open(profile_path, 'a') as f:
            f.write(f"\n# Added by Vigi CLI for {line_to_add.split('=')[0]}\n{line_to_add}\n")
        return True
    except IOError as e:
        console.print(f"⚠️ [yellow]Could not write to {profile_path}: {e}. Try manually.[/yellow]")
    return False

def _set_env_var_permanently_unix(key: str, value: str) -> bool:
    """Attempts to set an environment variable permanently for the current user on Unix-like systems."""
    home = Path.home()
    line_to_add = f'export {key}="{value}"' # Ensure value is quoted for safety
    
    current_shell_path = os.environ.get("SHELL", "")
    current_shell_name = Path(current_shell_path).name if current_shell_path else ""
    
    profiles_updated = []
    
    # Prioritize shell-specific profiles
    if current_shell_name == "zsh":
        # For Zsh, .zshrc is generally for interactive settings.
        # .zshenv is sourced for all invocations, but might be too early for some things.
        # .zprofile for login shells.
        # Common practice: .zshrc for exports that should be available in interactive shells.
        target_profiles = [home / ".zshrc", home / ".zshenv", home / ".zprofile"]
    elif current_shell_name == "bash":
        # For Bash, .bashrc is for interactive non-login shells.
        # .bash_profile (or .profile if .bash_profile doesn't exist) for login shells.
        # Often .bash_profile sources .bashrc.
        target_profiles = [home / ".bashrc", home / ".bash_profile"]
    else: # Fallback for other shells or if SHELL env var is not set/recognized
        target_profiles = [home / ".profile"] # A common general profile

    # Try to update the identified profiles
    for profile_path in target_profiles:
        if _add_to_shell_profile(profile_path, line_to_add):
            profiles_updated.append(profile_path.name)
            # For many common setups, updating the main interactive rc file is enough.
            # We'll print a message referring to the first successful one.
            break # Stop after successfully updating one of the primary target profiles.
            
    # If no shell-specific profile was updated, try a general one if not already tried
    if not profiles_updated:
        general_fallback_profiles = [home / ".profile"]
        if current_shell_name == "bash" and not any(p == home / ".bash_profile" for p in target_profiles) and not (home / ".bash_profile").exists():
            # If .bash_profile doesn't exist, bash often reads .profile on login
            if home / ".profile" not in target_profiles: # Ensure not already tried
                 target_profiles.append(home / ".profile")

        for profile_path in general_fallback_profiles:
            if profile_path.name not in [Path(p).name for p in target_profiles]: # Check by name to avoid duplicate logic if path objects differ
                if _add_to_shell_profile(profile_path, line_to_add):
                    profiles_updated.append(profile_path.name)
                    break


    if profiles_updated:
        console.print(f"✅ [green]{key} added to your shell profile(s): {', '.join(profiles_updated)}.[/green]")
        first_updated_profile = profiles_updated[0]
        source_command = f"source ~/{first_updated_profile}"
        if first_updated_profile.startswith('.'): # e.g. .profile
             source_command = f"source ~/{first_updated_profile}"
        else: # Should not happen with common profiles, but for safety
             source_command = f"source {first_updated_profile}"

        console.print(f"   [green]Please run '[bold cyan]{source_command}[/bold cyan]' or open a new terminal for changes to take effect.[/green]")
        return True
    else:
        console.print(f"⚠️ [yellow]Could not automatically determine or write to your shell profile to set {key}.[/yellow]")
        console.print(f"   [yellow]Please add the following line to your shell's startup file (e.g., .bashrc, .zshrc, .profile):[/yellow]")
        console.print(f"     [bold cyan]{line_to_add}[/bold cyan]")
        return False

def ensure_api_key_is_set() -> bool:
    """
    Checks if the GEMINI_API_KEY is set. If not, prompts the user and attempts to set it.
    Returns True if the key is now set (either was already or user provided it), False otherwise.
    """
    api_key = os.getenv(API_KEY_ENV_VAR)
    if api_key:
        return True

    console.print(Rule(f"[yellow]Missing {API_KEY_ENV_VAR}[/yellow]", style="yellow"))
    console.print(
        f"The [bold yellow]{API_KEY_ENV_VAR}[/bold yellow] environment variable is not set. "
        "This key is required to use the AI features."
    )
    console.line()

    api_key_input = _prompt_for_api_key()

    if not api_key_input:
        console.print(f"❌ [bold red]No API key provided. Cannot proceed with AI features.[/bold red]")
        console.print(f"   Please set the [bold yellow]{API_KEY_ENV_VAR}[/bold yellow] environment variable manually and try again.")
        console.line()
        return False

    os.environ[API_KEY_ENV_VAR] = api_key_input
    console.print(f"✅ [green]{API_KEY_ENV_VAR} has been set for the current session.[/green]")

    try:
        set_permanently = questionary.confirm(
            "Do you want to try to set this API key permanently in your environment?",
            default=True,
            auto_enter=False, # User must explicitly press enter
            style=QuestionaryStyle([('qmark', 'fg:#FF9D00 bold'),('question', 'bold')]),
            qmark="💾"
        ).ask()
        if set_permanently is None: # User cancelled (e.g. Ctrl+C)
            console.print(f"ℹ️ [info]API key permanent set choice cancelled. {API_KEY_ENV_VAR} is set for this session only.[/info]")
            set_permanently = False # Treat cancellation as "no"
    except Exception: 
        console.print("[bold yellow]Questionary prompt failed, falling back to simple confirmation.[/bold yellow]")
        set_permanently = RichConfirm.ask(f"Set {API_KEY_ENV_VAR} permanently?", default=True, console=console)


    if set_permanently:
        console.line()
        if sys.platform == "win32":
            _set_env_var_permanently_windows(API_KEY_ENV_VAR, api_key_input)
        else:
            _set_env_var_permanently_unix(API_KEY_ENV_VAR, api_key_input)
    else:
        console.print(f"ℹ️ [info]Okay, {API_KEY_ENV_VAR} is set for this session only.[/info]")

    console.line()
    return True
# --- END API Key Management ---



# Wrapper for display_personas_entry_point to defer import
def display_personas_entry_point_wrapper(value: bool):
    if value:
        from .tools_and_personas import _display_personas_impl as display_personas_callback_internal
        # This callback typically exits, so no need to return its value unless Typer specifically needs it
        display_personas_callback_internal(value)
        raise typer.Exit() # Explicitly exit if the callback doesn't
    return value # Should not be reached if callback exits


# Wrapper for display_persona_details_callback to defer import
def display_persona_details_callback_wrapper(value: Optional[str]):
    if value is not None: # Option was provided
        from .tools_and_personas import _display_persona_details_impl as display_persona_details_actual_callback
        display_persona_details_actual_callback(value) # This callback likely handles typer.Exit
        raise typer.Exit() # Explicitly exit
    return value # Must return value for Typer if not exiting

# Wrapper for ChatHandler.list_ids callback to defer import
def list_chats_callback_wrapper(value: bool):
    if value: # Flag was provided
        from .chat_manage import ChatHandler
        ChatHandler.list_ids(value) # This callback likely handles typer.Exit
        raise typer.Exit() # Explicitly exit
    return value # Must return value for Typer


# Updated epilog_text (assuming this is correct from previous state)

class InteractiveHelpTyper(typer.Typer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format_epilog(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        current_command_epilog = self.epilog
        if not (ctx.parent is None and current_command_epilog): # Not main help or no epilog
            if current_command_epilog:
                formatter.write_paragraph()
                formatter.write_text(current_command_epilog)
            return

        epilog_to_render = current_command_epilog
        if sys.stdin.isatty(): # Only ask if interactive
            try:
                # import questionary # Already imported globally
                decision_attr_name = '_show_examples_main_app_help_decision'
                if hasattr(ctx, decision_attr_name):
                    show_examples = getattr(ctx, decision_attr_name)
                else:
                    show_examples = questionary.confirm(
                        "Show command examples in help?",
                        default=True,
                        auto_enter=False, # Make user confirm explicitly
                        kbi_msg="Example display choice cancelled. Defaulting to show."
                    ).ask()
                    if show_examples is None: # User cancelled prompt
                        show_examples = True # Default to showing examples on cancel
                    setattr(ctx, decision_attr_name, show_examples)
                if not show_examples:
                    epilog_to_render = None
            except Exception: # Fallback if questionary fails for any reason
                pass # Just show the epilog by default if prompt fails
        
        if epilog_to_render:
            formatter.write_paragraph()
            formatter.write_text(epilog_to_render)


app = InteractiveHelpTyper(rich_markup_mode="rich")

@app.callback(invoke_without_command=True)
def default_handler_main(
    ctx: typer.Context,
    prompt_args: Annotated[Optional[List[str]], typer.Argument(
        show_default=False,
        help="The prompt text. Can be entered as a single string or multiple words. Options like .dev, .talk should precede this.",
        metavar="[PROMPT_TEXT...]"
    )] = None,
    model: Annotated[str, typer.Option(
        help="LLM to use. Passed to developer/ch if .dev is used.",
        hidden=True,
    )] = cfg.get("DEFAULT_MODEL"),
    temperature: Annotated[float, typer.Option(
        min=0.0, max=2.0, help="Randomness of output.",
        hidden=True,
    )] = 0.0,
    top_p: Annotated[float, typer.Option(
        min=0.0, max=1.0, help="Limits highest probable tokens.",
        hidden=True,
    )] = 1.0,
    md: Annotated[bool, typer.Option(
        help="Prettify markdown output.",
        hidden=True,
    )] = (cfg.get("PRETTIFY_MARKDOWN") == "true"),
    shell: Annotated[bool, typer.Option( # Hidden general shell assistance
        "--assist-shell",
        help="Generate/execute shell commands. (Assistance Options)",
        rich_help_panel="Assistance Options",
        hidden=True 
    )] = False,
    interaction: Annotated[bool, typer.Option( # Hidden general shell assistance
        help="Interactive mode for shell assistance. (Assistance Options)",
        rich_help_panel="Assistance Options",
        hidden=True
    )] = (cfg.get("SHELL_INTERACTION") == "true"),
    describe_shell: Annotated[bool, typer.Option(
        "--describe-shell", "-d", help="Describe a shell command.", rich_help_panel="Assistance Options"
    )] = False,
    code: Annotated[bool, typer.Option(
        ".dev" ,
        help="Generate code with developer/ch. Use .talk for its chat mode.",
        rich_help_panel="Code Development Module",
    )] = False,
    shell_mode: Annotated[bool, typer.Option(
        ".shell",
        help="Invoke Vigi Shell: Interactive AI Shell, or single query processing.",
        rich_help_panel="Vigi Shell Module",
    )] = False,
    memshell_flag: Annotated[bool, typer.Option(
        ".memshell",
        help="Invoke Vigi Shell with session memory (interactive, retains context).",
        rich_help_panel="Vigi Shell Module",
    )] = False,
    devch_output_dir: Annotated[Optional[str], typer.Option( # Hidden
        "--devch-output-dir",
        help="Base output directory for developer/ch (with .dev).",
        rich_help_panel="Code Development Module",
        hidden=True,
    )] = None,
    devch_debug: Annotated[bool, typer.Option( # Hidden
        "--devch-debug",
        help="Enable debug logging for developer/ch (with .dev).",
        rich_help_panel="Code Development Module",
        hidden=True,
    )] = False,
    conversation: Annotated[bool, typer.Option(
        ".talk", "--conversation",
        help="Enable conversation. With .dev, enables developer/ch chat. Else, Vigi REPL/chat.",
        rich_help_panel="Persona and Chat Module",
    )] = False,
    docker: Annotated[bool, typer.Option(
        "--docker", help="Specialized assistance for Docker commands.", rich_help_panel="Docker Module",
    )] = False,
    functions: Annotated[bool, typer.Option(
        help="Allow AI to use predefined function calls.", rich_help_panel="Assistance Options",
    )] = (cfg.get("VIGI_USE_FUNCTIONS") == "true"),
    editor: Annotated[bool, typer.Option( # Hidden
        help="Open $EDITOR to provide a prompt.",
        hidden=True,
        )] = False,
    cache: Annotated[bool, typer.Option( # Hidden
        help="Cache completion results from AI.",
        hidden=True,
        )] = True,
    repl: Annotated[bool, typer.Option( # Hidden and Deprecated
        ".convo", help="Start a REPL session (DEPRECATED, use .talk or --conversation).", rich_help_panel="Persona and Chat Module", hidden=True,
    )] = False,
    repl_id: Annotated[Optional[str], typer.Option( # Hidden
        "--repl-id", help="Session ID for REPL/conversation (optional, cached if provided).", rich_help_panel="Persona and Chat Module",
        hidden=True,
    )] = None,
    show_chat_id: Annotated[Optional[str], typer.Option( # Hidden
        "--show-chat", help="Show messages from a specific chat ID.", rich_help_panel="Persona and Chat Module",
        hidden=True,
    )] = None,
    list_chats_flag: Annotated[bool, typer.Option( # Callback now handles exit
        "--list-chats", "-lc",
        help="List existing chat ids.",
        callback=list_chats_callback_wrapper, 
        rich_help_panel="Persona and Chat Module",
        is_eager=True, # This will cause the callback to run and exit early
        hidden=True,
    )] = False,
    select_persona_flag: Annotated[bool, typer.Option(
        ".prs", ".persona",
        help="Interactively select or create a persona, then starts a REPL session.",
        rich_help_panel="Persona and Chat Module",
        is_flag=True # It's just a flag, no value needed after it
    )] = False,
    show_role_trigger: Annotated[Optional[str], typer.Option( # Callback now handles exit
        "--show-role",
        help="Show details of a specific persona: --show-role MyRoleName",
        callback=display_persona_details_callback_wrapper,
        rich_help_panel="Persona and Chat Module",
        is_eager=True, # This will cause the callback to run and exit early
    )] = None, # Default to None, callback handles if value is passed
    display_personas_trigger: Annotated[bool, typer.Option( # Callback now handles exit
        ".shpersonas", ".shprs",
        help="List all available personas.",
        callback=display_personas_entry_point_wrapper,
        rich_help_panel="Persona and Chat Module",
        is_eager=True # This will cause the callback to run and exit early
    )] = False # Default to False, callback runs if flag is present
) -> None:

    # --- Ensure API key is set ---
    # Check if any eager, info-only flags that don't need AI are the primary reason for invocation.
    # Their callbacks typically call typer.Exit(), so this code block might not even be reached.
    # If it IS reached, it means Typer is proceeding with normal command processing.
    
    # The `is_eager=True` options for list_chats, show_role, display_personas should have
    # their callbacks executed *before* this main callback's body, and they should exit.
    # Thus, if we are *in* this body, those specific eager options likely weren't the *sole*
    # command or they didn't exit (which would be a bug in their callbacks).

    # A simple check: if we have no actual command/prompt args, and none of the main mode flags are set,
    # it's likely help was invoked OR it's an invalid invocation.
    # Typer handles `-h` / `--help` before the main callback if no command is given.
    # If a subcommand is given, help for that subcommand is handled.

    needs_ai_features = (code or shell_mode or memshell_flag or conversation or docker or 
                         select_persona_flag or (prompt_args and any(prompt_args))) # More direct check
    
    if needs_ai_features: # Only check API key if a feature requiring AI is invoked
        if not ensure_api_key_is_set():
            console.print(f"❌ [bold red]Exiting as {API_KEY_ENV_VAR} setup was not completed and AI features are required.[/bold red]")
            console.line()
            raise typer.Exit(code=1)
    
    # If we've reached here after `is_eager=True` callbacks, it means they didn't exit.
    # This typically happens if the user combines an eager flag with other args that
    # make Typer try to run the main handler.
    # We assume eager callbacks handle their exit, so no explicit `is_info_command` check here is strictly necessary
    # as long as their callbacks do exit.

    if ctx.invoked_subcommand is not None:
        return

    # stdin_content_str, cli_arg_prompt_str, effective_prompt logic (assuming correct from previous)
    stdin_content_str: Optional[str] = None
    if not sys.stdin.isatty():
        stdin_data_lines = []
        for line in sys.stdin:
            if "__sgpt__eof__" in line: # Specific EOF marker for sgpt compatibility
                break
            stdin_data_lines.append(line)
        if stdin_data_lines:
            stdin_content_str = "".join(stdin_data_lines).strip()
        try: # Attempt to reopen tty for subsequent interactive prompts if needed
            if os.name == "posix":
                sys.stdin = open("/dev/tty", "r")
            elif os.name == "nt":
                sys.stdin = open("CONIN$", "r") # For Windows
        except OSError:
            # If tty cannot be reopened, subsequent prompts (like API key, confirmation) might fail
            # This is a complex edge case; for now, we proceed.
            pass

    cli_arg_prompt_str: Optional[str] = None
    if prompt_args: # prompt_args is List[str] or None
        processed_args = [str(arg) for arg in prompt_args if arg is not None]
        if processed_args:
            cli_arg_prompt_str = " ".join(processed_args).strip()
            if not cli_arg_prompt_str: # Handle case of empty strings after join
                cli_arg_prompt_str = None
    
    effective_prompt: Optional[str] = None
    if stdin_content_str and cli_arg_prompt_str:
        effective_prompt = f"{stdin_content_str}\n\n{cli_arg_prompt_str}"
    elif stdin_content_str:
        effective_prompt = stdin_content_str
    elif cli_arg_prompt_str:
        effective_prompt = cli_arg_prompt_str

    if editor and not effective_prompt: # If editor flag and no other prompt, get from editor
        from .corefunctions import get_edited_prompt # Dynamic import
        effective_prompt = get_edited_prompt()


    # Persona selection and determination logic (assuming correct from previous state)
    role_class: Optional['DigitalPersona'] = None
    general_shell_assistance_flag = shell # from --assist-shell (hidden)
    # vigi_shell_mode_flag = shell_mode # .shell (already defined)

    vigi_main_conversation_mode = (conversation and not code) or \
                                  (repl and not code) # repl is deprecated

    if select_persona_flag: # .prs or .persona
        from .tools_and_personas import DigitalPersona # Dynamic import
        # import questionary # Already imported globally
        try:
            role_class = DigitalPersona.retrieve_persona()
        except InterruptedError: # Custom error from persona logic
            typer.secho("Persona selection/creation was cancelled. Exiting.", fg=typer.colors.YELLOW)
            raise typer.Exit(code=0)
        except (BadArgumentUsage, RuntimeError) as e:
            typer.secho(f"Error during persona processing: {e}", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        
        if role_class:
            vigi_main_conversation_mode = True # If persona selected, implies conversation
        # else: # Should not happen if retrieve_persona exits on failure/cancel
            # typer.secho("No persona selected/created. Exiting.", fg=typer.colors.YELLOW)
            # raise typer.Exit(code=1)
    else:
        from .tools_and_personas import DefaultPersonas, DigitalPersona # Dynamic import
        role_class = DefaultPersonas.determine_persona(general_shell_assistance_flag, describe_shell, code)

    if not role_class: # Should be caught by DefaultPersonas logic if no persona applies
        typer.secho("CRITICAL: Persona could not be determined. This indicates an issue with default persona logic.", fg=typer.colors.RED)
        raise typer.Exit(1) # Or provide a very basic fallback if desired


    # Module dispatching logic (assuming correct from previous state)
    if docker:
        from .docker_part.docker_main import docker_main # Dynamic import
        docker_main()
        raise typer.Exit()

    if memshell_flag: # .memshell
        from .shell_part.main import ai_shell_interactive # Dynamic import for older shell
        if effective_prompt:
            typer.secho(
                "Warning: .memshell is for interactive sessions; provided prompt ignored.",
                fg=typer.colors.YELLOW,
            )
        typer.echo("Starting Vigi Shell with session memory (.memshell)...")
        ai_shell_interactive() # This function should handle its own exit
        raise typer.Exit() # Ensure exit if it doesn't

    if shell_mode: # .shell
        # This now points to the VigiShellApp ('smart' shell)
        from .shell_smart.shell_main import vigi_shell_entry_point as smart_vigi_shell_entry_point
        smart_vigi_shell_entry_point(initial_query=effective_prompt if effective_prompt else None)
        raise typer.Exit()

    if code: # .dev
        from .developerch.main import main as developerch_main # Dynamic import
        dev_ch_conversation_mode = conversation # from .talk or --conversation

        if repl and not dev_ch_conversation_mode: # .convo with .dev is invalid
            raise BadArgumentUsage(
                "Cannot use .convo with .dev. Use '.dev .talk' for developer/ch chat."
            )

        original_argv = sys.argv[:]
        developerch_args = ['developerch_invoker'] # Dummy first arg for argparser
        if effective_prompt:
             developerch_args.extend(['--prompt', effective_prompt])
        # Pass relevant options to developerch_main
        if model != cfg.get("DEFAULT_MODEL"): # Only pass if not default
            developerch_args.extend(['--model', model])
        if devch_output_dir:
            developerch_args.extend(['--output_dir', devch_output_dir])
        if devch_debug:
            developerch_args.append('--debug') # Match devch's expected debug flag name
        if dev_ch_conversation_mode:
            developerch_args.append('--conversation')
        
        sys.argv = developerch_args # Temporarily replace sys.argv
        exit_code = 0
        try:
            # developerch_main might call sys.exit itself.
            # It should ideally be refactored to be callable and return status or raise exceptions.
            developerch_main() 
        except SystemExit as e_sys: # Capture sys.exit from developerch_main
            exit_code = e_sys.code if isinstance(e_sys.code, int) else (0 if e_sys.code is None else 1)
        except Exception as e_exc:
            typer.secho(f"Error running developer/ch module: {e_exc}", file=sys.stderr, fg=typer.colors.RED)
            exit_code = 1
        finally:
            sys.argv = original_argv # Restore original sys.argv
        raise typer.Exit(code=exit_code) # Exit with code from developerch


    if show_chat_id: # --show-chat <id>
        from .chat_manage import ChatHandler # Dynamic import
        ChatHandler.show_messages(show_chat_id, md)
        raise typer.Exit() # show_messages should probably exit, but ensure it.
    
    # Function calling schema preparation
    function_schemas_repl = None
    function_schemas_single = None
    if functions: # --functions flag
        from .tools_and_personas import collect_schemas # Dynamic import
        schemas = collect_schemas() or None # Ensure it's None if empty list/None
        function_schemas_repl = schemas # For REPL/conversation mode
        function_schemas_single = schemas # For single-shot mode


    if vigi_main_conversation_mode: # .talk or .prs (which sets this true)
        from .convo_manage import ReplHandler # Dynamic import
        if not effective_prompt and not repl_id and select_persona_flag : # If .prs and no prompt
             typer.echo(f"Starting Vigi conversation with selected persona: {role_class.identifier}")
        
        ReplHandler(repl_id, role_class, md).handle(
            init_prompt=effective_prompt if effective_prompt else "", # Pass empty if None
            model=model,
            temperature=temperature,
            top_p=top_p,
            caching=cache,
            functions=function_schemas_repl, # Pass schemas for REPL mode
        )
        raise typer.Exit() # ReplHandler.handle should ideally exit, but ensure it.


    # --- Default single-shot query execution if no other mode was triggered ---
    if not effective_prompt: # If NO prompt and NO mode was triggered.
        typer.secho("No prompt provided and no specific mode selected (e.g., .shell, .talk, .dev).", fg=typer.colors.YELLOW)
        console.line()
        typer.echo(ctx.get_help()) # Show help
        raise typer.Exit(code=1)

    # Check for conflicting general shell assistance flags if --assist-shell path is taken
    if general_shell_assistance_flag and describe_shell:
        raise BadArgumentUsage(
            "Cannot use general shell assistance (--assist-shell) and --describe-shell together."
        )
    
    if repl_id == ".dev": # Should not be possible due to earlier checks, but defensive.
        raise BadArgumentUsage("Session ID for --repl-id cannot be '.dev'.")


    # At this point, it's a single-shot query to the default handler
    from .base_manage import DefaultHandler # Dynamic import
    full_completion = DefaultHandler(role_class, md).handle(
        prompt=effective_prompt, # effective_prompt is guaranteed to be non-None here
        model=model,
        temperature=temperature,
        top_p=top_p,
        caching=cache,
        functions=function_schemas_single # Pass schemas for single-shot mode
    )

    # Post-completion interaction loop for shell commands (if general_shell_assistance_flag was true)
    # This is the hidden --assist-shell path
    active_shell_interaction_loop = general_shell_assistance_flag and interaction and full_completion

    while active_shell_interaction_loop:
        from click.types import Choice as ClickChoice # Dynamic import, specific for typer.prompt
        from .corefunctions import run_command # Dynamic import
        console.line()
        # Use questionary for better prompt if available, fallback to typer.prompt
        try:
            action_choices = [
                questionary.Choice(title="[E]xecute Command", value="e"),
                questionary.Choice(title="[A]bort", value="a"),
            ]
            default_action = "e" if cfg.get("DEFAULT_EXECUTE_SHELL_CMD") == "true" else "a"
            
            option_choice_q = questionary.select(
                "Choose action for generated shell command:",
                choices=action_choices,
                default=next((c for c in action_choices if c.value == default_action), None),
                style=QuestionaryStyle([('qmark', 'fg:#00FF00 bold'),('question', 'bold')]), # Green qmark
                qmark="⚙️"
            ).ask()
            option_choice = option_choice_q if option_choice_q else default_action # Handle None from cancel
        except Exception: # Fallback if Questionary fails
            console.print("[yellow]Questionary prompt failed, using basic prompt.[/yellow]")
            option_choice = typer.prompt(
                text="Choose action: [E]xecute, [A]bort",
                type=ClickChoice(("e", "a"), case_sensitive=False),
                default="e" if cfg.get("DEFAULT_EXECUTE_SHELL_CMD") == "true" else "a",
                show_choices=True, show_default=True,
            )
        console.line()
        
        if option_choice == "e":
            run_command(full_completion) # This function needs to handle command execution
            break 
        elif option_choice == "a":
            typer.secho("Shell command execution aborted by user.", fg=typer.colors.YELLOW)
            break
        # else loop continues if an invalid choice somehow got through (shouldn't with Choice type)

if __name__ == "__main__":
    try:
        app()
    except Exception as e:
        # Fallback for any unhandled exceptions during app() call if rich traceback not active
        # Should be rare if rich.traceback.install() is active early
        console.print(f"[bold red]An unexpected error occurred in main execution: {e}[/bold red]")
        # Optionally, print full traceback here for non-rich scenarios
        # import traceback
        # console.print(traceback.format_exc())
        sys.exit(1)
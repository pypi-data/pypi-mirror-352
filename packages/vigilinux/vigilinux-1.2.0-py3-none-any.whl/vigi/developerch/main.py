import sys
import time
import argparse
import os
import json
import re
from pathlib import Path
from datetime import datetime, timezone
import logging
from typing import Optional, List, Dict, Any, Tuple
import asyncio
import shutil # For terminal size

try:
    import questionary
    from questionary import Style, Separator, Choice
except ImportError:
    print("The 'questionary' library is required. 'pip install questionary'")
    sys.exit(1)

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.markdown import Markdown
    from rich.syntax import Syntax
    from rich.tree import Tree
    from rich.live import Live
    from rich.spinner import Spinner
    from rich.prompt import Confirm
    from rich.table import Table
    from rich.padding import Padding
    from rich.theme import Theme
    from rich.rule import Rule
    from rich.traceback import install as rich_traceback_install
    rich_traceback_install(show_locals=False) # Prettier tracebacks
except ImportError:
    print("The 'rich' library is required for the enhanced UI. 'pip install rich'")
    sys.exit(1)


# Import the PURELY SYNCHRONOUS functions directly
from .prompts import (
    plan,
    specify_file_paths,
    generate_project_slug
)
# Import the ASYNC versions of functions that have sync wrappers in prompts.py
from .prompts import (
    generate_code as prompts_generate_code_async,
    handle_conversation as prompts_handle_conversation_async,
    generate_modification as prompts_generate_modification_async,
    answer_question as prompts_answer_question_async
)
from .utils import generate_folder, write_file, load_codebase, save_codebase, get_file_tree as util_get_file_tree


MODEL_NAME = "gemini-1.5-pro-latest"
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# --- Rich Console and Theme ---
custom_rich_theme = Theme({
    "info": "dim cyan",
    "warning": "yellow",
    "danger": "bold red",
    "success": "green",
    "tip": "dim blue",
    "debug": "dim magenta",
    "header_main": "blue_violet", # For pyfiglet part 1
    "header_tag": "steel_blue",  # For pyfiglet part 2
    "panel_border": "blue_violet",
    "file": "bold green",
    "directory": "bold blue",
    "ai_response": "bright_white",
    "rule_title": "bold blue_violet",
})
console = Console(theme=custom_rich_theme, highlight=False)

CONFIG_DIR = Path.home() / "Desktop"
HISTORY_FILE = CONFIG_DIR / "vg_dev_history.json"

# --- UI Constants ---
BACK_ACTION_TEXT = "[↩️ Back]"
BACK_TO_MAIN_MENU_TEXT = "[↩️ Back to Main Menu]"
EXIT_ACTION_TEXT = "[🚪 Exit]"

# --- Custom Style for Questionary (remains important) ---
custom_style = Style([
    ('qmark', 'fg:#673ab7 bold'),
    ('question', 'bold'),
    ('answer', 'fg:#f44336 bold'),
    ('pointer', 'fg:#673ab7 bold'),
    ('highlighted', 'fg:#673ab7 bold'),
    ('selected', 'fg:#03a9f4'),
    ('separator', 'fg:#cc5454'),
    ('instruction', 'fg:#858585'),
    ('text', ''),
    ('disabled', 'fg:#858585 italic')
])

# --- UI Helper Functions (Header reverted, others use Rich) ---
def print_header(text: str): # Reverted header
    import pyfiglet
    terminal_width = shutil.get_terminal_size().columns
    main_font = "big"
    try:
        main_art = pyfiglet.figlet_format(text, font=main_font)
        tag_art = pyfiglet.figlet_format("< / >", font=main_font)
    except pyfiglet.FontNotFound:
        # Basic fallback if font is missing
        console.print(Rule(f"[bold header_main]{text} < / >[/bold header_main]", style="header_main"))
        console.line()
        return

    main_lines = main_art.splitlines()
    tag_lines = tag_art.splitlines()
    combined_lines = []
    max_lines = max(len(main_lines), len(tag_lines))

    # Pad shorter art to match longest
    main_lines += [""] * (max_lines - len(main_lines))
    tag_lines += [""] * (max_lines - len(tag_lines))

    spacer = "    "  # Spacer between the two figlet arts
    for m_line, t_line in zip(main_lines, tag_lines):
        # Calculate width of each line to help with centering if needed
        # For now, direct combination and centering the whole block
        combined_line_art = m_line + spacer + t_line
        combined_lines.append(combined_line_art.center(terminal_width)) # Center each combined line

    # Define ANSI colors directly for Pyfiglet part
    # Rich handles its own color parsing within Text.from_ansi or print markup
    pyfiglet_colors = ["\033[38;5;99m", "\033[38;5;105m", "\033[38;5;111m", "\033[38;5;117m", "\033[38;5;123m"]
    reset_color = "\033[0m"

    console.line() # Space before header
    for i, line_content in enumerate(combined_lines):
        color_code = pyfiglet_colors[i % len(pyfiglet_colors)]
        # We print directly using Python's print for this specific header
        # as Rich's ANSI parsing might interfere with precise pyfiglet color cycling.
        print(f"{color_code}{line_content}{reset_color}")
    console.line() # Space after header

def print_success(text: str): console.print(f"✅ [success]{text}[/success]")
def print_warning(text: str): console.print(f"⚠️ [warning]{text}[/warning]")
def print_info(text: str): console.print(f"ℹ️ [info]{text}[/info]")
def print_error_msg(text: str): console.print(f"❌ [danger]{text}[/danger]")
def print_tip(text: str): console.print(f"💡 [tip]{text}[/tip]")
def print_debug(text: str):
    if logger.getEffectiveLevel() <= logging.DEBUG:
         console.print(f"🐞 [debug]DEBUG: {text}[/debug]")


def _run_in_thread_with_new_loop(async_func, *args, **kwargs):
    return asyncio.run(async_func(*args, **kwargs))

# --- Rich-enhanced Get File Tree ---
def get_rich_file_tree(start_path: str) -> Tree:
    path_obj = Path(start_path)
    tree = Tree(
        f":📂: [link file://{path_obj}]{path_obj.name}",
        guide_style="bold bright_blue",
    )
    ignore_dirs = {".git", "__pycache__", ".DS_Store", ".vscode", "node_modules", "venv", ".env", ".pytest_cache", ".mypy_cache", "build", "dist", ".vigi_dev_meta"}
    ignore_files = {"*.pyc"}

    def add_to_tree(pth: Path, branch: Tree, level=0):
        if level > 5: # Increased depth slightly
            branch.add("[dim orange]... (depth limit reached)[/dim orange]")
            return
        try:
            dir_items = list(pth.iterdir())
        except PermissionError:
            branch.add("[dim red]🚫 Access Denied[/dim red]")
            return
        except FileNotFoundError:
            branch.add("[dim red]❓ Path Not Found[/dim red]")
            return

        for item in sorted(dir_items, key=lambda x: (not x.is_dir(), x.name.lower())):
            if item.name in ignore_dirs or any(item.match(p) for p in ignore_files):
                continue
            if item.is_dir():
                style = "directory"
                icon = "📁"
                child_branch = branch.add(Text.assemble((icon, "default"), (" ", "default"), (item.name, style), ("/", "default")),
                                          style=style) # More explicit Text assemble
                add_to_tree(item, child_branch, level + 1)
            else:
                style = "file"
                icon = "📄"
                branch.add(Text.assemble((icon, "default"), (" ", "default"), (item.name, style)), style=style)
    try:
        add_to_tree(path_obj, tree)
    except Exception as e:
        tree.add(f"[danger]Error reading directory structure: {e}[/danger]")
    return tree


# --- Terminal Folder Selector (Uses Rich for its internal prints) ---
def _is_vigi_dev_project(path: Path) -> bool:
    return (path.resolve() / ".vigi_dev_meta" / "project_context.json").is_file()

async def _ask_for_project_directory_terminal_async() -> Optional[str]:
    current_path = Path.home().resolve()
    terminal_width = shutil.get_terminal_size().columns

    while True:
        console.line() # Spacer
        # ... (rest of the logic is the same, internal prints are Rich, Questionary handles the list)
        # Code from previous version's _ask_for_project_directory_terminal_async can be pasted here
        # Ensure any direct 'print' inside this loop is replaced by console.print
        try:
            entries = await asyncio.to_thread(os.listdir, current_path)
            choices_meta = []
            for entry_name in entries:
                entry_path = current_path / entry_name
                try:
                    is_dir = await asyncio.to_thread(entry_path.is_dir)
                    if is_dir:
                         choices_meta.append({"name": entry_name, "path": entry_path, "is_dir": True})
                except (PermissionError, FileNotFoundError):
                    continue
        except PermissionError:
            console.print(f"🚫 [danger]Permission denied for '{current_path}'[/danger]")
            if current_path.parent != current_path:
                current_path = current_path.parent
                continue
            else:
                console.print("[warning]Cannot navigate further. Please check permissions.[/warning]")
                return None
        except FileNotFoundError:
            console.print(f"❓ [warning]Path not found: '{current_path}'. Resetting to Home.[/warning]")
            current_path = Path.home().resolve()
            continue
        except Exception as e:
            logger.error(f"Error listing directory {current_path}: {e}", exc_info=True)
            console.print(f"❗[danger]Error accessing '{current_path}'.[/danger]")
            if current_path.parent != current_path:
                current_path = current_path.parent
                continue
            else:
                return None

        q_choices = []
        is_current_project = await asyncio.to_thread(_is_vigi_dev_project, current_path)

        if is_current_project:
            q_choices.append(Choice(
                title=f"[🎯 Select Vigi_Dev Project: {current_path.name} ✨]",
                value={"action": "select_current_project", "path": current_path}
            ))
        else:
             q_choices.append(Choice(
                title=f"[➡️ Navigate into: {current_path.name}] (Not a Vigi_Dev project folder)",
                value={"action": "navigate_into_current", "path": current_path} # Essentially navigates
            ))

        if current_path.parent != current_path:
             q_choices.append(Choice(title="[⬆️ Go to Parent Directory (..)]", value={"action": "go_up", "path": current_path.parent}))
        q_choices.append(Separator())
        sorted_entries = sorted([item for item in choices_meta if item["is_dir"]], key=lambda x: x["name"].lower())

        for item in sorted_entries:
            is_sub_project = await asyncio.to_thread(_is_vigi_dev_project, item['path'])
            title = f"📁 {item['name']}/"
            if is_sub_project:
                title += " ✨ (Vigi_Dev Project)"
            q_choices.append(Choice(title=title, value={"action": "navigate", "path": item['path']}))

        q_choices.append(Separator())
        q_choices.append(Choice(title="[✏️ Enter Path Manually]", value={"action": "manual_path"}))
        q_choices.append(Choice(title="[❌ Cancel Selection]", value={"action": "cancel"}))

        path_str_for_prompt = str(current_path)
        max_len_for_message = terminal_width - 35
        truncated_path_for_message = (
            f"{path_str_for_prompt[:(max_len_for_message - 3) // 2]}..."
            f"{path_str_for_prompt[-(max_len_for_message - 3) // 2:]}"
            if len(path_str_for_prompt) > max_len_for_message and max_len_for_message > 20
            else path_str_for_prompt
        )
        select_message = f"Browse & select Vigi_Dev project folder. Current: [blue_violet]{truncated_path_for_message}[/blue_violet]"

        chosen_item = await questionary.select(
            message=select_message, choices=q_choices, style=custom_style, qmark="🗂️"
        ).ask_async()
        console.line() # Spacer

        if chosen_item is None: return None
        action = chosen_item["action"]

        if action == "navigate" or action == "go_up" or action == "navigate_into_current":
            current_path = chosen_item["path"].resolve()
        elif action == "select_current_project":
            return str(chosen_item["path"].resolve())
        elif action == "manual_path":
            manual_path_str = await questionary.text(
                "Enter full path to the Vigi_Dev project folder:", default=str(current_path), style=custom_style, qmark="✍️"
            ).ask_async()
            console.line() # Spacer
            if manual_path_str:
                manual_path = Path(manual_path_str.strip()).resolve()
                if await asyncio.to_thread(manual_path.is_dir):
                    current_path = manual_path
                    if await asyncio.to_thread(_is_vigi_dev_project, current_path):
                        console.print(f"✨ [success]Path '{current_path.name}' is a valid Vigi_Dev project.[/success]")
                        console.line()
                        confirm_select = await questionary.confirm(
                             f"Select this Vigi_Dev project: '{current_path.name}'?", default=True, style=custom_style, qmark="❓"
                         ).ask_async()
                        if confirm_select: return str(current_path)
                    else:
                        console.print(f"⚠️ [warning]Path '{current_path.name}' is a directory but not a Vigi_Dev project. Listing contents...[/warning]")
                else:
                    console.print(f"🚫 [danger]Path '{manual_path_str}' is not a valid directory.[/danger]")
            continue
        elif action == "cancel":
            return None


# --- Project History and Basic Utils ---
def _ensure_config_dir(): CONFIG_DIR.mkdir(parents=True, exist_ok=True)
def load_project_history() -> List[Dict[str, str]]:
    _ensure_config_dir()
    if not HISTORY_FILE.exists(): return []
    try:
        with open(HISTORY_FILE, 'r') as f: history = json.load(f)
        valid_history = [entry for entry in history if entry.get("path") and Path(entry["path"]).exists()]
        valid_history.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        if len(valid_history) != len(history):
            save_project_history(valid_history)
        return valid_history
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading project history: {e}. Starting empty.")
        print_warning(f"Could not load project history from {HISTORY_FILE}. It might be corrupted.")
        return []

def save_project_history(history: List[Dict[str, str]]):
    _ensure_config_dir(); seen_paths = {}; unique_history = []
    valid_history_to_save = [
        entry for entry in history
        if entry.get("path") and Path(entry["path"]).exists() and _is_vigi_dev_project(Path(entry["path"]))
    ]
    for entry in sorted(valid_history_to_save, key=lambda x: x.get("created_at", ""), reverse=True):
        path = entry.get("path")
        if path and path not in seen_paths: seen_paths[path] = entry; unique_history.append(entry)
    unique_history.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    try:
        with open(HISTORY_FILE, 'w') as f: json.dump(unique_history, f, indent=2)
    except IOError as e: logger.error(f"Error saving project history: {e}")

def add_project_to_history(project_name: str, project_path: str, original_prompt: Optional[str] = None):
    history = load_project_history()
    history = [entry for entry in history if entry.get("path") != project_path]
    new_entry = {"name": project_name, "path": project_path, "created_at": datetime.now(timezone.utc).isoformat(), "original_prompt": original_prompt or ""}
    history.append(new_entry)
    save_project_history(history)

async def _initialize_project(original_prompt: str, project_root_abs: str, project_name_for_meta: str, debug_mode: bool, model: str) -> Optional[dict]:
    if not original_prompt: print_error_msg("Cannot initialize project without an initial prompt."); return None

    console.line()
    console.print(Panel(Padding(f"Initializing project [b]'{project_name_for_meta}'[/b]", (1,2)),
                        title="[rule_title]🛠️ Project Setup[/rule_title]", border_style="panel_border",
                        subtitle=f"Location: [blue_violet]{project_root_abs}[/blue_violet]", expand=False))
    console.line()
    if debug_mode: print_debug(f"Initializing project '{project_name_for_meta}' at: {project_root_abs}")

    generate_folder(project_root_abs)
    meta_dir = os.path.join(project_root_abs, ".vigi_dev_meta"); generate_folder(meta_dir)

    with console.status("[bold green]Working on project plan...", spinner="dots") as status:
        console.line()
        status.update("📄 Step 1/3: Planning project structure...")
        shared_deps_content = plan(original_prompt, None, model=model)
        write_file(os.path.join(meta_dir, "shared_deps.md"), shared_deps_content)
        write_file(os.path.join(meta_dir, "original_prompt.txt"), original_prompt)
        if debug_mode: print_debug(f"Shared Deps:\n{shared_deps_content[:200]}...")
        console.print("  [success]✓ Plan generated.[/success]")
        console.line()

        status.update("🗺️ Step 2/3: Determining file paths...")
        file_paths_from_llm_raw = specify_file_paths(original_prompt, shared_deps_content, model=model)
        if isinstance(file_paths_from_llm_raw, str):
            file_paths_from_llm = [fp.strip() for fp in file_paths_from_llm_raw.split('\n') if fp.strip()]
        elif isinstance(file_paths_from_llm_raw, list):
            file_paths_from_llm = [str(fp).strip() for fp in file_paths_from_llm_raw if str(fp).strip()]
        else:
            file_paths_from_llm = []
            print_warning(f"Unexpected format for file paths from LLM: {type(file_paths_from_llm_raw)}. No files will be generated.")
        if debug_mode: print_debug(f"Raw file_paths from LLM:\n{file_paths_from_llm_raw}\nProcessed: {file_paths_from_llm}")
        console.print(f"  [success]✓ File paths determined ({len(file_paths_from_llm)} files).[/success]")
        console.line()

        codebase = {}; sanitized_project_files = []
        if file_paths_from_llm:
            status.update(f"💻 Step 3/3: Generating code for {len(file_paths_from_llm)} file(s)...")
            for i, gen_path_orig in enumerate(file_paths_from_llm):
                # Path sanitization logic
                norm_path = os.path.normpath(gen_path_orig); _, path_no_drive = os.path.splitdrive(norm_path)
                rel_path_comp = path_no_drive.lstrip(os.sep).lstrip('/')
                if not rel_path_comp or rel_path_comp == '.':
                    if debug_mode: print_debug(f"Skipping invalid path: '{gen_path_orig}'"); continue
                abs_final_path = os.path.abspath(os.path.join(project_root_abs, rel_path_comp))
                if not abs_final_path.startswith(os.path.abspath(project_root_abs)):
                    if debug_mode: print_debug(f"Path '{gen_path_orig}' escapes. Skipping."); continue
                final_clean_rel_path = os.path.relpath(abs_final_path, project_root_abs)
                if final_clean_rel_path == '..' or final_clean_rel_path.startswith('..' + os.sep) or final_clean_rel_path == '.':
                    if debug_mode: print_debug(f"Path '{gen_path_orig}' invalid after relpath. Skipping."); continue
                sanitized_project_files.append(final_clean_rel_path)

                status.update(f"  ⚙️ Generating ({i+1}/{len(file_paths_from_llm)}): [file]{final_clean_rel_path}[/file]...")
                code = await asyncio.to_thread(
                    _run_in_thread_with_new_loop, prompts_generate_code_async,
                    original_prompt, shared_deps_content, final_clean_rel_path, None, model
                )
                write_file(abs_final_path, code)
                codebase[final_clean_rel_path] = code
            console.print("  [success]✓ Code generation complete.[/success]")
            console.line()
        else:
            print_warning("No file paths were determined. Project will be empty initially.")
            console.line()

    project_context = {
        "original_prompt": original_prompt, "project_slug": project_name_for_meta,
        "shared_deps": shared_deps_content, "file_paths": sanitized_project_files,
        "output_dir": project_root_abs, "conversation_history": [], "codebase": codebase
    }
    context_to_save = {k: v for k, v in project_context.items() if k != "codebase"}
    try:
        with open(os.path.join(meta_dir, "project_context.json"), 'w') as f: json.dump(context_to_save, f, indent=2)
        if debug_mode: print_debug("Initial project context saved.")
        add_project_to_history(project_name_for_meta, project_root_abs, original_prompt)
        print_success(f"✨ Project '{project_name_for_meta}' initialized successfully!")
    except Exception as e:
        print_error_msg(f"Could not save initial project context or history: {e}")
    console.line()
    return project_context

def _load_project_context(project_root_abs: str, debug_mode: bool) -> Optional[dict]:
    console.line()
    meta_context_file = os.path.join(project_root_abs, ".vigi_dev_meta", "project_context.json")
    if os.path.exists(meta_context_file):
        try:
            with open(meta_context_file, 'r') as f: context_data = json.load(f)
            normalized_context_output_dir = Path(context_data.get("output_dir", "")).resolve()
            normalized_project_root_abs = Path(project_root_abs).resolve()

            if normalized_context_output_dir != normalized_project_root_abs:
                print_warning(f"Context output_dir ('{normalized_context_output_dir}') mismatch. Updating to '{normalized_project_root_abs}'.")
                context_data["output_dir"] = str(normalized_project_root_abs)

            context_data["codebase"] = load_codebase(str(normalized_project_root_abs))
            context_data.setdefault("conversation_history", [])
            if debug_mode: print_debug(f"Loaded existing project context from {meta_context_file}")
            project_name = context_data.get("project_slug", Path(str(normalized_project_root_abs)).name)
            add_project_to_history(project_name, str(normalized_project_root_abs), context_data.get("original_prompt"))
            print_success(f"🚀 Successfully loaded project: {project_name}")
            console.line()
            return context_data
        except Exception as e:
            print_error_msg(f"Could not load project context from {meta_context_file}: {e}")
            logger.error(f"Could not load project context: {e}", exc_info=True)
    else:
        print_warning(f"No project context file found at {meta_context_file}")
    console.line()
    return None

async def _start_conversation_mode(project_context: Dict[str, Any], initial_user_message: Optional[str], debug_mode: bool, model: str):
    if not project_context: print_error_msg("Cannot start conversation without project context."); return
    project_slug = project_context.get("project_slug", Path(project_context.get("output_dir", "Unknown")).name)

    console.line()
    console.print(Panel(Padding(f"Chatting about project [b]'{project_slug}'[/b]", (1,2)),
                        title="[rule_title]💬 Conversation Mode[/rule_title]", border_style="panel_border",
                        subtitle=f"📍 Location: [blue_violet]{project_context.get('output_dir')}[/blue_violet]", expand=False))
    console.line()
    print_tip("Press Ctrl+C to cancel input or action. Type 'exit' or 'quit' as your message to save & leave.")
    console.line()

    current_message_to_process = initial_user_message
    exit_flag = False

    while not exit_flag:
        actual_intent = None
        final_user_input = None

        if current_message_to_process:
            print_info(f"👉 Processing initial message: \"{current_message_to_process[:70].strip()}...\"")
            console.line()
            action_choices = [
                Choice("📝 Modify code based on this", value="modify"),
                Choice("❓ Ask a question based on this", value="ask"),
                Choice("💬 General chat using this", value="chat"),
                Separator(),
                Choice("🗑️ Discard message & choose new action", value="discard_and_new_action"),
                Choice(EXIT_ACTION_TEXT, value="exit_conversation"),
            ]
            action_for_current_message = await questionary.select(
                "How should this message be handled?", choices=action_choices, style=custom_style, qmark="💡"
            ).ask_async()
            console.line()

            if action_for_current_message is None or action_for_current_message == "exit_conversation":
                exit_flag = True; continue
            if action_for_current_message == "discard_and_new_action":
                current_message_to_process = None; continue
            actual_intent = action_for_current_message
            final_user_input = current_message_to_process
            current_message_to_process = None
        else:
            action_choices = [
                Choice("📝 Request Code Modification", value="modify"),
                Choice("❓ Ask Question (Project/Code)", value="ask"),
                Choice("💬 General Chat/Request", value="chat"),
                Separator(),
                Choice(EXIT_ACTION_TEXT, value="exit_conversation"),
            ]
            chosen_action = await questionary.select(
                "Choose an action:", choices=action_choices, style=custom_style, qmark="🎯"
            ).ask_async()
            console.line()

            if chosen_action is None or chosen_action == "exit_conversation":
                exit_flag = True; continue
            actual_intent = chosen_action
            prompt_message_map = {
                "modify": (f"Describe code modifications for '{project_slug}':", "✍️"),
                "ask": (f"Your question about '{project_slug}':", "❓"),
                "chat": (f"Your message for '{project_slug}' (General chat):", "💬")
            }
            prompt_msg, q_mark = prompt_message_map.get(actual_intent, ("Your input:", "👤"))

            user_provided_input_text = await questionary.text(
                prompt_msg, style=custom_style, qmark=q_mark
            ).ask_async()
            console.line()

            if user_provided_input_text is None: print_info("Input cancelled."); continue
            final_user_input = user_provided_input_text.strip()
            if not final_user_input: print_info("Empty input."); console.line(); continue
            if final_user_input.lower() in ["exit", "quit"]: exit_flag = True; continue


        project_context["conversation_history"].append({"role": "user", "content": final_user_input})
        ai_response_text = ""
        with console.status("[bold green]🤖 AI is thinking...", spinner="moon") as status:
            console.line() # Space before spinner starts if it's long running
            if actual_intent == "modify":
                if debug_mode: print_debug(f"Mod request: {final_user_input[:50]}...")
                modified_files_dict = await asyncio.to_thread(
                    _run_in_thread_with_new_loop, prompts_generate_modification_async,
                    project_context, final_user_input, model
                )
                response_parts = []
                if modified_files_dict and not modified_files_dict.get("error"):
                    modified_keys, skipped_details = [], []
                    for file_p, new_code_val in modified_files_dict.items():
                        if isinstance(new_code_val, str):
                            write_file(os.path.join(project_context["output_dir"], file_p), new_code_val)
                            project_context["codebase"][file_p] = new_code_val
                            if file_p not in project_context["file_paths"]: project_context["file_paths"].append(file_p)
                            modified_keys.append(f"[file]{file_p}[/file]")
                        else: skipped_details.append(f"[file]{file_p}[/file] (bad format)")
                    if modified_keys:
                        msg = f"Applied modifications to: {', '.join(modified_keys)}."
                        response_parts.append(msg); print_success(msg)
                    if skipped_details:
                        msg = f"Skipped modifications for: {', '.join(skipped_details)}."
                        response_parts.append(msg); print_warning(msg)
                    if not modified_keys and not skipped_details:
                        msg = "AI indicated no specific file modifications."
                        response_parts.append(msg); print_info(msg)
                elif modified_files_dict and modified_files_dict.get("error"):
                    err_msg = modified_files_dict['error']
                    response_parts.append(f"Modification failed: {err_msg}"); print_warning(f"Mod error: {err_msg}")
                else:
                    response_parts.append("No mods processed."); print_warning("Modification attempt: no changes.")
                ai_response_text = " ".join(response_parts).strip() or "No actionable response for modifications."
            elif actual_intent == "ask":
                if debug_mode: print_debug(f"Question: {final_user_input[:50]}...")
                ai_response_text = await asyncio.to_thread(
                    _run_in_thread_with_new_loop, prompts_answer_question_async,
                    project_context, final_user_input, model
                )
            elif actual_intent == "chat":
                if debug_mode: print_debug(f"Chat: {final_user_input[:50]}...")
                project_context["file_tree"] = util_get_file_tree(project_context["output_dir"])
                ai_response_text = await asyncio.to_thread(
                    _run_in_thread_with_new_loop, prompts_handle_conversation_async,
                    project_context, final_user_input, model
                )
        project_context["conversation_history"].append({"role": "assistant", "content": ai_response_text})
        console.line()
        console.print(Panel(Padding(Markdown(ai_response_text), (1,2)), title="[orange]🤖 Vigi [/orange]", border_style="green", expand=False, style="ai_response"))
        console.line()

    meta_dir = os.path.join(project_context["output_dir"], ".vigi_dev_meta")
    generate_folder(meta_dir)
    context_to_save = {k:v for k,v in project_context.items() if k != "codebase"}
    try:
        with open(os.path.join(meta_dir, "project_context.json"), 'w') as f: json.dump(context_to_save, f, indent=2)
        print_success(f"💾 Project context for '{project_slug}' saved.")
    except Exception as e:
        print_error_msg(f"Failed to save project context: {e}")
    console.line()
    print_info("Exiting conversation mode.")
    console.line()


async def _run_single_pass(initial_prompt: str, project_context: Dict[str, Any], debug_mode: bool, model: str):
    if not project_context: print_error_msg("Cannot run single-pass without project context."); return
    project_slug = project_context.get("project_slug", "Unknown Project")
    project_root_abs = project_context.get("output_dir")
    if not initial_prompt: print_error_msg("Prompt required for single-pass execution."); sys.exit(1)

    console.line()
    console.print(Panel(Padding(f"Running single pass for project [b]'{project_slug}'[/b]", (1,2)),
                        title="[rule_title]🚀 Single Pass Mode[/rule_title]", border_style="panel_border",
                        subtitle=f"📍 Location: [blue_violet]{project_root_abs}[/blue_violet]", expand=False))
    console.line()
    console.print(Panel(Padding(Text(initial_prompt, justify="left"), (1,2)), title="[dim cyan]📄 Using Prompt[/dim cyan]", border_style="dim cyan", expand=False))
    console.line()

    print_success(f"Project '{project_slug}' setup complete. Files are in [blue_violet]{project_root_abs}[/blue_violet]")
    console.line()

    console.print(Panel(Padding(get_rich_file_tree(project_root_abs), (1,1)), title="[dim green]🌲 Generated File Tree[/dim green]", border_style="dim green", expand=False))
    console.line(2)


async def get_user_project_setup(args_output_dir: Optional[str], args_prompt: Optional[str], debug_mode: bool, model: str) -> Tuple[Optional[str], Optional[str]]:
    project_root_abs: Optional[str] = None
    effective_initial_prompt_for_creation: Optional[str] = None

    if args_output_dir:
        candidate_path = Path(args_output_dir).resolve()
        if (candidate_path / ".vigi_dev_meta" / "project_context.json").exists():
            console.line()
            print_info(f"📂 Found Vigi_Dev project via --output_dir: [blue_violet]{candidate_path}[/blue_violet]. Loading.")
            console.line()
            return str(candidate_path), None
        else:
            print_warning(f"--output_dir '{args_output_dir}' not a Vigi_Dev project. Interactive setup if not creating.")

    while not project_root_abs:
        console.line()
        console.print(Rule(Text("Project Setup", style="rule_title"), style="panel_border"))
        console.line()
        main_choices = [
            Choice("🚀 Load Existing Project", value="Load Existing Project"),
            Choice("✨ Create New Project", value="Create New Project"),
            Separator(),
            Choice(EXIT_ACTION_TEXT, value="Exit")
        ]
        action = await questionary.select(
            "What would you like to do?", choices=main_choices, style=custom_style, qmark="👋"
        ).ask_async()
        console.line()

        if action == "Exit" or action is None:
            print_info("Exiting Vigi_Dev. Goodbye!"); console.line(); sys.exit(0)

        if action == "Load Existing Project":
            load_choices = [
                Choice("📜 Load from Recent History", value="history"),
                Choice("📁 Select Folder Manually", value="other"),
                Separator(),
                Choice(BACK_TO_MAIN_MENU_TEXT, value="--back-main--")
            ]
            load_method_action = await questionary.select(
                 "How to load project?", choices=load_choices, style=custom_style, qmark="🔎"
            ).ask_async()
            console.line()

            if load_method_action == "--back-main--" or load_method_action is None: continue
            if load_method_action == "history":
                history = load_project_history()
                if not history: console.print("[tip]No project history. Try creating or loading manually.[/tip]"); console.line(); continue
                project_hist_choices = [
                    Choice(title=f"{e['name']} (📂 {Path(e['path']).name}) | {e.get('original_prompt', '')[:30]}...", value=e['path'])
                    for e in history[:15]
                ]
                project_hist_choices.extend([Separator(), Choice(BACK_ACTION_TEXT, value="--back-load-menu--")])
                selected_path_history = await questionary.select(
                    "Select from history:", choices=project_hist_choices, style=custom_style, qmark="📜"
                ).ask_async()
                console.line()
                if selected_path_history == "--back-load-menu--" or selected_path_history is None: continue
                if selected_path_history:
                    print_info(f"📜 Loading from history: [blue_violet]{Path(selected_path_history).name}[/blue_violet]")
                    console.line(); return selected_path_history, None
            elif load_method_action == "other":
                selected_folder_path_str = await _ask_for_project_directory_terminal_async() # Already has console.line()
                if selected_folder_path_str:
                    selected_folder_path = Path(selected_folder_path_str).resolve()
                    if _is_vigi_dev_project(selected_folder_path):
                        print_info(f"📂 Loading selected folder: [blue_violet]{selected_folder_path.name}[/blue_violet]")
                        console.line(); return str(selected_folder_path), None
                    else: console.print(f"[danger]Folder '{selected_folder_path.name}' is not a Vigi_Dev project.[/danger]")
                else: console.print("[tip]No folder selected or selection cancelled.[/tip]")
                console.line(); continue
        elif action == "Create New Project":
            console.line()
            print_info("✨ Let's create a new project!")
            console.line()
            base_sel_choices = [
                Choice("🖥️ Desktop", value="Desktop"), Choice("📥 Downloads", value="Downloads"),
                Choice("📄 Documents", value="Documents"), Choice("📍 Current Directory (.)", value="Current Dir (.)"),
                Choice("📁 Custom Path...", value="Custom"), Separator(),
                Choice(BACK_TO_MAIN_MENU_TEXT, value="--back--")
            ]
            base_key = await questionary.select(
                 "Where to create project folder?", choices=base_sel_choices, style=custom_style, qmark="🗺️"
            ).ask_async()
            console.line()
            if base_key == "--back--" or base_key is None: continue
            base_dirs_map = {"Desktop": Path.home()/"Desktop", "Downloads": Path.home()/"Downloads",
                             "Documents": Path.home()/"Documents", "Current Dir (.)": Path.cwd()}
            base_path = base_dirs_map.get(base_key)
            if base_key == "Custom":
                custom_str = await questionary.text(
                    "Enter custom base path:", style=custom_style, qmark="✍️",
                    validate=lambda t: True if t.strip() and Path(t.strip()).resolve().is_dir() else "Must be existing directory."
                ).ask_async()
                console.line()
                if custom_str and custom_str.strip(): base_path = Path(custom_str.strip()).resolve()
                else: console.print("[tip]Custom path entry cancelled.[/tip]"); console.line(); continue
            
            name_str = await questionary.text(
                "Project Name (folder name):", style=custom_style, qmark="🏷️",
                validate=lambda t: True if t.strip() else "Name cannot be empty."
            ).ask_async()
            console.line()
            if not name_str or not name_str.strip(): console.print("[tip]Project name entry cancelled.[/tip]"); console.line(); continue

            s_name = re.sub(r'\s+', '_', re.sub(r'[^\w\-_ \.]', '_', name_str.strip()))
            candidate_root = base_path / s_name

            if candidate_root.exists():
                if (candidate_root / ".vigi_dev_meta" / "project_context.json").exists():
                    if await questionary.confirm(f"Project '{s_name}' already exists. Load it?", default=True, style=custom_style, qmark="❓").ask_async():
                        console.line()
                        print_info(f"📂 Loading existing project: [blue_violet]{candidate_root.name}[/blue_violet]")
                        console.line(); return str(candidate_root), None
                    else: continue
                else:
                    init_choices = [
                        Choice("✔️ Initialize Vigi_Dev here", value="init"),
                        Choice("✍️ Choose different name/location", value="back"),
                        Choice(EXIT_ACTION_TEXT, value="exit")
                    ]
                    choice = await questionary.select(
                         f"Dir '{candidate_root.name}' exists but isn't a Vigi_Dev project. Action?",
                         choices=init_choices, style=custom_style, qmark="🤔"
                    ).ask_async()
                    console.line()
                    if choice == "exit" or choice is None: print_info("Exiting."); console.line(); sys.exit(0)
                    if choice == "back": continue
            project_root_abs = str(candidate_root)
            print_info(f"New project: [blue_violet]{project_root_abs}[/blue_violet] (Name: [b]{s_name}[/b])")
            console.line()

            effective_initial_prompt_for_creation = args_prompt
            if not effective_initial_prompt_for_creation:
                effective_initial_prompt_for_creation = await questionary.text(
                    "Describe your new project (e.g., 'a snake game in python with pygame'):",
                    style=custom_style, qmark="💬",
                    validate=lambda t: True if t.strip() else "Prompt cannot be empty."
                ).ask_async()
                console.line()
            if not effective_initial_prompt_for_creation or not effective_initial_prompt_for_creation.strip():
                print_warning("Initial prompt required. Starting over."); console.line(); project_root_abs = None; continue
            return project_root_abs, effective_initial_prompt_for_creation
    return None, None

async def main_async(args):
    print_header("VIGI DEV ASSIST") # Reverted to original Pyfiglet based header
    project_root_abs_str: Optional[str] = None
    project_creation_prompt: Optional[str] = None
    console.line()

    if args.output_dir:
        output_path_resolved = Path(args.output_dir).resolve()
        is_existing_vigi_project = (output_path_resolved / ".vigi_dev_meta" / "project_context.json").exists()
        if is_existing_vigi_project:
            project_root_abs_str = str(output_path_resolved)
            print_info(f"📂 Directly loading project from --output_dir: [blue_violet]{project_root_abs_str}[/blue_violet]")
        elif args.prompt:
            project_root_abs_str = str(output_path_resolved)
            project_creation_prompt = args.prompt
            if output_path_resolved.exists() and not is_existing_vigi_project:
                 print_warning(f"Directory '{output_path_resolved}' exists (not Vigi_Dev). Will initialize non-interactively.")
            elif not output_path_resolved.exists() and not output_path_resolved.parent.exists():
                print_error_msg(f"Parent for new project '{output_path_resolved.parent}' DNE."); sys.exit(1)
            print_info(f"🛠️ Non-interactive new project at: [blue_violet]{project_root_abs_str}[/blue_violet]")
            if args.debug: console.print(Panel(Padding(args.prompt, (1,2)), title="[dim]Initial Prompt (CLI)[/dim]", border_style="dim"))
        console.line()


    if not project_root_abs_str:
        project_root_abs_str, project_creation_prompt = await get_user_project_setup(args.output_dir, args.prompt, args.debug, args.model)

    if not project_root_abs_str: print_info("No project selected/created. Exiting."); console.line(); sys.exit(0)

    project_root_path = Path(project_root_abs_str).resolve()
    project_context: Optional[Dict[str, Any]] = None

    console.line()
    if project_creation_prompt:
        project_context = await _initialize_project(project_creation_prompt, str(project_root_path), project_root_path.name, args.debug, args.model)
    else:
        project_context = _load_project_context(str(project_root_path), args.debug)
        if not project_context:
            if not (project_root_path / ".vigi_dev_meta" / "project_context.json").exists():
                print_warning(f"No .vigi_dev_meta at [blue_violet]{project_root_path}[/blue_violet].")
                console.line()
                if args.prompt:
                    should_init_q = await questionary.confirm(
                        f"Initialize new Vigi_Dev project at '{project_root_path.name}' with CLI prompt?", default=True, style=custom_style, qmark="❓"
                    ).ask_async() if sys.stdin.isatty() else True
                    console.line()
                    if should_init_q:
                        project_context = await _initialize_project(args.prompt, str(project_root_path), project_root_path.name, args.debug, args.model)
                        project_creation_prompt = args.prompt
                    else: print_error_msg("Not a project and init declined. Exiting."); console.line(); sys.exit(1)
                else: print_error_msg(f"Not Vigi_Dev project and no --prompt to init. Exiting."); console.line(); sys.exit(1)
            else: print_error_msg(f"Failed to load context from [blue_violet]{project_root_path}[/blue_violet]. Exiting."); console.line(); sys.exit(1)

    if not project_context: print_error_msg("Fatal: Failed to get/create project context. Exiting."); console.line(); sys.exit(1)

    console.line()
    current_session_prompt = args.prompt if not project_creation_prompt else None
    if args.conversation:
        await _start_conversation_mode(project_context, current_session_prompt, args.debug, args.model)
    else:
        prompt_for_single_pass = current_session_prompt or project_context.get("original_prompt")
        if not prompt_for_single_pass:
            print_error_msg("No prompt for single-pass. Use --prompt or ensure project has original_prompt."); console.line(); sys.exit(1)
        await _run_single_pass(prompt_for_single_pass, project_context, args.debug, args.model)

def main():
    parser = argparse.ArgumentParser(
        description=Text.assemble(("Vigi_Dev - Your AI-Powered Coding Assistant", "bold blue_violet")),
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="Examples:\n"
               "  %(prog)s -c                                  # Interactive session, prompts for project\n"
               "  %(prog)s -o ./my_game -p \"create snake game\"   # Create new non-interactively (single-pass)\n"
               "  %(prog)s -o ./my_game -p \"create snake game\" -c # Create new non-interactively, then start conversation\n"
               "  %(prog)s -o ./my_game -c                       # Load existing project and start conversation\n"
               "  %(prog)s -o ./my_game -p \"add score\"          # Load project, provide one-off prompt (single-pass)\n"
               "  %(prog)s -o ./my_game -p \"add score\" -c       # Load project, start conversation with \"add score\""
    )
    parser.add_argument("--prompt", "-p", type=str, help="Initial prompt for new/session.")
    parser.add_argument("--output_dir", "-o", type=str, help="Project path for load/create.")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable detailed debug logging.")
    parser.add_argument("--conversation", "-c", action="store_true", help="Start interactive conversation mode.")
    parser.add_argument("--model", "-m", type=str, default=MODEL_NAME, help=f"AI model (default: {MODEL_NAME}).")

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
        logging.getLogger('prompts').setLevel(logging.DEBUG)
        logging.getLogger('utils').setLevel(logging.DEBUG)
        console.line()
        print_debug("Debug mode enabled. Verbose backend logging to console/files if configured.")
        console.line()
    else:
        logger.setLevel(logging.WARNING)
        logging.getLogger('prompts').setLevel(logging.WARNING)
        logging.getLogger('utils').setLevel(logging.WARNING)

    if not sys.stdin.isatty(): # Non-interactive checks
        console.line()
        if not args.output_dir:
            print_error_msg("Non-interactive: --output_dir required."); parser.print_help(); console.line(); sys.exit(1)
        is_existing = Path(args.output_dir).resolve().joinpath(".vigi_dev_meta", "project_context.json").exists()
        if not is_existing and not args.prompt:
            print_error_msg("Non-interactive new project: --prompt required."); parser.print_help(); console.line(); sys.exit(1)
        if args.conversation and not args.prompt:
            print_warning("Non-interactive conversation with no initial --prompt may not be useful.")
        console.line()

    try:
        asyncio.run(main_async(args))
    except Exception: # Rich traceback handles the specific exception type
        console.print_exception(show_locals=args.debug, width=console.width)
        console.line()
        sys.exit(1)
    except KeyboardInterrupt:
        console.line(2)
        console.print("[yellow]👋 User interruption. Exiting Vigi_Dev.[/yellow]")
        console.line()
        sys.exit(0)


if __name__ == "__main__":
    main()
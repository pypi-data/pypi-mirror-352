############################################################
#                                                          #
#             Custom-Crafted for GitHub: naumanAhmed3      #
#                                                          #
#          <<<<< Core Application Utilities >>>>>          #
#                                                          #
############################################################
"""
Provides a collection of general-purpose utility functions and classes
used throughout the application. This includes text processing,
output formatting for the terminal, clipboard operations, user input handling,
and network connectivity checks.
"""

import json
import os
import sys
from typing import Optional, List, Any 

import pyperclip 
import requests  
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.key_binding import KeyBindings 
from prompt_toolkit.formatted_text import FormattedText 
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text 

from .config import ApplicationSettings

class CoreHelpers:
    """
    A collection of static utility methods for common tasks such as string cleaning,
    pretty-printing to the console, processing AI model responses, handling user input,
    and checking internet connectivity.
    """

    @staticmethod
    def sanitize_ai_output_string(raw_json_text: str) -> str:
        processed_text = raw_json_text.strip()
        if processed_text.startswith("```json"):
            processed_text = processed_text[len("```json"):]
            if processed_text.endswith("```"):
                processed_text = processed_text[:-len("```")]
        elif processed_text.startswith("```"):
            processed_text = processed_text[len("```"):]
            if processed_text.endswith("```"):
                processed_text = processed_text[:-len("```")]
        processed_text = processed_text.strip()
        first_brace_pos = processed_text.find("{")
        if first_brace_pos != -1:
            processed_text = processed_text[first_brace_pos:]
        last_brace_pos = processed_text.rfind("}")
        if last_brace_pos != -1:
            processed_text = processed_text[: last_brace_pos + 1]
        return processed_text.strip()

    @staticmethod
    def display_formatted_instruction_set(
        instruction_list: list, 
        display_interface: Console, 
        app_config: ApplicationSettings
    ) -> None:
        commands_text_elements = []
        for i, instr in enumerate(instruction_list):
            commands_text_elements.append(Text(f"{i+1}. ", style="dim") + Text(instr, style="bold white"))
        
        if len(commands_text_elements) == 1:
            content_to_display = commands_text_elements[0]
        else:
            content_to_display = Text("\n") .join(commands_text_elements)

        panel_width = app_config.STANDARD_OUTPUT_PANE_WIDTH if app_config.STANDARD_OUTPUT_PANE_WIDTH else None
        display_interface.print(
            Panel(
                content_to_display,
                title="[b]Suggested Command(s)[/b]", 
                title_align="left",
                border_style=app_config.VS_CMD_PANEL_TITLE_STYLE, 
                padding=(1,2), 
                width=panel_width
            )
        )

    @staticmethod
    def render_ai_instruction_response(
        ai_model_json_output: Optional[str],
        display_interface: Console,
        is_condensed_mode: bool,
        app_config: ApplicationSettings
    ) -> list:
        if not ai_model_json_output:
            return [] 
        effective_pane_width = app_config.STANDARD_OUTPUT_PANE_WIDTH if app_config.STANDARD_OUTPUT_PANE_WIDTH else None
        try:
            parsed_json_data = json.loads(ai_model_json_output)
        except json.decoder.JSONDecodeError:
            display_interface.print(
                Text("Error: The AI's response could not be parsed as valid JSON.", style=app_config.VS_ERROR_STYLE)
            )
            display_interface.log(f"Invalid JSON received from AI: {ai_model_json_output}")
            return []

        if parsed_json_data.get("error", 0) != 0 or "commands" not in parsed_json_data:
            error_message_from_ai = parsed_json_data.get("message", "The AI could not determine instructions for this request.")
            display_interface.print(
                Text(f"AI Error: {error_message_from_ai}", style=app_config.VS_ERROR_STYLE)
            )
            return []
            
        instruction_data_list = parsed_json_data.get("commands", [])
        if not instruction_data_list and parsed_json_data.get("error", 0) == 0:
            display_interface.print(
                Text("The AI returned an empty list of instructions for this request.", style=app_config.VS_WARNING_STYLE)
            )
            return []

        extracted_instruction_strings: List[str] = []
        if is_condensed_mode:
            extracted_instruction_strings = [str(instr) for instr in instruction_data_list if isinstance(instr, str)]
            if not all(isinstance(instr, str) for instr in instruction_data_list):
                display_interface.print(Text("Format Error: Condensed mode expected instruction strings.", style=app_config.VS_ERROR_STYLE))
                display_interface.log(f"Unexpected condensed mode output structure: {instruction_data_list}")
                return []
        else:
            if not all(isinstance(instr_obj, dict) for instr_obj in instruction_data_list):
                display_interface.print(Text("Format Error: Detailed mode expected instruction objects.", style=app_config.VS_ERROR_STYLE))
                display_interface.log(f"Unexpected detailed mode output structure: {instruction_data_list}")
                return []
            extracted_instruction_strings = [instr_obj.get("cmd_to_execute", "") for instr_obj in instruction_data_list]

        CoreHelpers.display_formatted_instruction_set(extracted_instruction_strings, display_interface, app_config)

        if not is_condensed_mode:
            explanation_renderables = []
            for i, instruction_object in enumerate(instruction_data_list): 
                if isinstance(instruction_object, dict): 
                    cmd_expls = instruction_object.get("cmd_explanations", [])
                    if cmd_expls:
                        explanation_renderables.append(Text(f"\nCommand {i+1}: {extracted_instruction_strings[i]}", style="bold underline white"))
                        for expl in cmd_expls:
                            explanation_renderables.append(Text(f"- {expl}"))
                    
                    arg_details = instruction_object.get("arg_explanations", {})
                    if arg_details:
                        if not cmd_expls: 
                             explanation_renderables.append(Text(f"\nCommand {i+1}: {extracted_instruction_strings[i]}", style="bold underline white"))
                        explanation_renderables.append(Text("Arguments:", style="italic"))
                        for arg_key, arg_value in arg_details.items():
                            explanation_renderables.append(Text.assemble(("  - `", "green"), (arg_key, "bold green"), ("`: ", "green"), (arg_value, "green"))) 
            
            if explanation_renderables:
                explanation_content = Text("\n").join(explanation_renderables)
                display_interface.print(
                    Panel(
                        explanation_content,
                        title="[b]Instruction Breakdown[/b]", 
                        title_align="left",
                        border_style=app_config.VS_EXPLANATION_PANEL_TITLE_STYLE, 
                        padding=(1,2),
                        width=effective_pane_width
                    )
                )
        return extracted_instruction_strings

    @staticmethod
    def transfer_text_to_system_clipboard(text_content: List[str]) -> None:
        pyperclip.copy("\n".join(text_content))

    @staticmethod
    def solicit_end_user_text_input(
        prompt_text_str: str, 
        input_session_manager: PromptSession,
        display_interface: Console, 
        app_config: ApplicationSettings, 
        path_autocompleter: Optional[Completer] = None,
        autocompletion_display_style: Optional[Any] = None, 
        custom_key_action_override: Optional[KeyBindings] = None,
    ) -> str:
        active_key_bindings = custom_key_action_override if custom_key_action_override is not None else app_config.custom_key_actions
        
        user_provided_text = input_session_manager.prompt(
            prompt_text_str, 
            style=app_config.TERMINAL_INPUT_FIELD_STYLE, 
            completer=path_autocompleter,
            complete_style=autocompletion_display_style,
            key_bindings=active_key_bindings,
        ).strip()

        if user_provided_text.lower() in ["quit", "exit", ":q"]:
            display_interface.print(Text("\nExiting Vigi Shell. Goodbye!", style=app_config.VS_INFO_STYLE))
            sys.exit(0)
        
        return user_provided_text

    @staticmethod
    def verify_internet_reachability(test_url: str = "http://www.google.com", access_timeout: int = 8) -> bool:
        try:
            requests.get(test_url, timeout=access_timeout)
            return True
        except requests.ConnectionError:
            return False
        except requests.exceptions.Timeout:
            return False

# utils.py

# ... (other imports) ...
from typing import Optional, List, Any, Callable # Add Callable

class FilesystemPathAutocompleter(Completer):
    """
    A custom prompt_toolkit completer for suggesting file and directory paths
    as the user types in the terminal. It can use a custom current working directory.
    """
    def __init__(self, current_custom_cwd: Optional[Callable[[], str]] = None):
        """
        Initializes the path completer.

        Args:
            current_custom_cwd (Optional[Callable[[], str]]): A callable that returns the
                string of the current virtual working directory to base completions on.
                If None, os.getcwd() is used.
        """
        self.get_current_cwd = current_custom_cwd if current_custom_cwd else os.getcwd

    def get_completions(self, document_context, completion_event): # type: ignore
        if completion_event.completion_requested: 
            current_working_dir = self.get_current_cwd() # Use the callable
            # ... (rest of the get_completions method remains the same as before) ...
            text_leading_up_to_cursor = document_context.text_before_cursor
            if ' ' in text_leading_up_to_cursor and \
               (text_leading_up_to_cursor.count('"') % 2 == 1 or text_leading_up_to_cursor.count("'") % 2 == 1):
                last_quote_char = '"' if text_leading_up_to_cursor.rfind('"') > text_leading_up_to_cursor.rfind("'") else "'"
                last_quote_index = text_leading_up_to_cursor.rfind(last_quote_char)
                path_segment_to_complete = text_leading_up_to_cursor[last_quote_index + 1:]
            else:
                path_segment_to_complete = text_leading_up_to_cursor.lstrip().split(" ")[-1]

            if path_segment_to_complete.startswith("~/"):
                expanded_path_base = os.path.expanduser(path_segment_to_complete)
                 # For tilde expansion, the base directory for listing should still be derived from the expanded path
                directory_for_listing = os.path.dirname(expanded_path_base)

            elif path_segment_to_complete.startswith("/"):
                expanded_path_base = path_segment_to_complete
                directory_for_listing = os.path.dirname(expanded_path_base)
            else:
                expanded_path_base = os.path.join(current_working_dir, path_segment_to_complete)
                directory_for_listing = os.path.dirname(expanded_path_base)


            item_prefix_to_match = os.path.basename(expanded_path_base)

            if not path_segment_to_complete or path_segment_to_complete.endswith(os.sep):
                directory_for_listing = expanded_path_base # if ends with sep, list this dir
                item_prefix_to_match = "" 

            if os.path.isdir(directory_for_listing):
                try:
                    for filesystem_item_name in os.listdir(directory_for_listing):
                        if filesystem_item_name.lower().startswith(item_prefix_to_match.lower()):
                            full_item_system_path = os.path.join(directory_for_listing, filesystem_item_name)
                            
                            # Determine how the completion text should be displayed and inserted
                            # This part needs to be careful about whether the original input was relative or absolute
                            if path_segment_to_complete.startswith("~/"):
                                completion_insert_text = "~/" + os.path.relpath(full_item_system_path, os.path.expanduser("~"))
                            elif path_segment_to_complete.startswith("/"): # Absolute path completion
                                completion_insert_text = full_item_system_path
                            else: # Relative path completion (relative to current_working_dir)
                                completion_insert_text = os.path.relpath(full_item_system_path, current_working_dir)
                            
                            display_name_for_completion = filesystem_item_name
                            if os.path.isdir(full_item_system_path):
                                display_name_for_completion += os.sep 
                            
                            start_replacement_offset = -len(item_prefix_to_match)
                            # More robust way to calculate start_position:
                            # Find the start of the segment being completed
                            path_parts = path_segment_to_complete.split(os.sep)
                            if len(path_parts) > 1 and not path_segment_to_complete.endswith(os.sep):
                                start_replacement_offset = -len(path_parts[-1])
                            elif path_segment_to_complete.endswith(os.sep):
                                start_replacement_offset = 0 # Append after separator
                            else: # Completing the first part or whole segment
                                start_replacement_offset = -len(path_segment_to_complete)


                            yield Completion(
                                completion_insert_text,
                                display=display_name_for_completion,
                                start_position=start_replacement_offset,
                            )
                except OSError: 
                    pass
###################################################################
#                                                                 #
#                Bootstrapped for GitHub: naumanAhmed3            #
#                                                                 #
#                    <<<<< Vigi Shell Interface >>>>>             #
#                                                                 #
###################################################################
"""
This module is the main entry point for Vigi Shell, a command-line interface
that translates natural language into shell commands using AI.
It provides a continuous, interactive shell-like experience with options
after command generation and handling for 'cd' commands.
"""

import subprocess 
import sys
import os
from typing import Optional, Tuple, List 
import getpass
# import click # Not used directly in this file after recent changes
import google.generativeai as gen_ai_api 
import inquirer 
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.shortcuts import CompleteStyle
from rich.console import Console
from rich.panel import Panel 
from rich.text import Text 
from rich.padding import Padding 
from rich.align import Align 

from .config import ApplicationSettings
from .cmd_gen_prompts import SystemInstructionBuilder
from .gemini_interface import AICommunicationGateway
from .utils import CoreHelpers, FilesystemPathAutocompleter

class VigiShellApp:
    """
    Manages Vigi Shell's core logic, providing an interactive loop
    for natural language to shell command translation, including interactive
    options for handling generated commands and 'cd' state.
    """
    def __init__(self, app_config_instance: ApplicationSettings, ai_gateway_instance: AICommunicationGateway, display_manager_instance: Console):
        self.app_config = app_config_instance
        self.ai_comm_layer = ai_gateway_instance
        self.terminal_display = display_manager_instance
        self.command_history = InMemoryHistory() 
        self.user_input_session = PromptSession(
            history=self.command_history, 
            auto_suggest=AutoSuggestFromHistory()
        )
        self.default_ai_engine_id: str = ApplicationSettings.PRIMARY_AI_ENGINE # Use primary for command gen
        self.default_use_condensed_output: bool = False 
        self.current_virtual_cwd: str = os.getcwd() 

    def display_welcome_message(self):
        """Displays a styled welcome message for Vigi Shell."""
        welcome_text = Text("◢ Vigi Shell ◣", style=self.app_config.VS_WELCOME_STYLE)
        sub_text = Text("Your AI-Powered Command Line Assistant", style="dim italic bright_white")
        usage_text1 = Text("Type your command in natural language (e.g., 'list all python files').", style="dim cyan")
        usage_text2 = Text("To execute a command directly, end it with '!' (e.g., 'ls -la !').", style="dim cyan")
        usage_text3 = Text("Type 'quit' or 'exit' to leave Vigi Shell.", style="dim cyan")
        summary_info = Text(f"Output summarization is {'ON' if self.app_config.SUMMARIZE_COMMAND_OUTPUT_AUTOMATICALLY else 'OFF'}.", style="dim bright_blue")


        self.terminal_display.print(Align.center(Padding(welcome_text, (1,0,0,0))))
        self.terminal_display.print(Align.center(sub_text))
        self.terminal_display.print(Align.center(usage_text1))
        self.terminal_display.print(Align.center(usage_text2))
        self.terminal_display.print(Align.center(usage_text3))
        self.terminal_display.print(Align.center(summary_info))
        self.terminal_display.print("-" * (self.terminal_display.width // 2), justify="center")

    def _handle_cd_command(self, command_parts: List[str]) -> bool:
        """
        Handles 'cd' commands by changing the virtual current working directory.
        Args:
            command_parts (List[str]): The command split into parts.
        Returns:
            bool: True if 'cd' was handled, False otherwise.
        """
        if command_parts and command_parts[0] == "cd":
            if len(command_parts) > 1:
                target_dir_segment = " ".join(command_parts[1:])
                expanded_target_dir = os.path.expandvars(os.path.expanduser(target_dir_segment))
                
                if not os.path.isabs(expanded_target_dir):
                    prospective_dir = os.path.join(self.current_virtual_cwd, expanded_target_dir)
                else:
                    prospective_dir = expanded_target_dir
                
                normalized_dir = os.path.normpath(prospective_dir)

                if os.path.isdir(normalized_dir):
                    self.current_virtual_cwd = normalized_dir
                    self.terminal_display.print(Text(f"Current directory set to: {self.current_virtual_cwd}", style=self.app_config.VS_INFO_STYLE))
                else:
                    self.terminal_display.print(Text(f"Error: Directory not found: {normalized_dir}", style=self.app_config.VS_ERROR_STYLE))
            else: 
                home_dir = os.path.expanduser("~")
                self.current_virtual_cwd = home_dir
                self.terminal_display.print(Text(f"Current directory set to: {self.current_virtual_cwd}", style=self.app_config.VS_INFO_STYLE))
            return True
        return False


    def _execute_command_in_sequence(self, command_string: str, execution_cwd: str) -> Tuple[str, str, bool]:
        """
        Executes a single command string.
        Returns: (stdout, stderr, success_status)
        """
        self.terminal_display.print(Text(f"Executing (in {execution_cwd}): {command_string}", style="italic green"))
        stdout_full, stderr_full = "", ""
        try:
            process = subprocess.Popen(
                command_string, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                bufsize=1, 
                universal_newlines=True,
                cwd=execution_cwd 
            )
            
            stdout_lines = []
            if process.stdout:
                for line in process.stdout:
                    self.terminal_display.print(Text(line.rstrip(), style=self.app_config.VS_EXEC_OUTPUT_STYLE))
                    stdout_lines.append(line)
            stdout_full = "".join(stdout_lines)
            
            stderr_lines = []
            if process.stderr:
                for line in process.stderr:
                    self.terminal_display.print(Text(line.rstrip(), style=self.app_config.VS_ERROR_STYLE))
                    stderr_lines.append(line)
            stderr_full = "".join(stderr_lines)
            
            process.wait() 
            success = process.returncode == 0
            if not success:
                self.terminal_display.print(Text(f"Command exited with code {process.returncode}", style=self.app_config.VS_WARNING_STYLE))
            return stdout_full, stderr_full, success

        except FileNotFoundError:
            err_msg = f"Error: Command not found: {command_string.split()[0]}"
            self.terminal_display.print(Text(err_msg, style=self.app_config.VS_ERROR_STYLE))
            return "", err_msg, False
        except Exception as e:
            err_msg = f"Error executing command: {e}"
            self.terminal_display.print(Text(err_msg, style=self.app_config.VS_ERROR_STYLE))
            return "", err_msg, False
        
    def _display_ai_summary(self, summary_text: Optional[str]):
        """Displays the AI-generated summary in a styled panel."""
        if summary_text:
            self.terminal_display.print(
                Panel(
                    Text(summary_text, style=self.app_config.VS_AI_SUMMARY_STYLE),
                    title="[b]Execution Response[/b]",
                    title_align="left",
                    border_style=self.app_config.VS_AI_SUMMARY_PANEL_BORDER_STYLE,
                    padding=(1, 1),
                    width=self.app_config.STANDARD_OUTPUT_PANE_WIDTH if self.app_config.STANDARD_OUTPUT_PANE_WIDTH else None
                )
            )
            self.terminal_display.print() # Extra newline for spacing

    def _request_and_display_summary(self, original_query: str, executed_command: str, stdout: str, stderr: str, success: bool):
        """Helper to request and display summary if enabled and conditions met."""
        if self.app_config.SUMMARIZE_COMMAND_OUTPUT_AUTOMATICALLY:
            if stdout or stderr or not success: # Only summarize if there's output or an error
                summary = self.ai_comm_layer.request_output_summary_from_ai(
                    original_user_query=original_query,
                    executed_command=executed_command,
                    command_stdout=stdout,
                    command_stderr=stderr,
                    command_success=success
                )
                self._display_ai_summary(summary)

    def process_single_query(self, initial_query: str):
        """Processes a single query, offers execution, and exits."""
        if not initial_query:
            self.terminal_display.print(Text("No query provided for single execution.", style=self.app_config.VS_WARNING_STYLE))
            return
        current_nl_query = initial_query.strip()
        if not current_nl_query: return

        if current_nl_query.endswith("!"):
            command_to_execute = current_nl_query[:-1].strip()
            if command_to_execute:
                command_parts = command_to_execute.split()
                if not self._handle_cd_command(command_parts):
                    stdout, stderr, success = self._execute_command_in_sequence(command_to_execute, self.current_virtual_cwd)
                    self._request_and_display_summary(current_nl_query, command_to_execute, stdout, stderr, success)
            else:
                self.terminal_display.print(Text("No command provided before '!' suffix.", style=self.app_config.VS_WARNING_STYLE))
            self.terminal_display.print()
            return

        ai_generated_output_json = self.ai_comm_layer.request_instruction_from_ai(
            user_query_text=current_nl_query,
            use_condensed_output=self.default_use_condensed_output,
            ai_engine_id=self.default_ai_engine_id,
            target_os_for_instruction=self.app_config.current_os_descriptor
        )
        generated_instructions = CoreHelpers.render_ai_instruction_response(
            ai_model_json_output=ai_generated_output_json,
            display_interface=self.terminal_display,
            is_condensed_mode=self.default_use_condensed_output,
            app_config=self.app_config
        )
        if not generated_instructions:
            self.terminal_display.print(Text("Vigi Shell could not determine commands. Please rephrase.", style=self.app_config.VS_WARNING_STYLE))
            return

        user_action_choices = ["Execute Command(s)", "Copy to Clipboard", "Abort"]
        try:
            user_decision = inquirer.prompt([inquirer.List("chosen_action", message="What would you like to do?", choices=user_action_choices)])
            if not user_decision:
                self.terminal_display.print(Text("\nNo action selected. Exiting.", style=self.app_config.VS_WARNING_STYLE))
                return
            selected_user_action = user_decision["chosen_action"]
        except (KeyboardInterrupt, Exception) as e:
            self.terminal_display.print(Text(f"\nAction selection cancelled or error: {e}. Exiting.", style=self.app_config.VS_WARNING_STYLE))
            return

        if selected_user_action == "Abort":
            self.terminal_display.print(Text("\nOperation aborted.", style=self.app_config.VS_INFO_STYLE))
        elif selected_user_action == "Copy to Clipboard":
            CoreHelpers.transfer_text_to_system_clipboard(generated_instructions)
            self.terminal_display.print(Text("↪ Commands copied!", style=self.app_config.VS_INFO_STYLE))
        elif selected_user_action == "Execute Command(s)":
            self.terminal_display.print(Text("\nExecuting command(s)...", style="bold blue"))
            for index, instruction_to_run in enumerate(generated_instructions):
                if instruction_to_run:
                    self.terminal_display.print(Text(f"Running [{index+1}/{len(generated_instructions)}]: ", style="blue") + Text(instruction_to_run, style="bold white"))
                    command_parts = instruction_to_run.split()
                    if not self._handle_cd_command(command_parts):
                       stdout, stderr, success = self._execute_command_in_sequence(instruction_to_run, self.current_virtual_cwd)
                       self._request_and_display_summary(current_nl_query, instruction_to_run, stdout, stderr, success)
        self.terminal_display.print()

    def start_interactive_shell_loop(self):
        """Starts the main interactive loop."""
        self.display_welcome_message()
        while True:
            display_cwd = os.path.basename(self.current_virtual_cwd) if self.current_virtual_cwd != os.path.expanduser("~") else "~"
            prompt_text = Text.assemble(
                ("Vigi - ", self.app_config.VS_PROMPT_SYMBOL_STYLE),
                (f"({getpass.getuser()}'s AI Assistant)"),
                (f" [{display_cwd}]", self.app_config.VS_VIRTUAL_CWD_STYLE),
                (" ╰┈➤ ", self.app_config.VS_PROMPT_SYMBOL_STYLE)
            ).plain
            current_nl_query = CoreHelpers.solicit_end_user_text_input(
                prompt_text_str=prompt_text, input_session_manager=self.user_input_session,
                display_interface=self.terminal_display, app_config=self.app_config,
                path_autocompleter=FilesystemPathAutocompleter(current_custom_cwd=lambda: self.current_virtual_cwd),
                autocompletion_display_style=CompleteStyle.MULTI_COLUMN,
            )
            if not current_nl_query: continue

            if current_nl_query.endswith("!"):
                command_to_execute = current_nl_query[:-1].strip()
                if command_to_execute:
                    command_parts = command_to_execute.split()
                    if not self._handle_cd_command(command_parts):
                        stdout, stderr, success = self._execute_command_in_sequence(command_to_execute, self.current_virtual_cwd)
                        self._request_and_display_summary(current_nl_query, command_to_execute, stdout, stderr, success)
                else:
                    self.terminal_display.print(Text("No command before '!' suffix.", style=self.app_config.VS_WARNING_STYLE))
                self.terminal_display.print(); continue

            ai_generated_output_json = self.ai_comm_layer.request_instruction_from_ai(
                user_query_text=current_nl_query, use_condensed_output=self.default_use_condensed_output,
                ai_engine_id=self.default_ai_engine_id, target_os_for_instruction=self.app_config.current_os_descriptor
            )
            generated_instructions = CoreHelpers.render_ai_instruction_response(
                ai_model_json_output=ai_generated_output_json, display_interface=self.terminal_display,
                is_condensed_mode=self.default_use_condensed_output, app_config=self.app_config
            )
            if not generated_instructions:
                self.terminal_display.print(Text("Vigi Shell could not determine commands.", style=self.app_config.VS_WARNING_STYLE))
                continue
            
            user_action_choices = ["Execute Command(s)", "Copy to Clipboard", "Refine Query", "New Query", "Quit Vigi Shell"]
            try:
                user_decision = inquirer.prompt([inquirer.List("chosen_action", message="What next?", choices=user_action_choices)])
                if not user_decision: self.terminal_display.print(Text("\nNo action. Continuing...", style=self.app_config.VS_WARNING_STYLE)); continue
                selected_user_action = user_decision["chosen_action"]
            except (KeyboardInterrupt, Exception) as e:
                self.terminal_display.print(Text(f"\nAction cancelled or error: {e}. Continuing...", style=self.app_config.VS_WARNING_STYLE)); continue

            if selected_user_action == "Quit Vigi Shell":
                self.terminal_display.print(Text("\nExiting Vigi Shell. Goodbye!", style=self.app_config.VS_INFO_STYLE)); break
            elif selected_user_action == "Refine Query":
                self.terminal_display.print(Text("Hint: Up Arrow to recall last query.", style="dim italic"))
            elif selected_user_action == "Copy to Clipboard":
                CoreHelpers.transfer_text_to_system_clipboard(generated_instructions)
                self.terminal_display.print(Text("↪ Commands copied!", style=self.app_config.VS_INFO_STYLE))
            elif selected_user_action == "Execute Command(s)":
                self.terminal_display.print(Text("\nExecuting command(s)...", style="bold blue"))
                for index, instruction_to_run in enumerate(generated_instructions):
                    if instruction_to_run:
                        self.terminal_display.print(Text(f"Running [{index+1}/{len(generated_instructions)}]: ", style="blue") + Text(instruction_to_run, style="bold white"))
                        command_parts = instruction_to_run.split()
                        if not self._handle_cd_command(command_parts):
                           stdout, stderr, success = self._execute_command_in_sequence(instruction_to_run, self.current_virtual_cwd)
                           self._request_and_display_summary(current_nl_query, instruction_to_run, stdout, stderr, success)
            self.terminal_display.print()

master_terminal_display = Console(highlight=False, log_path=False) # Disable default Rich logging to file for cleaner output unless needed
master_app_settings = ApplicationSettings() 
master_instruction_builder = SystemInstructionBuilder() 

def vigi_shell_entry_point(initial_query: Optional[str] = None): 
    if not CoreHelpers.verify_internet_reachability():
        master_terminal_display.print(Text("Connectivity Issue: Vigi Shell needs internet.", style=master_app_settings.VS_ERROR_STYLE))
        sys.exit(-1) 
    
    try:
        api_key_to_use = os.getenv("GEMINI_API_KEY")
        if not api_key_to_use:
             # This is a placeholder and likely non-functional. Emphasize ENV var.
            master_terminal_display.print(Text("Warning: GEMINI_API_KEY not set. Using placeholder (likely non-functional).", style=master_app_settings.VS_WARNING_STYLE))
            api_key_to_use = "AIzaSyDf60XmRblpeR5gFUgRE8kqkzi2N8-rtl8" # Replace or remove
            # A better approach for missing key:
            # master_terminal_display.print(Text("Fatal Error: GEMINI_API_KEY environment variable not set.", style=master_app_settings.VS_ERROR_STYLE))
            # sys.exit(-1)
        gen_ai_api.configure(api_key=api_key_to_use)
    except Exception as api_config_error:
        master_terminal_display.print(Text(f"Fatal Error configuring Google AI API: {api_config_error}", style=master_app_settings.VS_ERROR_STYLE))
        sys.exit(-1)

    ai_interaction_service = AICommunicationGateway(master_app_settings, master_instruction_builder, master_terminal_display)
    vigi_shell_instance = VigiShellApp(master_app_settings, ai_interaction_service, master_terminal_display)

    if initial_query:
        vigi_shell_instance.process_single_query(initial_query)
    else:
        vigi_shell_instance.start_interactive_shell_loop()

if __name__ == "__main__":
    # For direct testing of shell_main.py:
    # vigi_shell_entry_point() # Interactive mode
    # vigi_shell_entry_point(initial_query="list all text files in current dir and tell me how many there are") # Single query
    # vigi_shell_entry_point(initial_query="show me the current date !") # Direct execution
    pass
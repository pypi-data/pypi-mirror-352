##########################################################
#                                                        #
#          Developed for GitHub: naumanAhmed3            #
#                                                        #
#                Vigi Shell Configuration                #
#                                                        #
##########################################################
"""
Manages all application-wide settings, constants, and foundational utilities
like API key retrieval and terminal key bindings for Vigi Shell.
"""

import os
import platform
import sys
from typing import Optional

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.keys import Keys
from prompt_toolkit.styles import Style as PromptToolkitStyle 
from rich.console import Console
from rich.style import Style as RichStyle 

class ApplicationSettings:
    """
    Encapsulates all static and runtime configuration parameters for Vigi Shell.
    """
    STANDARD_OUTPUT_PANE_WIDTH = 100 
    
    TERMINAL_INPUT_FIELD_STYLE = PromptToolkitStyle.from_dict( 
        {
            "prompt": "bold cyan", 
        }
    )
    VS_WELCOME_STYLE = RichStyle(color="bright_magenta", bold=True)
    VS_PROMPT_SYMBOL_STYLE = RichStyle(color="bright_cyan", bold=True) 
    VS_CMD_PANEL_TITLE_STYLE = RichStyle(color="bright_blue", bold=True)
    VS_EXPLANATION_PANEL_TITLE_STYLE = RichStyle(color="bright_green", bold=True)
    VS_ERROR_STYLE = RichStyle(color="red", bold=True)
    VS_WARNING_STYLE = RichStyle(color="yellow", bold=True)
    VS_INFO_STYLE = RichStyle(color="blue")
    VS_EXEC_OUTPUT_STYLE = RichStyle(color="grey70") 
    VS_VIRTUAL_CWD_STYLE = RichStyle(color="dark_olive_green2", bold=True) 
    VS_AI_SUMMARY_STYLE = RichStyle(color="bright_yellow", italic=True) # Style for AI summary text
    # Corrected line:
    VS_AI_SUMMARY_PANEL_BORDER_STYLE = RichStyle(color="yellow", dim=True) # Style for AI summary panel border

    PRIMARY_AI_ENGINE = "gemini"
    SECONDARY_AI_ENGINE = "flash" # Often faster, good for summaries
    VALID_AI_ENGINE_IDS = {PRIMARY_AI_ENGINE, SECONDARY_AI_ENGINE}
    GOOGLE_AI_ENGINE_ENDPOINTS = {
        PRIMARY_AI_ENGINE: "models/gemini-1.5-flash",
        SECONDARY_AI_ENGINE: "models/gemini-1.5-flash-latest",
    }

    GOOGLE_AUTH_TOKEN_ENV_VAR = "GOOGLE_API_KEY"
    INSTRUCTION_GENERATION_TEMPERATURE = 0.01
    OUTPUT_SUMMARY_TEMPERATURE = 0.3 # Slightly more creative for natural language summaries
    SUMMARIZE_COMMAND_OUTPUT_AUTOMATICALLY = True # Toggle for the new feature
    MAX_OUTPUT_FOR_SUMMARY_PROMPT = 2000 # Max characters of stdout/stderr to send for summary

    def __init__(self):
        self.current_os_descriptor: str = platform.platform()
        self.custom_key_actions: KeyBindings = self._initialize_terminal_key_handlers()

    def _initialize_terminal_key_handlers(self) -> KeyBindings:
        key_action_registry = KeyBindings()
        @key_action_registry.add(Keys.Enter, eager=True)
        def _handle_enter_key(event_data: KeyPressEvent) -> None:
            input_buffer = event_data.app.current_buffer
            if input_buffer.complete_state: 
                if input_buffer.complete_state.current_completion:
                    input_buffer.apply_completion(input_buffer.complete_state.current_completion)
                    return 
            input_buffer.validate_and_handle()
        return key_action_registry

    def retrieve_environment_setting(self, setting_name: str, display_interface: Console) -> str:
        setting_value = os.environ.get(setting_name, None)
        if not setting_value:
            display_interface.print(
                f"[bold red]Critical Error: The environment setting '{setting_name}' was not found.\n"
                f"Please ensure this variable is set in your environment.\n"
                f"Example: export {setting_name}=<your_actual_value>[/bold red]"
            )
            sys.exit(-1)
        return setting_value

    def retrieve_optional_environment_setting(self, setting_name: str, display_interface: Console) -> Optional[str]:
        setting_value = os.environ.get(setting_name, None)
        if not setting_value:
            display_interface.print(
                f"[bold yellow]Warning: The optional environment setting '{setting_name}' was not found.\n"
                f"This might limit some functionalities. If needed, please set this variable.\n"
                f"Example: export {setting_name}=<your_optional_value>[/bold yellow]"
            )
        return setting_value
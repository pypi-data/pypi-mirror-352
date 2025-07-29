# vigi/repl_handler.py
from typing import Any, List, Dict, Optional
import typer
from rich.panel import Panel 
from rich.text import Text
from rich.console import Console
from rich import box 
from rich.align import Align 
from rich.rule import Rule

from .tools_and_personas import DefaultPersonas, DigitalPersona
from .corefunctions import run_command # Assuming this might still be needed by other parts
from .chat_manage import ChatHandler
import getpass

import functools
import logging
import multiprocessing
import re
import sys
from io import StringIO
from typing import Dict, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SanitizationAndExecution(BaseModel):

    globals: Optional[Dict] = Field(default_factory=dict, alias="_globals")
    locals: Optional[Dict] = Field(default_factory=dict, alias="_locals")

    @staticmethod
    def sanitize_input(query: str) -> str:
        """Sanitize input to the python REPL."""
        query = re.sub(r"^(\s|`)*(?i:python)?\s*", "", query)
        query = re.sub(r"(\s|`)*$", "", query)
        return query

    @classmethod
    def worker(
        cls,
        command: str,
        globals: Optional[Dict],
        locals: Optional[Dict],
        queue: multiprocessing.Queue,
    ) -> None:
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        try:
            cleaned_command = cls.sanitize_input(command)
            exec(cleaned_command, globals, locals)
            sys.stdout = old_stdout
            queue.put(mystdout.getvalue())
        except Exception as e:
            sys.stdout = old_stdout
            queue.put(repr(e))

    def execute_code(self, command: str, timeout: Optional[int] = None) -> str:
        """Run command with own globals/locals and returns anything printed."""
        queue: multiprocessing.Queue = multiprocessing.Queue()
        if timeout is not None:
            p = multiprocessing.Process(
                target=self.worker, args=(command, self.globals, self.locals, queue)
            )
            p.start()
            p.join(timeout)
            if p.is_alive():
                p.terminate()
                return "Execution timed out"
        else:
            self.worker(command, self.globals, self.locals, queue)
        return queue.get()
 
python_code_runner = SanitizationAndExecution()


class ReplHandler(ChatHandler):
    def __init__(self, chat_id: Optional[str], role: DigitalPersona, markdown: bool) -> None:
        super().__init__(chat_id, role, markdown)
        # self.console is initialized by the parent class (ChatHandler -> ConvoProcesser)

    @classmethod
    def _get_multiline_input(cls, console_instance: Console) -> str:
        """Collects multiline input from the user."""
        lines = []
        # Print instruction for multiline input
        console_instance.print(Text("  └─ Typing (end with \"\"\" on a new line):", style="dim blue"))
        while True:
            try:
                # Typer prompt for each line of multiline input
                line = typer.prompt("    ", prompt_suffix="", show_default=False, default="") 
                if line == '"""':
                    break
                lines.append(line)
            except typer.Abort: # User pressed Ctrl+C
                return "" # Indicate no input collected
            except EOFError: # User pressed Ctrl+D (Unix) or Ctrl+Z+Enter (Windows)
                return "\n".join(lines) # Return whatever was collected
        return "\n".join(lines)

    def _display_user_submitted_multiline(self, message_content: str):
        """Prints the user's fully submitted multiline message."""
        user_name_display = Text(f"{getpass.getuser().upper()} ➤ ", style="bold bright_blue")
        # Print the user prefix once for the entire multiline block
        self.console.print(user_name_display)
        for line_idx, line in enumerate(message_content.splitlines()):
            # The first line of content starts after the prefix.
            # Subsequent lines are indented for clarity.
            line_prefix = "  " if line_idx > 0 else ""
            self.console.print(Text(f"{line_prefix}{line}", style="white"))

    def _print_ai_prefix_and_get_response(self, persona_name: str, prompt_for_ai: str, **kwargs: Any) -> str:
        """
        Prints the AI's prefix, calls super().handle() to get and print the AI's response
        (via consoleUI.py's printer), and handles spacing.
        """
        self.console.line(1) # Ensure a blank line BEFORE the AI's prefix and response.
        
        ai_prefix_text = Text(f"{persona_name.upper()} ➤ ", style="bold green")
        # This calls the printer from consoleUI.py, which should start printing on the current line.
        logging.getLogger().setLevel(logging.CRITICAL)  # Silence all logging
        response_content = super().handle(prompt=prompt_for_ai, **kwargs)
        logging.getLogger().setLevel(logging.WARNING)  # Restore
        
        
        # The printer in consoleUI.py is expected to call self.console.line() at its end.
        # We add one more line for a bit more visual separation before the next user prompt.
        return [ ai_prefix_text , response_content ]

    def handle(self, init_prompt: str, **kwargs: Any) -> None:
        # Initial setup messages
        if self.initiated and self.chat_id:
            self.console.line()
            self.console.print(Text("--- Chat Restored ---", style="dim magenta", justify="center"))
            self.show_messages(self.chat_id, self.markdown) # This might have its own complex formatting
            self.console.print(Text("--- End of Restored Chat ---", style="dim magenta", justify="center"))
            self.console.line(2)

        persona_display_name = self.role.identifier if self.role else "Assistant"
       
        self.console.print(
            f" 💬 Chatting with {persona_display_name}.", style="bold magenta", justify="center"
        )
        self.console.print(Text("Type 'exit' or Ctrl+C to end.", style="dim", justify="center"))
        self.console.line() # Blank line after initial info

        # --- Handle Initial Prompt if one was passed ---
        if init_prompt:
            # Display the initial prompt as if the user typed it.
            # This assumes init_prompt is the first "user turn."
            self.console.print(Text(f"{getpass.getuser().upper()} ➤ {init_prompt}", style="bold bright_blue"))
            
            # Get AI's response to the initial prompt
            self._print_ai_prefix_and_get_response(persona_display_name, init_prompt, **kwargs)

        # --- AI Greeting ---
        # Construct the prompt for the AI's greeting
        greeting_ai_prompt = f"Warmly Greet to user `{getpass.getuser()}` as per your name which is `{self.role.identifier}` role which is `{self.role.definition}` and also ask them how can you assist them."
        # Get AI's greeting response
        self._print_ai_prefix_and_get_response(persona_display_name, greeting_ai_prompt, **kwargs)

        # --- Main Interaction Loop ---
        while True:
            current_user_query = "" 
            try:
                # User types their input here. This line will look like: USERNAME ➤ [cursor]
                user_input_prefix = Text(f"{getpass.getuser().upper()} ➤ ", style="bold bright_blue")
                self.console.print(user_input_prefix, end="")
                prompt_text_from_user = typer.prompt("", prompt_suffix="", show_default=False, default="")
            except (KeyboardInterrupt, EOFError): # User wants to exit
                self.console.print(Text("\nExiting chat.", style="bold red", justify="center"))
                self.console.line()
                return

            # Process user input
            if prompt_text_from_user.strip() == '"""': 
                # User initiated multiline input
                actual_multiline_input = self._get_multiline_input(self.console) 
                current_user_query = actual_multiline_input.strip()
                if current_user_query:
                    # Multiline input is collected, now display it formatted.
                    # The typer.prompt for '"""' doesn't show the content itself.
                    self.console.line() # Space before displaying the collected multiline
                    self._display_user_submitted_multiline(current_user_query)
                # If multiline input is empty, current_user_query is empty, loop will continue.

            elif prompt_text_from_user.lower() in ("exit", "exit()", "quit", "quit()"):
                self.console.print(Text("Exiting chat.", style="bold red", justify="center"))
                self.console.line()
                return
            else: # Single-line input from user
                current_user_query = prompt_text_from_user.strip()
                # For single-line input, the text is already visible on the console
                # from the `typer.prompt` line. No need to re-print it here.

            # If, after processing, there's no query (e.g., empty multiline, or just Enter on single line)
            if not current_user_query: 
                self.console.line() # Add some space and prompt again
                continue
            
            # --- AI's Turn to Respond to User Query ---
            # Get AI's response to the current user query
            vigi_response_from_ai = self._print_ai_prefix_and_get_response(
                persona_display_name, current_user_query, **kwargs
            )
            self.console.print(vigi_response_from_ai[0], style="bold yellow", end="")
            if (self.role.identifier == "Code Generator"):
                self.console.print(vigi_response_from_ai[1], style="bold italic yellow" )
            else:
                self.console.print(vigi_response_from_ai[1], style="bold italic purple" ) 

            self.console.line()

            # --- Handle Code Execution if applicable ---
            if (self.role.identifier == "Code Generator"):
               
                self.console.line() # Space before potential execution result
                execution_output = python_code_runner.execute_code(vigi_response_from_ai[1]) # vigi_response_from_ai is AI's code
                
                self.console.print(Rule(style="yellow"))
                self.console.print(Text("Execution Result 🛠️ ➤➤", style="bold yellow"), end="")
                self.console.print(Text(execution_output, style="italic green"))
                self.console.print(Rule(style="yellow"))
                
                self.console.line()
            
            # Spacing for the next user prompt is handled by the trailing self.console.line(1)
            # within _print_ai_prefix_and_get_response.
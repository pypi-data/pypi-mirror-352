# chat_handler.py 

import json
from pathlib import Path
from typing import Any, Callable, Dict, Generator, List, Optional

import typer
from click import BadArgumentUsage
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel 
from rich.text import Text 
from rich.rule import Rule 

from .config import cfg
from .tools_and_personas import DefaultPersonas, DigitalPersona 
from .corefunctions import option_callback
from .handler import ConvoProcesser 
# *** NEW IMPORT ***
from .handler import generate_model_response as api_generate_model_response # Import the actual function

CHAT_CACHE_LENGTH = int(cfg.get("CHAT_CACHE_LENGTH"))
CHAT_CACHE_PATH = Path(cfg.get("CHAT_CACHE_PATH"))


class ChatSession:
    # ... (ChatSession class remains IDENTICAL to the previous correct version) ...
    def __init__(self, length: int, storage_path: Path):
        self.length = length
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Generator[str, None, None]:
            chat_id = kwargs.pop("chat_id", "repl_temp") 
            current_turn_messages = kwargs.pop("messages", []) 

            if not isinstance(current_turn_messages, list):
                if isinstance(current_turn_messages, dict):
                    current_turn_messages = [current_turn_messages]
                else: 
                    current_turn_messages = []
            
            previous_messages_history = self._read(chat_id)
            
            combined_messages: List[Dict[str,str]] = []
            has_system_prompt_in_current = any(m.get("role") == "system" for m in current_turn_messages)

            if previous_messages_history:
                if has_system_prompt_in_current and previous_messages_history[0].get("role") == "system":
                    combined_messages.extend(previous_messages_history)
                    combined_messages.extend([m for m in current_turn_messages if m.get("role") != "system"])
                else:
                    combined_messages.extend(previous_messages_history)
                    combined_messages.extend(current_turn_messages)
            else: 
                combined_messages.extend(current_turn_messages)

            kwargs["message_sequence"] = combined_messages 
            
            response_text = ""
            for word in func(*args, **kwargs): 
                response_text += word
                yield word
            
            if response_text: 
                combined_messages.append({"role": "assistant", "content": response_text})
                if chat_id != "repl_temp":
                    self._write(combined_messages, chat_id)
        return wrapper

    def _read(self, chat_id: str) -> List[Dict[str, str]]:
        file_path = self.storage_path / chat_id
        if not file_path.exists():
            return []
        try:
            parsed_cache = json.loads(file_path.read_text(encoding="utf-8"))
            return parsed_cache if isinstance(parsed_cache, list) else []
        except json.JSONDecodeError:
            file_path.unlink(missing_ok=True) 
            return [] 
        except Exception:
            return []

    def _write(self, messages: List[Dict[str, str]], chat_id: str) -> None:
        file_path = self.storage_path / chat_id
        if not messages:
            try:
                with file_path.open("w", encoding="utf-8") as f:
                    json.dump([], f)
            except Exception: 
                pass 
            return

        system_prompt_present = messages[0].get("role") == "system"
        truncated_messages = messages # Default to no truncation
        
        if system_prompt_present:
            num_other_messages_to_keep = self.length - 1 if self.length > 0 else 0
            if len(messages) -1 > num_other_messages_to_keep : 
                start_index_for_others = len(messages) - num_other_messages_to_keep
                truncated_messages = messages[:1] + messages[start_index_for_others:]
        else: 
            if len(messages) > self.length:
                truncated_messages = messages[len(messages) - self.length:]
        
        try:
            with file_path.open("w", encoding="utf-8") as f:
                json.dump(truncated_messages, f, indent=2)
        except Exception: 
            pass

    def invalidate(self, chat_id: str) -> None:
        file_path = self.storage_path / chat_id
        file_path.unlink(missing_ok=True)

    def get_messages(self, chat_id: str) -> List[Dict[str, str]]:
        return self._read(chat_id)

    def exists(self, chat_id: Optional[str]) -> bool:
        return bool(chat_id and bool(self._read(chat_id)))

    def list(self) -> List[Path]:
        files = self.storage_path.glob("*")
        return sorted(files, key=lambda f: f.stat().st_mtime)


class ChatHandler(ConvoProcesser):
    chat_session = ChatSession(CHAT_CACHE_LENGTH, CHAT_CACHE_PATH)

    def __init__(self, chat_id: Optional[str], role: DigitalPersona, markdown: bool) -> None:
        super().__init__(role, markdown)
        self.chat_id = chat_id if chat_id else "temp"
        self.role = role
        if self.chat_id in ("temp", "repl_temp"):
            self.chat_session.invalidate(self.chat_id)
        self.console = Console() 
        self.validate()

    # ... (properties, initial_message_content, list_ids, show_messages, validate remain the same) ...
    @property
    def initiated(self) -> bool:
        return self.chat_session.exists(self.chat_id)

    @property
    def is_same_role(self) -> bool:
        messages = self.chat_session.get_messages(self.chat_id)
        if not messages or messages[0].get("role") != "system":
            return True 
        initial_system_message_content = messages[0]["content"]
        return self.role.matches_persona(initial_system_message_content)

    @classmethod
    def initial_message_content(cls, chat_id: str) -> str:
        messages = cls.chat_session.get_messages(chat_id)
        return messages[0]["content"] if messages and messages[0].get("role") == "system" else ""

    @classmethod
    @option_callback
    def list_ids(cls, value: bool) -> None: 
        if not value: return
        chat_files = cls.chat_session.list()
        if not chat_files:
            typer.echo("No chat sessions found.")
        else:
            typer.echo("Available chat sessions (IDs):")
            for chat_file in chat_files:
                typer.echo(f"- {chat_file.name}")
        raise typer.Exit()


    @classmethod
    def show_messages(cls, chat_id_to_show: str, use_markdown_rendering: bool) -> None:
        console = Console()
        messages = cls.chat_session.get_messages(chat_id_to_show)

        if not messages:
            console.print(f"[yellow]No messages found for chat ID: {chat_id_to_show}[/yellow]")
            return
        console.print(Rule(f"Chat History: {chat_id_to_show}", style="bold magenta", align="center"))
        
        persona_name_from_history = "Assistant" 
        initial_sys_content_for_chat = ""
        if messages and messages[0].get("role") == "system":
            initial_sys_content_for_chat = messages[0]["content"]
            extracted_name = DigitalPersona.extract_persona_identifier(initial_sys_content_for_chat)
            if extracted_name:
                persona_name_from_history = extracted_name
        
        code_theme = cfg.get("CODE_THEME")
        default_user_color = cfg.get("DEFAULT_COLOR") 

        for i, message_data in enumerate(messages):
            role = message_data.get("role", "unknown")
            content = message_data.get("content", "")
            if role == "system": continue 
            title_text_markup = ""
            panel_border_style = "bright_blue" # Default
            
            if role == "user":
                title_text_markup = "[b green]You[/b green]"
                panel_border_style = "green"
                display_content = Text(content, style=default_user_color)
            elif role == "assistant":
                title_text_markup = f"[b bright_blue]{persona_name_from_history}[/b bright_blue]"
                markdown_applicable_for_this_chat = "APPLY MARKDOWN" in initial_sys_content_for_chat
                if use_markdown_rendering and markdown_applicable_for_this_chat:
                    display_content = Markdown(content, code_theme=code_theme)
                else:
                    display_content = Text(content)
            elif role == "function":
                func_name = message_data.get("name", "N/A")
                title_text_markup = f"[b yellow]Function ({func_name})[/b yellow]"
                panel_border_style = "yellow"
                display_content = Text(str(content), style="bright_black")
            else: 
                title_text_markup = f"[b red]{role.capitalize()}[/b red]"
                panel_border_style = "red"
                display_content = Text(content)

            console.print(Panel(display_content,title=Text.from_markup(title_text_markup),border_style=panel_border_style,expand=False, padding=(0,1)))
            if i < len(messages) - 1: console.print("") 


    def validate(self) -> None:
        if self.initiated:
            initial_sys_content = self.initial_message_content(self.chat_id)
            if initial_sys_content: 
                chat_role_name = DigitalPersona.extract_persona_identifier(initial_sys_content)
                if not chat_role_name:
                    if self.role.identifier != DefaultPersonas.DEFAULT.value: 
                        pass
                elif not self.role.matches_persona(initial_sys_content): 
                    raise BadArgumentUsage(
                        f'Cannot change chat role to "{self.role.identifier}" '
                        f'since it was initiated as "{chat_role_name}" chat.'
                    )

    # *** MODIFIED _original_get_completion ***
    def _original_get_completion(self, **kwargs: Any) -> Generator[str, None, None]:
        # This now directly calls the imported standalone 'generate_model_response' function
        # from handler.py.
        # It receives `kwargs` from the `ChatSession` decorator's wrapper,
        # which includes the full `messages` history in `kwargs['message_sequence']`.
        # All other necessary parameters (model_identifier, etc.) are also in kwargs.
        yield from api_generate_model_response(**kwargs) # Call the imported function

    @chat_session
    def get_completion(self, **kwargs: Any) -> Generator[str, None, None]:
        # This decorated method calls the internal _original_get_completion.
        # The decorator handles history and caching.
        yield from self._original_get_completion(**kwargs)

    def make_messages(self, prompt: str) -> List[Dict[str, str]]:
        messages_for_turn: List[Dict[str, str]] = []
        history = self.chat_session._read(self.chat_id)
        if not history: # Only add system prompt if there's no history at all for this chat_id
            messages_for_turn.append({"role": "system", "content": self.role.definition})
        messages_for_turn.append({"role": "user", "content": prompt})
        return messages_for_turn

    def handle(self, **kwargs: Any) -> str:
        prompt = kwargs.pop('prompt', "") 
        if not prompt: return ""

        messages_for_this_turn_for_decorator = self.make_messages(prompt)
        
        completion_generator = self.get_completion(
            chat_id=self.chat_id,
            messages=messages_for_this_turn_for_decorator,
            model_identifier=kwargs.get('model'),
            creativity_level=kwargs.get('temperature'),
            probability_threshold=kwargs.get('top_p'),
            available_operations=kwargs.get('functions'),
            enable_caching=kwargs.get('caching', True),
            persona_identifier=self.role.identifier
        )
        
        disable_stream = cfg.get("DISABLE_STREAMING") == "false"
        full_response_text = "".join(word for word in completion_generator)
        
        return full_response_text
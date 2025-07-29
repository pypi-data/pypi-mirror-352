#handler.py
import json
from pathlib import Path
from typing import Any, Callable, Dict, Generator, List, Optional
from abc import ABC, abstractmethod

from .hold_data import Cache
from .config import cfg
from .tools_and_personas import fetch_procedure
from .consoleUI import select_appropriate_printing_function_based_on_markdown_flag as get_printer
from .tools_and_personas import DefaultPersonas, DigitalPersona

# API Communication Setup
query_executor: Callable[..., Any] = lambda *args, **kwargs: Generator[Any, None, None]
service_gateway = cfg.get("API_BASE_URL")
use_alternative_provider = cfg.get("USE_VIGI_CORE") == "true"
request_parameters = {
    "timeout": int(cfg.get("REQUEST_TIMEOUT")),
    "api_key": cfg.get("VIGI_API_KEY"),
    "base_url": None if service_gateway == "default" else service_gateway,
}

if use_alternative_provider:
    import litellm  # type: ignore
    query_executor = litellm.completion
    litellm.suppress_debug_info = True
    request_parameters.pop("api_key")
else:
    from openai import OpenAI
    api_client = OpenAI(**request_parameters)  # type: ignore
    query_executor = api_client.chat.completions.create
    request_parameters = {}

# Response Storage
response_cache = Cache(int(cfg.get("CACHE_LENGTH")), Path(cfg.get("CACHE_PATH")))

def process_external_operation(
    conversation_history: List[Dict[str, Any]],
    operation_name: str,
    operation_parameters: str
) -> Generator[str, None, None]:
    """Handle execution of external operations"""
    conversation_history.append({
        "role": "assistant",
        "content": f"Initiating operation: {operation_name}",
        "function_call": {"name": operation_name, "arguments": operation_parameters},
    })

    if conversation_history and conversation_history[-1]["role"] == "assistant":
        yield "\n"

    parsed_parameters = json.loads(operation_parameters)
    formatted_parameters = ", ".join(f'{k}="{v}"' for k, v in parsed_parameters.items())
    yield f"> @ToolCalling `{operation_name}({formatted_parameters})` \n\n"

    operation_result = fetch_procedure(operation_name)(**parsed_parameters)
    if cfg.get("SHOW_FUNCTIONS_OUTPUT") == "true":
        yield f"```text\n{operation_result}\n```\n"
    
    conversation_history.append({
        "role": "function", 
        "content": str(operation_result), 
        "name": operation_name
    })

@response_cache
def generate_model_response(
    model_identifier: str,
    creativity_level: float,
    probability_threshold: float,
    message_sequence: List[Dict[str, Any]],
    available_operations: Optional[List[Dict[str, str]]],
    *,
    enable_caching: bool,
    persona_identifier: str
) -> Generator[str, None, None]:
    """Generate responses from the language model"""
    current_operation = accumulated_args = ""
    is_specialized_persona = persona_identifier in {
        DefaultPersonas.SHELL.value,
        DefaultPersonas.CODE.value,
        DefaultPersonas.DESCRIBE_SHELL.value
    }
    
    operations_to_use = None if is_specialized_persona else available_operations
    api_call_config = request_parameters.copy()
    
    if operations_to_use:
        api_call_config.update({
            "tool_choice": "auto",
            "tools": operations_to_use,
            "parallel_tool_calls": False
        })

    try:
        model_response = query_executor(
            model=model_identifier,
            temperature=creativity_level,
            top_p=probability_threshold,
            messages=message_sequence,
            stream=True,
            **api_call_config
        )

        for response_chunk in model_response:
            content_delta = response_chunk.choices[0].delta
            operation_triggers = (
                content_delta.get("tool_calls") 
                if use_alternative_provider 
                else content_delta.tool_calls
            )
            
            if operation_triggers:
                for trigger in operation_triggers:
                    if trigger.function.name:
                        current_operation = trigger.function.name
                    if trigger.function.arguments:
                        accumulated_args += trigger.function.arguments
            
            if response_chunk.choices[0].finish_reason == "tool_calls":
                yield from process_external_operation(
                    message_sequence, 
                    current_operation, 
                    accumulated_args
                )
                yield from generate_model_response(
                    model_identifier=model_identifier,
                    creativity_level=creativity_level,
                    probability_threshold=probability_threshold,
                    message_sequence=message_sequence,
                    available_operations=operations_to_use,
                    enable_caching=False,
                    persona_identifier=persona_identifier
                )
                return

            yield content_delta.content or ""
    except KeyboardInterrupt:
        if hasattr(model_response, "close"):
            model_response.close()

# Change base class name back to Handler
class ConvoProcesser(ABC):
    def __init__(self, role: DigitalPersona, markdown: bool) -> None:
        self.role = role
        self.markdown = "APPLY MARKDOWN" in role.definition and markdown
        self.printer = get_printer(
            self.markdown,
            cfg.get("CODE_THEME"),
            cfg.get("DEFAULT_COLOR")
        )

    @abstractmethod
    def make_messages(self, prompt: str) -> List[Dict[str, str]]:  # Renamed back
        pass

    def handle(  # Original method signature
        self,
        prompt: str,
        model: str,
        temperature: float,
        top_p: float,
        caching: bool,
        functions: Optional[List[Dict[str, str]]] = None,
        **kwargs: Any
    ) -> str:
        disable_stream = cfg.get("DISABLE_STREAMING") == "true"
        messages = self.make_messages(prompt.strip())
        
        generator = generate_model_response(
            model_identifier=model,
            creativity_level=temperature,
            probability_threshold=top_p,
            message_sequence=messages,
            available_operations=functions,
            enable_caching=caching,
            persona_identifier=self.role.identifier
        )

        return self.printer(generator, not disable_stream)
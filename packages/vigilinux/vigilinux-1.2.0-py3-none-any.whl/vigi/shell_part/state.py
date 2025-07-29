# ai_shell_gemini/state.py
from typing import TypedDict, Optional, List, Dict, Union, Literal
from langchain_core.messages import BaseMessage 

# We will use LangChain's memory objects instead of manually managing conversation_history in state.
# However, we might pass the memory object itself via state if needed by multiple components,
# or configure the runnable graph with memory directly.
# For now, let's remove it from AgentState and assume memory is handled at the chain/graph invocation level.

class PlanStep(TypedDict):
    type: str
    description: str
    command_or_tool_name: Optional[str]
    args: Optional[Dict]
    code: Optional[str]
    pre_requisites: Optional[List[Dict]]
    status: Optional[str]
    result: Optional[str]

class SystemConfigDetails(TypedDict, total=False):
    is_system_config: bool
    dependency_name: Optional[str]
    dependency_install_command: Optional[str]
    dependency_check_command: Optional[str]
    command_if_dep_installed: Optional[str]

class AgentState(TypedDict):
    original_query: str
    parsed_intent: Optional[str]
    # conversation_history: Optional[List[Dict[str, str]]] # REMOVED
    chat_memory_messages: Optional[List[BaseMessage]] # MODIFIED
    current_plan: Optional[List[PlanStep]]
    current_step_index: int

    needs_search: bool
    search_query: Optional[str]
    search_results: Optional[List[dict]]
    search_summary: Optional[str]
    user_confirmed_search_info: Optional[bool]

    generated_code_content: Optional[str]
    generated_command: Optional[str]
    generated_command_purpose: Optional[str]
    command_explanation: Optional[str]
    safety_assessment: Optional[str]
    safety_rating: Optional[str]
    os_type: str # This should persist in interactive mode

    executed_command: Optional[str]
    execution_stdout: Optional[str]
    execution_stderr: Optional[str]
    execution_return_code: Optional[int]
    execution_summary: Optional[str]

    needs_retry: bool
    retry_attempt: int
    is_trying_file_search: bool

    needs_user_clarification: bool
    clarification_question: Optional[str]
    clarification_options: Optional[List[str]]
    user_feedback_for_clarification: Optional[str]
    clarification_context: Optional[str]

    tool_call_needed: bool
    tool_name: Optional[str]
    tool_args: Optional[Dict]
    tool_output: Optional[str]

    prereq_check_results: Optional[Dict[str, bool]]

    user_feedback: Optional[str]
    error_message: Optional[str]
    is_error: bool

    # System Configuration Flow
    system_config_details: Optional[SystemConfigDetails]
    needs_dependency_check: bool
    dependency_already_installed: Optional[bool]
    user_approved_dependency_install: Optional[bool]
    needs_dependency_installation: bool
    dependency_install_stdout: Optional[str]
    dependency_install_stderr: Optional[str]
    dependency_install_return_code: Optional[int]
    
    execution_summary_override: Optional[str] # Added in previous step, ensure it's here.

    # We might add 'chat_memory' here if passing the memory object through state
    # chat_memory: Optional[Any] # e.g., ConversationBufferMemory
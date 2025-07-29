# ai_shell_gemini/graph.py
from langgraph.graph import StateGraph, END
from .state import AgentState
from .agents import (
    get_os_type_node, code_generator_node, decide_search_needed_node,
    perform_search_node, command_generator_node, command_explainer_node,
    safety_validator_node, execute_command_node, handle_execution_error_node,
    check_dependency_installed_node, install_dependency_node,
    summarize_execution_node
)

# DEBUG_GRAPH = False # Could add a flag later
# def gprint(msg):
#     if DEBUG_GRAPH: print(msg)

workflow = StateGraph(AgentState)

# Add all nodes
workflow.add_node("get_os", get_os_type_node)
workflow.add_node("generate_code_if_needed", code_generator_node)
workflow.add_node("decide_search", decide_search_needed_node)
workflow.add_node("perform_search", perform_search_node)
workflow.add_node("generate_command", command_generator_node)
workflow.add_node("check_dependency_installed", check_dependency_installed_node)
workflow.add_node("install_dependency", install_dependency_node)
workflow.add_node("explain_command", command_explainer_node)
workflow.add_node("validate_safety", safety_validator_node)
workflow.add_node("execute_command", execute_command_node)
workflow.add_node("summarize_execution", summarize_execution_node)
workflow.add_node("handle_error_and_retry_decision", handle_execution_error_node)

workflow.set_entry_point("get_os")

def route_after_get_os(state: AgentState):
    if state.get("user_feedback_for_clarification") is not None and \
       state.get("clarification_context") != "dependency_install_approval":
        # gprint("--- Graph: Routing from OS to command generation (general feedback) ---")
        return "generate_command"
    if state.get("needs_dependency_installation") and state.get("user_approved_dependency_install"):
        # gprint("--- Graph: Routing from OS to install_dependency (approved install) ---")
        return "install_dependency"
    # gprint("--- Graph: Routing from OS to generate_code_if_needed (standard flow) ---")
    return "generate_code_if_needed"

workflow.add_conditional_edges("get_os", route_after_get_os, {
    "generate_code_if_needed": "generate_code_if_needed",
    "generate_command": "generate_command",
    "install_dependency": "install_dependency"
})

workflow.add_edge("generate_code_if_needed", "decide_search")

def route_after_search_decision(state: AgentState):
    if state.get("is_error"): return END
    if state.get("user_feedback_for_clarification") is not None:
        # gprint("--- Graph: Routing from search decision to command generation (user feedback) ---")
        return "generate_command"
    return "perform_search" if state.get("needs_search") else "generate_command"

workflow.add_conditional_edges("decide_search", route_after_search_decision, {
    "perform_search": "perform_search",
    "generate_command": "generate_command",
    END: END
})
workflow.add_edge("perform_search", "generate_command")


def route_after_command_generation(state: AgentState):
    if state.get("generated_command_purpose") == "history_qa":
        # gprint("--- Graph: Command generator answered from history. Ending. ---")
        return END
    if state.get("is_error"): # Catches NO_ACTION_NEEDED, LLM errors etc.
        # gprint(f"--- Graph: Error after command_gen ('{state.get('error_message')}'). Ending. ---")
        return END 
    if state.get("needs_user_clarification"): # Should be caught by is_error usually if it implies graph end
        # gprint("--- Graph: Command generator needs clarification. Ending for main.py. ---")
        return END
    if state.get("needs_dependency_check"):
        # gprint("--- Graph: Routing from command_gen to check_dependency_installed ---")
        return "check_dependency_installed"
    if not state.get("generated_command"): 
        # gprint("--- Graph: No command and no dependency check needed (e.g. dep flow). Ending. ---")
        return END 
    # gprint("--- Graph: Routing from command_gen to validate_safety ---")
    return "validate_safety"

workflow.add_conditional_edges("generate_command", route_after_command_generation, {
    "check_dependency_installed": "check_dependency_installed",
    "validate_safety": "validate_safety",
    END: END
})

def route_after_dependency_check(state: AgentState):
    if state.get("is_error"): return END
    if state.get("needs_user_clarification") and state.get("clarification_context") == "dependency_install_approval":
        # gprint("--- Graph: Dependency check needs user approval for install. Ending for main.py. ---")
        return END
    # If dependency is installed (or not needed for this path)
    # AND a command_if_dep_installed was specified (even if it's an empty string, generated_command would be "")
    if state.get("dependency_already_installed") and state.get("generated_command") is not None:
        # gprint("--- Graph: Dependency installed or not needed. Routing to validate_safety. ---")
        return "validate_safety"
    # If dependency is installed but no command_if_dep_installed was provided (generated_command is None)
    if state.get("dependency_already_installed") and state.get("generated_command") is None:
        # gprint("--- Graph: Dependency already installed, no further command. Ending (summary will handle). ---")
        return "summarize_execution" # Let summarize_execution handle it
    return END 

workflow.add_conditional_edges("check_dependency_installed", route_after_dependency_check, {
    "validate_safety": "validate_safety",
    "summarize_execution": "summarize_execution",
    END: END
})

def route_after_dependency_installation(state: AgentState):
    if state.get("is_error"): 
        # gprint("--- Graph: Dependency installation failed. Routing to summarize_execution. ---")
        return "summarize_execution"
    # If installation was successful AND a command_if_dep_installed was specified (even if empty string)
    if state.get("generated_command") is not None:
        # gprint("--- Graph: Dependency installation successful. Routing to validate_safety. ---")
        return "validate_safety"
    if state.get("generated_command") is None: # Successful install, but no follow-up command
        return "summarize_execution" # Let summarize_execution handle it
    # gprint("--- Graph: Unexpected state after dependency installation. Ending. ---")
    return END 

workflow.add_conditional_edges("install_dependency", route_after_dependency_installation, {
    "validate_safety": "validate_safety",
    "summarize_execution": "summarize_execution", 
    END: END
})

workflow.add_edge("validate_safety", "explain_command")

def route_to_execution_or_user(state: AgentState): 
    if state.get("is_error"): return END 
    # gprint("--- Graph: Routing from explanation to execute_command ---")
    return "execute_command" 

workflow.add_conditional_edges("explain_command", route_to_execution_or_user, {
    "execute_command": "execute_command",
    END: END
})

def route_after_execution(state: AgentState):
    if state.get("needs_user_clarification"): 
        # gprint("--- Graph: Execution node (or error handler) triggered user clarification. Ending for main.py. ---")
        return END
    if state.get("needs_retry"): 
        # gprint("--- Graph: Execution needs retry. Routing to handle_error_and_retry_decision. ---")
        return "handle_error_and_retry_decision"
    # gprint("--- Graph: Execution finished (success or non-retryable error). Routing to summarize_execution. ---")
    return "summarize_execution"

workflow.add_conditional_edges("execute_command", route_after_execution, {
    "handle_error_and_retry_decision": "handle_error_and_retry_decision",
    "summarize_execution": "summarize_execution",
    END: END 
})

workflow.add_edge("summarize_execution", END) 

def route_after_error_handling(state: AgentState):
    if state.get("is_error"): 
        # gprint("--- Graph: Error handler determined a final error. Ending. ---")
        return END
    if state.get("needs_user_clarification"): 
        # gprint("--- Graph: Error handler triggered user clarification. Ending for main.py. ---")
        return END
    if state.get("needs_retry"): 
        # gprint(f"--- Graph: Looping back to generate_command for retry attempt {state.get('retry_attempt')} ---")
        return "generate_command"
    # gprint("--- Graph: Error handling resolved without further action. Ending. ---")
    return END 
workflow.add_conditional_edges("handle_error_and_retry_decision", route_after_error_handling, {
    "generate_command": "generate_command",
    END: END
})

try:
    app = workflow.compile()
    # print("--- LangGraph Compiled Successfully (v.interactive) ---") # Keep for startup
except Exception as e:
    print(f"Error compiling LangGraph: {e}")
    app = None
import enum
import os
import json
import asyncio
import logging
import re # For slug generation fallback in api
from pathlib import Path
from typing import List, Dict, Any, Optional # Added Optional
from dataclasses import dataclass

import questionary # Added for interactive intent selection
from questionary import Choice, Separator # Added for interactive intent selection

from .prompts import (
    plan, 
    specify_file_paths, 
    generate_code, 
    handle_conversation, 
    generate_modification, 
    answer_question,
    generate_project_slug # Import new function
)
from .utils import write_file, get_file_tree # Added get_file_tree for context

# Placeholder for your Agent Protocol imports and setup
# from agent_protocol import Agent, Step, Task, AgentDB, Artifact
# For demonstration, we'll use mock objects for Agent features.
# Replace these with your actual Agent Protocol components.

class MockAgentDB:
    def __init__(self):
        self.tasks = {}
        self.steps = {}
        self.artifacts = {}
        self._task_id_counter = 0
        self._step_id_counter = 0

    async def get_task(self, task_id: str) -> Optional[Dict]: # Changed to Dict for simplicity
        return self.tasks.get(task_id)

    async def create_step(self, task_id: str, name: str, is_last: bool = False, additional_properties: Optional[Dict] = None) -> Dict:
        self._step_id_counter += 1
        step_id = str(self._step_id_counter)
        step_data = {
            "task_id": task_id,
            "step_id": step_id,
            "name": name,
            "is_last": is_last,
            "status": "created",
            "output": None,
            "additional_properties": additional_properties or {}
        }
        if task_id not in self.steps:
            self.steps[task_id] = []
        self.steps[task_id].append(step_data)
        Agent.log(f"Task {task_id}: Created step {step_id} - {name}")
        # In a real agent, this would trigger step_handler
        return step_data
    
    async def update_step(self, task_id: str, step_id: str, output: Optional[str] = None, status: Optional[str] = None, is_last: Optional[bool] = None):
        if task_id in self.steps:
            for step in self.steps[task_id]:
                if step["step_id"] == step_id:
                    if output is not None: step["output"] = output
                    if status is not None: step["status"] = status
                    if is_last is not None: step["is_last"] = is_last
                    Agent.log(f"Task {task_id}: Updated step {step_id} - Status: {status}, Output: {output if output else 'N/A'}")
                    return
        Agent.log(f"Task {task_id}: Could not find step {step_id} to update.", level="WARNING")


    async def create_artifact(self, task_id: str, step_id: str, relative_path: str, file_name: str):
        artifact_data = {
            "task_id": task_id,
            "step_id": step_id,
            "relative_path": relative_path,
            "file_name": file_name,
            "uri": f"file://workspace/{task_id}/{relative_path}/{file_name}" # Example URI
        }
        if task_id not in self.artifacts:
            self.artifacts[task_id] = []
        self.artifacts[task_id].append(artifact_data)
        Agent.log(f"Task {task_id}: Created artifact for step {step_id} - {file_name} at {relative_path}")


class MockAgent:
    db = MockAgentDB()
    _workspace_root = os.path.abspath(os.path.join(os.getcwd(), "agent_workspace"))

    def __init__(self):
        self._task_handler = None
        self._step_handler = None
        if not os.path.exists(self._workspace_root):
            os.makedirs(self._workspace_root, exist_ok=True)
        
        # Basic logging setup for the agent
        self.logger = logging.getLogger("AgentProtocol")
        if not self.logger.hasHandlers():
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - AGENT - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO) # Default, can be changed

    @classmethod
    def get_workspace(cls, task_id: str) -> str:
        task_workspace = os.path.join(cls._workspace_root, task_id)
        # if not os.path.exists(task_workspace): # This should be created by _define_project_root_and_slug
        #     os.makedirs(task_workspace, exist_ok=True)
        return task_workspace
    
    @classmethod
    def log(cls, message: str, level: str = "INFO"):
        # This would integrate with your agent's logging system
        # For now, print to console or use a basic logger
        # print(f"AGENT LOG ({level}): {message}")
        getattr(cls().logger, level.lower(), cls().logger.info)(message)


    def setup_agent(self, task_handler, step_handler):
        self._task_handler = task_handler
        self._step_handler = step_handler
        Agent.log("Agent setup complete.")
        return self # Allow chaining

    async def _process_task(self, task_data: Dict): # Changed Task to Dict
        if self._task_handler:
            await self._task_handler(task_data) # Pass dict directly
        # In a real agent, new steps created by task_handler would be queued
        # and then _step_handler would be invoked for each.
        # For this mock, we might need to simulate step processing if task_handler creates steps.
        if task_data["task_id"] in self.db.steps:
            for step_item in self.db.steps[task_data["task_id"]]: # Renamed step to step_item to avoid conflict
                if step_item["status"] == "created": # Only process new steps
                    await self._process_step(step_item)


    async def _process_step(self, step_data: Dict): # Changed Step to Dict
        if self._step_handler:
            Agent.log(f"Task {step_data['task_id']}: Processing step {step_data['step_id']} - {step_data['name']}")
            try:
                updated_step = await self._step_handler(step_data) # step_handler should return the modified step_data dict
                # Update step in DB based on what step_handler returns or does
                if updated_step:
                     await self.db.update_step(
                        updated_step["task_id"], 
                        updated_step["step_id"], 
                        output=updated_step.get("output"), 
                        status=updated_step.get("status", "completed"), # Default to completed
                        is_last=updated_step.get("is_last", False)
                    )
                else: # If step_handler doesn't return, assume it updated DB itself or errored
                     Agent.log(f"Task {step_data['task_id']}: Step {step_data['step_id']} did not return updated data.", level="WARNING")

            except Exception as e:
                Agent.log(f"Task {step_data['task_id']}: Error processing step {step_data['step_id']} ({step_data['name']}): {e}", level="ERROR")
                await self.db.update_step(step_data["task_id"], step_data["step_id"], status="error", output=str(e))


    async def start(self): # Mock start, perhaps process a dummy task
        Agent.log("Agent starting...")
        # Example: Create and process a dummy task
        # In a real scenario, tasks would come from an external queue or API.
        self.db._task_id_counter += 1
        dummy_task_id = str(self.db._task_id_counter)
        dummy_task = {
            "task_id": dummy_task_id,
            "input": "Create a simple python script that prints hello world.",
            "additional_properties": {
                # "output_dir": os.path.join(os.getcwd(), "agent_test_projects") # Example user-specified base
            } 
        }
        self.db.tasks[dummy_task_id] = dummy_task
        Agent.log(f"Created dummy task {dummy_task_id}")
        await self._process_task(dummy_task)
        Agent.log("Agent finished processing initial dummy task (if any). Standing by.")

# Instantiate the mock agent for use in this file
Agent = MockAgent()


@dataclass
class ProjectContext:
    shared_deps: str
    file_paths: List[str]
    output_dir: str # This will be the final, slug-inclusive project root
    conversation_history: List[Dict[str, str]]
    codebase: Dict[str, str]
    project_slug: str # Store the generated slug
    original_prompt: str # Store the original prompt


class StepTypes(str, enum.Enum):
    DEFINE_PROJECT_ROOT = "define_project_root" # New initial step
    PLAN = "plan"
    SPECIFY_FILE_PATHS = "specify_file_paths"
    GENERATE_CODE = "generate_code" # Generic name for code generation steps
    CONVERSATION = "conversation"
    MODIFY_CODE = "modify_code"
    ANSWER_QUESTION = "answer_question"


async def _define_project_root_and_slug(task: Dict, model_name: str = 'gemini-1.5-pro-latest') -> str:
    """
    Determines the final project root directory including a generated slug.
    Stores the slug and final root in task['additional_properties'].
    Returns the final absolute project root path.
    This function itself is NOT a step handler, but logic to be called by one or by task_handler.
    """
    user_specified_base_dir = task['additional_properties'].get("output_dir")
    if user_specified_base_dir:
        base_dir_abs = os.path.abspath(user_specified_base_dir)
    else:
        base_dir_abs = Agent.get_workspace(task['task_id']) # Fallback to agent's general task workspace

    if not task.get('input'):
        Agent.log(f"Task {task['task_id']}: Task input is missing, cannot generate project slug.", level="ERROR")
        # Fallback slug if no input
        project_slug = f"project-{task['task_id']}"
    else:
        # generate_project_slug is sync; run in executor if in fully async agent.
        # For this mock, direct call is fine as Agent.start() manages the loop.
        # In a real async agent, this might be:
        # loop = asyncio.get_event_loop()
        # project_slug = await loop.run_in_executor(None, generate_project_slug, task['input'], model_name)
        project_slug = generate_project_slug(task['input'], model_name)


    final_project_root_abs = os.path.join(base_dir_abs, project_slug)

    task['additional_properties']["project_slug"] = project_slug
    task['additional_properties']["final_project_root"] = final_project_root_abs
    
    if not os.path.exists(final_project_root_abs):
        os.makedirs(final_project_root_abs, exist_ok=True)
    
    Agent.log(f"Task {task['task_id']}: Defined project root: {final_project_root_abs} (Slug: {project_slug})")
    return final_project_root_abs


def _get_or_create_context(task: Dict) -> ProjectContext:
    final_project_root = task['additional_properties'].get("final_project_root")
    project_slug = task['additional_properties'].get("project_slug", "unknown-slug")
    original_prompt = task.get('input', "No prompt provided.")


    if not final_project_root:
        Agent.log(f"Task {task['task_id']}: FATAL: final_project_root not defined when creating context. "
                  "This indicates an issue in the task setup or initial step.", level="ERROR")
        raise ValueError(f"Task {task['task_id']}: final_project_root is not set. Cannot create ProjectContext.")

    if "context" not in task['additional_properties']:
        if not os.path.exists(final_project_root): # Should have been created by _define_project_root_and_slug
            os.makedirs(final_project_root, exist_ok=True)
            Agent.log(f"Task {task['task_id']}: Created missing project directory at {final_project_root}", level="WARNING")

        task['additional_properties']["context"] = ProjectContext(
            shared_deps="",
            file_paths=[],
            output_dir=final_project_root,
            conversation_history=[],
            codebase={},
            project_slug=project_slug,
            original_prompt=original_prompt
        )
        Agent.log(f"Task {task['task_id']}: Created new ProjectContext for {project_slug} at {final_project_root}")
    else: # Context exists, ensure output_dir is correct (should be immutable after creation)
        existing_context = task['additional_properties']["context"]
        if existing_context.output_dir != final_project_root:
            Agent.log(f"Task {task['task_id']}: Context output_dir mismatch. Expected '{final_project_root}', found '{existing_context.output_dir}'. Re-aligning.", level="WARNING")
            existing_context.output_dir = final_project_root # Attempt to re-align
            existing_context.project_slug = project_slug
            # This scenario (changing output_dir of existing context) is complex if files were already written.
            # For now, we assume it's caught early or the old context is discarded.

    return task['additional_properties']["context"]


async def _step_define_project_root(task: Dict, step: Dict) -> Dict:
    """Step handler for defining the project root."""
    Agent.log(f"Task {task['task_id']}: Executing step {StepTypes.DEFINE_PROJECT_ROOT}")
    final_root = await _define_project_root_and_slug(task) # This updates task['additional_properties']
    step['output'] = f"Project root defined at: {final_root}"
    step['status'] = "completed"
    
    # Create the next step (PLAN)
    await Agent.db.create_step(task['task_id'], StepTypes.PLAN)
    return step


async def _generate_shared_deps(task: Dict, step: Dict) -> Dict:
    context = _get_or_create_context(task) # Ensures context (and its output_dir) is ready
    Agent.log(f"Task {task['task_id']}: Generating shared dependencies for {context.project_slug}")
    
    # `plan` function is synchronous in prompts.py, needs to be run in executor
    loop = asyncio.get_event_loop()
    context.shared_deps = await loop.run_in_executor(None, plan, context.original_prompt)
    
    # Write shared_deps to meta folder within project_root
    meta_dir = os.path.join(context.output_dir, ".VIGI_dev_meta")
    if not os.path.exists(meta_dir):
        os.makedirs(meta_dir, exist_ok=True)
    write_file(os.path.join(meta_dir, "shared_deps.md"), context.shared_deps)
    write_file(os.path.join(meta_dir, "original_prompt.txt"), context.original_prompt)


    await Agent.db.create_step(
        task['task_id'],
        StepTypes.SPECIFY_FILE_PATHS
        # No additional_properties needed as context holds shared_deps
    )
    step['output'] = f"Shared dependencies generated and saved for {context.project_slug}."
    # (Full shared_deps content might be too large for step output in some systems)
    step['status'] = "completed"
    return step


async def _generate_file_paths(task: Dict, step: Dict) -> Dict:
    context = _get_or_create_context(task)
    Agent.log(f"Task {task['task_id']}: Specifying file paths for {context.project_slug}")

    loop = asyncio.get_event_loop()
    raw_file_paths_from_llm = await loop.run_in_executor(
        None, specify_file_paths, context.original_prompt, context.shared_deps
    )
    
    newly_sanitized_paths = []
    if raw_file_paths_from_llm:
        abs_output_dir = os.path.abspath(context.output_dir) # This is project_root_abs
        for generated_path_orig in raw_file_paths_from_llm:
            normalized_path = os.path.normpath(generated_path_orig)
            _drive, path_without_drive = os.path.splitdrive(normalized_path)
            relative_path_component = path_without_drive.lstrip(os.sep).lstrip('/')

            if not relative_path_component or relative_path_component == '.':
                Agent.log(f"Task {task['task_id']}: Warning: Skipping invalid path from LLM: '{generated_path_orig}'")
                continue

            tentative_full_path = os.path.join(abs_output_dir, relative_path_component)
            abs_final_path = os.path.abspath(tentative_full_path)

            if not abs_final_path.startswith(abs_output_dir):
                Agent.log(f"Task {task['task_id']}: Warning: LLM path '{generated_path_orig}' escapes output dir. Skipping.")
                continue
            
            final_clean_relative_path = os.path.relpath(abs_final_path, abs_output_dir)
            if final_clean_relative_path == '..' or final_clean_relative_path.startswith('..' + os.sep) or final_clean_relative_path == '.':
                 Agent.log(f"Task {task['task_id']}: Warning: Sanitized path '{final_clean_relative_path}' is invalid. Skipping '{generated_path_orig}'.")
                 continue
            newly_sanitized_paths.append(final_clean_relative_path)
    
    context.file_paths = newly_sanitized_paths
    
    if not context.file_paths:
        step['output'] = "No valid file paths were specified after sanitization."
        step['is_last'] = True 
    else:
        step['output'] = f"Sanitized file paths for generation: {str(context.file_paths)}"
        # Create steps for generating code for each sanitized file path
        num_files = len(context.file_paths)
        for i, file_path_rel in enumerate(context.file_paths):
            is_last_codegen_step = (i == num_files - 1)
            # Check if this should be the absolute last step of the task
            # This depends on whether conversation/modification follows. For now, assume codegen is last in this flow.
            # This is_last might need to be managed by a higher-level orchestrator.
            # For a simple non-conversational task, the last file generation IS the last step.
            is_task_last = is_last_codegen_step and not task['additional_properties'].get("is_conversation", False)

            await Agent.db.create_step(
                task['task_id'],
                f"{StepTypes.GENERATE_CODE}: {file_path_rel}", # More descriptive step name
                is_last=is_task_last, 
                additional_properties={"file_path_to_generate": file_path_rel}
            )
    step['status'] = "completed"
    return step


async def _generate_code_for_file(task: Dict, step: Dict) -> Dict: # Renamed from _generate_code
    context = _get_or_create_context(task)
    file_path_to_generate = step['additional_properties']["file_path_to_generate"]
    Agent.log(f"Task {task['task_id']}: Generating code for file: {file_path_to_generate} in {context.project_slug}")

    # generate_code is async
    code_content = await generate_code(
        prompt=context.original_prompt, 
        plan_details=context.shared_deps, 
        current_file=file_path_to_generate
    )
    step['output'] = f"Code generated for {file_path_to_generate}." # Full code might be too large
    context.codebase[file_path_to_generate] = code_content

    full_path_on_disk = os.path.join(context.output_dir, file_path_to_generate)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, write_file, full_path_on_disk, code_content)
    
    path_obj = Path(file_path_to_generate)
    await Agent.db.create_artifact(
        task_id=task['task_id'],
        step_id=step['step_id'],
        relative_path=str(path_obj.parent) if path_obj.parent != Path(".") else "",
        file_name=path_obj.name,
    )
    step['status'] = "completed"
    return step


async def _handle_conversation_step(task: Dict, step: Dict) -> Dict:
    context = _get_or_create_context(task)
    user_input = task.get('input')  # For conversation, task.input might be the latest user message

    if user_input is None:
        step['output'] = "No input provided for conversation."
        step['status'] = "error"
        step['is_last'] = True  # Cannot proceed
        return step

    # Ask user for intent using questionary
    intent_action = await questionary.select(
        f"For user input: '{user_input[:70]}...' - What is the intended action?",
        choices=[
            Choice("Trigger code modification process", value="modify"),
            Choice("Trigger question answering process", value="ask"),
            Choice("Handle as general conversation", value="chat"),
            Separator(),
            Choice("Discard this input (no further action)", value="cancel")
        ],
        qmark="⚙️"  # Simple qmark for API context
    ).ask_async()

    if intent_action is None or intent_action == "cancel":  # User pressed Ctrl+C or chose Cancel
        step['output'] = "User cancelled intent selection or chose to discard input."
        step['status'] = "completed" 
        step['is_last'] = True  # End this interaction branch
        return step

    # Log user input to conversation history (original input, before intent clarification)
    context.conversation_history.append({"role": "user", "content": user_input})

    context_dict = {
        "original_prompt": context.original_prompt,
        "project_slug": context.project_slug,
        "shared_deps": context.shared_deps,
        "file_paths": context.file_paths,
        "output_dir": context.output_dir,
        "conversation_history": context.conversation_history,
        "codebase": context.codebase,
        "file_tree": get_file_tree(context.output_dir)
    }

    step['is_last'] = False # Default, will be set true if no sub-steps

    if intent_action == "modify":
        Agent.log(f"Task {task['task_id']}: User selected 'Modify Code' intent for input: '{user_input[:50]}...'")
        await Agent.db.create_step(
            task['task_id'],
            StepTypes.MODIFY_CODE,
            additional_properties={"modification_request": user_input} # Pass original user input
        )
        step['output'] = "Modification intent confirmed. Creating modification step."
    elif intent_action == "ask":
        Agent.log(f"Task {task['task_id']}: User selected 'Ask Question' intent for input: '{user_input[:50]}...'")
        await Agent.db.create_step(
            task['task_id'],
            StepTypes.ANSWER_QUESTION,
            additional_properties={"question": user_input} # Pass original user input
        )
        step['output'] = "Question intent confirmed. Creating answering step."
    elif intent_action == "chat":
        Agent.log(f"Task {task['task_id']}: Handling general conversation intent for: '{user_input[:50]}...'")
        response = await handle_conversation(context_dict, user_input) # handle_conversation is async
        context.conversation_history.append({"role": "assistant", "content": response})
        step['output'] = response  # The assistant's direct response
        step['is_last'] = True # Direct response, this interaction might be done.
    
    step['status'] = "completed"
    return step


async def _modify_code_step(task: Dict, step: Dict) -> Dict: # Renamed
    context = _get_or_create_context(task)
    request = step['additional_properties']["modification_request"]
    Agent.log(f"Task {task['task_id']}: Modifying code for {context.project_slug} based on: {request}")
    
    context_dict = { # Prepare dict for the prompt function
        "file_paths": context.file_paths,
        "codebase": context.codebase,
        "output_dir": context.output_dir # For context, though not directly used in prompt usually
    }
    
    modified_files_result = await generate_modification(context_dict, request) # generate_modification is async
    
    if modified_files_result.get("error"):
        step['output'] = f"Modification failed: {modified_files_result['error']}"
        step['status'] = "error"
    else:
        modified_count = 0
        skipped_count = 0
        skipped_files_info = []
        loop = asyncio.get_event_loop()
        for file_path_rel, new_code_val in modified_files_result.items():
            if isinstance(new_code_val, str):
                context.codebase[file_path_rel] = new_code_val
                full_disk_path = os.path.join(context.output_dir, file_path_rel)
                await loop.run_in_executor(None, write_file, full_disk_path, new_code_val)
                modified_count += 1
                # Create artifact for modified file
                path_obj = Path(file_path_rel)
                await Agent.db.create_artifact(
                    task_id=task['task_id'],
                    step_id=step['step_id'],
                    relative_path=str(path_obj.parent) if path_obj.parent != Path(".") else "",
                    file_name=path_obj.name,
                )
            else:
                skipped_count += 1
                info = f"File '{file_path_rel}' (type: {type(new_code_val).__name__})"
                skipped_files_info.append(info)
                Agent.log(f"Task {task['task_id']}: LLM returned non-string content for file '{file_path_rel}' during modification. Type: {type(new_code_val)}. Skipping write.", level="WARNING")

        output_messages = []
        if modified_count > 0:
            output_messages.append(f"Modified {modified_count} files successfully for {context.project_slug}.")
        if skipped_count > 0:
            output_messages.append(f"Skipped writing {skipped_count} files due to non-string content: {', '.join(skipped_files_info)}.")
        
        if not output_messages: # Neither modified nor skipped (e.g. empty result dict)
             step['output'] = f"No modifications were specified or applied for {context.project_slug}."
        else:
            step['output'] = " ".join(output_messages)
            
    step['status'] = "completed"
    step['is_last'] = True # Assume modification is a terminal action for this interaction
    return step


async def _answer_question_step(task: Dict, step: Dict) -> Dict: # Renamed
    context = _get_or_create_context(task)
    question = step['additional_properties']["question"]
    Agent.log(f"Task {task['task_id']}: Answering question for {context.project_slug}: {question}")

    context_dict = { # Prepare dict for the prompt function
        "file_paths": context.file_paths,
        "codebase": context.codebase,
        "output_dir": context.output_dir # For context
    }
        
    answer = await answer_question(context_dict, question) # answer_question is async
    context.conversation_history.append({"role": "assistant", "content": answer}) # Log answer to history
    step['output'] = answer
    step['status'] = "completed"
    step['is_last'] = True # Assume answering is a terminal action for this interaction
    return step


async def task_handler(task: Dict) -> None: # Task is now a Dict
    Agent.log(f"Task {task['task_id']}: Received. Input: {task.get('input')[:50]}...")
    if not task.get('input'): # Check task['input']
        Agent.log(f"Task {task['task_id']}: No input provided, cannot proceed.", level="ERROR")
        # Here you might update task status to error in a real system
        return
    
    # First step for any new, non-conversational task is to define its root structure
    # If it's a conversation, this might have been done, or we might load existing.
    # This logic needs to be robust for resuming tasks vs. new tasks.
    
    # For a new task, always start by defining the project root.
    # If "is_conversation" is true, it implies we might be resuming or continuing.
    # The _get_or_create_context will handle loading if final_project_root points to existing.
    
    is_conversation_mode = task['additional_properties'].get("is_conversation", False)
    
    if not task['additional_properties'].get("final_project_root"):
        Agent.log(f"Task {task['task_id']}: No final_project_root found, creating DEFINE_PROJECT_ROOT step.")
        await Agent.db.create_step(task['task_id'], StepTypes.DEFINE_PROJECT_ROOT)
    elif is_conversation_mode:
        # If it's conversation and root is defined, context should be loadable.
        # The conversation step will handle what to do next.
        _get_or_create_context(task) # Ensure context is loaded/created
        Agent.log(f"Task {task['task_id']}: Conversation mode with existing root. Creating CONVERSATION step.")
        await Agent.db.create_step(task['task_id'], StepTypes.CONVERSATION)
    else: # Root is defined, not conversation mode -> implies resuming a plan-based task
        _get_or_create_context(task) # Ensure context is loaded/created
        Agent.log(f"Task {task['task_id']}: Resuming non-conversation task. Creating PLAN step (or next logical).")
        # This needs more sophisticated logic to find the *actual* next step if resuming.
        # For a simplified model, we'll assume if root is defined, plan is next if no other steps exist.
        # A real agent would have a step queue.
        # For this mock, let's assume task_handler just kicks off the first stage.
        await Agent.db.create_step(task['task_id'], StepTypes.PLAN)


async def step_handler(step: Dict): # Step is now a Dict
    task_id = step['task_id']
    task = await Agent.db.get_task(task_id) # Retrieve task data
    if not task:
        Agent.log(f"Task {task_id} not found for step {step['step_id']}. Cannot process.", level="ERROR")
        return None # Or raise error

    step_name_enum = None
    try:
        # Try to map step name to StepTypes enum if it's a direct match
        step_name_enum = StepTypes(step['name'])
    except ValueError:
        # If not a direct match, it might be a dynamic GENERATE_CODE step
        if step['name'].startswith(f"{StepTypes.GENERATE_CODE}:"):
            step_name_enum = StepTypes.GENERATE_CODE
        else:
            Agent.log(f"Task {task_id}: Unknown step name '{step['name']}' for step {step['step_id']}.", level="ERROR")
            step['status'] = "error"
            step['output'] = f"Unknown step name: {step['name']}"
            return step # Return modified step to update DB

    if step_name_enum == StepTypes.DEFINE_PROJECT_ROOT:
        return await _step_define_project_root(task, step)
    elif step_name_enum == StepTypes.PLAN:
        return await _generate_shared_deps(task, step)
    elif step_name_enum == StepTypes.SPECIFY_FILE_PATHS:
        return await _generate_file_paths(task, step)
    elif step_name_enum == StepTypes.CONVERSATION:
        return await _handle_conversation_step(task, step)
    elif step_name_enum == StepTypes.MODIFY_CODE:
        return await _modify_code_step(task, step)
    elif step_name_enum == StepTypes.ANSWER_QUESTION:
        return await _answer_question_step(task, step)
    elif step_name_enum == StepTypes.GENERATE_CODE: # Handles dynamic names like "generate_code: app.py"
        # Ensure file_path_to_generate is present for these steps
        if "file_path_to_generate" not in step.get('additional_properties', {}):
            Agent.log(f"Task {task_id}: Step {step['name']} is missing 'file_path_to_generate'.", level="ERROR")
            step['status'] = "error"
            step['output'] = "Missing 'file_path_to_generate' in step properties."
            return step
        return await _generate_code_for_file(task, step)
    else: # Should have been caught by unknown step name check
        Agent.log(f"Task {task_id}: Unhandled step type derived: '{step_name_enum}' for step '{step['name']}'.", level="ERROR")
        step['status'] = "error"
        step['output'] = f"Unhandled step type: {step_name_enum}"
        return step

# Setup and start the agent (for standalone testing of api.py)
if __name__ == "__main__":
    async def run_agent_example():
        # Configure logging level for Agent for this example run
        Agent.logger.setLevel(logging.DEBUG) 
        logging.getLogger('prompts').setLevel(logging.DEBUG)


        await Agent.setup_agent(task_handler, step_handler).start()
        # After start, the dummy task (if any) would have been processed.
        # You could add more tasks or inspect Agent.db here for testing.
        
        # Example of creating another task manually after start (if agent doesn't auto-poll)
        Agent.db._task_id_counter +=1
        new_task_id = str(Agent.db._task_id_counter)
        new_task = {
            "task_id": new_task_id,
            "input": "Develop a Flask app with a single route that returns a JSON greeting.",
            "additional_properties": {
                 "output_dir": os.path.abspath(os.path.join(os.getcwd(), "agent_api_test_projects")), # User-specified base for project folders
                 "is_conversation": False # This is a generative task
            }
        }
        Agent.db.tasks[new_task_id] = new_task
        Agent.log(f"Manually created task {new_task_id} for agent processing.")
        await Agent._process_task(new_task) # Manually trigger processing for this example

        # Example of a conversational task
        Agent.db._task_id_counter +=1
        conv_task_id = str(Agent.db._task_id_counter)
        conv_task = {
            "task_id": conv_task_id,
            "input": "Can you change the greeting to be 'Hello, AI World!'?", # This input will trigger the questionary prompt
            "additional_properties": {
                 "output_dir": os.path.abspath(os.path.join(os.getcwd(), "agent_api_test_projects", "flask-json-greeting-app")), # Assuming previous task created this
                 "is_conversation": True,
                 # Pre-populate context if resuming (for a real agent, this would be loaded)
                 # "final_project_root": os.path.abspath(os.path.join(os.getcwd(), "agent_api_test_projects", "flask-json-greeting-app")),
                 # "project_slug": "flask-json-greeting-app"
            }
        }
        # Ensure the project root exists for conversation task for _get_or_create_context
        conv_project_root = os.path.abspath(os.path.join(os.getcwd(), "agent_api_test_projects", "flask-json-greeting-app"))
        if not os.path.exists(conv_project_root):
            os.makedirs(conv_project_root, exist_ok=True)
            # Create a dummy .VIGI_dev_meta/project_context.json if needed for _get_or_create_context
            meta_dir = os.path.join(conv_project_root, ".VIGI_dev_meta")
            os.makedirs(meta_dir, exist_ok=True)
            with open(os.path.join(meta_dir, "project_context.json"), "w") as f:
                json.dump({
                    "original_prompt": "Flask app greeting", 
                    "project_slug": "flask-json-greeting-app",
                    "shared_deps": "Flask", 
                    "file_paths": ["app.py"], 
                    "output_dir": conv_project_root, 
                    "conversation_history": []
                }, f)
            with open(os.path.join(conv_project_root, "app.py"), "w") as f:
                f.write("# Initial app.py content\nprint('Hello User')")


        conv_task['additional_properties']['final_project_root'] = conv_project_root
        conv_task['additional_properties']['project_slug'] = "flask-json-greeting-app"


        Agent.db.tasks[conv_task_id] = conv_task
        Agent.log(f"Manually created conversational task {conv_task_id} for agent processing.")
        # This will call task_handler, which will create a CONVERSATION step.
        # Then _process_step will call _handle_conversation_step, which will use questionary.
        await Agent._process_task(conv_task)

        Agent.log("Agent example run complete. Inspect 'agent_workspace' and 'agent_api_test_projects'.")

    asyncio.run(run_agent_example())
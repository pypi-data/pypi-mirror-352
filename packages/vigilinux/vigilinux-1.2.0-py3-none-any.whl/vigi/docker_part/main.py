import json
import platform
import os
import re 
import subprocess
from typing import TypedDict, List, Dict, Any, Optional

import questionary
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

try:
    from . import config
    from . import docker_project_creator
except ImportError: 
    import config
    import docker_project_creator


llm = None
LLM_PROVIDER = "gemini" 

def docker_start():
    if platform.system() == "Windows":
        docker_path = r"C:\Program Files\Docker\Docker\Docker Desktop.exe"
        if os.path.exists(docker_path):
            try:
                subprocess.Popen([docker_path], shell=False, close_fds=True) 
                print("Attempting to start Docker Desktop...")
            except Exception as e:
                print(f"Failed to start Docker Desktop: {e}")
        else:
            print(f"Docker Desktop not found at expected path: {docker_path}")
            print("Please ensure Docker Desktop is installed or start it manually.")
    elif platform.system() == "Darwin": 
        try:
            subprocess.Popen(["open", "-a", "Docker"], shell=False, close_fds=True)
            print("Attempting to start Docker Desktop on macOS...")
        except Exception as e:
            print(f"Failed to start Docker Desktop on macOS: {e}")
    else: 
        print("Docker Desktop auto-start is primarily for Windows/macOS. On Linux, ensure the Docker daemon/service is running.")


def v_print(message, **kwargs):
    config.v_print(message, **kwargs)

def initialize_llm(provider_name: str):
    global llm 
    provider_name_lower = provider_name.lower()
    if provider_name_lower not in config.LLM_CONFIGS:
        available_providers = ", ".join(config.LLM_CONFIGS.keys())
        raise ValueError(
            f"Unsupported LLM provider: '{provider_name}'. "
            f"Supported providers in config.py: {available_providers}"
        )

    llm_settings = config.LLM_CONFIGS[provider_name_lower]
    api_key_env_var_name = llm_settings.get("api_key_env_var")

    if not api_key_env_var_name:
        raise ValueError(
            f"Configuration for '{provider_name_lower}' is missing the "
            f"'api_key_env_var' field in config.py."
        )

    actual_api_key = os.getenv(api_key_env_var_name)

    if not actual_api_key: 
        raise ValueError(
            f"API key environment variable '{api_key_env_var_name}' for provider "
            f"'{provider_name_lower}' is not set or is empty. Please ensure this "
            f"environment variable is set with your API key."
        )

    v_print(f"Initializing LLM: {provider_name_lower.upper()} with model {llm_settings['model_name']}")

    if provider_name_lower == "groq":
        llm = ChatGroq(
            model_name=llm_settings["model_name"],
            temperature=llm_settings["temperature"],
            api_key=actual_api_key
        )
    elif provider_name_lower == "gemini":
        llm = ChatGoogleGenerativeAI(
            model=llm_settings["model_name"],
            temperature=llm_settings["temperature"],
            google_api_key=actual_api_key
        )
    else:
        raise ValueError(
            f"LLM provider '{provider_name_lower}' initialization logic "
            f"not implemented, though defined in config."
        )
    return llm 

class DockerTask(BaseModel):
    intent: str = Field(description="The classified intent of the user's query related to Docker operations.")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters extracted for the Docker operation.")
    generated_command: Optional[str] = Field(default=None, description="The Docker command string generated, if any.")
    user_query: str = Field(description="The original user query.")

class AgentState(TypedDict):
    user_query: str
    identified_task: Optional[DockerTask]
    docker_command: Optional[str] 
    command_output: Optional[str]
    error_message: Optional[str]
    history: List[Any] 
    image_search_keyword: Optional[str]
    image_options: Optional[List[Dict[str, Any]]]
    selected_image_for_pull: Optional[str]
    final_response_for_user: Optional[str]
    
    project_directory: Optional[str]
    dockerfile_content: Optional[str]
    dockerignore_content: Optional[str]
    generated_build_command: Optional[str] 
    generated_run_command: Optional[str]
    selected_image_to_run: Optional[str] # For RUN_EXISTING_IMAGE flow


def parse_docker_search_output(search_output_str: str) -> List[Dict[str, Any]]:
    images = []
    if not search_output_str.strip():
        return []
    for line in search_output_str.strip().split('\n'):
        try:
            img_data = json.loads(line)
            try:
                img_data['StarCount'] = int(img_data.get('StarCount', 0))
            except ValueError:
                img_data['StarCount'] = 0
            images.append(img_data)
        except json.JSONDecodeError:
            v_print(f"Warning: Could not parse line from docker search: {line}")
    return images

def get_image_platforms_from_inspect(inspect_output_str: str) -> List[str]:
    platforms = []
    try:
        data = json.loads(inspect_output_str)
        if "manifests" in data and isinstance(data["manifests"], list):
            for manifest_descriptor in data["manifests"]:
                platform_info = manifest_descriptor.get("platform")
                if platform_info and isinstance(platform_info, dict):
                    os_val = platform_info.get("os")
                    arch_val = platform_info.get("architecture")
                    if os_val and arch_val:
                        platforms.append(f"{os_val}/{arch_val}")
        elif "platform" in data and isinstance(data["platform"], dict): 
            platform_info = data["platform"]
            os_val = platform_info.get("os")
            arch_val = platform_info.get("architecture")
            if os_val and arch_val:
                platforms.append(f"{os_val}/{arch_val}")
        elif "architecture" in data and "os" in data: 
            os_val = data.get("os")
            arch_val = data.get("architecture")
            if os_val and arch_val:
                platforms.append(f"{os_val}/{arch_val}")
        else:
            v_print(f"Warning: Manifest data does not contain expected 'manifests' list or 'platform' dict: {str(data)[:500]}")
    except json.JSONDecodeError as e:
        v_print(f"JSONDecodeError in get_image_platforms_from_inspect: {e}. Input: {inspect_output_str[:500]}")
    except Exception as e: 
        v_print(f"Unexpected error in get_image_platforms_from_inspect: {e}. Input: {inspect_output_str[:500]}", exc_info=True)
    return list(set(platforms))


def classify_intent_node(state: AgentState) -> AgentState:
    v_print("--- Classifying Intent ---")
    user_query = state["user_query"]

    if llm is None:
        error_msg = "LLM is not available for intent classification."
        v_print(f"Error in classify_intent_node: {error_msg}")
        return {**state, "error_message": error_msg, "identified_task": DockerTask(intent="UNKNOWN", user_query=user_query)}

    system_prompt_content = """You are an expert Docker assistant. Your task is to classify the user's intent and extract relevant parameters for Docker operations.
You MUST respond with ONLY a single JSON object. Do NOT include any explanations, conversational text, or markdown formatting outside of the JSON object itself.
If the user asks for multiple actions (e.g., "pull image X and then run it"), identify the first logical Docker operation. For "pull image X and then run it", the intent should be related to pulling image X.

Possible intents and parameters:
- SEARCH_PULL_IMAGE_INTERACTIVE: User wants to search and then pull an image.
  - parameters: {"image_keyword": "search_term"}
- PULL_IMAGE: User wants to pull a specific image.
  - parameters: {"image_name": "name", "tag": "optional_tag"}
- CREATE_DOCKER_PROJECT: User wants to create Dockerfile and .dockerignore for the current working directory.
  - parameters: {}
- RUN_EXISTING_IMAGE: User wants to run an existing local image.
  - parameters: {"image_name_query": "user's term for image", "run_options_raw": "e.g., -p 80:8000 --name myapp -it"}
- UNKNOWN: If intent cannot be determined.
  - parameters: {}

Example for 'pull the redis image and run it':
{
  "intent": "SEARCH_PULL_IMAGE_INTERACTIVE",
  "parameters": { "image_keyword": "redis" }
}
Example for 'help me dockerize my current project' or 'create a dockerfile':
{
  "intent": "CREATE_DOCKER_PROJECT",
  "parameters": {}
}
Example for 'run my custom-built nginx image with port 8080 mapped to 80':
{
  "intent": "RUN_EXISTING_IMAGE",
  "parameters": { "image_name_query": "custom-built nginx", "run_options_raw": "-p 8080:80" }
}
Example for 'run redis':
{
  "intent": "RUN_EXISTING_IMAGE",
  "parameters": { "image_name_query": "redis", "run_options_raw": "" }
}
Now, classify the following user query. Remember, ONLY the JSON object."""

    prompt_messages = [
        SystemMessage(content=system_prompt_content),
        HumanMessage(content=user_query)
    ]
    
    raw_llm_response_content = ""
    json_str_to_parse = ""

    try:
        response = llm.invoke(prompt_messages)
        raw_llm_response_content = response.content
        v_print(f"LLM Full Raw Response (content property): >>>{raw_llm_response_content}<<<")
        
        content_to_process = raw_llm_response_content.strip()
        v_print(f"LLM Content to Process (stripped): >>>{content_to_process}<<<")

        match_markdown = re.search(r"```json\s*(\{[\s\S]+?\})\s*```", content_to_process, re.DOTALL)
        
        if match_markdown:
            json_str_to_parse = match_markdown.group(1).strip()
            v_print(f"Extracted JSON from markdown block: >>>{json_str_to_parse}<<<")
        elif content_to_process.startswith('{') and content_to_process.endswith('}'):
            json_str_to_parse = content_to_process
            v_print(f"No markdown block. Assuming entire stripped response is JSON: >>>{json_str_to_parse}<<<")
        else:
            json_str_to_parse = content_to_process 
            v_print(
                "Warning: Response not markdown-fenced and not clearly a JSON object by start/end. "
                f"Attempting to parse stripped response as is: >>>{json_str_to_parse}<<<"
            )

        if not json_str_to_parse.strip():
             v_print(
                f"Error: Extracted JSON string is empty or whitespace only after processing. "
                f"Original LLM content: >>>{raw_llm_response_content}<<<"
            )
             raise json.JSONDecodeError("Extracted JSON string is empty after processing.", raw_llm_response_content, 0)

        task_data = json.loads(json_str_to_parse)
        if "user_query" not in task_data:
            task_data["user_query"] = user_query
            
        identified_task = DockerTask(**task_data)
        
        return {**state, "identified_task": identified_task, "error_message": None}
    
    except json.JSONDecodeError as e:
        v_print(
            f"JSONDecodeError: {e}\n"
            f"Problematic JSON string attempted for parsing: >>>{json_str_to_parse}<<<\n"
            f"LLM Full Raw Response (content property): >>>{raw_llm_response_content}<<<"
        )
        error_msg = (
            f"LLM output could not be parsed as JSON. Error: {e}. "
            f"Parser input (approx): '{json_str_to_parse[:200]}...'. "
            f"LLM raw (approx): '{raw_llm_response_content[:200]}...'"
        )
        return {**state, "error_message": error_msg, "identified_task": DockerTask(intent="UNKNOWN", user_query=user_query)}
    except Exception as e:
        v_print(f"General error in classify_intent_node: {e}", exc_info=True)
        llm_resp_for_log = raw_llm_response_content if 'raw_llm_response_content' in locals() and raw_llm_response_content else "Not available or empty"
        v_print(f"LLM Full Raw Response (at time of general error): >>>{llm_resp_for_log}<<<")
        return {**state, "error_message": str(e), "identified_task": DockerTask(intent="UNKNOWN", user_query=user_query)}


def interactive_image_search_and_pull_node(state: AgentState) -> AgentState:
    v_print("--- Interactive Image Search and Pull ---")
    task = state.get("identified_task")
    if not task or not task.parameters.get("image_keyword"):
        return {**state, "error_message": "Image keyword not provided for search."}

    keyword = task.parameters["image_keyword"]
    v_print(f"Searching for Docker images with keyword: {keyword}")

    try:
        sys_info_proc = subprocess.run(
            ["docker", "system", "info", "--format", "{{.OSType}}/{{.Architecture}}"],
            capture_output=True, text=True, check=True, timeout=30
        )
        system_platform = sys_info_proc.stdout.strip().lower()
        if system_platform == "linux/x86_64":
            system_platform = "linux/amd64"
        if not system_platform or '/' not in system_platform:
            raise ValueError(f"Could not determine valid system platform: '{system_platform}'")
        v_print(f"Current system platform (Docker Engine): {system_platform}")
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError) as e:
        err_msg = f"Failed to get system platform: {e}"
        print(f"ERROR: {err_msg}"); v_print(err_msg)
        return {**state, "error_message": err_msg}
    except FileNotFoundError:
        err_msg = "Docker command not found. Cannot determine system platform."
        print(f"ERROR: {err_msg}"); return {**state, "error_message": err_msg}

    try:
        search_proc = subprocess.run(
            ["docker", "search", keyword, "--format", "{{json .}}", "--no-trunc", "--limit", "25"],
            capture_output=True, text=True, check=True, timeout=60
        )
        search_results = parse_docker_search_output(search_proc.stdout)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        err_msg = f"Failed to search Docker Hub for '{keyword}': {e.stderr or e}"
        print(f"ERROR: {err_msg}"); v_print(err_msg)
        return {**state, "error_message": err_msg, "command_output": e.stdout if hasattr(e, 'stdout') else ""}
    except FileNotFoundError:
        err_msg = "Docker command not found. Cannot search for images."
        print(f"ERROR: {err_msg}"); return {**state, "error_message": err_msg}

    if not search_results:
        msg = f"No images found for keyword '{keyword}'."
        print(msg); return {**state, "error_message": msg}

    sorted_images = sorted(search_results, key=lambda img: img.get('StarCount', 0), reverse=True)
    image_options_to_present = sorted_images[:5] 
    
    compatible_image_pulled = False
    pulled_image_name = None
    pull_attempt_output = None 
    final_error_message = None

    while image_options_to_present and not compatible_image_pulled:
        choices = [
            questionary.Choice(
                title=(
                    f"{img['Name']} (Stars: {img.get('StarCount', 0)}) - "
                    f"{str(img.get('Description', 'No description')).strip()[:70]}..."
                ),
                value=img['Name']
            ) for img in image_options_to_present
        ]
        choices.extend([
            questionary.Separator(),
            questionary.Choice(title="[Cancel Selection]", value="##CANCEL##")
        ])
        
        selected_image_name_ans = questionary.select(
            "Select a Docker image to inspect and potentially pull:",
            choices=choices,
            use_shortcuts=True
        ).ask()

        if selected_image_name_ans is None or selected_image_name_ans == "##CANCEL##":
            final_error_message = "Image selection cancelled by user."
            print(final_error_message); break
        
        selected_image_name = selected_image_name_ans # Ensure it's not None for processing

        print(f"\nInspecting {selected_image_name} for compatibility with {system_platform}...")
        is_compatible = False
        try:
            inspect_command = ["docker", "buildx", "imagetools", "inspect", "--raw", selected_image_name]
            v_print(f"Executing inspect command: {' '.join(inspect_command)}")
            inspect_proc = subprocess.run(
                inspect_command, capture_output=True, text=True, check=True, timeout=60
            )
            raw_manifest_json_str = inspect_proc.stdout.strip()
            v_print(f"Raw inspect output for {selected_image_name}:\n{raw_manifest_json_str[:500]}...")

            image_platforms = get_image_platforms_from_inspect(raw_manifest_json_str)
            v_print(f"Parsed platforms for {selected_image_name}: {image_platforms}")

            image_platforms_lower = [p.lower() for p in image_platforms]

            if not image_platforms_lower:
                print(f"Warning: Could not determine any supported platforms for {selected_image_name} from inspect output. Assuming incompatible.")
            else:
                is_compatible = system_platform in image_platforms_lower
        
        except subprocess.CalledProcessError as e:
            err_msg = f"Failed to inspect image {selected_image_name}: {e.stderr or e.stdout or e}"
            print(f"ERROR: {err_msg}")
            v_print(f"Inspect command failed. Stderr: {e.stderr}. Stdout: {e.stdout}")
            image_options_to_present = [img for img in image_options_to_present if img['Name'] != selected_image_name]
            if not image_options_to_present:
                final_error_message = "No remaining images to try after inspection error."
            continue 
        except FileNotFoundError: 
            err_msg = "Docker command (buildx imagetools) not found. Cannot inspect image."
            print(f"ERROR: {err_msg}"); final_error_message = err_msg; break
        except Exception as e: 
            err_msg = f"Unexpected error during inspection of {selected_image_name}: {e}"
            print(f"ERROR: {err_msg}")
            v_print(err_msg, exc_info=True)
            image_options_to_present = [img for img in image_options_to_present if img['Name'] != selected_image_name]
            if not image_options_to_present:
                final_error_message = "No remaining images to try after inspection processing error."
            continue

        if is_compatible:
            print(f"Image {selected_image_name} IS compatible with your system ({system_platform}).")
            if questionary.confirm(f"Pull image {selected_image_name}?", default=True).ask():
                print(f"Attempting to pull {selected_image_name}...")
                try:
                    pull_proc = subprocess.run(
                        ["docker", "pull", selected_image_name],
                        capture_output=True, text=True, check=True, timeout=300
                    )
                    pull_attempt_output = pull_proc.stdout
                    print(f"Successfully pulled {selected_image_name}!"); 
                    v_print(f"Pull output:\n{pull_attempt_output}")
                    compatible_image_pulled = True
                    pulled_image_name = selected_image_name
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                    err_msg = f"Failed to pull {selected_image_name}: {e.stderr or e}"
                    pull_attempt_output = (e.stdout if hasattr(e, 'stdout') else "") + "\n" + (e.stderr if hasattr(e, 'stderr') else str(e))
                    print(f"ERROR: {err_msg}")
                except FileNotFoundError:
                    err_msg = "Docker command not found. Cannot pull image."
                    print(f"ERROR: {err_msg}"); final_error_message = err_msg; break
            else:
                print(f"Skipping pull for {selected_image_name}.")
                image_options_to_present = [img for img in image_options_to_present if img['Name'] != selected_image_name]
                if not image_options_to_present: final_error_message = "No other images to select after skipping pull."
        else: 
            print(f"Image {selected_image_name} is NOT compatible with your system ({system_platform}).")
            print(f"Supported platforms for {selected_image_name}: {image_platforms_lower or ['Could not determine']}")
            image_options_to_present = [img for img in image_options_to_present if img['Name'] != selected_image_name]
            if not image_options_to_present:
                final_error_message = "No compatible images found among the top choices, and no other options remain."
                print(final_error_message)

    if compatible_image_pulled and pulled_image_name:
        return {
            **state,
            "docker_command": f"docker pull {pulled_image_name}", 
            "command_output": pull_attempt_output or f"Successfully pulled {pulled_image_name}.",
            "error_message": None,
            "selected_image_for_pull": pulled_image_name
        }
    else:
        if not final_error_message:
            final_error_message = "No compatible image was selected or pulled."
        return {
            **state,
            "docker_command": None,
            "command_output": pull_attempt_output, 
            "error_message": final_error_message,
            "selected_image_for_pull": None
        }

def docker_project_creation_node(state: AgentState) -> AgentState:
    v_print("--- Interactive Docker Project Creation ---")
    current_dir = os.getcwd()
    
    try:
        project_data = docker_project_creator.create_docker_project_interactive(current_dir, v_print)
        
        actions_log = project_data.get("actions_log", [])
        
        build_cmd_from_creator = project_data.get("build_command")
        run_cmd_from_creator = project_data.get("run_command")
        
        # --- Ask to Build Image ---
        if build_cmd_from_creator and project_data.get("dockerfile_path"): # Only if Dockerfile was actually created
            if questionary.confirm(
                f"Dockerfile created. Do you want to build the Docker image now using:\n  `{build_cmd_from_creator}`?",
                default=True
            ).ask():
                v_print(f"User opted to build. Executing: {build_cmd_from_creator} in {current_dir}")
                print(f"Attempting to build image... Command: {build_cmd_from_creator}")
                try:
                    process = subprocess.run(
                        build_cmd_from_creator, shell=True, capture_output=True, text=True, 
                        timeout=600, check=False, cwd=current_dir
                    )
                    if process.returncode == 0:
                        msg = f"Image built successfully using: `{build_cmd_from_creator}`"
                        print(msg)
                        actions_log.append(msg)
                        if process.stdout.strip(): 
                            actions_log.append(f"Build output:\n{process.stdout.strip()}")
                            v_print(f"Build stdout:\n{process.stdout.strip()}")
                        
                        # --- Ask to Run Container ---
                        if run_cmd_from_creator:
                            if questionary.confirm(
                                f"Build successful. Do you want to run the container now using:\n  `{run_cmd_from_creator}`?",
                                default=True
                            ).ask():
                                v_print(f"User opted to run. Executing: {run_cmd_from_creator}")
                                print(f"Attempting to run container... Command: {run_cmd_from_creator}")
                                try:
                                    run_process = subprocess.run(
                                        run_cmd_from_creator, shell=True, capture_output=True, 
                                        text=True, timeout=120, check=False # cwd not usually needed for run
                                    )
                                    if run_process.returncode == 0:
                                        msg_run = f"Container started successfully using: `{run_cmd_from_creator}`"
                                        print(msg_run)
                                        actions_log.append(msg_run)
                                        if run_process.stdout.strip():
                                            actions_log.append(f"Run output (container ID for -d):\n{run_process.stdout.strip()}")
                                            v_print(f"Run stdout:\n{run_process.stdout.strip()}")
                                    else:
                                        err_msg_run = f"Failed to run container. Command: `{run_cmd_from_creator}`.\nError: {run_process.stderr.strip() or run_process.stdout.strip() or f'Exit code {run_process.returncode}'}"
                                        print(f"ERROR: {err_msg_run}")
                                        actions_log.append(err_msg_run)
                                except Exception as e_run:
                                    err_msg_run = f"Exception running container command '{run_cmd_from_creator}': {e_run}"
                                    print(f"ERROR: {err_msg_run}")
                                    actions_log.append(err_msg_run)
                            else:
                                actions_log.append(f"Container run with `{run_cmd_from_creator}` skipped by user.")
                                print("Container run skipped.")
                    else: # Build success, but no run_cmd_from_creator (should not happen if build_cmd was there)
                        actions_log.append("Build successful, but no run command was suggested by creator.")


                except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e_build_proc:
                    err_msg_build = f"Failed to build image. Command: `{build_cmd_from_creator}`.\nError: {e_build_proc.stderr.strip() if e_build_proc.stderr else (e_build_proc.stdout.strip() if e_build_proc.stdout else str(e_build_proc))}"
                    print(f"ERROR: {err_msg_build}")
                    actions_log.append(err_msg_build)
                except Exception as e_build:
                    err_msg_build = f"Exception building image with command '{build_cmd_from_creator}': {e_build}"
                    print(f"ERROR: {err_msg_build}")
                    actions_log.append(err_msg_build)
                    v_print(err_msg_build, exc_info=True)
            else:
                actions_log.append(f"Image build with `{build_cmd_from_creator}` skipped by user.")
                print("Image build skipped.")
        elif build_cmd_from_creator: # Dockerfile was not created, but build_cmd exists
             actions_log.append("Image build skipped as Dockerfile was not created/saved.")


        # --- Compile final summary ---
        # Start with the summary from the creator (file paths, suggested commands)
        final_summary_parts = [project_data.get("summary_message","Project setup summary not available.")]
        
        # Add logs of actions taken (file creation, build, run)
        if actions_log: # actions_log now includes build/run attempts from this node
            final_summary_parts.append("\n--- Actions Log ---")
            final_summary_parts.extend(actions_log) # creator log already in actions_log
        
        return {
            **state,
            "project_directory": current_dir,
            "dockerfile_content": project_data.get("dockerfile_content"),
            "dockerignore_content": project_data.get("dockerignore_content"),
            "generated_build_command": build_cmd_from_creator, # Store for final_result_node
            "generated_run_command": run_cmd_from_creator,   # Store for final_result_node
            "command_output": "\n".join(final_summary_parts), # This is the main result of this node
            "error_message": project_data.get("error_message"), # Preserve original file creation errors
            "docker_command": None # This node doesn't set a command for execute_command_node
        }
    except Exception as e:
        v_print(f"Error during Docker project creation process: {e}", exc_info=True)
        print(f"ERROR: An unexpected issue occurred while setting up the Docker project: {e}")
        return {
            **state,
            "project_directory": current_dir,
            "error_message": f"Failed to complete Docker project setup: {e}",
            "command_output": "Docker project setup was interrupted by an unexpected error."
        }

def parse_docker_images_json_output(images_output_str: str) -> List[Dict[str, Any]]:
    images = []
    if not images_output_str.strip():
        return []
    for line in images_output_str.strip().split('\n'):
        try:
            img_data = json.loads(line)
            img_data.setdefault('Repository', '<???>')
            img_data.setdefault('Tag', '<???>')
            img_data.setdefault('ID', '<???>')
            img_data.setdefault('Size', '<???>')
            images.append(img_data)
        except json.JSONDecodeError:
            v_print(f"Warning: Could not parse line from 'docker images': {line}")
    return images

def find_image_and_prepare_run_node(state: AgentState) -> AgentState:
    v_print("--- Find Image and Prepare Run Command ---")
    task = state.get("identified_task")
    if not task or task.intent != "RUN_EXISTING_IMAGE":
        return {**state, "error_message": "Task not appropriate for finding and running image."}

    image_name_query = task.parameters.get("image_name_query", "").lower()
    run_options_raw = task.parameters.get("run_options_raw", "")

    if not image_name_query:
        return {**state, "error_message": "No image name provided to search for."}

    try:
        images_proc = subprocess.run(
            ["docker", "images", "--format", "{{json .}}"],
            capture_output=True, text=True, check=True, timeout=30
        )
        local_images_raw = images_proc.stdout
        local_images = parse_docker_images_json_output(local_images_raw)

    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        err_msg = f"Failed to list local Docker images: {e.stderr or e.stdout or e}"
        print(f"ERROR: {err_msg}"); v_print(err_msg)
        return {**state, "error_message": err_msg}
    except FileNotFoundError:
        err_msg = "Docker command not found. Cannot list local images."
        print(f"ERROR: {err_msg}"); return {**state, "error_message": err_msg}

    if not local_images:
        msg = "No local Docker images found. You might need to pull or build an image first."
        print(msg); return {**state, "error_message": msg}

    matched_images = []
    for img in local_images:
        repo = img.get("Repository", "").lower()
        tag = img.get("Tag", "").lower()
        full_name_tag = f"{repo}:{tag}"
        
        if image_name_query == full_name_tag or image_name_query == repo:
            matched_images.append(img)
        elif image_name_query in repo and not any(m['Repository'] == repo and m['Tag'] == tag for m in matched_images):
             matched_images.append(img)
    
    if not matched_images: # Broader search if primary matches failed
        for img in local_images:
            repo_tag = f"{img.get('Repository', '').lower()}:{img.get('Tag', '').lower()}"
            if image_name_query in repo_tag and not any(m['Repository'] == img['Repository'] and m['Tag'] == img['Tag'] for m in matched_images):
                matched_images.append(img)

    unique_image_refs = set()
    unique_matched_images = []
    for img in matched_images:
        ref = (img.get("Repository"), img.get("Tag"))
        if ref not in unique_image_refs:
            unique_image_refs.add(ref)
            unique_matched_images.append(img)
    matched_images = unique_matched_images

    selected_image_full_name = None
    if not matched_images:
        msg = f"No local image found matching '{image_name_query}'. Try pulling one (e.g., 'pull {image_name_query}') or check spelling."
        print(msg); return {**state, "error_message": msg}
    elif len(matched_images) == 1:
        img = matched_images[0]
        selected_image_full_name = f"{img['Repository']}:{img['Tag']}"
        print(f"Found unique local image: {selected_image_full_name}")
    else:
        print(f"Found multiple local images matching '{image_name_query}':")
        choices = [
            questionary.Choice(
                title=f"{img['Repository']}:{img['Tag']} (ID: {img['ID'][:12]}, Size: {img['Size']})",
                value=f"{img['Repository']}:{img['Tag']}"
            ) for img in matched_images
        ]
        choices.append(questionary.Choice(title="[Cancel Selection]", value="##CANCEL##"))
        
        user_choice_ans = questionary.select(
            "Select the image you want to run:",
            choices=choices
        ).ask()

        if user_choice_ans is None or user_choice_ans == "##CANCEL##":
            msg = "Image selection cancelled."
            print(msg); return {**state, "error_message": msg}
        selected_image_full_name = user_choice_ans
    
    prompt_message = (
        f"Image to run: {selected_image_full_name}\n"
        f"Initial run options from your query: '{run_options_raw}'\n"
        "Enter/Confirm Docker run options (e.g., '-p 8080:80 --name myapp -d'), or leave blank for current:"
    )
    user_added_options_ans = questionary.text(prompt_message, default=run_options_raw).ask()
    
    if user_added_options_ans is None: # User pressed Esc
         return {**state, "error_message": "Run command setup cancelled by user."}

    final_run_options = user_added_options_ans.strip()
    final_command = f"docker run {final_run_options} {selected_image_full_name}".strip().replace("  ", " ") # Clean up spaces
    
    print(f"Prepared Docker command: {final_command}")
    
    return {
        **state, 
        "selected_image_to_run": selected_image_full_name, 
        "docker_command": final_command,
        "error_message": None
    }

def generate_command_node(state: AgentState) -> AgentState:
    v_print("--- Generating Command (for non-interactive or simple tasks) ---")
    task = state.get("identified_task")

    if not task or task.intent == "UNKNOWN":
        return {
            **state,
            "docker_command": None,
            "error_message": state.get("error_message", "Task intent is unknown or task not identified.")
        }

    # These intents have their own command generation/execution logic or are interactive.
    if task.intent in ["SEARCH_PULL_IMAGE_INTERACTIVE", "CREATE_DOCKER_PROJECT", "RUN_EXISTING_IMAGE"]:
        if task.intent == "SEARCH_PULL_IMAGE_INTERACTIVE" and state.get("selected_image_for_pull"):
             # Command already set by interactive_image_search_and_pull_node (implicitly docker pull)
             return state 
        # For CREATE_DOCKER_PROJECT, commands are handled within its node.
        # For RUN_EXISTING_IMAGE, command is set by find_image_and_prepare_run_node.
        return {**state, "docker_command": state.get("docker_command")} # Pass through if already set


    params = task.parameters
    command_parts = ["docker"]
    try:
        if task.intent == "PULL_IMAGE": # Direct pull intent
            if not params.get("image_name"):
                return {**state, "error_message": "Image name required for PULL_IMAGE intent."}
            command_parts.append("pull")
            image_name = params["image_name"]
            if params.get("tag"):
                image_name += f":{params['tag']}"
            command_parts.append(image_name)
        else:
            # If we reach here with an unhandled intent, it's an issue.
            return {**state, "error_message": f"Command generation not implemented for intent: {task.intent}"}
        
        final_command_str = " ".join(command_parts)
        return {**state, "docker_command": final_command_str, "error_message": None}

    except KeyError as e:
        error_msg = f"Missing parameter {e} for intent {task.intent}."
        v_print(f"Error in generate_command_node: {error_msg}")
        return {**state, "error_message": error_msg}
    except Exception as e:
        v_print(f"Unexpected error in generate_command_node: {e}", exc_info=True)
        return {**state, "error_message": str(e)}


def execute_command_node(state: AgentState) -> AgentState:
    v_print("--- Executing Command ---")
    command = state.get("docker_command") 

    if not command: 
        v_print("No 'docker_command' found in state to execute.")
        return {
            **state,
            "command_output": state.get("command_output", "No command was specified for execution."), 
            "error_message": state.get("error_message")
        }
    
    v_print(f"Executing: {command}")
    try:
        process = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300, check=False) # Increased timeout
        
        if process.returncode == 0:
            output = process.stdout.strip() if process.stdout else "Command executed successfully with no output."
            v_print(f"Command success. Output:\n{output}")
            return {**state, "command_output": output, "error_message": None}
        else:
            error_output = process.stderr.strip() if process.stderr else "Command failed with no specific error output."
            full_output = f"Stdout (if any):\n{process.stdout.strip()}\nStderr:\n{error_output}".strip()
            v_print(f"Command failed. Exit code: {process.returncode}. Full output:\n{full_output}")
            return {**state, "command_output": full_output, "error_message": error_output or f"Command '{command}' failed with exit code {process.returncode}."}

    except subprocess.TimeoutExpired:
        timeout_msg = f"Command '{command}' timed out."
        v_print(timeout_msg)
        return {**state, "error_message": timeout_msg, "command_output": "Operation timed out."}
    except FileNotFoundError: 
        fnf_msg = "Docker command not found. Please ensure Docker is installed and in your PATH."
        v_print(f"{fnf_msg} (while trying to execute: {command})")
        return {**state, "error_message": fnf_msg}
    except Exception as e:
        exec_err_msg = f"Error executing command '{command}': {e}"
        v_print(exec_err_msg, exc_info=True)
        return {**state, "error_message": str(e), "command_output": f"Error during execution: {e}"}


def route_after_classification(state: AgentState) -> str:
    v_print("--- Routing after classification ---")
    if state.get("error_message"):
        v_print(f"Routing to final_result_node due to error: {state['error_message']}")
        return "final_result_node"
    
    task = state.get("identified_task")
    if not task: 
        state["error_message"] = "Task classification failed to produce a task object."
        v_print("Routing to final_result_node: No task object.")
        return "final_result_node"

    v_print(f"Identified intent: {task.intent}")
    if task.intent == "SEARCH_PULL_IMAGE_INTERACTIVE":
        if not task.parameters or not task.parameters.get("image_keyword"):
            state["error_message"] = "Cannot perform interactive search: Image keyword missing."
            v_print(f"Routing to final_result_node: {state['error_message']}")
            return "final_result_node"
        v_print("Routing to interactive_image_search_node.")
        return "interactive_image_search_node"
    elif task.intent == "CREATE_DOCKER_PROJECT":
        v_print("Routing to docker_project_creation_node.")
        return "docker_project_creation_node"
    elif task.intent == "RUN_EXISTING_IMAGE":
        v_print("Routing to find_image_and_prepare_run_node.")
        return "find_image_and_prepare_run_node"
    elif task.intent == "UNKNOWN":
        state["error_message"] = (
            state.get("error_message") or 
            f"I couldn't determine a specific Docker action for: '{state.get('user_query', 'your request')}'. Please try rephrasing."
        )
        v_print("Routing to final_result_node: Intent is UNKNOWN.")
        return "final_result_node"
    elif task.intent == "PULL_IMAGE": 
        v_print("Routing to generate_command_node for PULL_IMAGE.")
        return "generate_command_node"
    else: 
        state["error_message"] = f"Routing not defined for intent: {task.intent}."
        v_print(f"Routing to final_result_node: {state['error_message']}")
        return "final_result_node"


def should_execute_command(state: AgentState) -> str:
    v_print("--- Checking if command should be executed ---")
    if state.get("error_message"): # Error from a previous node (e.g., find_image, generate_command)
        v_print(f"Routing to final_result_node due to error before execution: {state['error_message']}")
        return "final_result_node"
    
    docker_command = state.get("docker_command") 
    
    # CREATE_DOCKER_PROJECT handles its own optional command executions (build/run)
    # and its main output is the summary from project_data.
    identified_task = state.get("identified_task")
    if identified_task and identified_task.intent == "CREATE_DOCKER_PROJECT":
        v_print("Routing to final_result_node after Docker project creation (its own node handles build/run).")
        return "final_result_node"

    if not docker_command:
        # If no command and no error, it might be an interactive flow that completed
        # or an intent that doesn't generate a command for this path.
        if not state.get("error_message") and not state.get("command_output"):
             state["error_message"] = "No Docker command was generated or selected for execution by this path."
        v_print(f"Routing to final_result_node: No command to execute from this path. Error: {state.get('error_message')}, Output: {state.get('command_output')}")
        return "final_result_node"
    
    v_print(f"Proceeding to execute_command_node for command: {docker_command}")
    return "execute_command_node"


def final_result_node(state: AgentState) -> AgentState:
    v_print("--- Final Result Node ---")
    user_query = state.get("user_query", "Unknown query")
    identified_task = state.get("identified_task")
    command_executed_by_agent = state.get("docker_command") # Command that execute_command_node ran
    output = state.get("command_output") 
    error = state.get("error_message")
    
    final_message_parts = []

    if error:
        final_message_parts.append(f"Error processing your request ('{user_query}'): {error}")
        # If there's also output, it might be from a failed command or partial success
        if output and output.strip() and (error not in output if error and output else True):
             final_message_parts.append(f"Details/Output (if any):\n{output.strip()}")

    elif identified_task and identified_task.intent == "CREATE_DOCKER_PROJECT":
        # This node's output is primarily the summary from project_data, including build/run actions
        final_message_parts.append(f"For your request: '{user_query}' (Dockerize Project)")
        if output and output.strip(): # output here is the comprehensive summary from docker_project_creation_node
            final_message_parts.append(f"\n{output.strip()}")
        else:
            final_message_parts.append("Docker project setup process completed (or was skipped/cancelled).")
        # Suggested commands are part of the output string already from docker_project_creation_node

    elif identified_task and identified_task.intent == "RUN_EXISTING_IMAGE":
        final_message_parts.append(f"For your request: '{user_query}' (Run Existing Image)")
        selected_img = state.get('selected_image_to_run', 'Not specified')
        final_message_parts.append(f"Image: {selected_img}")
        if command_executed_by_agent:
             final_message_parts.append(f"Attempted command: `{command_executed_by_agent}`")
        if output and output.strip():
            final_message_parts.append(f"Execution Output:\n{output.strip()}")
        else: # Could be -d or just no output if successful
            final_message_parts.append("Command submitted to Docker. If run in detached mode (-d), check `docker ps` for status.")
            
    elif command_executed_by_agent: # Covers PULL_IMAGE or other direct commands
        final_message_parts.append(f"For your request: '{user_query}'")
        if identified_task:
             final_message_parts.append(f"Identified task: {identified_task.intent}")
             if identified_task.intent == "SEARCH_PULL_IMAGE_INTERACTIVE" and state.get("selected_image_for_pull"):
                 final_message_parts.append(f"Selected image for pull: {state['selected_image_for_pull']}")
             elif identified_task.parameters:
                 display_params = {k: v for k, v in identified_task.parameters.items() if k != "user_query"}
                 if display_params:
                     params_str = ", ".join(f"{k}: {v}" for k, v in display_params.items())
                     final_message_parts.append(f"Parameters: {params_str}")
        
        final_message_parts.append(f"Executed command: `{command_executed_by_agent}`")
        if output and output.strip():
            final_message_parts.append(f"Execution Output:\n{output.strip()}")
        else:
             final_message_parts.append("Command processed.")

    elif identified_task and identified_task.intent == "SEARCH_PULL_IMAGE_INTERACTIVE":
        # This case handles if interactive pull finished but didn't set command_executed_by_agent
        # (e.g., user cancelled pull after selection, or error during pull not caught as command_executed_by_agent context)
        final_message_parts.append(f"For your request: '{user_query}' (Search/Pull Image)")
        if state.get("selected_image_for_pull"):
            final_message_parts.append(f"Image selected for pull: {state.get('selected_image_for_pull')}")
        if output and output.strip(): # Output from the pull attempt
            final_message_parts.append(f"Details:\n{output.strip()}")
        else:
            final_message_parts.append("Interactive image search/pull process completed or cancelled.")


    elif identified_task and identified_task.intent == "UNKNOWN" and not error: 
        # This 'error' check is to avoid double messaging if UNKNOWN also had an LLM parsing error
        final_message_parts.append(
            f"I couldn't determine a specific Docker action for: '{user_query}'. Please try rephrasing."
        )
    else: # Fallback for other scenarios or if output exists without a command
        final_message_parts.append(f"Processed request: '{user_query}'.")
        if output and output.strip(): 
            final_message_parts.append(f"Details:\n{output.strip()}")
        elif not error: # Avoid "No specific command" if there was an error message already
            final_message_parts.append("No specific command was run by the agent in this step, or the action was completed/cancelled interactively.")


    final_response_str = "\n".join(final_message_parts)
    v_print(f"To User (from final_result_node): {final_response_str}")
    
    current_history = state.get("history", [])
    if not isinstance(current_history, list):
        v_print(f"Warning: History was not a list, reinitializing. Type was: {type(current_history)}")
        current_history = []
        
    ai_message = AIMessage(content=final_response_str)
    # Avoid duplicating the last AI message if it's the same (e.g., if final_result_node is hit multiple times without change)
    if not current_history or current_history[-1].content != ai_message.content:
        current_history.append(ai_message)
    
    return {**state, "history": current_history, "final_response_for_user": final_response_str}

# --- Workflow Definition ---
workflow = StateGraph(AgentState)

workflow.add_node("classify_intent_node", classify_intent_node)
workflow.add_node("interactive_image_search_node", interactive_image_search_and_pull_node)
workflow.add_node("docker_project_creation_node", docker_project_creation_node)
workflow.add_node("find_image_and_prepare_run_node", find_image_and_prepare_run_node) # New node
workflow.add_node("generate_command_node", generate_command_node)
workflow.add_node("execute_command_node", execute_command_node)
workflow.add_node("final_result_node", final_result_node) 

workflow.set_entry_point("classify_intent_node")

workflow.add_conditional_edges(
    "classify_intent_node",
    route_after_classification,
    {
        "interactive_image_search_node": "interactive_image_search_node",
        "docker_project_creation_node": "docker_project_creation_node",
        "find_image_and_prepare_run_node": "find_image_and_prepare_run_node", # New route
        "generate_command_node": "generate_command_node",
        "final_result_node": "final_result_node"
    }
)

# Paths from interactive/creator nodes mostly go to final_result_node as they manage their own outputs
workflow.add_edge("interactive_image_search_node", "final_result_node") 
workflow.add_edge("docker_project_creation_node", "final_result_node") 

# Path from find_image_and_prepare_run_node (which sets a command)
workflow.add_conditional_edges(
    "find_image_and_prepare_run_node",
    should_execute_command, # This checks if state.docker_command is set
    {
        "execute_command_node": "execute_command_node",
        "final_result_node": "final_result_node" 
    }
)

# Path from generic command generation
workflow.add_conditional_edges(
    "generate_command_node",
    should_execute_command,
    {
        "execute_command_node": "execute_command_node",
        "final_result_node": "final_result_node" 
    }
)
workflow.add_edge("execute_command_node", "final_result_node")
workflow.add_edge("final_result_node", END)

checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)


def run_conversation_cli():
    if llm is None:
        print("Cannot start conversation: LLM is not initialized.")
        return

    thread_id_counter = 0 
    print("\nDocker LangGraph Helper Initialized (CLI Mode).")
    
    llm_provider_name_lower = LLM_PROVIDER.lower()
    llm_model_name = "Unknown Model"
    if llm_provider_name_lower in config.LLM_CONFIGS:
        llm_model_name = config.LLM_CONFIGS[llm_provider_name_lower].get("model_name", "Unknown Model")
    
    print(f"Using LLM: {LLM_PROVIDER.upper()} with model {llm_model_name}")
    print("Examples: 'dockerize my project', 'create a dockerfile', 'pull an image', 'run redis image'")
    print("Type 'exit' or 'quit' to end.")
    
    current_history: List[Any] = [] 

    while True:
        try:
            user_input = input("\nUser: ")
        except KeyboardInterrupt:
            print("\nExiting due to KeyboardInterrupt...")
            break
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting.")
            break
        if not user_input.strip():
            continue

        thread_id_counter +=1
        config_for_run = {"configurable": {"thread_id": str(thread_id_counter)}}
        
        if not isinstance(current_history, list):
            v_print(f"Warning: current_history was not a list ({type(current_history)}). Reinitializing.")
            current_history = []
        current_history.append(HumanMessage(content=user_input))
        
        initial_agent_state: AgentState = {
            "user_query": user_input,
            "history": list(current_history), 
            "identified_task": None,
            "docker_command": None,
            "command_output": None,
            "error_message": None,
            "image_search_keyword": None,
            "image_options": None,
            "selected_image_for_pull": None,
            "final_response_for_user": None,
            "project_directory": None,
            "dockerfile_content": None,
            "dockerignore_content": None,
            "generated_build_command": None,
            "generated_run_command": None,
            "selected_image_to_run": None, # New field
        }
        
        v_print(f"DEBUG: Invoking app.stream for query: '{user_input}' with thread_id {thread_id_counter}")
        final_graph_output_state = None
        try:
            for event_value in app.stream(initial_agent_state, config=config_for_run, stream_mode="values"): # type: ignore
                v_print(f"DEBUG: Stream event (values mode). Keys: {list(event_value.keys()) if isinstance(event_value, dict) else 'Not a dict'}")
                final_graph_output_state = event_value 
        except Exception as e:
            print(f"\nAI: An unexpected error occurred during graph execution: {e}") 
            v_print(f"Graph execution error: {e}", exc_info=True) 
            if not isinstance(current_history, list): current_history = []
            current_history.append(AIMessage(content=f"I encountered an internal error processing your request: {e}"))
            continue 

        v_print(f"DEBUG: Stream finished. Final graph output state type: {type(final_graph_output_state)}")
        if isinstance(final_graph_output_state, dict):
             v_print(f"DEBUG: Final graph output state keys: {list(final_graph_output_state.keys())}")

        if isinstance(final_graph_output_state, dict):
            ai_response_text = final_graph_output_state.get("final_response_for_user")
            if ai_response_text is None: 
                ai_response_text = "No specific response message generated by the graph's final node."
                v_print(f"DEBUG: 'final_response_for_user' was missing or None. State: {final_graph_output_state}")
            
            print(f"\nAI:\n{ai_response_text}") # Added newline for better formatting of multi-line AI responses
            updated_history = final_graph_output_state.get("history")
            if isinstance(updated_history, list):
                current_history = updated_history 
            else:
                v_print("Warning: History from final graph state was not a list. Local history might be stale.")
                temp_history = [] 
                if isinstance(initial_agent_state.get("history"), list) and initial_agent_state["history"]:
                    temp_history.extend(initial_agent_state["history"][:-1]) 
                temp_history.append(HumanMessage(content=user_input)) 
                temp_history.append(AIMessage(content=ai_response_text)) 
                current_history = temp_history
        else: 
            error_msg_for_ai = "I had trouble processing that request and didn't get a clear final result structure."
            if final_graph_output_state is None:
                error_msg_for_ai = "My processing stream didn't produce any final output."
            
            print(f"\nAI: {error_msg_for_ai}") 
            if not isinstance(current_history, list): current_history = []
            current_history.append(AIMessage(content=error_msg_for_ai))


def perform_startup_checks_cli():
    print("Performing startup checks (CLI Mode)...") 
    try:
        print("Attempting to start Docker Desktop (if applicable)...")
        docker_start() 
        
        if platform.system() in ["Windows", "Darwin"]:
            print("Waiting a few seconds for Docker to initialize...")
            import time
            time.sleep(5)

        print("Checking for Docker version...") 
        subprocess.run(["docker", "--version"], check=True, capture_output=True, text=True, timeout=10)
        print("Docker version check: OK") 

        print("Checking Docker system info (daemon responsiveness)...") 
        subprocess.run(["docker", "system", "info", "--format", "{{.OSType}}"], check=True, capture_output=True, text=True, timeout=20)
        print("Docker system info check: OK") 

        print("Checking for Docker Buildx version (for image inspection)...") 
        subprocess.run(["docker", "buildx", "version"], check=True, capture_output=True, text=True, timeout=10)
        print("Docker Buildx version check: OK") 
        
        print("Docker and Docker Buildx found, daemon seems responsive.") 

        if 'questionary' not in globals():
            print("WARNING: Questionary library seems to be missing from global scope.") 
        else:
            print("Questionary library is available for interactive features.") 
        return True
    except FileNotFoundError:
        print("ERROR: Docker command not found. Please ensure Docker is installed and in your PATH.") 
    except subprocess.CalledProcessError as e:
        error_detail = f"{e.stderr.strip() if e.stderr else (e.stdout.strip() if e.stdout else str(e))}"
        print(f"ERROR: Docker command failed during startup check. Is Docker running? Details: {error_detail}") 
    except subprocess.TimeoutExpired:
        print("ERROR: Docker command timed out during startup check. Docker daemon might be unresponsive or still starting.") 
    except Exception as e:
        print(f"ERROR: An unexpected error occurred during startup checks: {e}")
        v_print("Unexpected startup check error", exc_info=True)
    return False


def docker_main(llm_provider_arg = 'gemini'): 
    global llm 
    global LLM_PROVIDER 
    
    LLM_PROVIDER = llm_provider_arg 
    try:
        initialize_llm(LLM_PROVIDER) 
    except ValueError as e:
        print(f"FATAL: Could not initialize LLM on startup: {e}")
        print("Please check your environment variables and config.py settings.")
        llm = None 

    if llm is None: 
        print("Exiting application due to LLM initialization failure (see errors above).")
    elif perform_startup_checks_cli():
        try:
            run_conversation_cli()
        except Exception as e: 
            print(f"\nAn unexpected error occurred in the main conversation loop: {e}")
            v_print(f"Main loop error: {e}", exc_info=True) 
    else:
        print("Exiting application due to failed startup checks (see errors above).")


if __name__ == "__main__":
    default_provider = "groq" if os.getenv("GROQ_API_KEY") else "gemini"
    
    import sys
    selected_provider = default_provider
    if len(sys.argv) > 1 and sys.argv[1].lower() in config.LLM_CONFIGS:
        selected_provider = sys.argv[1].lower()
        print(f"Using LLM provider from command line argument: {selected_provider.upper()}")
    else:
        selected_provider = os.getenv("ASSISTANT_LLM_PROVIDER", default_provider).lower()
        print(f"Using LLM provider (from env or default): {selected_provider.upper()}")

    docker_main(llm_provider_arg=selected_provider)
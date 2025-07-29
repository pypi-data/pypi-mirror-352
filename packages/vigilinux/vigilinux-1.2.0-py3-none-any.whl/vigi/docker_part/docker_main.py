import json
import platform
import os
import re
import subprocess
from typing import TypedDict, List, Dict, Any, Optional

import questionary
import colorama # Import colorama
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
import time

try:
    from . import config
    from . import docker_project_creator
    from .config import AnsiColors, Theme # Import color themes
except ImportError:
    import config
    import docker_project_creator
    from config import AnsiColors, Theme # Import color themes


llm = None
LLM_PROVIDER = "gemini"

def docker_start():
    # User sees themed status/error messages. Verbose logs internal attempts.
    if platform.system() == "Windows":
        docker_path = r"C:\Program Files\Docker\Docker\Docker Desktop.exe"
        if os.path.exists(docker_path):
            try:
                subprocess.Popen([docker_path], shell=False, close_fds=True)
                v_print(Theme.F(Theme.STATUS, "Attempting to start Docker Desktop (Windows)..."))
            except Exception as e:
                print(Theme.F(Theme.ERROR, f"Failed to auto-start Docker Desktop: {e}")) # User sees error
        else:
            print(Theme.F(Theme.WARNING, f"Docker Desktop not found at {docker_path} for auto-start.")) # User sees warning
    elif platform.system() == "Darwin": # macOS
        try:
            subprocess.Popen(["open", "-a", "Docker"], shell=False, close_fds=True)
            # CHANGED THIS LINE from print to v_print:
            v_print(Theme.F(Theme.STATUS, "Attempting to start Docker Desktop (macOS)..."))
        except Exception as e:
            print(Theme.F(Theme.ERROR, f"Failed to auto-start Docker Desktop on macOS: {e}")) # User sees error
    else:
        v_print("Docker Desktop auto-start is for Windows/macOS. Linux daemon should be managed separately.")

def v_print(message, **kwargs):
    config.v_print(message, **kwargs) # Relies on config.v_print's internal styling

def initialize_llm(provider_name: str):
    global llm
    provider_name_lower = provider_name.lower()
    if provider_name_lower not in config.LLM_CONFIGS:
        available_providers = ", ".join(config.LLM_CONFIGS.keys())
        raise ValueError(
            Theme.F(Theme.ERROR,
                f"Unsupported LLM provider: '{provider_name}'. "
                f"Supported providers in config.py: {available_providers}"
            )
        )

    llm_settings = config.LLM_CONFIGS[provider_name_lower]
    api_key_env_var_name = llm_settings.get("api_key_env_var")

    if not api_key_env_var_name:
        raise ValueError(
            Theme.F(Theme.ERROR,
                f"Configuration for '{provider_name_lower}' is missing the "
                f"'api_key_env_var' field in config.py."
            )
        )

    actual_api_key = os.getenv(api_key_env_var_name)

    if not actual_api_key:
        raise ValueError(
             Theme.F(Theme.ERROR,
                f"API key environment variable '{api_key_env_var_name}' for provider "
                f"'{provider_name_lower}' is not set or is empty. Please ensure this "
                f"environment variable is set with your API key."
             )
        )

    v_print(f"Initializing LLM: {Theme.F(Theme.SYSTEM_INFO, provider_name_lower.upper())} with model {Theme.F(Theme.SYSTEM_INFO, llm_settings['model_name'])}")


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
             Theme.F(Theme.ERROR,
                f"LLM provider '{provider_name_lower}' initialization logic "
                f"not implemented, though defined in config."
            )
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
If an image name seems like a general keyword (e.g., "redis", "nginx", "beef") rather than a fully qualified name (e.g., "ubuntu:latest", "my-org/my-image"), and the user wants to pull it, prefer the SEARCH_PULL_IMAGE_INTERACTIVE intent to allow selection. Only use PULL_IMAGE if the name is very specific and likely an official image (like "ubuntu", "alpine", "hello-world") or fully qualified (e.g. "organization/image_name").

Possible intents and parameters:
- SEARCH_PULL_IMAGE_INTERACTIVE: User wants to search and then pull an image, especially for general keywords or to explore options.
  - parameters: {"image_keyword": "search_term"}
- PULL_IMAGE: User wants to pull a very specific, canonical, or fully qualified image directly.
  - parameters: {"image_name": "name", "tag": "optional_tag"}
- CREATE_DOCKER_PROJECT: User wants to create Dockerfile and .dockerignore for the current working directory. This includes projects like Python, Node.js, or static HTML/CSS/JS sites.
  - parameters: {}
- RUN_EXISTING_IMAGE: User wants to run an existing local image.
  - parameters: {"image_name_query": "user's term for image", "run_options_raw": "e.g., -p 80:8000 --name myapp -it"}
- UNKNOWN: If intent cannot be determined.
  - parameters: {}
- LIST_LOCAL_IMAGES: User wants to see locally available Docker images.
  - parameters: {}
- LIST_CONTAINERS: User wants to see running or all containers.
  - parameters: {"show_all": true/false}  # true to show all containers (including stopped ones)
- LIST_RUNNING_CONTAINERS: User specifically wants to see running containers.
  - parameters: {}


Example for 'show me my local images':
{
  "intent": "LIST_LOCAL_IMAGES",
  "parameters": {}
}
Example for 'list all containers including stopped ones':
{
  "intent": "LIST_CONTAINERS",
  "parameters": { "show_all": true }
}
Example for 'what containers are running?':
{
  "intent": "LIST_RUNNING_CONTAINERS",
  "parameters": {}
}

Example for 'pull the redis image and run it':
{
  "intent": "SEARCH_PULL_IMAGE_INTERACTIVE",
  "parameters": { "image_keyword": "redis" }
}
Example for 'pull the beef image':
{
  "intent": "SEARCH_PULL_IMAGE_INTERACTIVE",
  "parameters": { "image_keyword": "beef" }
}
Example for 'pull ubuntu':
{
  "intent": "PULL_IMAGE",
  "parameters": { "image_name": "ubuntu" }
}
Example for 'pull my-company/my-custom-app:v2':
{
  "intent": "PULL_IMAGE",
  "parameters": { "image_name": "my-company/my-custom-app", "tag": "v2" }
}
Example for 'help me dockerize my current project' or 'create a dockerfile for my static website':
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



# Helper function to format Docker output as tables
def format_docker_table(headers: List[str], rows: List[List[str]]) -> str:
    """Formats data as an ASCII table with aligned columns"""
    col_widths = [max(len(str(item)) for item in col) for col in zip(headers, *rows)]
    header_line = "  ".join(h.ljust(w) for h, w in zip(headers, col_widths))
    separator = "  ".join('-' * w for w in col_widths)
    data_lines = []
    for row in rows:
        data_lines.append("  ".join(str(cell).ljust(w) for cell, w in zip(row, col_widths)))
    return "\n".join([header_line, separator] + data_lines)

# New node: List local Docker images
def list_local_images_node(state: AgentState) -> AgentState:
    v_print("--- Listing Local Images ---")
    try:
        # Get images in JSON format
        cmd = ["docker", "images"]
        result = subprocess.run(cmd + ["--format", "{{json .}}"], capture_output=True, text=True, check=True)

        images = []
        for line in result.stdout.strip().splitlines():
            try:
                img = json.loads(line)
                images.append([
                    img.get("Repository", "<none>"),
                    img.get("Tag", "<none>"),
                    img.get("ID", "")[:12],
                    img.get("Size", "?")
                ])
            except json.JSONDecodeError as e:
                v_print(f"Warning: Could not parse line from 'docker images': {line} - Error: {e}")
                continue

        if not images:
            output = Theme.F(Theme.WARNING, "No local Docker images found.")
        else:
            headers = ["REPOSITORY", "TAG", "IMAGE ID", "SIZE"]
            output = format_docker_table(headers, images)
            output = Theme.F(Theme.SYSTEM_INFO, output)

        return {**state, "command_output": output, "error_message": None}

    except Exception as e:
        error_msg = f"Failed to list local images: {str(e)}"
        v_print(error_msg, exc_info=True)
        return {**state, "error_message": error_msg}

# New node: List Docker containers
def list_containers_node(state: AgentState) -> AgentState:
    v_print("--- Listing Containers ---")
    task = state.get("identified_task")
    show_all = False

    if task and task.intent == "LIST_CONTAINERS":
        show_all = task.parameters.get("show_all", False)
    elif task and task.intent == "LIST_RUNNING_CONTAINERS": # Explicitly handle this
        show_all = False

    try:
        # Get containers in JSON format
        cmd = ["docker", "ps", "--format", "{{json .}}"]
        if show_all:
            cmd.append("-a")

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        containers = []
        for line in result.stdout.strip().splitlines():
            try:
                container = json.loads(line)
                containers.append([
                    container.get("ID", "")[:12],
                    container.get("Image", ""),
                    container.get("Command", "")[:20] + "..." if len(container.get("Command", "")) > 20 else container.get("Command", ""),
                    container.get("Status", ""),
                    container.get("Ports", ""),
                    container.get("Names", "")
                ])
            except json.JSONDecodeError as e:
                v_print(f"Warning: Could not parse line from 'docker ps': {line} - Error: {e}")
                continue

        if not containers:
            status = "all" if show_all else "running"
            output = Theme.F(Theme.WARNING, f"No {status} containers found.")
        else:
            headers = ["CONTAINER ID", "IMAGE", "COMMAND", "STATUS", "PORTS", "NAMES"]
            output = format_docker_table(headers, containers)
            output = Theme.F(Theme.SYSTEM_INFO, output)

        return {**state, "command_output": output, "error_message": None}

    except Exception as e:
        error_msg = f"Failed to list containers: {str(e)}"
        v_print(error_msg, exc_info=True)
        return {**state, "error_message": error_msg}


def interactive_image_search_and_pull_node(state: AgentState) -> AgentState:
    v_print("--- Interactive Image Search ---", level="debug")
    task = state.get("identified_task")
    if not task or not task.parameters.get("image_keyword"):
        return {
            **state, "error_message": "Image keyword not provided for search.",
            "docker_command": None, "command_output": None, "selected_image_for_pull": None
        }

    keyword = task.parameters["image_keyword"]
    print(Theme.F(Theme.STATUS, f"Searching Docker Hub for '{Theme.F(Theme.HIGHLIGHT, keyword)}'..."))

    system_platform: Optional[str] = None
    try: # Get system platform
        sys_info_proc = subprocess.run(
            ["docker", "system", "info", "--format", "{{.OSType}}/{{.Architecture}}"],
            capture_output=True, text=True, check=True, timeout=10
        )
        system_platform_raw = sys_info_proc.stdout.strip().lower()
        if system_platform_raw == "linux/x86_64": system_platform = "linux/amd64"
        elif system_platform_raw and '/' in system_platform_raw: system_platform = system_platform_raw
        else: v_print(f"Warning: Invalid system platform: '{system_platform_raw}'", level="debug")

        if system_platform:
            v_print(f"System platform: {system_platform}")

        else:
            print(Theme.F(Theme.WARNING, "Warning: Could not determine system platform. Compatibility checks may be limited."))
    except Exception as e:
        err_msg = f"Could not get system platform: {e}"
        print(Theme.F(Theme.ERROR, f"ERROR: {err_msg}"))
        print(Theme.F(Theme.WARNING, "Proceeding without system platform info."))


    try: # Docker search
        search_proc = subprocess.run(
            ["docker", "search", keyword, "--format", "{{json .}}", "--no-trunc", "--limit", "25"],
            capture_output=True, text=True, check=True, timeout=30
        )
        search_results = parse_docker_search_output(search_proc.stdout)
    except Exception as e:
        err_msg = f"Failed to search Docker Hub for '{keyword}': {getattr(e, 'stderr', str(e))}"
        print(Theme.F(Theme.ERROR, f"ERROR: {err_msg}"))
        return {**state, "error_message": err_msg, "selected_image_for_pull": None, "docker_command": None, "command_output": None}

    if not search_results:
        print(Theme.F(Theme.WARNING, f"No images found for '{keyword}'."))
        return {**state, "error_message": f"No images found for '{keyword}'.", "selected_image_for_pull": None}

    sorted_images = sorted(search_results, key=lambda img: img.get('StarCount', 0), reverse=True)

    choices = []
    for img in sorted_images[:7]: # Show top 7
        plain_name = img['Name'][:35].ljust(35)
        plain_stars = f"(★{img.get('StarCount', 0)})".ljust(10)
        description_str = str(img.get('Description', '')).strip()
        plain_description = ('- ' + description_str[:40] + '...') if description_str else ''
        full_title = f"{plain_name} {plain_stars} {plain_description}"
        choices.append(questionary.Choice(title=full_title, value=img['Name']))

    choices.append(questionary.Separator())
    # --- MODIFICATION 1: Give the cancel choice a specific value ---
    choices.append(questionary.Choice(title="Cancel Selection", value="##CANCEL##")) # <-- ADDED value

    selected_image_ans = questionary.select(
        "Select an image (or Cancel):",
        choices=choices,
        pointer= "🔖" ,
        use_shortcuts=True
    ).ask()

    # --- MODIFICATION 2: Check for the cancellation value ---
    if selected_image_ans is None or selected_image_ans == "##CANCEL##":
        user_friendly_cancel_msg = "Image search cancelled by user."
        print(Theme.F(Theme.WARNING, user_friendly_cancel_msg))
        return {
            **state,
            "docker_command": None,
            "command_output": None,
            "error_message": user_friendly_cancel_msg, # This message goes to final_result_node
            "selected_image_for_pull": None
        }
    # --- END OF MODIFICATIONS ---

    selected_image_name = selected_image_ans # Now we are sure it's an image name.

    # Initialize variables for the inspection/pull logic
    is_compatible = False
    pulled_image_name = None
    pull_attempt_output = None
    compatible_image_pulled_flag = False # Flag for successful pull
    final_error_message_for_node = None # Specific error from this node's operations
    image_platforms_lower: List[str] = []


    if system_platform:
        print(Theme.F(Theme.STATUS, f"\nInspecting {Theme.F(Theme.HIGHLIGHT, selected_image_name)} for compatibility with {Theme.F(Theme.HIGHLIGHT, system_platform)}..."))
        try:
            inspect_command = ["docker", "buildx", "imagetools", "inspect", "--raw", selected_image_name]
            inspect_proc = subprocess.run(inspect_command, capture_output=True, text=True, check=True, timeout=60)
            image_platforms = get_image_platforms_from_inspect(inspect_proc.stdout)
            image_platforms_lower = [p.lower() for p in image_platforms]
            if not image_platforms_lower:
                print(Theme.F(Theme.WARNING, f"Could not determine platforms for {Theme.F(Theme.HIGHLIGHT, selected_image_name)} from inspection."))
            else:
                is_compatible = system_platform in image_platforms_lower
        except subprocess.CalledProcessError as e:
            err_msg = f"Inspection failed for {selected_image_name}: {e.stderr or e.stdout or str(e)}"
            print(Theme.F(Theme.ERROR, f"ERROR: {err_msg}"))
            if not questionary.confirm(f"Pull {selected_image_name} anyway?", default=False).ask(): # Default to No if inspection fails
                final_error_message_for_node = err_msg
            else: is_compatible = True # User override
        except FileNotFoundError:
            err_msg = "Docker 'buildx imagetools' not found. Cannot inspect platforms. Consider installing 'docker-buildx' or ensuring it's in PATH."
            print(Theme.F(Theme.ERROR, f"ERROR: {err_msg}"))
            final_error_message_for_node = err_msg
        except Exception as e:
            err_msg = f"Error during inspection of {selected_image_name}: {e}"
            print(Theme.F(Theme.ERROR, f"ERROR: {err_msg}"))
            if not questionary.confirm(f"Pull {selected_image_name} anyway?", default=False).ask(): # Default to No for general errors
                final_error_message_for_node = err_msg
            else: is_compatible = True # User override
    else: # system_platform is None
        print(Theme.F(Theme.WARNING, f"\nSystem platform unknown. Skipping precise compatibility check for {Theme.F(Theme.HIGHLIGHT, selected_image_name)}."))
        is_compatible = False

    if final_error_message_for_node is None:
        if is_compatible:
            print(Theme.F(Theme.SUCCESS, f"Image {Theme.F(Theme.HIGHLIGHT, selected_image_name)} seems compatible (or you chose to proceed)."))
        else:
            if system_platform and image_platforms_lower:
                platform_str = ", ".join(image_platforms_lower)
                print(Theme.F(Theme.WARNING, f"{Theme.F(Theme.HIGHLIGHT,selected_image_name)} may not suit {system_platform} (image platforms: {platform_str})."))

            if not questionary.confirm(f"Pull 🐳{selected_image_name}🐳 anyway?", default=True if not system_platform else False).ask():
                final_error_message_for_node = f"Pull skipped for {selected_image_name} by user due to potential incompatibility."

        if final_error_message_for_node is None:
            if questionary.confirm(f"Confirm pull for 🐳{selected_image_name}🐳?", default=True).ask():
                print(Theme.F(Theme.STATUS, f"Pulling {Theme.F(Theme.COMMAND, selected_image_name)}..."))
                try:
                    # Changed to Popen to allow for potential real-time output if desired later,
                    # but wait() makes it behave like run() for now.
                    process = subprocess.Popen(["docker", "pull", selected_image_name], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = process.communicate(timeout=600) # Wait for completion

                    if stdout: print(Theme.F(AnsiColors.DIM, stdout.strip()))
                    if stderr and process.returncode !=0: print(Theme.F(Theme.ERROR, stderr.strip()))

                    if process.returncode == 0:
                        pull_attempt_output = f"Successfully pulled {selected_image_name}."
                        print(Theme.F(Theme.SUCCESS, f"Pulled {Theme.F(Theme.HIGHLIGHT, selected_image_name)} successfully!"))
                        compatible_image_pulled_flag = True
                        pulled_image_name = selected_image_name
                    else:
                        err_msg_pull = f"Failed to pull {selected_image_name} (Docker exit: {process.returncode}). Details: {stderr.strip() or stdout.strip() or 'No output from docker pull command.'}"
                        pull_attempt_output = err_msg_pull
                        # Already printed stderr, no need to print Theme.F(Theme.ERROR, err_msg_pull) again
                        final_error_message_for_node = err_msg_pull
                except Exception as e_pull:
                    err_msg_pull = f"Error during pull of {selected_image_name}: {e_pull}"
                    pull_attempt_output = err_msg_pull; print(Theme.F(Theme.ERROR, err_msg_pull))
                    final_error_message_for_node = err_msg_pull
            else:
                final_error_message_for_node = f"Pull for {selected_image_name} cancelled by user at confirmation."
                print(Theme.F(Theme.MUTED_SYSTEM_INFO, final_error_message_for_node))

    if compatible_image_pulled_flag and pulled_image_name:
        return {**state, "docker_command": f"docker pull {pulled_image_name}", # This is more for logging the action
                "command_output": pull_attempt_output or f"Pulled {pulled_image_name}.",
                "error_message": None, "selected_image_for_pull": pulled_image_name}
    else:
        if not final_error_message_for_node:
            final_error_message_for_node = f"Process for '{selected_image_name}' did not complete successfully or was cancelled." if selected_image_name else "Image selection/pull process did not complete or was cancelled."
        return {**state, "docker_command": None, # No command was "executed" by the agent at a higher level
                "command_output": pull_attempt_output, # Output from the pull attempt, if any
                "error_message": final_error_message_for_node, "selected_image_for_pull": None}



def docker_project_creation_node(state: AgentState) -> AgentState:
    v_print("--- Interactive Docker Project Creation ---")
    current_dir = os.getcwd()

    try:
        project_data = docker_project_creator.create_docker_project_interactive(current_dir, v_print)

        actions_log = project_data.get("actions_log", []) # Raw logs from creator

        build_cmd_from_creator = project_data.get("build_command")
        run_cmd_from_creator = project_data.get("run_command")

        if build_cmd_from_creator and project_data.get("dockerfile_path"):
            ask_build_msg = (
                f"Dockerfile created. Do you want to build the Docker image now using:\n"
                f"  {Theme.F(Theme.COMMAND, build_cmd_from_creator)}?"
            )
            if questionary.confirm(ask_build_msg, default=True).ask():
                v_print(f"User opted to build. Executing: {build_cmd_from_creator} in {current_dir}")
                print(Theme.F(Theme.STATUS, f"Attempting to build image... Command: {Theme.F(Theme.COMMAND, build_cmd_from_creator)}"))
                try:
                    # Use subprocess.run to capture all output, then print
                    process = subprocess.run(
                        build_cmd_from_creator, shell=True, capture_output=True, text=True,
                        timeout=600, check=False, cwd=current_dir
                    )
                    # Print stdout and stderr, dimming them for potentially long output
                    if process.stdout:
                        print(Theme.F(AnsiColors.DIM, process.stdout.strip()))
                    if process.stderr and process.returncode !=0: # Only show stderr if error
                        print(Theme.F(Theme.WARNING, process.stderr.strip()))


                    if process.returncode == 0:
                        msg = f"Image built successfully using: {Theme.F(Theme.COMMAND, build_cmd_from_creator)}"
                        print(Theme.F(Theme.SUCCESS, msg))
                        actions_log.append(f"Image built successfully using: {build_cmd_from_creator}")


                        if run_cmd_from_creator:
                            ask_run_msg = (
                                f"Build successful. Do you want to run the container now using:\n"
                                f"  {Theme.F(Theme.COMMAND, run_cmd_from_creator)}?"
                            )
                            if questionary.confirm(ask_run_msg, default=True).ask():
                                v_print(f"User opted to run. Executing: {run_cmd_from_creator}")
                                print(Theme.F(Theme.STATUS, f"Attempting to run container... Command: {Theme.F(Theme.COMMAND, run_cmd_from_creator)}"))
                                try:
                                    run_process = subprocess.run(
                                        run_cmd_from_creator, shell=True, capture_output=True,
                                        text=True, timeout=120, check=False
                                    )
                                    if run_process.returncode == 0:
                                        msg_run = f"Container started successfully using: {Theme.F(Theme.COMMAND, run_cmd_from_creator)}"
                                        print(Theme.F(Theme.SUCCESS, msg_run))
                                        actions_log.append(f"Container started successfully using: {run_cmd_from_creator}")
                                        if run_process.stdout.strip():
                                            run_output_msg = f"Run output (container ID for -d):\n{Theme.F(Theme.MUTED_SYSTEM_INFO, run_process.stdout.strip())}"
                                            print(run_output_msg)
                                            actions_log.append(f"Run output: {run_process.stdout.strip()}")
                                    else:
                                        err_msg_run_raw = run_process.stderr.strip() or run_process.stdout.strip() or f'Exit code {run_process.returncode}'
                                        err_msg_run = f"Failed to run container. Command: {Theme.F(Theme.COMMAND, run_cmd_from_creator)}.\nError: {Theme.F(Theme.ERROR, err_msg_run_raw)}"
                                        print(err_msg_run)
                                        actions_log.append(f"Failed to run container: {err_msg_run_raw}")
                                except Exception as e_run:
                                    err_msg_run_raw = str(e_run)
                                    err_msg_run = f"Exception running container command '{Theme.F(Theme.COMMAND, run_cmd_from_creator)}': {Theme.F(Theme.ERROR, err_msg_run_raw)}"
                                    print(err_msg_run)
                                    actions_log.append(f"Exception running container: {err_msg_run_raw}")
                            else:
                                msg_skip_run = f"Container run with `{run_cmd_from_creator}` skipped by user."
                                actions_log.append(msg_skip_run)
                                print(Theme.F(Theme.WARNING, "Container run skipped."))
                    else: # Build failed
                        build_err_raw = process.stderr.strip() or process.stdout.strip() or f'Exit code {process.returncode}'
                        err_msg_build = f"Failed to build image. Command: `{build_cmd_from_creator}`.\nError: {Theme.F(Theme.ERROR,build_err_raw)}"
                        print(err_msg_build)
                        actions_log.append(f"Failed to build image. Error: {build_err_raw}")
                except (subprocess.TimeoutExpired) as e_build_proc:
                    err_msg_build_raw = "Build timed out."
                    err_msg_build = f"Build timed out. Command: `{build_cmd_from_creator}`. {Theme.F(Theme.ERROR, err_msg_build_raw)}"
                    print(err_msg_build)
                    actions_log.append(err_msg_build_raw)
                except Exception as e_build:
                    err_msg_build_raw = str(e_build)
                    err_msg_build = f"Exception building image with command '{build_cmd_from_creator}': {Theme.F(Theme.ERROR, err_msg_build_raw)}"
                    print(err_msg_build)
                    actions_log.append(f"Exception building image: {err_msg_build_raw}")
                    v_print(err_msg_build.replace(Theme.COMMAND,"").replace(Theme.ERROR,"").replace(AnsiColors.RESET,""), exc_info=True) # Log plain for v_print
            else: # User skipped build
                msg_skip_build = f"Image build with `{build_cmd_from_creator}` skipped by user."
                actions_log.append(msg_skip_build)
                print(Theme.F(Theme.WARNING, "Image build skipped."))
        elif build_cmd_from_creator:
             actions_log.append("Image build skipped as Dockerfile was not created/saved.")


        final_summary_parts = [project_data.get("summary_message","Project setup summary not available.")]

        if actions_log:
            final_summary_parts.append(f"\n{Theme.F(Theme.SECTION_HEADER, '--- Actions Log (from Dockerize Project) ---')}")
            for log_item in actions_log: # actions_log from creator + this node's additions
                if isinstance(log_item, str): # Ensure it's a string
                    # Check for keywords to color log items appropriately if they are plain strings
                    if "ERROR:" in log_item or "Failed to" in log_item or "Exception" in log_item or "Warning:" in log_item:
                        final_summary_parts.append(Theme.F(Theme.WARNING, f"- {log_item}"))
                    elif "Successfully" in log_item or "saved to" in log_item or "created at" in log_item:
                        final_summary_parts.append(Theme.F(Theme.MUTED_SYSTEM_INFO, f"- {log_item}"))
                    else:
                        final_summary_parts.append(Theme.F(AnsiColors.DIM, f"- {log_item}"))
                else: # Should not happen, but good practice
                     final_summary_parts.append(Theme.F(AnsiColors.DIM, f"- {str(log_item)}"))


        return {
            **state,
            "project_directory": current_dir,
            "dockerfile_content": project_data.get("dockerfile_content"),
            "dockerignore_content": project_data.get("dockerignore_content"),
            "generated_build_command": build_cmd_from_creator,
            "generated_run_command": run_cmd_from_creator,
            "command_output": "\n".join(final_summary_parts),
            "error_message": project_data.get("error_message"),
            "docker_command": None
        }
    except Exception as e:
        v_print(f"Error during Docker project creation process: {e}", exc_info=True)
        error_msg = f"An unexpected issue occurred while setting up the Docker project: {e}"
        print(Theme.F(Theme.ERROR, f"ERROR: {error_msg}"))
        return {
            **state,
            "project_directory": current_dir,
            "error_message": error_msg,
            "command_output": Theme.F(Theme.ERROR, "Docker project setup was interrupted by an unexpected error.")
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
    v_print("--- Find Local Image & Prepare Run ---", level="debug")
    task = state.get("identified_task")
    if not task or task.intent != "RUN_EXISTING_IMAGE":
        return {**state, "error_message": "Internal: Task not RUN_EXISTING_IMAGE.", "selected_image_to_run": None, "docker_command": None}

    image_name_query = task.parameters.get("image_name_query", "").lower()
    run_options_raw = task.parameters.get("run_options_raw", "")
    if not image_name_query:
        msg = "No image name provided to search for."
        print(Theme.F(Theme.WARNING, msg))
        return {**state, "error_message": msg, "selected_image_to_run": None, "docker_command": None}

    print(Theme.F(Theme.STATUS, f"Searching local images for '{Theme.F(Theme.HIGHLIGHT, image_name_query)}'..."))
    try:
        images_proc = subprocess.run(["docker", "images", "--format", "{{json .}}"], capture_output=True, text=True, check=True, timeout=10)
        local_images = parse_docker_images_json_output(images_proc.stdout)
    except Exception as e:
        err_msg = f"Failed to list local Docker images: {getattr(e, 'stderr', str(e))}"
        print(Theme.F(Theme.ERROR, f"ERROR: {err_msg}"))
        return {**state, "error_message": err_msg, "selected_image_to_run": None, "docker_command": None}

    if not local_images:
        msg = "No local Docker images found. You might need to pull or build one first."
        print(Theme.F(Theme.WARNING, msg))
        return {**state, "error_message": msg, "selected_image_to_run": None, "docker_command": None}

    matched_images = []
    for img in local_images:
        repo = img.get("Repository", "").lower()
        tag = img.get("Tag", "").lower()
        repo_tag = f"{repo}:{tag}"
        if image_name_query == repo_tag or image_name_query == repo or image_name_query in repo_tag:
            if not any(m['ID'] == img['ID'] for m in matched_images):
                 matched_images.append(img)
    matched_images.sort(key=lambda x: (x.get("Repository", ""), x.get("Tag", "")))

    selected_image_full_name = None
    if not matched_images:
        msg = f"No local image found matching '{image_name_query}'."
        print(Theme.F(Theme.WARNING, msg))
        return {**state, "error_message": msg, "selected_image_to_run": None, "docker_command": None}
    elif len(matched_images) == 1:
        img = matched_images[0]
        selected_image_full_name = f"{img['Repository']}:{img['Tag']}"
        print(Theme.F(Theme.SUCCESS, f"Found: {Theme.F(Theme.HIGHLIGHT, selected_image_full_name)}"))
    else:
        print(Theme.F(Theme.STATUS, f"Multiple local images match '{Theme.F(Theme.HIGHLIGHT, image_name_query)}'. Please select one:"))
        choices = []
        for img in matched_images[:10]:
            plain_repo_tag = (img.get('Repository', '<???>') + ':' + img.get('Tag', '<???>'))[:40].ljust(40)
            plain_details = f"(ID: {img.get('ID', 'N/A')[:12]}, Size: {img.get('Size', 'N/A')})"
            full_title = f"{plain_repo_tag} {plain_details}"
            choices.append(questionary.Choice(title=full_title, value=f"{img['Repository']}:{img['Tag']}"))

        choices.append(questionary.Separator())
        choices.append(questionary.Choice(Theme.F(Theme.WARNING, "[ Cancel Selection ]"), value="##CANCEL##"))

        selected_image_ans = questionary.select("Select image to run:", choices=choices, use_shortcuts=True).ask()

        if selected_image_ans is None or selected_image_ans == "##CANCEL##":
            msg = "Image selection for run cancelled by user."
            print(Theme.F(Theme.WARNING, msg))
            return { # Ensure all relevant keys are set, even if None
                **state,
                "docker_command": None,
                "error_message": msg,
                "selected_image_to_run": None # Explicitly set to None on cancel
            }
        selected_image_full_name = selected_image_ans

    # If selected_image_full_name is still None here, it means something went wrong before selection (e.g. no matches)
    # but that case is handled by earlier returns. This point should only be reached if an image was selected.

    prompt_msg = f"Run {Theme.F(Theme.COMMAND, str(selected_image_full_name))} with options (current: '{run_options_raw if run_options_raw else '<none>'}'):"
    user_opts = questionary.text(prompt_msg, default=run_options_raw).ask()

    if user_opts is None:
        msg = "Run options configuration cancelled by user."
        print(Theme.F(Theme.WARNING, msg))
        return { # Ensure all relevant keys are set
            **state,
            "docker_command": None,
            "error_message": msg,
            "selected_image_to_run": selected_image_full_name # Keep selected image if options cancelled
        }

    final_opts = user_opts.strip()
    final_cmd = f"docker run {final_opts} {selected_image_full_name}".strip().replace("  "," ") # type: ignore
    print(Theme.F(Theme.STATUS, f"Prepared command: {Theme.F(Theme.COMMAND, final_cmd)}"))
    return {
        **state,
        "selected_image_to_run": selected_image_full_name,
        "docker_command": final_cmd,
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

    if task.intent in ["SEARCH_PULL_IMAGE_INTERACTIVE", "CREATE_DOCKER_PROJECT", "RUN_EXISTING_IMAGE"]:
        if task.intent == "SEARCH_PULL_IMAGE_INTERACTIVE" and state.get("selected_image_for_pull"):
             return state
        return {**state, "docker_command": state.get("docker_command")}


    params = task.parameters
    command_parts = ["docker"]
    try:
        if task.intent == "PULL_IMAGE":
            if not params.get("image_name"):
                return {**state, "error_message": "Image name required for PULL_IMAGE intent."}
            command_parts.append("pull")
            image_name = params["image_name"]
            if params.get("tag"):
                image_name += f":{params['tag']}"
            command_parts.append(image_name)
        else:
            return {**state, "error_message": f"Command generation not implemented for intent: {task.intent}"}

        final_command_str = " ".join(command_parts)
        v_print(f"Generated command: {Theme.F(Theme.COMMAND, final_command_str)}")
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
            "command_output": state.get("command_output", Theme.F(Theme.WARNING, "No command was specified for execution.")),
            "error_message": state.get("error_message")
        }

    v_print(f"Executing: {Theme.F(Theme.COMMAND, command)}")
    print(Theme.F(Theme.STATUS, f"Executing: {Theme.F(Theme.COMMAND, command)}"))
    try:
        process = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300, check=False)

        # Display output immediately, styled
        if process.stdout.strip():
            print(Theme.F(AnsiColors.DIM, process.stdout.strip()))
        if process.stderr.strip() and process.returncode != 0:
             print(Theme.F(Theme.ERROR if process.returncode !=0 else Theme.WARNING, process.stderr.strip()))


        if process.returncode == 0:
            output = process.stdout.strip() if process.stdout else Theme.F(Theme.SUCCESS, "Command executed successfully with no output.")
            v_print(f"Command success. Output (raw):\n{process.stdout.strip() or 'No output'}")
            if not process.stdout.strip(): # If command had no output, give positive feedback
                 print(Theme.F(Theme.SUCCESS, "Command executed successfully."))
            return {**state, "command_output": process.stdout.strip(), "error_message": None}
        else:
            error_output_raw = process.stderr.strip() or "Command failed with no specific error output."
            v_print(f"Command failed. Exit code: {process.returncode}. Raw error output: {error_output_raw}")
            # User has already seen styled stderr, no need to print again.
            # Return raw (un-styled) output and error for state
            return {**state, "command_output": (process.stdout.strip() + "\n" + error_output_raw).strip(), "error_message": error_output_raw or f"Command '{command}' failed with exit code {process.returncode}."}

    except subprocess.TimeoutExpired:
        timeout_msg_raw = f"Command '{command}' timed out."
        timeout_msg = f"Command '{Theme.F(Theme.COMMAND, command)}' timed out."
        v_print(timeout_msg_raw)
        print(Theme.F(Theme.ERROR, timeout_msg))
        return {**state, "error_message": timeout_msg_raw, "command_output": "Operation timed out."}
    except FileNotFoundError:
        fnf_msg = "Docker command not found. Please ensure Docker is installed and in your PATH."
        v_print(f"{fnf_msg} (while trying to execute: {command})")
        print(Theme.F(Theme.ERROR, fnf_msg))
        return {**state, "error_message": fnf_msg}
    except Exception as e:
        exec_err_msg_raw = f"Error executing command '{command}': {e}"
        exec_err_msg = f"Error executing command '{Theme.F(Theme.COMMAND, command)}': {Theme.F(Theme.ERROR,str(e))}"
        v_print(exec_err_msg_raw, exc_info=True)
        print(exec_err_msg)
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

    v_print(f"Identified intent: {Theme.F(Theme.HIGHLIGHT, task.intent)}")

    if task.intent == "LIST_LOCAL_IMAGES":
        v_print("Routing to list_local_images_node.")
        return "list_local_images_node"
    elif task.intent in ["LIST_CONTAINERS", "LIST_RUNNING_CONTAINERS"]:
        v_print("Routing to list_containers_node.")
        return "list_containers_node"

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
    if state.get("error_message"):
        v_print(f"Routing to final_result_node due to error before execution: {state['error_message']}")
        return "final_result_node"

    docker_command = state.get("docker_command")

    identified_task = state.get("identified_task")
    if identified_task and identified_task.intent == "CREATE_DOCKER_PROJECT":
        v_print("Routing to final_result_node after Docker project creation (its own node handles build/run).")
        return "final_result_node"

    if not docker_command:
        if not state.get("error_message") and not state.get("command_output"):
             state["error_message"] = "No Docker command was generated or selected for execution by this path."
        v_print(f"Routing to final_result_node: No command to execute from this path. Error: {state.get('error_message')}, Output: {state.get('command_output')}")
        return "final_result_node"

    v_print(f"Proceeding to execute_command_node for command: {Theme.F(Theme.COMMAND, str(docker_command))}")
    return "execute_command_node"


def final_result_node(state: AgentState) -> AgentState:
    v_print("--- Final Result Node ---")
    user_query = state.get("user_query", "Unknown query")
    identified_task = state.get("identified_task")
    command_executed_by_agent = state.get("docker_command")
    output = state.get("command_output")
    error = state.get("error_message")

    final_message_parts = []

    if error:
        final_message_parts.append(Theme.F(Theme.ERROR, f"Error processing your request ('{Theme.H_TEXT(user_query)}'): {error}"))
        # command_output from a failed command might contain the same error. Check to avoid redundancy.
        if output and output.strip() and (error not in output if error and output else True):
             # If output seems like a generic message (not from creator node), dim it.
             if Theme.SECTION_HEADER not in output and "docker build -t" not in output:
                final_message_parts.append(f"Details/Output (if any):\n{Theme.F(AnsiColors.DIM, output.strip())}")
             else: # Output from creator node is already well-themed.
                final_message_parts.append(f"Details/Output (if any):\n{output.strip()}")


    elif identified_task and identified_task.intent == "CREATE_DOCKER_PROJECT":
        final_message_parts.append(f"For your request: '{Theme.H_TEXT(user_query)}' (Dockerize Project)")
        if output and output.strip(): # This 'output' is the pre-formatted summary from the node
            final_message_parts.append(f"\n{output.strip()}")
        else:
            final_message_parts.append(Theme.F(Theme.MUTED_SYSTEM_INFO, "Docker project setup process completed (or was skipped/cancelled)."))

    elif identified_task and identified_task.intent == "RUN_EXISTING_IMAGE":
        final_message_parts.append(f"For your request: '{Theme.H_TEXT(user_query)}' (Run Existing Image)")
        selected_img = state.get('selected_image_to_run', 'Not specified')
        final_message_parts.append(f"Image: {Theme.F(Theme.HIGHLIGHT, selected_img)}")
        if command_executed_by_agent:
             final_message_parts.append(f"Attempted command: {Theme.F(Theme.COMMAND, command_executed_by_agent)}")
        if output and output.strip(): # This is output from `docker run`
            if len(output.strip().splitlines()) == 1 and len(output.strip()) == 64 and all(c in "0123456789abcdef" for c in output.strip()): # Likely a container ID
                 final_message_parts.append(f"Container ID: {Theme.F(Theme.SUCCESS, output.strip())}")
            else:
                 final_message_parts.append(f"Execution Output:\n{Theme.F(AnsiColors.DIM, output.strip())}")
        elif not error: # Avoid this message if an error occurred
            final_message_parts.append(Theme.F(Theme.MUTED_SYSTEM_INFO, "Command submitted to Docker. If run in detached mode (-d), check `docker ps` for status."))

    elif command_executed_by_agent:
        final_message_parts.append(f"For your request: '{Theme.H_TEXT(user_query)}'")
        if identified_task:
             final_message_parts.append(f"Identified task: {Theme.F(Theme.HIGHLIGHT, identified_task.intent)}")
             if identified_task.intent == "SEARCH_PULL_IMAGE_INTERACTIVE" and state.get("selected_image_for_pull"):
                 final_message_parts.append(f"Selected image for pull: {Theme.F(Theme.HIGHLIGHT, str(state['selected_image_for_pull']))}")

        final_message_parts.append(f"Executed command: {Theme.F(Theme.COMMAND, command_executed_by_agent)}")
        if output and output.strip():
             final_message_parts.append(f"Execution Output:\n{Theme.F(AnsiColors.DIM, output.strip())}")
        elif not error:
             final_message_parts.append(Theme.F(Theme.SUCCESS, "Command processed."))

    elif identified_task and identified_task.intent == "SEARCH_PULL_IMAGE_INTERACTIVE":
        final_message_parts.append(f"For your request: '{Theme.H_TEXT(user_query)}' (Search/Pull Image)")
        if state.get("selected_image_for_pull"):
            final_message_parts.append(f"Image involved in pull attempt: {Theme.F(Theme.HIGHLIGHT, str(state.get('selected_image_for_pull')))}")
        if output and output.strip(): # Output from the pull attempt
             final_message_parts.append(f"Details:\n{Theme.F(AnsiColors.DIM, output.strip())}")
        elif not error:
            final_message_parts.append(Theme.F(Theme.MUTED_SYSTEM_INFO, "Interactive image search/pull process completed or cancelled."))


    elif identified_task and identified_task.intent == "UNKNOWN" and not error:
        final_message_parts.append(
            Theme.F(Theme.WARNING, f"I couldn't determine a specific Docker action for: '{Theme.H_TEXT(user_query)}'. Please try rephrasing.")
        )
    else:
        final_message_parts.append(f"Processed request: '{Theme.H_TEXT(user_query)}'.")
        if output and output.strip():
            final_message_parts.append(f"Details:\n{Theme.F(AnsiColors.DIM, output.strip())}")
        elif not error:
            final_message_parts.append(Theme.F(Theme.MUTED_SYSTEM_INFO, "No specific command was run by the agent in this step, or the action was completed/cancelled interactively."))


    final_response_str = "\n".join(final_message_parts)
    # Strip color codes for v_print logging to keep it cleaner there
    plain_final_response = re.sub(r'\033\[[0-9;]*m', '', final_response_str)
    v_print(f"To User (from final_result_node, plain): {plain_final_response}")

    current_history = state.get("history", [])
    if not isinstance(current_history, list):
        v_print(f"Warning: History was not a list, reinitializing. Type was: {type(current_history)}")
        current_history = []

    ai_message = AIMessage(content=final_response_str) # Store themed response
    if not current_history or current_history[-1].content != ai_message.content:
        current_history.append(ai_message)

    return {**state, "history": current_history, "final_response_for_user": final_response_str}

# --- Workflow Definition ---
workflow = StateGraph(AgentState)
workflow.add_node("list_local_images_node", list_local_images_node)
workflow.add_node("list_containers_node", list_containers_node)

workflow.add_node("classify_intent_node", classify_intent_node)
workflow.add_node("interactive_image_search_node", interactive_image_search_and_pull_node)
workflow.add_node("docker_project_creation_node", docker_project_creation_node)
workflow.add_node("find_image_and_prepare_run_node", find_image_and_prepare_run_node)
workflow.add_node("generate_command_node", generate_command_node)
workflow.add_node("execute_command_node", execute_command_node)
workflow.add_node("final_result_node", final_result_node)

workflow.set_entry_point("classify_intent_node")

workflow.add_conditional_edges(
    "classify_intent_node",
    route_after_classification,
    {
        "list_local_images_node": "list_local_images_node",      # Added mapping
        "list_containers_node": "list_containers_node",          # Added mapping
        "interactive_image_search_node": "interactive_image_search_node",
        "docker_project_creation_node": "docker_project_creation_node",
        "find_image_and_prepare_run_node": "find_image_and_prepare_run_node",
        "generate_command_node": "generate_command_node",
        "final_result_node": "final_result_node" # Fallback / error route
    }
)

workflow.add_edge("interactive_image_search_node", "final_result_node")
workflow.add_edge("docker_project_creation_node", "final_result_node")

workflow.add_conditional_edges(
    "find_image_and_prepare_run_node",
    should_execute_command,
    {
        "execute_command_node": "execute_command_node",
        "final_result_node": "final_result_node"
    }
)

workflow.add_edge("list_local_images_node", "final_result_node")
workflow.add_edge("list_containers_node", "final_result_node")

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
    global app
    import getpass
    import shutil
    if llm is None:
        print(Theme.F(Theme.ERROR, "LLM not initialized. Cannot start Docker Assistant."))
        return

    try:
        username = getpass.getuser()
    except Exception:
        username = "User"

    assistant_name = "Docky" # Docker Assistant Name (or keep Vigi if you prefer)
    docker_emoji = "🐳" # Docker whale emoji

    thread_id_counter = 0

    # --- Welcome Message ---
    terminal_width = shutil.get_terminal_size().columns

    # Header using Docker blue (assuming defined in Theme) or fallback
    header_color = getattr(Theme, "DOCKER_BLUE", Theme.SYSTEM_INFO) # Use DOCKER_BLUE if defined
    section_header_style = getattr(Theme, "SECTION_DOCKER_HEADER", Theme.SECTION_HEADER)

    welcome_header = f"{docker_emoji} {assistant_name} Shell {docker_emoji}" # Centered Header
    welcome_line1 = "Your AI-Powered Docker Assistant"
    welcome_line2 = "Ask about Docker, manage images, containers, and more!"
    welcome_line3 = "Examples: 'pull ubuntu', 'list my images', 'dockerize python app'"
    welcome_line4 = "Type 'quit' or 'exit' to leave the shell."
    separator_char = "═" # Double line for a bit more "robust" feel
    separator_line = separator_char * (min(terminal_width - 6, 60)) # Shorter, more contained separator

    print(f"\n{Theme.F(section_header_style, welcome_header.center(terminal_width))}")
    print(f"{Theme.F(header_color, welcome_line1.center(terminal_width))}") # Use docker_blue
    print(f"{Theme.F(Theme.MUTED_SYSTEM_INFO, welcome_line2.center(terminal_width))}")
    print(f"{Theme.F(AnsiColors.DIM, welcome_line3.center(terminal_width))}") # Dim examples slightly
    print(f"{Theme.F(AnsiColors.DIM, welcome_line4.center(terminal_width))}")
    print(f"{Theme.F(AnsiColors.DIM, separator_line.center(terminal_width))}\n")

    if config.VERBOSE:
        llm_info_str = LLM_PROVIDER.upper()
        if LLM_PROVIDER.lower() in config.LLM_CONFIGS:
            model_name = config.LLM_CONFIGS[LLM_PROVIDER.lower()].get("model_name", "Unknown Model")
            llm_info_str += f" ({model_name})"
        print(Theme.F(Theme.VERBOSE_PREFIX, f" LLM Active: {llm_info_str}\n"))

    current_history: List[Any] = []

    # --- Prompts ---
    prompt_arrow_style = getattr(Theme, "PROMPT_ARROW", AnsiColors.BRIGHT_CYAN) # Configurable arrow color
    prompt_arrow = "╰┈➤" # Unicode arrow from your design
    user_emoji = "👤" # Simple user emoji

    # User Prompt: 👤 nouman ╰┈➤
    user_prompt_display = (
        f"\n{Theme.F(Theme.USER_PROMPT, f'{user_emoji} {username}')} "
        f"{Theme.F(prompt_arrow_style, prompt_arrow)} "
    )

    # AI Prompt: 🐳 Docky ╰┈➤
    ai_prompt_prefix = (
        f"\n{Theme.F(getattr(Theme, 'DOCKER_BLUE', Theme.AI_PROMPT), f'{docker_emoji} {assistant_name}')} "
        f"{Theme.F(prompt_arrow_style, prompt_arrow)}\n"
    )


    while True:
        try:
            user_input = input(user_prompt_display).strip()
        except KeyboardInterrupt:
            print(Theme.F(Theme.WARNING, "\nExiting Docker Assistant..."))
            break
        if user_input.lower() in ["exit", "quit"]:
            print(Theme.F(Theme.SYSTEM_INFO, f"Goodbye from {assistant_name}! {docker_emoji}"))
            break
        if not user_input:
            continue
        # Help command removed as info is in the banner now

        thread_id_counter += 1
        config_for_run = {"configurable": {"thread_id": str(thread_id_counter)}}

        current_history.append(HumanMessage(content=user_input))
        initial_agent_state: AgentState = { # type: ignore
            "user_query": user_input, "history": list(current_history), "identified_task": None,
            "docker_command": None, "command_output": None, "error_message": None,
            "image_search_keyword": None, "image_options": None, "selected_image_for_pull": None,
            "final_response_for_user": None, "project_directory": None, "dockerfile_content": None,
            "dockerignore_content": None, "generated_build_command": None, "generated_run_command": None,
            "selected_image_to_run": None,
        }

        processing_gear = "⚙️" # Gear emoji for processing
        processing_indicator = Theme.F(AnsiColors.DIM, f"{processing_gear} {assistant_name} is working...")
        print(processing_indicator, end='\r')

        v_print(f"Invoking app.stream: '{user_input}' (Thread: {thread_id_counter})", level="debug")
        final_graph_output_state = None
        try:
            for event_value in app.stream(initial_agent_state, config=config_for_run, stream_mode="values"):
                v_print(f"Stream event: {list(event_value.keys() if isinstance(event_value, dict) else 'Non-dict')}", level="debug")
                final_graph_output_state = event_value
            print(" " * (len(processing_indicator) + 10), end='\r') # Clear line effectively
        except Exception as e:
            print(" " * (len(processing_indicator) + 10), end='\r')
            error_message_raw = f"An unexpected error occurred: {e}"
            error_message_themed = Theme.F(Theme.ERROR, error_message_raw)
            print(f"{ai_prompt_prefix}{error_message_themed}")
            v_print(f"Graph error: {e}", exc_info=config.VERBOSE)
            current_history.append(AIMessage(content=error_message_themed))
            continue

        if isinstance(final_graph_output_state, dict):
            ai_response_text = final_graph_output_state.get("final_response_for_user")
            if ai_response_text is None:
                ai_response_text = Theme.F(Theme.WARNING, "I don't have a specific Docker response for that right now.")
            print(f"{ai_prompt_prefix}{ai_response_text}") # AI response from final_result_node

            updated_history = final_graph_output_state.get("history")
            if isinstance(updated_history, list): current_history = updated_history
            else: current_history.append(AIMessage(content=ai_response_text or "Task processed."))
        else:
            fallback_msg = Theme.F(Theme.WARNING, "Assistant had an issue structuring the response.")
            print(f"{ai_prompt_prefix}{fallback_msg}")
            current_history.append(AIMessage(content=fallback_msg))
def perform_startup_checks_cli():
    v_print(Theme.F(Theme.STATUS, "Performing startup checks..."))
    all_ok = True
    try:
        v_print("Attempting to start Docker Desktop if applicable...")
        docker_start()
        if platform.system() in ["Windows", "Darwin"]:
            v_print("Waiting for Docker to potentially initialize...", level="debug")
            time.sleep(2) # 'time' must be imported

        def check_command(label, cmd_args, check_msg="OK", fail_msg="Failed"):
            nonlocal all_ok
            v_print(f"Checking: {label}...", end=" ")
            try:
                if config.VERBOSE:
                    # If verbose, let output go to terminal, don't capture
                    subprocess.run(cmd_args, check=True, text=True, timeout=10)
                else:
                    # If not verbose, capture output to suppress it from user screen
                    subprocess.run(cmd_args, check=True, capture_output=True, text=True, timeout=10)

                v_print(Theme.F(Theme.SUCCESS, check_msg)) # This only prints if VERBOSE is True
            except Exception as e:
                v_print(Theme.F(Theme.ERROR, f"{fail_msg} ({e})"))
                print(Theme.F(Theme.ERROR, f"Startup Error ({label}): {e}")) # User sees specific error
                all_ok = False

        check_command("Docker version", ["docker", "--version"])
        check_command("Docker daemon responsiveness", ["docker", "system", "info", "--format", "{{.ID}}"])
        check_command("Docker Buildx", ["docker", "buildx", "version"])

        if 'questionary' not in globals():
            v_print(Theme.F(Theme.WARNING, "Questionary library seems missing (interactive features may be affected)."))
        else:
            v_print("Questionary library: OK")

        return all_ok

    except Exception as e:
        print(Theme.F(Theme.ERROR, f"A critical error occurred during startup checks: {e}"))
        v_print("Unexpected critical startup error", exc_info=config.VERBOSE)
        return False

def docker_main(llm_provider_arg = 'gemini'):
    colorama.init(autoreset=True) # Initialize Colorama here
    global llm
    global LLM_PROVIDER

    LLM_PROVIDER = llm_provider_arg
    try:
        initialize_llm(LLM_PROVIDER)
    except ValueError as e: # Error already themed by initialize_llm
        print(f"FATAL: Could not initialize LLM on startup: {e}") # e is already themed.
        print(Theme.F(Theme.WARNING,"Please check your environment variables and config.py settings."))
        llm = None

    if llm is None:
        print(Theme.F(Theme.ERROR, "Exiting application due to LLM initialization failure (see errors above)."))
    elif perform_startup_checks_cli():
        try:
            run_conversation_cli()
        except Exception as e:
            print(Theme.F(Theme.ERROR, f"\nAn unexpected error occurred in the main conversation loop: {e}"))
            v_print(f"Main loop error: {e}", exc_info=True)
    else:
        print(Theme.F(Theme.ERROR, "Exiting application due to failed startup checks (see errors above)."))


if __name__ == "__main__":
    # This colorama init is mostly for the main script's direct prints if not calling docker_main immediately.
    # docker_main will also call it.
    colorama.init(autoreset=True)

    default_provider = "groq" if os.getenv("GROQ_API_KEY") else "gemini"

    import sys
    selected_provider = default_provider
    if len(sys.argv) > 1 and sys.argv[1].lower() in config.LLM_CONFIGS:
        selected_provider = sys.argv[1].lower()
        print(Theme.F(Theme.SYSTEM_INFO,f"Using LLM provider from command line argument: {selected_provider.upper()}"))
    else:
        selected_provider = os.getenv("ASSISTANT_LLM_PROVIDER", default_provider).lower()
        print(Theme.F(Theme.SYSTEM_INFO,f"Using LLM provider (from env or default): {selected_provider.upper()}"))

    docker_main(llm_provider_arg=selected_provider)

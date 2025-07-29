# ai_shell_gemini/agents.py
import platform
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder
)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from typing import Optional, Dict, List, Any
import json
import traceback
import os
import subprocess

from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv

from rich.console import Console as RichConsole
from .state import AgentState, SystemConfigDetails

agent_console = RichConsole()
load_dotenv()
MAX_RETRY_ATTEMPTS = 2 # Reduced for testing, can be 2 or 3

# --- API Call Counter ---
class APICallCounter:
    def __init__(self):
        self.count = 0
    def increment(self):
        self.count += 1
    def reset(self):
        self.count = 0
    def get_count(self):
        return self.count

api_call_counter = APICallCounter()

class LLMApiCallCounterCallback(BaseCallbackHandler):
    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> Any:
        """Run when LLM starts running."""
        api_call_counter.increment()

llm = None
search_tool = None
llm_callbacks = [LLMApiCallCounterCallback()]

try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.1,
        timeout=120,
        callbacks=llm_callbacks,
       
    )
except Exception as e:
    agent_console.print(f"[bold red]CRITICAL:[/bold red] Error initializing LLM. Ensure GOOGLE_API_KEY is set correctly: {e}")

try:
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if tavily_api_key:
        search_tool = TavilySearchResults(max_results=2)
except Exception as e:
    agent_console.print(f"[bold yellow]WARNING:[/bold yellow] Error initializing Tavily Search: {e}. Web search disabled.")

def get_os_type_node(state: AgentState) -> AgentState:
    if state.get("os_type"):
        return {"os_type": state["os_type"], "is_error": False}
    if llm is None: return {"is_error": True, "error_message": "LLM not initialized."}
    os_map = {"Linux": "linux", "Darwin": "macos", "Windows": "windows"}
    system_platform = platform.system()
    detected_os = os_map.get(system_platform, "unknown")
    agent_console.print(f"OS Detected: [bold sky_blue1]{detected_os}[/bold sky_blue1]")
    return {"os_type": detected_os, "is_error": False}

def code_generator_node(state: AgentState) -> AgentState:
    if state.get("user_feedback_for_clarification") is not None or \
       state.get("needs_dependency_check") or \
       state.get("needs_dependency_installation"):
        return {"generated_code_content": state.get("generated_code_content")}
    if state.get("is_error") or llm is None:
        return {"generated_code_content": None}
    original_query = state.get("original_query", "")
    prompt_text = (
        "You are an intelligent assistant. Analyze the user's query: '{query}'.\n"
        "Does this query *explicitly ask for the generation of a block of code* (e.g., a script, a program snippet, a configuration file content)?\n"
        "If code block generation is NOT required, respond with the exact string 'NO_CODE_NEEDED' and nothing else.\n"
        "If code block generation IS required, generate *only the code block(s) themselves*, fulfilling the user's request. "
        "If the request implies multiple files, provide the content for each file clearly labeled with a comment like '# filename.ext' immediately preceding the code block for that file.\n"
        "Do not add any explanations before or after the code block(s) or 'NO_CODE_NEEDED' string."
    )
    prompt_template = ChatPromptTemplate.from_template(prompt_text)
    code_gen_chain = prompt_template | llm | StrOutputParser()
    try:
        generated_output = code_gen_chain.invoke({"query": original_query}).strip()
        if generated_output == "NO_CODE_NEEDED":
            return {"generated_code_content": None}
        if generated_output.startswith("```") and generated_output.endswith("```"):
            lines = generated_output.splitlines()
            if len(lines) > 1 and (not lines[1].startswith("```") or not lines[-2].endswith("```")):
                 generated_output = "\n".join(lines[1:-1]).strip()
            else:
                 generated_output = generated_output[3:-3].strip()
        if not generated_output: return {"generated_code_content": None}
        return {"generated_code_content": generated_output}
    except Exception as e:
        agent_console.print(f"[bold red]Code Generation Exception:[/bold red] {e}. Assuming no code generated.")
        return {"generated_code_content": None}

def decide_search_needed_node(state: AgentState) -> AgentState:
    if state.get("user_feedback_for_clarification") is not None or \
       state.get("needs_dependency_check") or \
       state.get("needs_dependency_installation"):
        return {"needs_search": False}
    if state.get("is_error") or llm is None or search_tool is None or state.get("retry_attempt", 0) > 0:
        return {"needs_search": False}
    original_query = state.get("original_query", "")
    prompt_template = ChatPromptTemplate.from_messages([
        ("system",
         "You are an assistant determining if a user's query *absolutely requires* external web search to generate a shell command. "
         "Only say 'yes' if the query involves:\n"
         "- Specific non-standard tool names or software that isn't part of a common OS distribution.\n"
         "- A task that inherently requires up-to-the-minute information.\n"
         "For common tasks like 'list files', 'set brightness', say 'no'. "
         "Be very conservative; prefer 'no'. Respond with 'yes' or 'no'.\n"
         "If 'yes', on a new line, provide a concise web search query. Example:\nyes\ninstall specific tool XYZ Ubuntu 22.04"),
        ("human", "User query: '{query}'")
    ])
    chain = prompt_template | llm | StrOutputParser()
    try:
        response = chain.invoke({"query": original_query}).strip()
        lines = response.split('\n', 1)
        decision = lines[0].lower().strip()
        if decision == "yes" and len(lines) > 1 and lines[1].strip():
            search_q = lines[1].strip()
            return {"needs_search": True, "search_query": search_q}
        return {"needs_search": False}
    except Exception as e:
        agent_console.print(f"[bold red]Error in deciding search:[/bold red] {e}. Defaulting to no search.")
        return {"needs_search": False}

def perform_search_node(state: AgentState) -> AgentState:
    if not state.get("needs_search") or not state.get("search_query") or search_tool is None:
        return {"search_results": None, "search_summary": None, "user_confirmed_search_info": False}
    query = state.get("search_query","")
    original_query = state.get("original_query","")
    try:
        raw_results = search_tool.invoke(query)
        results_content = [item["content"] for item in raw_results if isinstance(item, dict) and "content" in item] if isinstance(raw_results, list) else [raw_results] if isinstance(raw_results, str) else []
        if not results_content:
            return {"search_results": raw_results, "search_summary": "Search returned no usable content.", "user_confirmed_search_info": False}
        summary_prompt_text = (
            "Based on the user's original query: '{original_query}', "
            "summarize key information from these search results for formulating a shell command. "
            "Focus on command examples, tool names, critical parameters. Concise (1-3 sentences max).\n\n"
            "Search Results Digest:\n"
        )
        for i, content_item in enumerate(results_content[:3]):
            safe_content = content_item.replace('{', '{{').replace('}', '}}')
            summary_prompt_text += f"{i+1}. {safe_content}\n"
        summary_prompt_obj = ChatPromptTemplate.from_template(summary_prompt_text)
        summary_chain = summary_prompt_obj | llm | StrOutputParser()
        search_summary = summary_chain.invoke({"original_query": original_query})
        return {"search_results": raw_results, "search_summary": search_summary, "user_confirmed_search_info": True}
    except Exception as e:
        agent_console.print(f"[bold red]Error during search execution or summarization:[/bold red] {e}")
        return {"search_results": None, "search_summary": f"Error during search: {str(e)}", "user_confirmed_search_info": False}

def _generate_command_attempt(
    intent: str,
    os_type: str,
    search_summary: Optional[str],
    previous_command: Optional[str],
    error_output: Optional[str],
    generated_code_content: Optional[str],
    state: AgentState,
    is_fallback_for_vagueness: bool = False,
    is_retry_for_file_not_found: bool = False,
    is_retry_for_search_failure: bool = False,
    user_feedback_for_clarification: Optional[str] = None,
    clarification_context: Optional[str] = None
) -> str:
    system_instruction_parts = []
    current_error_output_str = error_output if error_output is not None else ""
    previous_command_str = previous_command if previous_command is not None else "None"

    history_qna_instruction = (
        "\nIf the user's query is a direct question about the *content of the conversation history* "
        "(e.g., 'What was the output of the last command?', 'What did you just tell me?', 'What was the command you ran to do X?'), "
        "and the answer can be clearly determined from the `chat_history` provided (see prior AI messages for summaries/commands), "
        "output `CHAT_HISTORY_ANSWER: Your concise answer based *only* on the provided history.` "
        "Do not try to generate a new shell command for these types of meta-questions. "
        "If the history is empty or doesn't contain the answer for such a question, and no shell command is appropriate, it might be `NO_ACTION_NEEDED`."
    )
    non_actionable_instruction = (
        "\nIf the user's current goal/query is ONLY a simple greeting (e.g., 'hi', 'hello'), "
        "a non-task-oriented question that cannot be answered from conversation history (e.g., 'how are you?'), "
        "or a very vague statement for which NO shell command, file operation, system configuration, or history-based answer is appropriate, "
        "output the exact string `NO_ACTION_NEEDED` and nothing else. "
        "However, if the query contains misspellings but seems to describe a task, attempt to understand and fulfill that task.\n"
    )
    typo_resilience_instruction = (
        "Try to understand the user's intent for a shell command or system task even if there are minor misspellings "
        "or grammatical errors in their request. If the intent for a task is reasonably clear, attempt to generate the command."
    )
    json_linux_brightness = """
        {{
          "dependency_name": "brightnessctl",
          "dependency_install_command": "sudo apt-get update && sudo apt-get install -y brightnessctl",
          "dependency_check_command": "command -v brightnessctl",
          "command_if_dep_installed": "brightnessctl s 50%"
        }}
    """.strip()
    json_macos_brightness_example = """
        {{
          "dependency_name": "macbrightness",
          "dependency_install_command": "brew install macbrightness",
          "dependency_check_command": "command -v macbrightness",
          "command_if_dep_installed": "macbrightness set 0.5"
        }}
    """.strip()
    raw_system_config_instructions = (
        "\n\nSystem Configuration Tasks (e.g., 'set brightness to 50%'):\n"
        "1. If the query is a system configuration task for {os_type_placeholder}:\n"
        "   a. Native command? Output: `SYSTEM_CONFIG::NATIVE::the_native_command`\n"
        "   b. Requires dependency? Output: `SYSTEM_CONFIG::DEPENDENCY::JSON_DETAILS` (JSON with keys: "
        "\"dependency_name\", \"dependency_install_command\", \"dependency_check_command\", \"command_if_dep_installed\").\n"
        "      The value for \"command_if_dep_installed\" CAN BE AN EMPTY STRING if no further command is needed after installation/check (e.g., user just asked to 'install tool X').\n"
        "      Example JSON for Linux brightnessctl:\n"
        "{json_example_linux_brightness}\n"
        "      Example JSON for macOS 'macbrightness':\n"
        "{json_example_macos_brightness}\n"
        "2. Not system config? Generate commands as per other instructions.\n"
        "3. Is system config? ONLY output in `SYSTEM_CONFIG::` formats."
    )
    formatted_system_config_instructions = raw_system_config_instructions.format(
        os_type_placeholder=os_type,
        json_example_linux_brightness=json_linux_brightness,
        json_example_macos_brightness=json_macos_brightness_example
    )

    windows_specific_instructions = ""
    if os_type == "windows":
        windows_specific_instructions = (
            "\n**WINDOWS SPECIFIC INSTRUCTIONS:**\n"
            "1.  For **Windows**, prefer `cmd.exe` compatible commands unless the user explicitly asks for PowerShell or the task complexity inherently requires PowerShell.\n"
            "2.  To create an empty file in `cmd.exe`: `type nul > path\\to\\file.txt` or `echo. > path\\to\\file.txt`.\n"
            "3.  To create a directory: `mkdir path\\to\\directory`.\n"
            "4.  Avoid `New-Item`, `Get-ChildItem` (unless PowerShell is explicitly intended and context confirmed). "
            "If a previous `New-Item` command failed with 'not recognized', it means `cmd.exe` was used. Generate a `cmd.exe` alternative.\n"
            "5.  **`for` loop variables in `cmd.exe`:** When generating `for` loops directly for `cmd.exe` (i.e., not inside a .bat or .cmd script), loop variables MUST use a single percent sign (e.g., `%i`, `%a`). Double percent signs (e.g., `%%i`, `%%a`) are ONLY for batch scripts."
        )

    is_user_requested_search_retry = (
        user_feedback_for_clarification and
        user_feedback_for_clarification.lower().strip() in ["yes", "try again", "ok try again", "sure", "go ahead"] and
        clarification_context == "search_failed_clarification"
    )
    effective_retry_search = is_retry_for_search_failure or is_user_requested_search_retry

    strict_output_format_instruction = (
        "\n**CRITICAL OUTPUT FORMATTING:** Your entire output MUST be *only* the raw shell command itself "
        "(e.g., `ls -l`, `mkdir my_folder`), or one of the special keywords (`CHAT_HISTORY_ANSWER: ...`, "
        "`SYSTEM_CONFIG::...`, `NO_ACTION_NEEDED`, `USER_REQUESTED_SKIP`, `ERROR: ...`, `CLARIFICATION_NEEDED: Your question here.`).\n"
        "ABSOLUTELY DO NOT include any other text, explanations, markdown (like ```sh), "
        "or any conversational phrases like 'Okay, here is the command:' or 'Proposed command:' or 'Explanation:'. "
        "Your response should be directly executable or be one of the special keywords."
    )

    data_reuse_instruction = (
        "\n**Reusing Information from Chat History (CRITICAL FOR EFFICIENCY & ACCURACY):**\n"
        "Before generating any command, meticulously review the `chat_history`, particularly recent AI summaries of command executions or direct statements of fact by the AI.\n"
        "1.  **Identify Reusable Data:** If a previous AI message clearly states a specific piece of information that the current user query needs (e.g., an IP address, a full file path, a process ID, a specific setting value that was just confirmed/set), this data is potentially reusable.\n"
        "    - Example summary in history: 'Your IP address is 192.168.0.101.'\n"
        "    - Example user query: 'Write my IP address to the file foo.txt.'\n"
        "2.  **Prioritize Direct Use:** If such directly usable data is found AND it's recent and relevant to the current query:\n"
        "    a.  You **SHOULD** construct a command that uses this data *directly* (e.g., by embedding the literal value into the command).\n"
        "        - Correct approach for example (Windows): `echo 192.168.0.101 > \"%USERPROFILE%\\Desktop\\foo.txt\"`\n"
        "        - Correct approach for example (Linux/macOS): `echo '192.168.0.101' > ~/Desktop/foo.txt`\n"
        "    b.  You **SHOULD NOT** generate a command to re-acquire or re-calculate this information if it's already clearly stated and sufficient in the history.\n"
        "        - Incorrect approach for example: `ipconfig | findstr ... > foo.txt` (This re-runs a command unnecessarily if the IP is known).\n"
        "3.  **When to Re-acquire:** Only generate a command to re-acquire information if:\n"
        "    a.  The information is not present or is ambiguous in the chat history.\n"
        "    b.  The information is likely to be stale and the query implies needing the absolute latest value (e.g., 'what is my IP *now*?', 'check current disk space').\n"
        "    c.  The user explicitly asks to re-run a command.\n"
        "4.  **Clarity is Key:** If you use data from history, ensure the value is precise. If an AI summary mentioned multiple IPs (e.g., 'Your IPs are 10.0.0.5 and 192.168.1.100'), and the user just says 'my IP', you might need to ask for clarification, or pick the most relevant one based on context (e.g., the one associated with the primary active interface if discernible from history), or if highly uncertain, fall back to re-acquiring it with a robust command.\n"
        "This principle of reusing known, recent, and relevant information from conversation history is paramount. Avoid redundant actions."
    )
    information_retrieval_guideline = (
        "\n**Information Retrieval for the User:**\n" 
        "If the user requests specific information about *their own system or accounts* "
        "(e.g., network configuration, process details, hardware info), "
        "and a standard, non-destructive OS command exists to retrieve this information, "
        "you **SHOULD** generate that command. Prioritize commands that are known to be robust and directly output the desired information. "
        "When providing examples, especially for CMD.EXE, ensure they are directly executable if run standalone. If showing a `for /f` loop for parsing, the commands *inside* the `in ('...')` block might need specific escaping (e.g., `^` for special characters, `\"` for quotes if the outer quotes are single, etc.).\n"
        "Examples of robust commands for common tasks:\n"
        "  - **Linux IP Address (primary IPv4):** `hostname -I | awk '{{print $1}}'` (gets first IP if multiple) OR `ip -4 addr show scope global | awk '/inet / {{print $2}}' | cut -d/ -f1 | head -n 1`.\n"
        "  - **Linux IPv6 Address (example for a specific interface like eth0):** `ip -6 addr show dev eth0 | grep 'inet6 ' | awk '{{print $2}}' | cut -d/ -f1 | head -n 1`. Adapt interface name as needed or find a more general command if possible for the OS. If too complex or OS variant dependent, consider clarification.\n"
        "  - **macOS IP Address (primary IPv4, e.g., on en0):** `ipconfig getifaddr en0`. If 'en0' is not found, try common alternatives like 'en1'.\n"
        "  - **macOS IPv6 Address (example for en0):** `ipconfig getifaddr_v6 en0`.\n"
        "  - **Windows (CMD.EXE) IP Address:**\n"
        "    - To show IPv4 addresses for a specific, known interface (e.g., \"Ethernet\"): `netsh interface ipv4 show ipaddresses name=\"Ethernet\"`. The IP line from this output would be like '    IP Address:                           192.168.1.100'.\n"
        "    - To extract just the IP from the above for 'Ethernet' using a `for` loop (for direct cmd.exe execution): `for /f \"tokens=3\" %a in ('netsh interface ipv4 show ipaddresses name^=\"Ethernet\" ^| findstr \"IP Address:\"') do @echo %a`.\n"
        "    - To list all IPv4 configurations (user may need to select): `ipconfig | findstr \"IPv4 Address\"`.\n"
        "    - If PowerShell is contextually appropriate and a single primary IP is needed: `(Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias (Get-NetConnectionProfile).InterfaceAlias).IPAddress` is preferred.\n"
        "  - **Windows (CMD.EXE) Wi-Fi Password (for profile 'MyNet'):** `netsh wlan show profile name=\"MyNet\" key=clear`.\n"
        "Do not refuse solely on the basis that it's 'sensitive' if it's their own data and a direct command exists. "
        "Avoid commands that are overly fragile or rely on unstable output formatting if better alternatives exist." 
    )

    clarification_instruction = (
        "\n**Requesting Clarification (If Absolutely Necessary):**\n"
        "1. Your primary goal is to generate a shell command to fulfill the user's request. If the request involves retrieving information, attempt to generate a command to do so (see 'Information Retrieval for the User' guidelines).\n"
        "2. If, and only if, you CANNOT retrieve essential information with a command (e.g., the information is not discoverable via a standard OS command, it's a user-specific secret like a password not stored by the system, or you are very unsure how to get specific info like a particular type of IPv6 address on this OS and history/search doesn't help), "
        "AND this information is CRITICAL to proceed with the user's explicit task, then you MUST output `CLARIFICATION_NEEDED: Your concise question to the user.`\n"
        "   - Example Scenario: User asks to 'append my work server's IP to the file', but 'work server IP' is not in history and not discoverable by a general command. Output: `CLARIFICATION_NEEDED: What is the IP address of your work server?`\n"
        "   - Example Scenario: User query: 'Find all .log files modified by user \"bob\" last Tuesday and zip them with password \"mysecret\".' If you cannot determine 'last Tuesday' reliably or zipping with password requires a specific tool check. Output: `CLARIFICATION_NEEDED: To confirm, what was the exact date for 'last Tuesday'? Also, do you have a preferred tool for password-protected zipping (e.g., 7zip, zip)?`\n"
        "3. Only use `CLARIFICATION_NEEDED:` as a last resort when you are blocked. Do not use it for simple confirmations if you can make a reasonable assumption or if the task is inherently safe. If the user's request is too vague to form any command, you might respond with `NO_ACTION_NEEDED` or `ERROR: Query too vague...` as per other instructions, rather than `CLARIFICATION_NEEDED:` for very general vagueness."
    )


    if user_feedback_for_clarification and not is_user_requested_search_retry:
        system_instruction_parts.extend([
            f"You are an expert shell command generation AI for {os_type} systems.",
            data_reuse_instruction, 
            f"The user's original query (before clarification) was: \"{intent.replace('{', '{{').replace('}', '}}')}\".",
            "You previously asked for clarification.",
            f"User Feedback: \"{user_feedback_for_clarification.replace('{', '{{').replace('}', '}}')}\"",
            clarification_instruction, 
            information_retrieval_guideline,
            "\nYour primary goal now is to generate a shell command to **FULFILL THE ORIGINAL INTENT** using the feedback.",
            windows_specific_instructions if os_type == "windows" else "",
            non_actionable_instruction, typo_resilience_instruction,
            "If you cannot proceed, output 'ERROR: Cannot proceed with feedback: [reason].'"
        ])
    elif effective_retry_search:
        retry_search_instructions = [
            f"You are an expert shell command generation AI for {os_type} systems.",
            f"The previous SEARCH/LIST command ` {previous_command_str.replace('{', '{{').replace('}', '}}')} ` on **{os_type}** failed or found no results. Error (if any): ` {current_error_output_str.replace('{', '{{').replace('}', '}}')} `.",
            f"The user's original intent was: \"{intent.replace('{', '{{').replace('}', '}}')}\". The user wants to try a different approach to this search.",
            f"Generate a *new and different* search or list command suitable for **{os_type}**. **CRITICALLY, DO NOT repeat or slightly modify the previous failed command `{previous_command_str.replace('{', '{{').replace('}', '}}')}`.** You MUST suggest a distinct alternative. Analyze the error: if it was 'unknown primary or operator' for `find`, the `-printf` option is likely the issue on this OS ({os_type}).",
            "Common file search tools and correct syntax:",
            "  - **Linux:** `find <path> -type f -name \"*.txt\" -printf \"%s %p\\n\"` (GNU find is common). Or `find <path> -ls`. `locate '*.txt'`. `grep -r 'pattern' /path`.",
            "  - **macOS:** `mdfind -name '*.txt' -onlyin <path>` for Spotlight. For `find`: `find <path> -type f -name \"*.txt\" -ls` (for general listing) OR `find <path> -type f -name \"*.txt\" -print0 | xargs -0 stat -f '%z %N'` (for size and name). **On macOS, `find` DOES NOT support `-printf`. Use `-ls` or `-exec stat ...` instead for metadata.**",
            "  - **Windows:** PowerShell: `Get-ChildItem -Path <path> -Filter '*.txt' -Recurse | Select-Object Length, FullName, LastWriteTime`. CMD: `dir /s /b <path>\\*.txt`.",
            "If the original query was complex (e.g., 'content of largest text file'), and the find part failed: **FIRST, focus on reliably *finding and listing the file(s) with relevant metadata (like size for 'largest')*** with this retry. Do NOT try to cat or process content in the same command if the listing part is tricky. Let the user see the list first.",
            "Ensure the output is prefixed with `SEARCH_COMMAND_ACTION: `.",
            "If unable to formulate a genuinely different and better search, output 'ERROR: Cannot formulate alternative search/list command.'"
        ]
        system_instruction_parts.extend(retry_search_instructions)
    elif is_retry_for_file_not_found:
        system_instruction_parts.extend([
            f"You are an expert shell command generation AI for {os_type} systems.",
            f"Previous DIRECT ACTION command ` {previous_command_str.replace('{', '{{').replace('}', '}}')} ` failed: file not found (` {current_error_output_str.replace('{', '{{').replace('}', '}}')} `).",
            f"User's intent: \"{intent.replace('{', '{{').replace('}', '}}')}\".",
            "Generate a *new shell command to locate the missing file/folder* relevant to the original intent. This command should be a search/listing command.",
            f"Use OS-appropriate tools for **{os_type}** (see search tool examples above).",
             windows_specific_instructions if os_type == "windows" else "",
            "If unable, output 'ERROR: Cannot formulate a search command for the missing file.'"
        ])
    elif generated_code_content:
        escaped_llm_code_content = generated_code_content.replace("{", "{{").replace("}", "}}")
        system_instruction_parts.extend([
            f"You are an expert shell command generation AI for {os_type} systems.",
            data_reuse_instruction, 
            f"User's request: \"{intent.replace('{', '{{').replace('}', '}}')}\"",
            "Pre-generated code content:", "--- CODE CONTENT START ---", escaped_llm_code_content, "--- CODE CONTENT END ---",
            clarification_instruction, 
            information_retrieval_guideline,
            "\nGenerate a *single chained shell command* to set up the project.",
            f"Use correct {os_type} path format.",
            windows_specific_instructions if os_type == "windows" else "",
            "\nIf unclear, output 'ERROR: Cannot generate commands from provided code content.'",
        ])
    else: # Standard path
        system_instruction_parts.extend([
            f"You are an exceptionally skilled shell command generation AI for {os_type} systems. Goal: translate user intent into accurate, effective, safe shell commands for **{os_type}**.",
            data_reuse_instruction, 
            clarification_instruction, 
            information_retrieval_guideline,
            "Capabilities: file/dir ops, process mgmt, system status/info, basic networking, env mgmt, system config.",
            typo_resilience_instruction,
            history_qna_instruction,
            non_actionable_instruction,
            windows_specific_instructions if os_type == "windows" else "",
            formatted_system_config_instructions,
            "\nFor non-system-config tasks (if not NO_ACTION_NEEDED or CHAT_HISTORY_ANSWER or CLARIFICATION_NEEDED):",
            "If location specified, `cd` there first using `&&`.",
            f"For finding/locating files/text on {os_type}, prefix command with `SEARCH_COMMAND_ACTION: `.",
            f"   Use appropriate tools for **{os_type}**.",
            "For other actions, generate command directly.",
            f"If a query is complex, like 'find the largest/longest file AND show its content', for **{os_type}**: ",
            "STRONGLY PREFER a two-step approach if a single chained command is prone to errors on this OS:\n"
            "  1. First, generate ONLY the `SEARCH_COMMAND_ACTION:` to reliably find and list the target file(s) along with necessary metadata (e.g., size). The output should clearly show the file path.\n",
            ( "     Example for finding largest files on macOS (lists top 5 size and path): "
              "`SEARCH_COMMAND_ACTION: find ~/Desktop -type f -name '*.txt' -print0 | xargs -0 stat -f '%z %N' | sort -nr | head -n 5`"
              if os_type == "macos" else
              "     Example for finding largest files on Linux (lists top 5 size and path): "
              "`SEARCH_COMMAND_ACTION: find ~/Desktop -type f -name '*.txt' -printf '%s %p\\n' | sort -nr | head -n 5`"
              if os_type == "linux" else
              f"     Example for finding largest files on {os_type} (CMD.exe: `forfiles /P %USERPROFILE%\\Desktop /M *.txt /S /C \"cmd /c echo @fsize @path\" | sort /R | findstr /V /B /C:\"@fsize\" | more +4` if you need to skip header, else simpler `dir /S /B /O-S %USERPROFILE%\\Desktop\\*.txt` then process). (PowerShell, lists top 5 size and path): "
              "`SEARCH_COMMAND_ACTION: Get-ChildItem ~/Desktop -Filter '*.txt' -Recurse | Sort-Object Length -Descending | Select-Object -First 5 Length,FullName`"
              if os_type == "windows" else
              f"     For {os_type}, devise a command to list files by size, largest first. "
            ),
            "  2. After this command lists files, the user can then issue a NEW, SEPARATE query like 'show content of /path/to/that/file.txt'.\n"
            f"Only attempt a single, chained command (e.g., with `... | xargs cat` or similar complex piping for processing) if you are VERY confident it's simple, common, and robust for **{os_type}**. If there's any doubt, use the two-step approach for finding/listing first."
        ])
        if search_summary:
            safe_search_summary = search_summary.replace('{', '{{').replace('}', '}}')
            system_instruction_parts.append(f"\nWeb Search Context (Use if relevant, otherwise ignore):\n{safe_search_summary}")

    if previous_command and current_error_output_str and \
       not any([is_retry_for_file_not_found, effective_retry_search, user_feedback_for_clarification, generated_code_content]):
        safe_prev_cmd = previous_command.replace('{', '{{').replace('}', '}}')
        safe_err_out = current_error_output_str.replace('{', '{{').replace('}', '}}')

        critical_error_instructions = [
            f"\nCRITICAL: Previous command ` {safe_prev_cmd} ` failed (` {safe_err_out or '(No error output)'} `) for reason other than 'file not found' or 'search failure'."
        ]
        
        common_shell_keywords = [
            "sudo", "apt", "yum", "dnf", "pacman", "zypper", 
            "ls", "cd", "pwd", "mkdir", "rm", "mv", "cp", "touch", "cat", "less", "more", "head", "tail", 
            "grep", "find", "awk", "sed", "sort", "uniq", "wc", 
            "echo", "printf", "read", 
            "curl", "wget", "ping", "ssh", "scp", "ftp", "rsync", 
            "git", "svn", 
            "docker", "podman", "kubectl", "oc", 
            "az", "aws", "gcloud", "ibmcloud", 
            "terraform", "ansible", "chef", "puppet", "vagrant", 
            "make", "cmake", "gcc", "g++", "clang", "javac", "java", "mvn", "gradle", 
            "python", "python3", "node", "npm", "yarn", "pip", "pip3", "ruby", "gem", "bundle", "perl", "php", "composer", "go", "rustc", "cargo", 
            "systemctl", "service", "launchctl", "brew", 
            "tar", "zip", "unzip", "gzip", "gunzip", "bzip2", "7z", 
            "df", "du", "free", "top", "htop", "ps", "kill", "bg", "fg", "jobs", 
            "chmod", "chown", "chgrp", "useradd", "usermod", "userdel", "groupadd", 
            "date", "sleep", "watch", "cron", "at", 
            "man", "help", "info", 
            "alias", "unalias", "export", "unset", "source", "exit", 
            "dir", "copy", "del", "ren", "md", "rd", "type", "cls", "ver", "set", "path", "assoc", "ftype", 
            "ipconfig", "netstat", "tasklist", "taskkill", "schtasks", "sc", "reg", "shutdown", "wevtutil", "bitsadmin", "certutil", "diskpart", "format", "label", "mode", "print", "runas", "subst", "systeminfo", "tree", "fc", "comp", "expand", "replace", "xcopy", "robocopy", "net", "wmic",
            "powershell", "pwsh", 
            "Get-", "Set-", "New-", "Remove-", "Add-", "Update-", "Invoke-", "Test-", "Resolve-", "Start-", "Stop-", 
            "Enable-", "Disable-", "Register-", "Unregister-", "Export-", "Import-", "Out-", "Format-", "Select-", "Sort-", 
            "Where-", "ForEach-Object", "Group-Object", "Measure-Object", "Compare-Object", "Convert-", "ConvertTo-", 
            "ConvertFrom-", "Read-Host", "Write-Output", "Write-Host", "Write-Error", "Write-Warning", "Write-Verbose", "Write-Debug",
            "Start-Sleep", "Start-Process", "Stop-Process", "Get-Process", "Get-Service", "Start-Service", "Stop-Service", "Restart-Service",
            "Get-ChildItem", "Get-Content", "Set-Content", "Add-Content", "Clear-Content", "Copy-Item", "Move-Item", "Remove-Item", "New-Item", "Rename-Item",
            "Get-Location", "Set-Location", "Push-Location", "Pop-Location",
            "Test-Path", "Resolve-Path",
            "Get-Command", "Get-Help", "Update-Help", "Save-Help",
            "Get-NetIPAddress", "Get-NetAdapter", "New-NetRoute", "Test-Connection", "Invoke-WebRequest", "Invoke-RestMethod"
        ]
        is_likely_natural_language_failure = True
        # Ensure previous_command_str is not None before using it.
        # The previous_command_str is already defined at the top of the function.
        if previous_command_str and previous_command_str != "None":
            first_word_of_prev_cmd = previous_command_str.split(" ", 1)[0].lower()
            if first_word_of_prev_cmd in [kw.lower() for kw in common_shell_keywords]:
                 is_likely_natural_language_failure = False
            elif any(previous_command_str.lower().startswith(kw.lower()) for kw in common_shell_keywords if '-' in kw or '\\' in kw or '/' in kw):
                 is_likely_natural_language_failure = False

        if "Proposed Command Preview:" in previous_command_str or "Purpose:" in previous_command_str or "Explanation:" in previous_command_str :
            critical_error_instructions.append(
                "The previous command seems to be a malformed attempt to execute a command preview or explanation text. "
                "This is a critical error in your previous generation. "
                "You MUST now generate ONLY the raw shell command based on the user's original intent: '{intent}'. "
                "DO NOT repeat any part of the previous erroneous command. Focus solely on the user's task."
            )
        elif is_likely_natural_language_failure and previous_command_str and previous_command_str != "None" and \
          ( (current_error_output_str.endswith(": not found") or "command not found" in current_error_output_str.lower() or "is not recognized" in current_error_output_str.lower()) and \
            not previous_command_str.strip().startswith("$") and not previous_command_str.strip().startswith("%") ):
            critical_error_instructions.append(
                f"The previous input ` {previous_command_str[:70].replace('{', '{{').replace('}', '}}')}... ` "
                "resulted in a 'not found' or 'not recognized' error. This suggests it might have been a descriptive sentence or question, not an executable command. "
                f"Please re-evaluate the original user intent: \"{intent.replace('{', '{{').replace('}', '}}')}\". "
                "If you need specific information from the user to form a valid command for this intent, "
                "output `CLARIFICATION_NEEDED: Your concise question to the user.` "
                "Otherwise, attempt to generate the correct shell command for the original intent. Do not repeat the failed input."
            )
        elif os_type == "windows" and ("not recognized" in current_error_output_str or "is not recognized" in current_error_output_str):
            critical_error_instructions.append(
                "This error on Windows often means a PowerShell command was attempted in `cmd.exe` or a command is misspelled/not in PATH. "
                "If the failed command looks like PowerShell (e.g., `New-Item`, `Get-ChildItem`), generate a `cmd.exe` equivalent if possible. "
                "For `cmd.exe` file creation: `type nul > path\\to\\file.txt` or `echo. > path\\to\\file.txt`. For directories: `mkdir path\\to\\dir`."
            )
        elif os_type == "windows" and "was unexpected at this time" in current_error_output_str.lower() and previous_command_str and "%%" in previous_command_str and "for " in previous_command_str.lower():
            critical_error_instructions.append(
                "The error 'was unexpected at this time' combined with a `for` loop containing `%%` variables (e.g., `%%a`) "
                "strongly suggests the command was intended for direct `cmd.exe` execution but used batch script syntax for loop variables. "
                "For direct execution in `cmd.exe` (not in a .bat or .cmd script), `for` loop variables MUST use a single percent sign (e.g., `%a`, `%i`). "
                "Please regenerate the command using single percent signs for all `for` loop variables. Ensure the logic to extract the correct information (e.g., the IP address, not just 'IPv4') is sound."
            )
        critical_error_instructions.append(
             "Analyze the error and the original user intent: \"{intent}\". If you can fix the command or generate a new one for the intent, do so. "
             "If you need clarification from the user to fulfill the original intent, use `CLARIFICATION_NEEDED: Your question.` "
             "If you cannot proceed, output 'ERROR: Cannot fix command based on previous error or re-attempt intent.'"
        )
        system_instruction_parts.extend(critical_error_instructions)

    system_instruction_parts.append(strict_output_format_instruction) 

    final_system_message_content = "\n".join(filter(None, system_instruction_parts))

    prompt_template_obj = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(final_system_message_content),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        HumanMessagePromptTemplate.from_template("{intent}")
    ])

    invoke_input_dict = {"intent": intent}
    chat_history_messages = state.get("chat_memory_messages")
    if chat_history_messages:
        invoke_input_dict["chat_history"] = chat_history_messages
    
    try:
        generator_chain = prompt_template_obj | llm | StrOutputParser()
        command = generator_chain.invoke(invoke_input_dict).strip()
        return command
    except Exception as e:
        agent_console.print(f"[bold red]LLM Invocation Exception during _generate_command_attempt:[/bold red] {e}")
        tb_str = traceback.format_exc()
        if isinstance(e, KeyError) and "Input to ChatPromptTemplate is missing variables" in str(e):
            agent_console.print("[bold red]--- DETECTED LANGCHAIN KEYERROR ---[/bold red]")
            agent_console.print(f"System Message Content given to SystemMessagePromptTemplate.from_template():\n{final_system_message_content[:2000]}...")
            agent_console.print(f"Invoke Input Dict given to LangChain chain: {invoke_input_dict}")
        return f"ERROR: LLM Invocation Failed during command generation: {str(e)}\nTraceback:\n{tb_str}"

def command_generator_node(state: AgentState) -> AgentState:
    if state.get("is_error") or llm is None:
        return {"is_error": True, "error_message": state.get("error_message", "LLM not initialized or error before command generation."), "needs_retry": False}

    intent = state.get("parsed_intent", state.get("original_query", ""))
    os_type = state.get("os_type", "")

    user_feedback_str = state.get("user_feedback_for_clarification")
    clarification_ctx_str = state.get("clarification_context")

    is_explicit_search_retry_from_feedback = (
        user_feedback_str is not None and
        user_feedback_str.lower().strip() in ["yes", "try again", "ok try again", "sure", "go ahead"] and
        clarification_ctx_str == "search_failed_clarification"
    )

    effective_is_retry_for_search_failure = (state.get("needs_retry") and state.get("is_trying_file_search")) or \
                                            is_explicit_search_retry_from_feedback

    previous_execution_stderr = state.get("execution_stderr","")
    attempting_file_not_found_retry_for_direct_action = (
        state.get("needs_retry") and
        state.get("generated_command_purpose") in ["direct_action", "system_config_action", "direct_action_after_feedback"] and
        any(phrase in previous_execution_stderr.lower() for phrase in ["no such file", "cannot find the file", "not found"]) and
        not state.get("is_trying_file_search")
    )
    
    effective_previous_command = state.get("executed_command")
    effective_error_output = previous_execution_stderr

    if state.get("needs_retry") and effective_previous_command:
        if "Proposed Command Preview:" in effective_previous_command or \
           "Purpose:" in effective_previous_command or \
           "Explanation:" in effective_previous_command:
            agent_console.print("[bold yellow]Command Gen Retry: Previous command looked like preview text. Sanitizing for LLM.[/bold yellow]")
            effective_previous_command = f"(Malformed previous command attempt: {effective_previous_command[:100]}...)" 
            effective_error_output = state.get("error_message", previous_execution_stderr) 

    command_str = _generate_command_attempt(
        intent=intent,
        os_type=os_type,
        search_summary=state.get("search_summary"),
        previous_command=effective_previous_command, 
        error_output=effective_error_output,       
        generated_code_content=state.get("generated_code_content"),
        state=state,
        is_fallback_for_vagueness=False,
        is_retry_for_file_not_found=attempting_file_not_found_retry_for_direct_action,
        is_retry_for_search_failure=effective_is_retry_for_search_failure,
        user_feedback_for_clarification=user_feedback_str,
        clarification_context=clarification_ctx_str
    )

    state_update_accumulator: Dict[str, Any] = {
        "generated_command_purpose": None,
        "system_config_details": SystemConfigDetails(is_system_config=False),
        "needs_dependency_check": False,
        "user_feedback_for_clarification": None, 
        "clarification_context": None,          
        "is_trying_file_search": False,
        "generated_command": None,
        "needs_user_clarification": False, # Initialize
        "clarification_question": None   # Initialize
    }

    if command_str.startswith("CHAT_HISTORY_ANSWER:"):
        answer = command_str.replace("CHAT_HISTORY_ANSWER:", "").strip()
        state_update_accumulator.update({
            "generated_command": None,
            "execution_summary": answer,
            "generated_command_purpose": "history_qa",
            "is_error": False,
            "needs_retry": False 
        })
        return state_update_accumulator
    
    if command_str.startswith("CLARIFICATION_NEEDED:"):
        question = command_str.replace("CLARIFICATION_NEEDED:", "").strip()
        if not question: 
            question = "I need more information to proceed. Could you please provide more details?"
        state_update_accumulator.update({
            "generated_command": None,
            "needs_user_clarification": True,
            "clarification_question": question,
            "clarification_context": "general_command_clarification", # Or a more specific context if LLM could provide
            "is_error": False, 
            "needs_retry": False
        })
        return state_update_accumulator

    if effective_is_retry_for_search_failure or attempting_file_not_found_retry_for_direct_action:
        if command_str.startswith("SEARCH_COMMAND_ACTION:"):
             state_update_accumulator["generated_command_purpose"] = "file_search"
        state_update_accumulator["is_trying_file_search"] = state.get("is_trying_file_search", False)

    if command_str == "NO_ACTION_NEEDED":
        state_update_accumulator.update({
            "generated_command": None,
            "error_message": "No specific shell action was identified for your query.",
            "execution_summary": "Okay, understood. What shell task can I help you with next?",
            "is_error": True, "needs_retry": False }) 
        return state_update_accumulator
    if command_str == "USER_REQUESTED_SKIP": 
        state_update_accumulator.update({
            "generated_command": None,
            "error_message": "User requested to skip operation.",
            "execution_summary": "Okay, skipping that.",
            "is_error": True, "needs_retry": False}) 
        return state_update_accumulator

    error_prefixes = [
        "ERROR: Query too vague", "ERROR: Cannot generate a suitable command",
        "ERROR: Cannot fix command based on previous error", "ERROR: Cannot generate command.",
        "ERROR: Cannot create file writing command", "ERROR: Cannot formulate a listing command",
        "ERROR: Cannot formulate a search command", "ERROR: Cannot formulate alternative search/list",
        "ERROR: Cannot proceed with feedback", "ERROR: LLM Invocation Failed",
        "ERROR: Cannot fix command based on previous error or re-attempt intent"
        ]
    if any(command_str.startswith(prefix) for prefix in error_prefixes):
        agent_console.print(f"[bold red]Command Generation Failed by LLM:[/bold red] {command_str}")
        state_update_accumulator.update({
            "generated_command": None, "error_message": command_str, "is_error": True,
            "needs_retry": False 
        })
        return state_update_accumulator

    current_system_config_details = SystemConfigDetails(is_system_config=False)
    if command_str.startswith("SYSTEM_CONFIG::NATIVE::"):
        native_cmd = command_str.replace("SYSTEM_CONFIG::NATIVE::", "").strip()
        if not native_cmd:
            error_msg = "ERROR: LLM provided SYSTEM_CONFIG::NATIVE:: but no command."
            state_update_accumulator.update({"generated_command": None, "error_message": error_msg, "is_error": True, "needs_retry": False}); return state_update_accumulator
        command_str = native_cmd
        current_system_config_details["is_system_config"] = True
        state_update_accumulator["generated_command_purpose"] = "system_config_action"
    elif command_str.startswith("SYSTEM_CONFIG::DEPENDENCY::"):
        json_str_part = command_str.replace("SYSTEM_CONFIG::DEPENDENCY::", "").strip()
        try:
            dep_info = json.loads(json_str_part)
            
            expected_keys_must_be_non_empty = ["dependency_name", "dependency_install_command", "dependency_check_command"]
            key_can_be_empty_string = "command_if_dep_installed"
            
            valid_structure = True
            problematic_keys_details = []

            for key in expected_keys_must_be_non_empty:
                if not (key in dep_info and isinstance(dep_info[key], str) and dep_info[key].strip()):
                    valid_structure = False
                    problematic_keys_details.append(f"'{key}' is missing, not a string, or empty")
            
            if not (key_can_be_empty_string in dep_info and isinstance(dep_info[key_can_be_empty_string], str)): 
                valid_structure = False
                problematic_keys_details.append(f"'{key_can_be_empty_string}' is missing or not a string")

            if not valid_structure:
                error_msg = (f"ERROR: LLM provided incomplete/invalid dependency info for SYSTEM_CONFIG. "
                             f"Problems: {'; '.join(problematic_keys_details)}. JSON: {json_str_part[:200]}...")
                agent_console.print(f"[bold red]Cmd Gen Failed (dep info):[/bold red] {error_msg}. JSON: {json_str_part[:200]}...")
                state_update_accumulator.update({"generated_command": None, "error_message": error_msg, "is_error": True, "needs_retry": False}); return state_update_accumulator

            current_system_config_details.update({
                "is_system_config": True, "dependency_name": dep_info["dependency_name"],
                "dependency_install_command": dep_info["dependency_install_command"],
                "dependency_check_command": dep_info["dependency_check_command"],
                "command_if_dep_installed": dep_info["command_if_dep_installed"]})
            state_update_accumulator["needs_dependency_check"] = True
            command_str = "" 
        except json.JSONDecodeError as e:
            error_msg = f"ERROR: LLM invalid JSON for SYSTEM_CONFIG::DEPENDENCY:: {e}. Received: '{json_str_part[:200]}...'"
            agent_console.print(f"[bold red]Cmd Gen Failed (JSON parse):[/bold red] {error_msg}")
            state_update_accumulator.update({"generated_command": None, "error_message": error_msg, "is_error": True, "needs_retry": False}); return state_update_accumulator
    elif command_str.startswith("SEARCH_COMMAND_ACTION:"):
        command_str = command_str.replace("SEARCH_COMMAND_ACTION:", "").strip()
        state_update_accumulator["generated_command_purpose"] = "file_search"
        state_update_accumulator["is_trying_file_search"] = True 
    elif state.get("generated_code_content") and not state_update_accumulator.get("needs_dependency_check"):
         state_update_accumulator["generated_command_purpose"] = "project_setup_with_code"
    elif not state_update_accumulator.get("generated_command_purpose"): 
         state_update_accumulator["generated_command_purpose"] = "direct_action"
         if state.get("user_feedback_for_clarification"): 
            state_update_accumulator["generated_command_purpose"] = "direct_action_after_feedback"


    state_update_accumulator["system_config_details"] = current_system_config_details

    if command_str or not state_update_accumulator.get("needs_dependency_check"): 
        if not command_str and not state_update_accumulator.get("needs_dependency_check"):
            error_msg = "ERROR: LLM returned an empty string for the command (and not a dependency flow or clarification)."
            agent_console.print(f"[bold red]Cmd Gen Failed (empty cmd):[/bold red] {error_msg}")
            current_purpose_for_retry_decision = state_update_accumulator.get("generated_command_purpose")

            allow_retry_for_empty_cmd = current_purpose_for_retry_decision in ["direct_action", "direct_action_after_feedback", "system_config_action"] or \
                                        (current_purpose_for_retry_decision == "file_search" and not effective_is_retry_for_search_failure)
            should_retry_graph = state.get("retry_attempt",0) < MAX_RETRY_ATTEMPTS and allow_retry_for_empty_cmd

            state_update_accumulator.update({
                "generated_command": None, "error_message": error_msg, "is_error": True,
                "needs_retry": should_retry_graph, 
                "is_trying_file_search": True if current_purpose_for_retry_decision == "file_search" and should_retry_graph else False
            })
            return state_update_accumulator

        original_command_str = command_str 
        if command_str.startswith("```") and command_str.endswith("```"):
            lines = command_str.splitlines()
            if len(lines) > 1 and (lines[0].strip().startswith("```") and (len(lines[0].strip().split()) < 3 or lines[0].strip().lower() in ["```sh", "```bash", "```"] ) ) and \
               (lines[-1].strip() == "```"): 
                  command_str = "\n".join(lines[1:-1]).strip()
            elif len(lines) == 1 and lines[0].strip().startswith("```") and lines[0].strip().endswith("```"):
                 command_str = lines[0].strip()[3:-3].strip()
        
        if command_str.startswith("`") and command_str.endswith("`") and len(command_str) > 1:
            command_str = command_str[1:-1]

        if not command_str.lower().startswith("cd "):
            for prefix in ["sh\n", "bash\n", "sh ", "bash ", "$ ", "# ", "user@host:~$ "]: 
                if command_str.startswith(prefix):
                    command_str = command_str[len(prefix):].strip()
                    break
        
        if (not command_str and not state_update_accumulator.get("needs_dependency_check")) or \
           "Proposed Command Preview:" in command_str or "Purpose:" in command_str:
            error_msg = f"ERROR: Command invalid after sanitation. "
            if not command_str: error_msg += f"(Original: '{original_command_str[:100]}...')"
            else: error_msg += f"Looks like preview text: '{command_str[:100]}...'"
            
            agent_console.print(f"[bold red]Cmd Gen Failed (invalid after sanitize):[/bold red] {error_msg}")
            state_update_accumulator.update({
                "generated_command": None, "error_message": error_msg, "is_error": True,
                "needs_retry": True if state.get("retry_attempt", 0) < MAX_RETRY_ATTEMPTS else False 
            })
            return state_update_accumulator

    if command_str: 
        state_update_accumulator["generated_command"] = command_str
    elif not state_update_accumulator.get("needs_dependency_check"): 
        error_msg = "ERROR: Command generation resulted in no command, no dependency check, and no clarification request."
        agent_console.print(f"[bold red]Cmd Gen Safeguard Fail:[/bold red] {error_msg}")
        state_update_accumulator.update({
            "generated_command": None, "error_message": error_msg, "is_error": True,
            "needs_retry": False 
        })
        return state_update_accumulator

    state_update_accumulator["error_message"] = None 
    state_update_accumulator["is_error"] = False
    state_update_accumulator["needs_retry"] = False
    return state_update_accumulator

def check_dependency_installed_node(state: AgentState) -> AgentState:
    if not state.get("needs_dependency_check") or not state.get("system_config_details"):
        return {"error_message": "Internal error: check_dependency_installed_node called inappropriately.", "is_error": True}
    config_details = state["system_config_details"]
    check_command = config_details.get("dependency_check_command")
    dep_name = config_details.get("dependency_name", "Unknown dependency")
    install_cmd = config_details.get("dependency_install_command", "Unknown install command")
    original_query = state.get("original_query", "fulfill your request")
    if not check_command:
        return {"error_message": f"No check command for {dep_name}.", "is_error": True, "needs_dependency_check": False}
    try:
        process = subprocess.run(check_command, shell=True, capture_output=True, text=True, check=False)
        if process.returncode == 0:
            agent_console.print(f"[green]:heavy_check_mark:[/green] Dependency '{dep_name}' is already installed.")
            return {
                "dependency_already_installed": True, "needs_dependency_check": False,
                "generated_command": config_details.get("command_if_dep_installed"), 
                "generated_command_purpose": "system_config_action" 
            }
        else:
            clarification_q = (
                f"The tool '{dep_name}' is required to '{original_query}'. "
                f"It can be installed with: `{install_cmd}`.\n"
                f"Do you want to approve installation of '{dep_name}'?"
            )
            return {
                "dependency_already_installed": False, "needs_dependency_check": False,
                "needs_user_clarification": True, "clarification_question": clarification_q,
                "clarification_context": "dependency_install_approval"
            }
    except Exception as e:
        agent_console.print(f"[bold red]Error executing dependency check '{check_command}':[/bold red] {e}")
        return {
            "error_message": f"Error checking {dep_name}: {e}", "is_error": True,
            "needs_dependency_check": False, "dependency_already_installed": False
        }

def install_dependency_node(state: AgentState) -> AgentState:
    if not (state.get("needs_dependency_installation") and \
            state.get("user_approved_dependency_install") and \
            state.get("system_config_details")):
        return {"error_message": "Internal error: install_dependency_node inappropriate call.", "is_error": True, "needs_dependency_installation": False} 
    config_details = state["system_config_details"]
    install_command = config_details.get("dependency_install_command")
    dep_name = config_details.get("dependency_name", "Unknown dependency")
    if not install_command:
        return {"error_message": f"No install command for {dep_name}.", "is_error": True, "needs_dependency_installation": False}
    agent_console.print(f":gear: Attempting to install '{dep_name}'...")
    try:
        process = subprocess.run(install_command, shell=True, capture_output=True, text=True, check=False)
        if process.returncode == 0:
            agent_console.print(f"[green]:heavy_check_mark:[/green] Dependency '{dep_name}' installed successfully.")
            return {
                "needs_dependency_installation": False,
                "dependency_install_return_code": process.returncode,
                "dependency_install_stdout": process.stdout.strip(),
                "dependency_install_stderr": process.stderr.strip(),
                "generated_command": config_details.get("command_if_dep_installed"), 
                "generated_command_purpose": "system_config_action", 
                "is_error": False, "error_message": None
            }
        else:
            error_msg = f"Failed to install dependency '{dep_name}'. RC: {process.returncode}. Error: {process.stderr.strip()[:500]}"
            agent_console.print(f"[red]:x: {error_msg}[/red]")
            return {
                "needs_dependency_installation": False,
                "dependency_install_return_code": process.returncode,
                "dependency_install_stdout": process.stdout.strip(),
                "dependency_install_stderr": process.stderr.strip(),
                "is_error": True, "error_message": error_msg
            }
    except Exception as e:
        error_msg = f"Exception during installation of '{dep_name}': {e}"
        agent_console.print(f"[bold red]Installation Exception:[/bold red] {error_msg}")
        return {
            "needs_dependency_installation": False,
            "is_error": True, "error_message": error_msg,
            "dependency_install_return_code": -1
        }

def command_explainer_node(state: AgentState) -> AgentState:
    if state.get("is_error") or llm is None or not state.get("generated_command"): return state
    generated_command_str = state.get("generated_command","")
    original_query_str = state.get("original_query","")
    purpose = state.get("generated_command_purpose")

    if "Proposed Command Preview:" in generated_command_str or "Purpose:" in generated_command_str:
        agent_console.print("[bold yellow]Explainer: Command looks like preview text. Skipping explanation to avoid loop.[/bold yellow]")
        return {"command_explanation": "Command appears to be malformed (contains preview text). Manual review advised.",
                "safety_rating": "DANGEROUS", 
                "safety_assessment": "Command structure is suspicious, likely an internal error."}


    system_message = "You are an expert command explainer. Be clear and concise."
    human_template = (
        "User's most recent query was: '{original_query}'\n"
        "The generated shell command is: sh\n{command}\n"
        "Its intended purpose is: {purpose}.\n\n"
        "Briefly explain this shell command to the user in a friendly and clear way, "
        "relating it back to their query and its purpose. Highlight key actions."
    )
    prompt_template_obj = ChatPromptTemplate.from_messages([
        ("system", system_message),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", human_template)
    ])
    explainer_chain = prompt_template_obj | llm | StrOutputParser()
    try:
        explanation_str = explainer_chain.invoke({
            "command": generated_command_str,
            "original_query": original_query_str,
            "purpose": purpose or "perform the requested action",
            "chat_history": state.get("chat_memory_messages", []) 
        })
        return {"command_explanation": explanation_str.strip()}
    except Exception as e:
        agent_console.print(f"[bold red]Command Explanation Exception:[/bold red] {e}")
        return {"command_explanation": f"Could not get explanation due to an error: {e}"}

def safety_validator_node(state: AgentState) -> AgentState:
    if state.get("is_error") or llm is None or not state.get("generated_command"): return state
    command_to_validate = state.get("generated_command","")

    if "Proposed Command Preview:" in command_to_validate or "Purpose:" in command_to_validate:
        agent_console.print("[bold red]Safety Validator: Command looks like preview text. Marking DANGEROUS.[/bold red]")
        return {"safety_rating": "DANGEROUS",
                "safety_assessment": "Command structure is malformed (contains preview text). Likely an internal error. Execution aborted.",
                "is_error": True, 
                "error_message": "Command malformed (contains preview text), safety validation failed."
                }

    purpose = state.get("generated_command_purpose")
    
    prompt_template_str = (
        "Analyze the shell command: sh\n{command}\n\n"
        "Identify the primary risks. Consider these categories:\n"
        "1. IRREVERSIBLE_SYSTEM_DAMAGE: Operations like `rm -rf /`, `dd`, `mkfs`, formatting drives, deleting critical system files/directories (e.g., C:\\Windows\\System32, /etc, /boot), widespread unintentional data loss.\n"
        "2. INFORMATION_EXPOSURE: Revealing sensitive data (passwords, API keys, private files), network reconnaissance that leaks detailed system vulnerabilities.\n"
        "3. PRIVILEGE_ESCALATION: Use of `sudo`, `runas`, or other admin-level execution. This is a risk factor; the command itself might be benign or harmful.\n"
        "4. ARBITRARY_CODE_EXECUTION: Piping from web to shell (`curl ... | bash`), executing downloaded scripts without review, enabling remote access services insecurely.\n"
        "5. SOFTWARE_INSTALLATION: Installing new packages or applications, especially from untrusted sources.\n"
        "6. MINOR_DATA_MODIFICATION_OR_DELETION: Modifying user files, non-critical configurations, creating/deleting user-space files/dirs (e.g. `rm mydocument.txt`).\n"
        "7. BENIGN_SYSTEM_OPERATION: Standard non-destructive system information queries, navigation, harmless user-level operations.\n\n"
        "Based on these, provide your response in exactly 3 lines:\n"
        "Line 1: Overall Safety Rating (SAFE, CAUTION, DANGEROUS).\n"
        "Line 2: Primary Risk Category (e.g., IRREVERSIBLE_SYSTEM_DAMAGE, INFORMATION_EXPOSURE, ARBITRARY_CODE_EXECUTION, PRIVILEGE_ESCALATION, SOFTWARE_INSTALLATION, MINOR_DATA_MODIFICATION_OR_DELETION, BENIGN_SYSTEM_OPERATION, NONE). If multiple apply, list the most severe one.\n"
        "Line 3: Concise explanation (max 15 words) justifying the rating and category. Highlight specific commands/patterns if DANGEROUS or CAUTION.\n\n"
        "Example for `rm -rf /usr`:\n"
        "DANGEROUS\n"
        "IRREVERSIBLE_SYSTEM_DAMAGE\n"
        "Deletes critical /usr directory irreversibly.\n\n"
        "Example for `netsh wlan show profile name=\"MyNet\" key=clear`:\n"
        "CAUTION\n"
        "INFORMATION_EXPOSURE\n"
        "Reveals Wi-Fi password in plain text.\n\n"
        "Example for `sudo apt update`:\n"
        "CAUTION\n" 
        "PRIVILEGE_ESCALATION\n"
        "Uses sudo for package list update.\n\n"
        "Command to analyze: sh\n{command}\n"
    )
    prompt_template_obj = ChatPromptTemplate.from_template(prompt_template_str)
    validator_chain = prompt_template_obj | llm | StrOutputParser()
    try:
        assessment_text = validator_chain.invoke({"command": command_to_validate}).strip()
        lines = assessment_text.split('\n', 2) 
        
        if len(lines) < 3: 
            agent_console.print(f"[bold yellow]Safety Validator: LLM did not return 3 lines. Original: '{assessment_text}'. Defaulting DANGEROUS.[/bold yellow]")
            return {"safety_rating": "DANGEROUS", 
                    "risk_category": "UNKNOWN_FORMAT_ERROR",
                    "safety_assessment": f"Validation format error: {assessment_text}. Assume DANGEROUS.",
                    "is_error": False 
                   }

        rating_str = lines[0].strip().upper()
        risk_category_str = lines[1].strip().upper()
        assessment_explanation = lines[2].strip()
        
        valid_ratings = ["SAFE", "CAUTION", "DANGEROUS"]
        final_rating = "DANGEROUS" 
        for valid_keyword in valid_ratings:
            if valid_keyword == rating_str: 
                final_rating = valid_keyword
                break
        
        HARMFUL_RISK_CATEGORIES = ["IRREVERSIBLE_SYSTEM_DAMAGE"] 
        
        if final_rating == "DANGEROUS" and any(cat_keyword in risk_category_str for cat_keyword in HARMFUL_RISK_CATEGORIES):
            auto_block_message = f"Command blocked: High risk of system damage ({risk_category_str}). Command: '{command_to_validate}'"
            agent_console.print(f"[bold red]Safety Validator: {auto_block_message}[/bold red]")
            return {
                "safety_rating": final_rating, "risk_category": risk_category_str,
                "safety_assessment": f"BLOCKED AUTOMATICALLY: {assessment_explanation} (Risk: {risk_category_str})",
                "is_error": True,
                "error_message": auto_block_message
            }
            
        return {"safety_rating": final_rating, "safety_assessment": assessment_explanation, "risk_category": risk_category_str, "is_error": False}

    except Exception as e:
        agent_console.print(f"[bold red]Safety Validation Exception:[/bold red] {e}. Defaulting DANGEROUS.")
        return {"safety_rating": "DANGEROUS", 
                "risk_category": "VALIDATION_EXCEPTION",
                "safety_assessment": f"Validation failed due to exception: {str(e)}. Assume DANGEROUS.",
                "is_error": False 
               }

def execute_command_node(state: AgentState) -> AgentState:
    command_to_run = state.get("generated_command")
    if state.get("is_error") or not command_to_run: 
        return {
            "needs_retry": False, 
            "is_error": state.get("is_error", False), 
            "error_message": state.get("error_message") 
            }
    
    if "Proposed Command Preview:" in command_to_run or "Purpose:" in command_to_run or "Explanation:" in command_to_run:
        error_msg = f"CRITICAL EXECUTION HALT: Attempted to execute malformed command (contains preview text): '{command_to_run[:200]}...'"
        agent_console.print(f"[bold red]{error_msg}[/bold red]")
        return {
            "executed_command": command_to_run, 
            "execution_stdout": "",
            "execution_stderr": error_msg,
            "execution_return_code": -999, 
            "needs_retry": True,  
            "is_error": False,     
            "error_message": error_msg, 
            "is_trying_file_search": False, 
            "execution_summary_override": None
        }


    purpose = state.get("generated_command_purpose")
    agent_console.print(f":running: Executing: [bold white on blue]`{command_to_run}`[/bold white on blue]")
    try:
        process = subprocess.run(command_to_run, shell=True, capture_output=True, text=True, check=False, cwd=os.getcwd())
        stdout_content = process.stdout.strip()
        stderr_content = process.stderr.strip()
        actual_return_code = process.returncode

        current_update: Dict[str, Any] = {
            "executed_command": command_to_run,
            "execution_stdout": stdout_content,
            "execution_stderr": stderr_content,
            "execution_return_code": actual_return_code,
            "is_error": False,
            "needs_retry": False, 
            "execution_summary_override": None
        }

        command_failed_initially = actual_return_code != 0
        final_command_failed_status = command_failed_initially

        is_mkdir_type_command = False
        normalized_command_lower = command_to_run.lower()
        if "mkdir " in normalized_command_lower or " md " in normalized_command_lower or \
           normalized_command_lower.startswith("mkdir ") or normalized_command_lower.startswith("md "): 
            is_mkdir_type_command = True

        if command_failed_initially and is_mkdir_type_command:
            error_lower = stderr_content.lower()
            if "already exists" in error_lower or \
               ("file exists" in error_lower and "cannot create directory" in error_lower):
                agent_console.print(f"[dim]Directory creation '{command_to_run}' reported 'already exists'. Treating as intent fulfilled.[/dim]")
                final_command_failed_status = False
                current_update["execution_summary_override"] = f"The directory '{command_to_run.split()[-1]}' already exists."
                current_update["execution_return_code"] = 0
                current_update["execution_stderr"] = f"(Note: Original command stderr: '{stderr_content}'. Interpreted as directory already present.)"


        if purpose in ["file_search", "list_files_for_vague_query"]:
            if final_command_failed_status or (not stdout_content and not current_update["execution_summary_override"]): 
                 current_update.update({"needs_retry": True, "is_trying_file_search": True})
        elif purpose in ["project_setup_with_code", "system_config_action"]:
            if final_command_failed_status:
                error_type = purpose.replace("_", " ").title()
                error_message_for_state = (f"{error_type} command failed (RC: {actual_return_code}). "
                             f"Cmd: `{command_to_run}`\nErr: {stderr_content}\nOut: {stdout_content}")
                
                allow_retry_for_this_error_type = False
                if stderr_content and \
                   ("not recognized" in stderr_content.lower() or \
                    "is not recognized" in stderr_content.lower() or \
                    ("cannot find the path specified" in stderr_content.lower() and "echo" in command_to_run.lower())): 
                    allow_retry_for_this_error_type = True
                
                current_update["needs_retry"] = allow_retry_for_this_error_type
                current_update["is_error"] = not allow_retry_for_this_error_type 
                current_update["error_message"] = error_message_for_state
        else: 
            current_update["needs_retry"] = final_command_failed_status 
            if final_command_failed_status:
                 current_update["error_message"] = f"Command '{command_to_run}' failed. RC: {actual_return_code}. Stderr: {stderr_content}"
        return current_update
    except Exception as e:
        error_msg = f"Python subprocess error for `{command_to_run}`: {str(e)}"
        agent_console.print(f"[bold red]Subprocess Execution Exception:[/bold red] {e}")
        return {
            "executed_command": command_to_run,
            "execution_stdout": "",
            "execution_stderr": error_msg,
            "execution_return_code": -1,
            "needs_retry": True,
            "is_error": False, 
            "error_message": error_msg,
            "execution_summary_override": None
        }

def summarize_execution_node(state: AgentState) -> AgentState:
    if llm is None:
        return {"execution_summary": "LLM not available for summarization."}

    if state.get("execution_summary_override") is not None:
        return {"execution_summary": state.get("execution_summary_override"), "is_error": False}

    if state.get("generated_command_purpose") == "history_qa" and state.get("execution_summary"):
        return {} 

    executed_command = state.get("executed_command")
    return_code = state.get("execution_return_code")

    if return_code == -999 and "CRITICAL EXECUTION HALT" in (state.get("execution_stderr", "") or ""): 
        return {"execution_summary": state.get("execution_stderr"), "is_error": True} 

    if executed_command is None or return_code is None:
        if state.get("is_error") and state.get("error_message"):
            return {"execution_summary": state.get("error_message")}

        dep_name = state.get("system_config_details", {}).get("dependency_name", "dependency")
        
        dep_install_rc = state.get("dependency_install_return_code")
        if dep_install_rc is not None:
            dep_name = state.get("system_config_details", {}).get("dependency_name", "dependency")
            if dep_install_rc == 0:
                 return {"execution_summary": f"Dependency '{dep_name}' was installed successfully."}
            return {"execution_summary": f"Attempt to install dependency '{dep_name}' failed. Details: {state.get('dependency_install_stderr', 'N/A')}"}

        if state.get("dependency_already_installed") is True and \
           state.get("needs_dependency_check") is False and \
           state.get("system_config_details", {}).get("is_system_config"): 
             return {"execution_summary": f"Dependency '{dep_name}' is already installed."}
        
        return {"execution_summary": "No command was executed, so no summary to provide."}

    original_query = state.get("original_query", "the user's request")
    stdout = state.get("execution_stdout", "")
    stderr = state.get("execution_stderr", "")
    purpose = state.get("generated_command_purpose", "perform an action")


    max_output_len = 500
    stdout_brief = stdout[:max_output_len] + ("..." if len(stdout) > max_output_len else "")
    stderr_brief = stderr[:max_output_len] + ("..." if len(stderr) > max_output_len else "")
    system_prompt_content = (
        "You are an expert at summarizing shell command executions for users in a friendly and precise way."
    )
    human_prompt_content = (
         "The user's most recent relevant request was: '{original_query}'\n\n"
         "To address this, the system executed the command: `{executed_command}` (Intended purpose: {purpose})\n"
         "Return Code: {return_code}\n\n"
         "Standard Output (if any, brief):\n{stdout}\n\n"
         "Standard Error (if any, brief):\n{stderr}\n\n"
         "Based on all the above (including conversation context if provided via chat history), provide a concise, user-friendly natural language summary of the outcome, directly addressing the user's original request. "
         "Focus on what the user wanted to achieve. Be direct and clear. Maximum 2-3 sentences.\n"
         "If the command was to find files and it produced output (stdout is not empty), state what kind of files were found and if it matches the request. Mention if the list might be long if stdout was truncated.\n"
         "If it was supposed to find files and found nothing (stdout is empty, even if RC=0 for tools like mdfind), explicitly state that no matching files were found.\n"
         "If it failed (RC != 0), explain the failure simply based on the error (stderr). If stderr is a note like '(Note: Original command stderr: ...)', summarize based on the implied success.\n"
         "If an action was performed successfully with no output, state that the action was completed."
    )
    final_summary_prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt_content),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", human_prompt_content)
    ])
    summarizer_chain = final_summary_prompt_template | llm | StrOutputParser()
    try:
        summary = summarizer_chain.invoke({
            "original_query": original_query,
            "executed_command": executed_command,
            "purpose": purpose or "Unknown",
            "return_code": str(return_code),
            "stdout": stdout_brief if stdout_brief else "(No standard output)",
            "stderr": stderr_brief if stderr_brief else "(No error output)",
            "chat_history": state.get("chat_memory_messages", [])
        })
        return {"execution_summary": summary.strip(), "is_error": False}
    except Exception as e:
        agent_console.print(f"[bold red]Error during execution summarization:[/bold red] {e}")
        fallback_summary = f"Command '{executed_command}' "
        if return_code == 0:
            fallback_summary += "executed."
            if stdout_brief and stdout_brief != "(No standard output)":
                fallback_summary += f" Output: {stdout_brief}"
            elif not stdout_brief or stdout_brief == "(No standard output)":
                fallback_summary += " (No output)"
        else:
            fallback_summary += f"failed (RC: {return_code})."
            if stderr_brief and stderr_brief != "(No error output)":
                fallback_summary += f" Error: {stderr_brief}"
        return {"execution_summary": fallback_summary, "is_error": False}


def handle_execution_error_node(state: AgentState) -> AgentState:
    if not state.get("needs_retry"): return state 

    executed_cmd_str = state.get('executed_command', 'unknown command')
    stderr_msg_str = state.get('execution_stderr', '')
    error_message_from_exec = state.get('error_message', '') 
    purpose = state.get("generated_command_purpose")
    retry_attempt = state.get("retry_attempt", 0)
    return_code = state.get("execution_return_code")

    if return_code == -999 and "CRITICAL EXECUTION HALT" in (stderr_msg_str or ""):
        if retry_attempt < MAX_RETRY_ATTEMPTS:
            agent_console.print(f"[bold orange_red1]Error Handler: Malformed command detected. Attempting retry {retry_attempt + 1}/{MAX_RETRY_ATTEMPTS +1 } to regenerate command.[/bold orange_red1]")
            return {
                "retry_attempt": retry_attempt + 1,
                "generated_command": None, 
                "command_explanation": None, "safety_rating": None, "safety_assessment": None,
                "error_message": error_message_from_exec or stderr_msg_str, 
                "is_error": False, 
                "needs_retry": True, 
                "is_trying_file_search": False, 
                "execution_stdout": state.get("execution_stdout"), 
                "execution_stderr": stderr_msg_str, 
                "executed_command": executed_cmd_str 
            }
        else:
            final_err_msg = f"CRITICAL FAILURE: System repeatedly generated malformed commands after {MAX_RETRY_ATTEMPTS + 1} attempts. Last attempt: '{executed_cmd_str}'. Last error: '{stderr_msg_str}'"
            agent_console.print(f"[bold red]{final_err_msg}[/bold red]")
            return {"error_message": final_err_msg, "is_error": True, "needs_retry": False}


    if state.get("is_trying_file_search"): 
        output_str_part = ""
        if state.get("execution_stdout"):
            output_str_part = f'Output (if any): {state.get("execution_stdout")[:200]}...\n'
        error_str_part = ""
        if stderr_msg_str:
            error_str_part = f'Error message (if any): {stderr_msg_str}\n'

        failure_description = "failed or found no results"
        rc_val = state.get('execution_return_code')
        if not state.get("execution_stdout") and not stderr_msg_str and rc_val is not None and rc_val != 0:
            failure_description = f"failed with return code {rc_val} and produced no output"
        elif not state.get("execution_stdout") and not stderr_msg_str and rc_val == 0:
             failure_description = "completed but found no results"

        clarif_question = (
            f"The search/list command ` {executed_cmd_str} ` {failure_description}.\n"
            f"{output_str_part}"
            f"{error_str_part}"
            f"\nWould you like to try a different search/list command, provide a specific path, or type 'skip' to stop?"
        )
        return {
             "error_message": None, 
             "is_error": False,
             "needs_retry": False, 
             "is_trying_file_search": False, 
             "needs_user_clarification": True,
             "clarification_question": clarif_question,
             "clarification_context": "search_failed_clarification"
         }

    llm_context_error_message = error_message_from_exec or stderr_msg_str 

    if purpose in ["system_config_action", "project_setup_with_code"]:
        if not state.get("needs_retry"): 
            final_error_msg = error_message_from_exec or f"Command for '{purpose}' ('{executed_cmd_str}') failed with a non-retryable error. Error: '{stderr_msg_str[:200]}...'"
            return {"error_message": final_error_msg, "is_error": True, "needs_retry": False}

    if retry_attempt < MAX_RETRY_ATTEMPTS:
        agent_console.print(f"Error Handler: Attempting retry {retry_attempt + 1}/{MAX_RETRY_ATTEMPTS + 1} for command: `{executed_cmd_str}`")
        return {
            "retry_attempt": retry_attempt + 1,
            "generated_command": None, 
            "command_explanation": None, "safety_rating": None, "safety_assessment": None,
            "error_message": llm_context_error_message, 
            "is_error": False, 
            "needs_retry": True, 
            "is_trying_file_search": False 
        }
    else: 
        final_error_msg = (f"Command failed after {MAX_RETRY_ATTEMPTS + 1} attempts. "
                           f"Last: \"{executed_cmd_str}\". Error: \"{llm_context_error_message[:200]}...\"")
        agent_console.print(f"[bold red]Error Handler: Max retries reached. {final_error_msg}[/bold red]")
        return {"error_message": final_error_msg, "is_error": True, "needs_retry": False, "is_trying_file_search": False}

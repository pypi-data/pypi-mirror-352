# ai_shell_gemini/main.py
import typer
from typing import Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm as RichConfirm, Prompt as RichPrompt
from rich.text import Text
import time
import os
import uuid # Added
import json # Added
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, message_to_dict, messages_from_dict # Added helpers
from langchain.memory import ConversationBufferMemory
from langchain_core.chat_history import BaseChatMessageHistory # Changed import path

# Imports for VectorStore-Backed Memory
from langchain_community.vectorstores import FAISS # Added
from langchain_google_genai import GoogleGenerativeAIEmbeddings # Added
from langchain_core.documents import Document # Added
from langchain.docstore.in_memory import InMemoryDocstore # Added
try:
    import faiss # Added
except ImportError:
    print("Warning: 'faiss-cpu' or 'faiss-gpu' package not found. VectorStore memory will not be available.")
    faiss = None


from .state import AgentState, SystemConfigDetails
from .graph import app as langgraph_app, END
from .agents import llm as agent_llm, api_call_counter

cli_app = typer.Typer(
    name="ai-shell",
    help="AI Shell: Your command-line copilot. Use '.shell query' for single commands or '.inshell' for an interactive session.",
    add_completion=False
)
console = Console()

interactive_session_data = {
    "os_type": None,
    "chat_memory": None, # Will store ConversationBufferMemory instance (backed by VectorStoreChatMessageHistory)
    "chat_session_id": None, # Added
}

# --- VectorStoreChatMessageHistory Implementation ---
class VectorStoreChatMessageHistory(BaseChatMessageHistory):
    """Chat message history backed by a FAISS vector store."""

    def __init__(self, session_id: str, vectorstore: FAISS):
        if faiss is None:
            raise ImportError("The 'faiss' package is required to use VectorStoreChatMessageHistory with FAISS.")
        self.vectorstore = vectorstore
        self.session_id = session_id

    @property
    def messages(self) -> List[BaseMessage]:
        """Retrieve messages from FAISS for the current session."""
        if not hasattr(self.vectorstore, "docstore") or not hasattr(self.vectorstore.docstore, "_dict"):
            # This implementation is specific to FAISS with InMemoryDocstore
            # console.print("[dim]Warning: VectorStoreChatMessageHistory.messages is optimized for FAISS with InMemoryDocstore.[/dim]")
            return []

        # Accessing all documents in the InMemoryDocstore
        # Note: self.vectorstore.docstore._dict contains Document objects if InMemoryDocstore is used.
        all_docs_in_store = list(self.vectorstore.docstore._dict.values())
        
        session_docs_data = []
        for doc in all_docs_in_store:
            if isinstance(doc, Document) and doc.metadata.get("session_id") == self.session_id:
                session_docs_data.append(doc)
        
        # Sort by timestamp, then sequence as a tie-breaker
        session_docs_data.sort(key=lambda d: (d.metadata.get("timestamp", 0.0), d.metadata.get("sequence", 0)))
        
        loaded_messages: List[BaseMessage] = []
        for doc_data in session_docs_data:
            try:
                msg_dict = json.loads(doc_data.page_content)
                loaded_messages.extend(messages_from_dict([msg_dict])) # messages_from_dict expects a list
            except json.JSONDecodeError:
                console.print(f"[dim red]Error decoding message from doc: {doc_data.page_content[:100]}...[/dim red]")
            except Exception as e:
                console.print(f"[dim red]Error processing stored message: {e}[/dim red]")
        return loaded_messages

    def add_message(self, message: BaseMessage) -> None:
        """Add a message to the FAISS store for the current session."""
        current_docs_for_session = 0
        # This count is specific to InMemoryDocstore structure.
        if hasattr(self.vectorstore, "docstore") and hasattr(self.vectorstore.docstore, "_dict"):
            all_docs_in_store = list(self.vectorstore.docstore._dict.values())
            for doc in all_docs_in_store:
                if isinstance(doc, Document) and doc.metadata.get("session_id") == self.session_id:
                    current_docs_for_session +=1
        next_sequence = current_docs_for_session

        doc_to_add = Document(
            page_content=json.dumps(message_to_dict(message)),
            metadata={
                "session_id": self.session_id,
                "type": message.type,
                "timestamp": time.time(),
                "sequence": next_sequence,
                "unique_doc_id": str(uuid.uuid4()) # For potential deletion by ID in FAISS
            }
        )
        self.vectorstore.add_documents([doc_to_add])

    def clear(self) -> None:
        """Clear messages from FAISS for the current session."""
        if not hasattr(self.vectorstore, "delete") or \
           not hasattr(self.vectorstore, "index_to_docstore_id") or \
           not hasattr(self.vectorstore.docstore, "_dict"):
            console.print("[dim yellow]Warning: VectorStoreChatMessageHistory.clear() requires FAISS with InMemoryDocstore. Session not cleared effectively.[/dim yellow]")
            return

        ids_to_delete = []
        # FAISS index_to_docstore_id maps internal FAISS index (int) to unique doc ID (str)
        # We need to iterate through the actual documents in the docstore to check metadata
        
        # Create a list of doc IDs to delete based on session_id
        # This is specific to InMemoryDocstore
        doc_ids_in_faiss_index = list(self.vectorstore.index_to_docstore_id.values())

        for doc_id_str in doc_ids_in_faiss_index:
            doc = self.vectorstore.docstore.get_document(doc_id_str) # doc_id_str is the key for InMemoryDocstore
            if doc and doc.metadata.get("session_id") == self.session_id:
                ids_to_delete.append(doc_id_str)
        
        if ids_to_delete:
            try:
                deleted_count = self.vectorstore.delete(ids_to_delete)
                if not deleted_count: # delete might return True/False or number of docs
                     console.print(f"[dim yellow]Warning: VectorStoreChatMessageHistory.clear() reported no deletions for {len(ids_to_delete)} docs for session {self.session_id}.[/dim yellow]")
                # else:
                #    console.print(f"[dim]Cleared {len(ids_to_delete)} messages from vector store for session {self.session_id}.[/dim]")
            except Exception as e:
                console.print(f"[dim red]Error during FAISS delete operation: {e}[/dim red]")
        # The self.messages property will reflect the cleared state on next access.

# --- End of VectorStoreChatMessageHistory ---


def get_initial_state_dict(current_query: str = "") -> dict:
    return {
        "original_query": current_query, "parsed_intent": current_query,
        "chat_memory_messages": [],
        "needs_search": False, "search_query": None, "search_results": None, "search_summary": None,
        "user_confirmed_search_info": False, "generated_command": None,
        "generated_code_content": None, "generated_command_purpose": None,
        "command_explanation": None, "safety_assessment": None, "safety_rating": None,
        "os_type": "", "user_feedback": None,
        "execution_stdout": None, "execution_stderr": None, "execution_return_code": None,
        "execution_summary": None, "executed_command": None,
        "needs_retry": False, "retry_attempt": 0, "is_trying_file_search": False,
        "needs_user_clarification": False, "clarification_question": None,
        "clarification_options": None, "user_feedback_for_clarification": None,
        "clarification_context": None, "error_message": None, "is_error": False,
        "current_plan": None, "current_step_index": 0, "tool_call_needed": False,
        "tool_name": None, "tool_args": None, "tool_output": None, "prereq_check_results": None,
        "system_config_details": SystemConfigDetails(is_system_config=False),
        "needs_dependency_check": False, "dependency_already_installed": None,
        "user_approved_dependency_install": None, "needs_dependency_installation": False,
        "dependency_install_stdout": None, "dependency_install_stderr": None,
        "dependency_install_return_code": None,
        "execution_summary_override": None,
    }

def check_prerequisites():
    if agent_llm is None:
        console.print(Panel("[bold red]LLM Initialization Failed![/bold red]\nCheck `GOOGLE_API_KEY`.", title="Critical Error", border_style="red"))
        raise typer.Exit(code=1)
    if langgraph_app is None:
        console.print(Panel("[bold red]LangGraph App Failed to Compile![/bold red]", title="Critical Error", border_style="red"))
        raise typer.Exit(code=1)
    if faiss is None:
        console.print(Panel("[bold yellow]FAISS Package Not Found![/bold yellow]\nVectorStore-backed memory for interactive sessions will not be available.\nPlease install 'faiss-cpu' or 'faiss-gpu'.", title="Optional Dependency Missing", border_style="yellow"))
        # Not exiting, as single-shot commands might still work. Interactive will fail later if faiss is truly needed.


@cli_app.callback()
def callback():
    load_dotenv()
    check_prerequisites()

def _process_query(current_run_state: AgentState, chat_memory_obj: Optional[ConversationBufferMemory] = None) -> AgentState:
    max_inner_loops = 7
    loop_count = 0

    while loop_count < max_inner_loops:
        loop_count += 1
        if chat_memory_obj:
            # Accesses VectorStoreChatMessageHistory.messages via ConversationBufferMemory
            current_run_state["chat_memory_messages"] = list(chat_memory_obj.chat_memory.messages)
        else:
            if loop_count == 1 and not current_run_state.get("chat_memory_messages"):
                 current_run_state["chat_memory_messages"] = []


        if current_run_state.get("needs_user_clarification"):
            console.rule("[bold yellow]User Clarification Needed[/bold yellow]", style="yellow")
            question = current_run_state.get("clarification_question", "The AI needs more information. Please elaborate:")
            context = current_run_state.get("clarification_context")

            if chat_memory_obj:
                # Add AI's question to memory
                # Check if the AI's question is already the last message (e.g., from a retry)
                last_msg_is_same_question = False
                if chat_memory_obj.chat_memory.messages: # Accesses VSCH.messages
                    last_message = chat_memory_obj.chat_memory.messages[-1]
                    if isinstance(last_message, AIMessage) and last_message.content == question:
                        last_msg_is_same_question = True
                
                if not last_msg_is_same_question:
                    chat_memory_obj.chat_memory.add_ai_message(question) # Uses VSCH.add_message


            current_run_state["needs_user_clarification"] = False
            current_run_state["user_feedback_for_clarification"] = None
            user_response_str = ""

            if context == "dependency_install_approval":
                dep_name = current_run_state.get("system_config_details", {}).get("dependency_name", "the required tool")
                user_response_bool = RichConfirm.ask(f"[yellow]{question}[/yellow]", console=console, default=False)
                current_run_state["user_approved_dependency_install"] = user_response_bool
                current_run_state["needs_dependency_installation"] = user_response_bool
                feedback_str = f"User {'approved' if user_response_bool else 'declined'} installation of {dep_name}."
                current_run_state["user_feedback_for_clarification"] = feedback_str
                user_response_str = "yes" if user_response_bool else "no" 
                if not user_response_bool:
                    current_run_state["is_error"] = True
                    current_run_state["error_message"] = f"User declined installation of dependency '{dep_name}'."
            else:
                user_input_str = RichPrompt.ask(f"[yellow]{question}[/yellow]", console=console)
                current_run_state["user_feedback_for_clarification"] = user_input_str
                user_response_str = user_input_str
                if context == "search_failed_clarification" and user_input_str.lower().strip() == "skip":
                    current_run_state["is_error"] = True
                    current_run_state["error_message"] = "User requested to skip after search failure."

            if chat_memory_obj and user_response_str:
                 chat_memory_obj.chat_memory.add_user_message(user_response_str) # Uses VSCH.add_message

            current_run_state["clarification_context"] = None
            current_run_state["needs_retry"] = False 
            current_run_state["retry_attempt"] = 0
            current_run_state["is_trying_file_search"] = False
            
            if not current_run_state.get("is_error"):
                 current_run_state["generated_command"] = None
                 current_run_state["generated_command_purpose"] = None
                 current_run_state["command_explanation"] = None
                 current_run_state["safety_rating"] = None
                 current_run_state["safety_assessment"] = None
                 current_run_state["executed_command"] = None
                 current_run_state["execution_stdout"] = None
                 current_run_state["execution_stderr"] = None
                 current_run_state["execution_return_code"] = None


        graph_stream_completed_fully = True
        processed_nodes_in_stream = set()
        try:
            with console.status("[bold green]AI Shell is thinking...", spinner="dots") as status:
                stream_input = current_run_state.copy() 

                for event_chunk in langgraph_app.stream(stream_input, {"recursion_limit": 60}):
                    if END in event_chunk:
                        if isinstance(event_chunk[END], dict): current_run_state.update(event_chunk[END])
                        break
                    
                    node_name = None
                    node_output_state = None
                    if isinstance(event_chunk, dict) and len(event_chunk) == 1:
                        node_name = list(event_chunk.keys())[0]
                        node_output_state = event_chunk[node_name]
                    else: 
                        console.print(f"[bold red]Warning: Unexpected event_chunk format: {event_chunk}[/bold red]")
                        continue

                    if isinstance(node_output_state, dict): current_run_state.update(node_output_state)

                    if node_name not in processed_nodes_in_stream:
                        if node_name == "generate_command": status.update("[bold green]Generating command...")
                        elif node_name == "explain_command": status.update("[bold green]Explaining command...")
                        elif node_name == "execute_command": status.update("[bold green]Executing command...")
                        elif node_name == "perform_search": status.update("[bold green]Performing web search...")
                        processed_nodes_in_stream.add(node_name)

                    if node_name == "explain_command":
                        cmd_to_run = current_run_state.get("generated_command")
                        safety_rating = current_run_state.get("safety_rating")
                        explanation = current_run_state.get("command_explanation", "No explanation available.")
                        assessment = current_run_state.get("safety_assessment", "No assessment available.")
                        purpose = current_run_state.get("generated_command_purpose")
                        panel_color = {"SAFE": "green", "CAUTION": "yellow", "DANGEROUS": "red"}.get(safety_rating, "blue")
                        status.stop()

                        command_preview_text_for_display = (
                            f"[bold {panel_color}]Proposed Command:[/bold {panel_color}]\n"
                            f"```sh\n{cmd_to_run}\n```\n\n"
                            f"[bold]Purpose:[/bold] {purpose or 'N/A'}\n"
                            f"[bold]Explanation:[/bold] {explanation}\n"
                            f"[bold]Safety Assessment ({safety_rating}):[/bold] {assessment}" )

                        history_message_for_preview = f"I plan to run the command: `{cmd_to_run}`. Explanation: {explanation[:100]}{'...' if len(explanation)>100 else ''}"
                        if "Could not get explanation" in explanation or "No explanation" in explanation or "Command appears to be malformed" in explanation:
                             history_message_for_preview = f"I plan to run the command: `{cmd_to_run}`."
                        
                        if chat_memory_obj:
                            last_msg_is_same_preview = False
                            if chat_memory_obj.chat_memory.messages: # Accesses VSCH.messages
                                last_message = chat_memory_obj.chat_memory.messages[-1]
                                if isinstance(last_message, AIMessage) and last_message.content == history_message_for_preview:
                                    last_msg_is_same_preview = True
                            if not last_msg_is_same_preview:
                                chat_memory_obj.chat_memory.add_ai_message(history_message_for_preview) # Uses VSCH.add_message


                        if safety_rating == "DANGEROUS":
                            # Construct and print the Panel with detailed information first
                            dangerous_command_display_panel = Panel(
                                f"{command_preview_text_for_display}\n\n"
                                f"[bold red]This command is rated DANGEROUS.[/bold red]", # Question moved to RichConfirm.ask
                                title="⚠️ DANGEROUS Command ⚠️",
                                border_style="red",
                                expand=False
                            )
                            console.print(dangerous_command_display_panel)

                            # Ask for confirmation with a simple string prompt
                            user_confirm_dangerous = RichConfirm.ask(
                                "[bold red]Execute this DANGEROUS command? ([Y]es/[N]o)[/bold red]",
                                default=False, console=console
                            )
                            if chat_memory_obj:
                                chat_memory_obj.chat_memory.add_user_message("Yes" if user_confirm_dangerous else "No") # Uses VSCH.add_message

                            if not user_confirm_dangerous:
                                current_run_state["is_error"] = True
                                current_run_state["error_message"] = f"User aborted execution of DANGEROUS command."
                                if chat_memory_obj: 
                                    chat_memory_obj.chat_memory.add_ai_message(current_run_state["error_message"]) # Uses VSCH.add_message
                                graph_stream_completed_fully = False; break
                        
                        status.start()

                    if current_run_state.get("needs_user_clarification") or current_run_state.get("is_error"):
                        graph_stream_completed_fully = False; break
                else: 
                    pass 
        except typer.Exit: raise
        except Exception as e:
            console.print(Panel(f"[bold red]Critical error during AI Shell stream:[/bold red]\n{str(e)}", title="System Error", border_style="red"))
            import traceback; console.print(f"[dim]{traceback.format_exc()}[/dim]")
            graph_stream_completed_fully = False
            current_run_state["is_error"] = True
            current_run_state["error_message"] = f"Stream exception: {str(e)}"

        if graph_stream_completed_fully and not current_run_state.get("needs_user_clarification"): break
        if current_run_state.get("is_error") and not current_run_state.get("needs_user_clarification"): break
        if loop_count >= max_inner_loops:
            console.print("[bold red]Max inner processing loops reached for this query.[/bold red]")
            if not current_run_state.get("is_error"):
                 current_run_state["error_message"] = "Max processing loops reached for the query."
                 current_run_state["is_error"] = True
            break
    return AgentState(**current_run_state)

@cli_app.command(name=".shell", help="Process a single query and exit.")
def ai_shell_single_command(query: str = typer.Argument(..., help="Your task in natural language.")):
    api_call_counter.reset() 
    console.print(Panel(f"[bold sky_blue1]Task:[/bold sky_blue1] {query}", title="Input", expand=False))
    current_run_state = get_initial_state_dict(current_query=query)
    final_state = _process_query(current_run_state, chat_memory_obj=None)
    _display_final_summary(final_state, chat_memory_obj=None, show_raw_output=True)

@cli_app.command(name=".inshell", help="Start an interactive AI Shell session.")
def ai_shell_interactive():
    console.print(Panel("[bold green]Welcome to Interactive AI Shell! [/bold green]\nType your commands or 'exit'/'quit' to leave.", title="AI Shell Interactive Mode", expand=False))
    
    if faiss is None: # Check again specifically for interactive mode
        console.print(Panel("[bold red]FAISS Package Not Found![/bold red]\nVectorStore-backed memory for interactive sessions requires 'faiss-cpu' or 'faiss-gpu'.\nPlease install it and try again.", title="Critical Dependency Missing", border_style="red"))
        raise typer.Exit(code=1)

    if interactive_session_data.get("chat_memory") is None:
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            console.print("[bold red]Error: GOOGLE_API_KEY not found in environment for embeddings.[/bold red]")
            raise typer.Exit(1)
        
        try:
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=google_api_key)
            # Determine embedding dimension (models/embedding-001 is 768)
            # It's better to hardcode if known, or retrieve dynamically if models can vary.
            text_embedding_dimension = 768 # For "models/embedding-001"
            # Optionally, test the embeddings connection:
            # try:
            #     _ = embeddings.embed_query("test")
            # except Exception as e:
            #     console.print(f"[bold red]Error initializing/testing embeddings model: {e}[/bold red]")
            #     raise typer.Exit(1)

        except ImportError:
            console.print("[bold red]Error: 'langchain_google_genai' package not found. Please install it.[/bold red]")
            raise typer.Exit(1)
        except Exception as e: # Catch other potential errors from GoogleGenerativeAIEmbeddings init
            console.print(f"[bold red]Error initializing embeddings model: {e}[/bold red]")
            console.print("[dim]Please check your GOOGLE_API_KEY and network connection.[/dim]")
            raise typer.Exit(1)

        faiss_index = faiss.IndexFlatL2(text_embedding_dimension)
        session_id = f"interactive_session_{str(uuid.uuid4())}"
        
        # FAISS will use an InMemoryDocstore by default if docstore is not specified,
        # which is what our VectorStoreChatMessageHistory implementation currently relies on.
        # For explicit control: docstore=InMemoryDocstore(), index_to_docstore_id={}
        vectorstore_for_history = FAISS(
            embedding_function=embeddings, 
            index=faiss_index,
            docstore=InMemoryDocstore(), # Explicitly use InMemoryDocstore
            index_to_docstore_id={}    # FAISS manages this mapping for InMemoryDocstore
        )

        chat_message_history = VectorStoreChatMessageHistory(
            session_id=session_id,
            vectorstore=vectorstore_for_history
        )
        
        memory_instance = ConversationBufferMemory(
            chat_memory=chat_message_history, 
            memory_key="chat_history", 
            return_messages=True
        )
        interactive_session_data["chat_memory"] = memory_instance
        interactive_session_data["chat_session_id"] = session_id
        console.print(f"[dim]Initialized new vector store-backed memory for session: {session_id}[/dim]")

    chat_memory_for_session: ConversationBufferMemory = interactive_session_data["chat_memory"]
    
    if interactive_session_data["os_type"]:
        console.print(f"[dim]Using remembered OS type: {interactive_session_data['os_type']}[/dim]")

    while True:
        console.line(1)
        api_call_counter.reset()
        query = RichPrompt.ask("[bold cyan]You[/bold cyan]")
        
        if query.lower() in ["exit", "quit"]:
            console.print("[bold yellow]Exiting Interactive AI Shell. Goodbye![/bold yellow]")
            # Optionally clear the vector store for the session here if desired
            # chat_memory_for_session.chat_memory.clear()
            break
        if not query.strip(): continue

        # Add user message to our VectorStore-backed history
        chat_memory_for_session.chat_memory.add_user_message(query)

        current_run_state = get_initial_state_dict(current_query=query)
        current_run_state["os_type"] = interactive_session_data.get("os_type", "")
        
        final_run_state = _process_query(current_run_state, chat_memory_obj=chat_memory_for_session)
        
        if final_run_state.get("os_type"):
            interactive_session_data["os_type"] = final_run_state.get("os_type")

        _display_final_summary(final_run_state, chat_memory_obj=chat_memory_for_session, show_raw_output=True)

def _display_final_summary(final_state: AgentState,
                           chat_memory_obj: Optional[ConversationBufferMemory] = None,
                           show_raw_output: bool = True):
    """Displays the final summary and optionally raw output."""
    exec_summary = final_state.get("execution_summary")
    stdout = final_state.get("execution_stdout")
    stderr = final_state.get("execution_stderr")
    executed_command = final_state.get("executed_command")
    return_code = final_state.get("execution_return_code")
    assistant_final_message_for_memory = None

    if show_raw_output and executed_command:
        if stdout or stderr or (return_code is not None and executed_command != final_state.get("generated_command") \
           and final_state.get("generated_command_purpose") not in ["history_qa"] ):
            console.rule("[Command Output]", style="dim white", characters="=")
            if stdout:
                output_standard = Panel(stdout, title="Standard Output", border_style="green", expand=False)
                console.print("[italic green]Stdout:[/italic green]")
                console.print(output_standard if len(stdout) < 2000 else Text(stdout[:2000] + "\n...(output truncated)..."))
            if stderr:
                is_already_exists_handled = final_state.get("execution_summary_override") and \
                                          "already exists" in (stderr or "").lower() and \
                                          "directory" in (final_state.get("execution_summary_override") or "").lower()

                if not is_already_exists_handled:
                    output_error = Panel(stderr, title="Standard Error", border_style="red", expand=False)
                    console.print("[italic red]Stderr:[/italic red]")
                    console.print(output_error if len(stderr) < 1000 else Text(stderr[:1000] + "\n...(stderr truncated)..."))
            
            if not stdout and not stderr and return_code == 0:
                 console.print(f"[dim](Command executed successfully with no output.)[/dim]")
            elif not stdout and not stderr and return_code != 0 and not (final_state.get("execution_summary_override") and "already exists" in (stderr or "")): 
                 console.print(f"[dim](Command failed with RC: {return_code} and no textual output.)[/dim]")
            console.rule(style="dim white", characters="=")

    panel_to_display = None

    if final_state.get("generated_command_purpose") == "history_qa" and exec_summary:
        panel_title = "AI Assistant"
        color = "bright_blue"
        panel_content = f"[bold {color}]Response:[/bold {color}]\n{exec_summary}"
        panel_to_display = Panel(panel_content, title=panel_title, border_style=color, expand=False)
        assistant_final_message_for_memory = exec_summary
    elif final_state.get("is_error") and final_state.get("error_message"):
        panel_title = "Operation Failed"
        color = "red"
        error_message = final_state['error_message']

        if error_message == "No specific shell action was identified for your query.":
            specific_no_action_summary = exec_summary if exec_summary and exec_summary != "Okay, understood. What shell task can I help you with next?" else None
            panel_content = f"[bold #FFD700]Info:[/bold #FFD700]\n{specific_no_action_summary or error_message}"
            panel_title = "Info"; color = "yellow"
            assistant_final_message_for_memory = specific_no_action_summary or error_message
        elif "User aborted execution" in error_message or "User declined installation" in error_message or "User requested to skip" in error_message:
            panel_content = f"[bold yellow]Action Skipped:[/bold yellow]\n{error_message}"
            panel_title = "User Action"; color = "yellow"
            assistant_final_message_for_memory = error_message
        else:
            panel_content = f"[bold red]Failed:[/bold red]\n{error_message}"
            if exec_summary and \
               exec_summary != final_state.get("execution_summary_override") and \
               "Could not generate a summary" not in exec_summary and \
               "No command was executed" not in exec_summary and \
               error_message not in exec_summary :
                 panel_content += f"\n\n[bold]Execution Attempt Summary (if any):[/bold]\n{exec_summary}"
            assistant_final_message_for_memory = error_message
        panel_to_display = Panel(panel_content, title=panel_title, border_style=color, expand=False)

    elif executed_command and exec_summary and "Could not generate a summary" not in exec_summary and "No command was executed" not in exec_summary :
        title = "AI Summary of Execution"
        color = "green" if return_code == 0 or (final_state.get("execution_summary_override") and return_code == 0) else "yellow"
        summary_panel_content = f"[bold {color}]Outcome:[/bold {color}]\n{exec_summary}"
        panel_to_display = Panel(summary_panel_content, title=title, border_style=color, expand=False)
        assistant_final_message_for_memory = exec_summary
    elif executed_command and (not exec_summary or "Could not generate a summary" in exec_summary or "No command was executed" in exec_summary):
        if return_code == 0 or (final_state.get("execution_summary_override") and return_code == 0):
            fb_content = f"Successfully executed: [green]{executed_command}[/green]"
            if final_state.get("execution_summary_override"):
                fb_content = f"{final_state.get('execution_summary_override')} (Command: `{executed_command}`)"
            elif not stdout and not show_raw_output: fb_content += "\n(No specific output)"
            panel_to_display = Panel(fb_content, title="Success (No AI Summary)", border_style="green")
            assistant_final_message_for_memory = final_state.get("execution_summary_override") or "Command executed successfully."
        else:
            fb_content = f"Command execution failed: [red]{executed_command}[/red]\nRC: {return_code}"
            if not stderr and not show_raw_output: fb_content += "\n(No specific error output)"
            panel_to_display = Panel(fb_content, title="Execution Failed (No AI Summary)", border_style="red")
            assistant_final_message_for_memory = f"Command '{executed_command}' failed with return code {return_code}."
    elif final_state.get("dependency_install_return_code") is not None and not executed_command: 
        dep_name = final_state.get("system_config_details", {}).get("dependency_name", "dependency")
        dep_rc = final_state.get("dependency_install_return_code")
        if dep_rc == 0 :
            dep_text = f"Dependency '{dep_name}' was handled successfully."
            if exec_summary and exec_summary != dep_text: dep_text += f"\nSummary: {exec_summary}"
            panel_to_display = Panel(dep_text, title="Dependency Info", border_style="blue")
            assistant_final_message_for_memory = exec_summary or dep_text
        elif exec_summary : 
            panel_to_display = Panel(f"[bold yellow]Dependency Outcome:[/bold yellow]\n{exec_summary}", title="Dependency Info", border_style="yellow")
            assistant_final_message_for_memory = exec_summary
    elif final_state.get("generated_command") and not executed_command and not final_state.get("is_error"):
        info_text = f"Command was generated but not executed: [yellow]{final_state.get('generated_command')}[/yellow]"
        if exec_summary: info_text += f"\nNote: {exec_summary}"
        panel_to_display = Panel(info_text, title="Info", border_style="blue")
        assistant_final_message_for_memory = exec_summary or info_text
    elif not panel_to_display and exec_summary: 
        panel_to_display = Panel(f"[bold sky_blue1]Info:[/bold sky_blue1]\n{exec_summary}", title="Information", border_style="sky_blue1")
        assistant_final_message_for_memory = exec_summary

    if panel_to_display:
        console.print(panel_to_display)

    num_api_calls = api_call_counter.get_count()
    console.print(f"[dim]LLM API calls for this query: {num_api_calls}[/dim]")

    if chat_memory_obj and assistant_final_message_for_memory:
        add_message_to_memory = True
        if chat_memory_obj.chat_memory.messages: # Accesses VSCH.messages
            last_message = chat_memory_obj.chat_memory.messages[-1]
            if isinstance(last_message, AIMessage) and last_message.content.strip() == assistant_final_message_for_memory.strip():
                add_message_to_memory = False
        if add_message_to_memory:
            chat_memory_obj.chat_memory.add_ai_message(assistant_final_message_for_memory) # Uses VSCH.add_message

if __name__ == "__main__":
    # Example: ensure GOOGLE_API_KEY is set for testing
    # You should set this in your .env file or environment
    # if 'GOOGLE_API_KEY' not in os.environ:
    #    os.environ['GOOGLE_API_KEY'] = 'YOUR_ACTUAL_API_KEY' 
    
    # For local testing, you might need to ensure GOOGLE_API_KEY is available
    # This is just an example, actual key should be managed securely via .env or environment
    # load_dotenv() # ensure .env is loaded if GOOGLE_API_KEY is there
    # if not os.getenv("GOOGLE_API_KEY"):
    #     print("Warning: GOOGLE_API_KEY not set. AI features may not work.")
    #     # os.environ['GOOGLE_API_KEY'] = 'dummy_key_for_testing_non_api_parts' # Or a real one for full test

    cli_app()
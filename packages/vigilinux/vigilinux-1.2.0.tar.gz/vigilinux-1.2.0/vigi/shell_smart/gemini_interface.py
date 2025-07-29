##############################################################
#                                                            #
#               Orchestrated by GitHub: naumanAhmed3         #
#                                                            #
#          <<<<< Generative AI Interaction Layer >>>>>       #
#                                                            #
##############################################################
"""
Manages all direct interactions with the Google Gemini Generative AI models.
It handles the creation of AI model instances, initiation of chat sessions,
sending requests for both chat and command generation, and processing the
AI's responses.
"""

import json
from typing import List, Optional 

import google.generativeai as gen_ai_api 
from google.generativeai import GenerativeModel as GeminiAIEngine 
from google.generativeai import ChatSession as GeminiAIChat 
from google.generativeai.types import GenerationConfig as AIGenerationOptions
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel

from .config import ApplicationSettings
from .cmd_gen_prompts import SystemInstructionBuilder
from .utils import CoreHelpers

class AICommunicationGateway:
    """
    Serves as the primary interface for communicating with Google's Gemini AI models.
    It abstracts the complexities of API calls, session management for chat,
    and response handling for both interactive chat and command generation tasks.
    """

    AI_CONTENT_SAFETY_CONFIGURATION = {
        "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
        "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
        "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
        "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE"
    }

    def __init__(self, app_config_instance: ApplicationSettings, instruction_builder_instance: SystemInstructionBuilder, display_manager_instance: Console):
        self.app_settings = app_config_instance
        self.ai_prompt_designer = instruction_builder_instance
        self.terminal_display = display_manager_instance

    def _instantiate_ai_engine_model(self, ai_engine_id: str) -> GeminiAIEngine:
        target_model_endpoint = self.app_settings.GOOGLE_AI_ENGINE_ENDPOINTS.get(ai_engine_id)
        if not target_model_endpoint:
            # Fallback to secondary if primary is misconfigured or ID is unknown, with a warning.
            self.terminal_display.log(f"[AI Gateway] [bold yellow]Warning: Unknown AI engine ID '{ai_engine_id}'. Falling back to secondary engine.[/bold yellow]")
            target_model_endpoint = self.app_settings.GOOGLE_AI_ENGINE_ENDPOINTS.get(self.app_settings.SECONDARY_AI_ENGINE)
            if not target_model_endpoint: # Should not happen if SECONDARY_AI_ENGINE is valid
                 raise ValueError(f"Fatal: Secondary AI engine ID '{self.app_settings.SECONDARY_AI_ENGINE}' is also invalid.")

        return GeminiAIEngine(target_model_endpoint)

    def establish_ai_chat_dialogue(self, ai_engine_id: str, prior_conversation_history: list = None) -> GeminiAIChat:
        ai_model_instance = self._instantiate_ai_engine_model(ai_engine_id)
        return ai_model_instance.start_chat(history=prior_conversation_history if prior_conversation_history else [])

    def stream_ai_chat_dialogue_response(
        self,
        user_message_text: str,
        active_chat_dialogue: GeminiAIChat,
        response_creativity_level: float,
    ) -> None:
        generation_parameters = AIGenerationOptions(temperature=response_creativity_level)
        ai_response_stream = active_chat_dialogue.send_message(
            user_message_text,
            stream=True,
            generation_config=generation_parameters,
            safety_settings=self.AI_CONTENT_SAFETY_CONFIGURATION
        )
        
        accumulated_response_parts = []
        display_pane_width = min(self.terminal_display.width, self.app_settings.STANDARD_OUTPUT_PANE_WIDTH or self.terminal_display.width)
        live_update_panel = Panel(
            "", 
            title="[bold blue]AI Assistant[/bold blue]",
            title_align="left",
            width=display_pane_width,
        )
        
        with Live(live_update_panel, refresh_per_second=10, console=self.terminal_display, transient=True) as live_display_manager:
            for response_chunk in ai_response_stream:
                chunk_text = response_chunk.text
                if chunk_text: 
                    accumulated_response_parts.append(chunk_text)
                    live_display_manager.update(Panel(
                        Markdown("".join(accumulated_response_parts), inline_code_theme="monokai"),
                        title="[bold blue]AI Assistant[/bold blue]",
                        title_align="left",
                        width=display_pane_width,
                    ))
        self.terminal_display.print()


    def request_instruction_from_ai(
        self, user_query_text: str, use_condensed_output: bool, ai_engine_id: str, target_os_for_instruction: str
    ) -> str:
        ai_model_instance = self._instantiate_ai_engine_model(ai_engine_id)
        prompt_message_sequence = list(self.ai_prompt_designer.assemble_instruction_generation_training_examples(use_condensed_output))
        prompt_message_sequence.append(
            self.ai_prompt_designer.format_actual_user_request_for_instruction_gen(user_query_text, target_os_for_instruction)
        )

        with self.terminal_display.status("[bold yellow]Vigi Shell is thinking (generating command)...[/bold yellow]", spinner="dots") as current_status_display:
            try:
                ai_api_response = ai_model_instance.generate_content(
                    contents=prompt_message_sequence,
                    generation_config=AIGenerationOptions(temperature=self.app_settings.INSTRUCTION_GENERATION_TEMPERATURE),
                    safety_settings=self.AI_CONTENT_SAFETY_CONFIGURATION,
                )

                if not ai_api_response.parts:
                    current_status_display.stop() 
                    if ai_api_response.prompt_feedback and ai_api_response.prompt_feedback.block_reason:
                        err_msg = f"Request blocked by AI content filter: {ai_api_response.prompt_feedback.block_reason_message}"
                        self.terminal_display.log(f"[AI Gateway] [bold red]{err_msg}[/bold red]")
                        return CoreHelpers.sanitize_ai_output_string(json.dumps({"error": 1, "message": err_msg}))
                    self.terminal_display.log("[AI Gateway] [bold red]AI returned an empty response for instruction generation.[/bold red]")
                    return CoreHelpers.sanitize_ai_output_string(json.dumps({"error": 1, "message": "AI returned an empty response"}))

                initial_ai_output_text = CoreHelpers.sanitize_ai_output_string(ai_api_response.text)
            except Exception as api_call_error:
                current_status_display.stop()
                err_msg = f"AI API Error: {api_call_error}"
                self.terminal_display.log(f"[AI Gateway] [bold red]Error during AI API call: {api_call_error}[/bold red]")
                return CoreHelpers.sanitize_ai_output_string(json.dumps({"error": 1, "message": err_msg}))

            try:
                json.loads(initial_ai_output_text) 
                return initial_ai_output_text 
            except json.JSONDecodeError as json_parsing_error:
                current_status_display.update("[yellow]AI output was not valid JSON. Requesting fix...[/yellow]")
                json_fix_prompt_sequence = prompt_message_sequence + [
                    self.ai_prompt_designer.format_actual_ai_response_for_instruction_gen(initial_ai_output_text)
                ]
                json_correction_request_text = (
                    f"The JSON output is malformed: {json_parsing_error}. "
                    f"Correct it and return only valid JSON:\n {initial_ai_output_text}"
                )
                json_fix_prompt_sequence.append({"role": "user", "parts": [json_correction_request_text]})

                try:
                    correction_api_response = ai_model_instance.generate_content(
                        contents=json_fix_prompt_sequence,
                        generation_config=AIGenerationOptions(temperature=self.app_settings.INSTRUCTION_GENERATION_TEMPERATURE),
                        safety_settings=self.AI_CONTENT_SAFETY_CONFIGURATION,
                    )

                    if not correction_api_response.parts: 
                        current_status_display.stop()
                        err_msg = "Failed to fix JSON (empty fix response)"
                        if correction_api_response.prompt_feedback and correction_api_response.prompt_feedback.block_reason:
                             err_msg = f"AI JSON fix blocked: {correction_api_response.prompt_feedback.block_reason_message}"
                             self.terminal_display.log(f"[AI Gateway] [bold red]{err_msg}[/bold red]")
                        else:
                            self.terminal_display.log("[AI Gateway] [bold red]AI empty response on JSON fix attempt.[/bold red]")
                        return CoreHelpers.sanitize_ai_output_string(json.dumps({"error": 1, "message": err_msg}))
                    
                    return CoreHelpers.sanitize_ai_output_string(correction_api_response.text)
                except Exception as fix_api_call_error:
                    current_status_display.stop()
                    err_msg = f"Failed to fix JSON (API error on fix): {fix_api_call_error}"
                    self.terminal_display.log(f"[AI Gateway] [bold red]Error during AI API call for JSON fix: {fix_api_call_error}[/bold red]")
                    return CoreHelpers.sanitize_ai_output_string(json.dumps({"error": 1, "message": err_msg}))

    def request_output_summary_from_ai(
        self,
        original_user_query: str,
        executed_command: str,
        command_stdout: str,
        command_stderr: str,
        command_success: bool
    ) -> Optional[str]: # Return type is string, even for errors or "no summary needed"
        """
        Requests a natural language summary of a command's output from the AI.
        """
        max_len = self.app_settings.MAX_OUTPUT_FOR_SUMMARY_PROMPT
        truncated_stdout = command_stdout[:max_len] + ("\n... (truncated)" if len(command_stdout) > max_len else "")
        truncated_stderr = command_stderr[:max_len] + ("\n... (truncated)" if len(command_stderr) > max_len else "")

        # Determine the core action based on common command prefixes for better "no output" summaries
        core_action_verb = "executed"
        cmd_lower = executed_command.lower()
        if cmd_lower.startswith("echo ") and ">" in cmd_lower:
            core_action_verb = "written to file"
        elif cmd_lower.startswith("mkfile") or cmd_lower.startswith("touch"):
            core_action_verb = "file creation attempted"
        elif cmd_lower.startswith("mkdir"):
            core_action_verb = "directory creation attempted"
        elif cmd_lower.startswith("del ") or cmd_lower.startswith("rm "):
            core_action_verb = "deletion attempted"
        elif cmd_lower.startswith("copy ") or cmd_lower.startswith("cp "):
            core_action_verb = "copy operation attempted"
        elif cmd_lower.startswith("move ") or cmd_lower.startswith("mv "):
            core_action_verb = "move operation attempted"


        prompt_parts = [
            "You are a command-line assistant. Your task is to provide an EXTREMELY CONCISE (1 sentence if possible) summary of a command's execution result.",
            f"User's original request: \"{original_user_query}\"",
            f"Command executed: `{executed_command}`",
        ]
        status_message = "The command reported successful execution." if command_success else "The command FAILED or reported errors."
        prompt_parts.append(status_message)

        # Only include stdout/stderr sections if they have content, to simplify the prompt for the AI
        # when there's no output.
        has_stdout = truncated_stdout.strip() and truncated_stdout.strip() != "<empty stdout>"
        has_stderr = truncated_stderr.strip() and truncated_stderr.strip() != "<empty stderr>"

        if has_stdout:
            prompt_parts.extend([
                "\nCommand's Standard Output (stdout):",
                "```text",
                truncated_stdout.strip(),
                "```",
            ])
        
        if has_stderr:
            prompt_parts.extend([
                "\nCommand's Standard Error (stderr):",
                "```text",
                truncated_stderr.strip(),
                "```",
            ])

        prompt_parts.append("\nYour Summary Task (be VERY brief):")
        if not command_success and has_stderr:
            prompt_parts.append("1. Explain the main error from stderr in one short sentence.")
        elif not command_success: # Failed but no stderr (e.g. command not found, caught by Python)
             prompt_parts.append("1. Briefly state that the command failed (e.g., 'Command failed to execute.').")
        elif command_success:
            if has_stdout:
                prompt_parts.append("1. In one sentence, what is the absolute key piece of information from stdout related to the user's request? Focus on the most direct answer.")
            elif not has_stdout and not has_stderr: # Successful, no stdout, no stderr
                # For commands like echo > file, mkdir, del (if quiet)
                prompt_parts.append(f"1. The command was successful and produced no direct output. Briefly confirm the action, e.g., 'Content {core_action_verb} successfully.' or 'Operation completed.'")
            elif has_stderr: # Successful but with stderr (warnings, etc.)
                prompt_parts.append("1. Command was successful but produced warnings/messages on stderr. Briefly mention this, e.g., 'Command succeeded with messages on stderr.' Do not detail stderr unless it's critical.")


        prompt_parts.extend([
            "\nIMPORTANT: Do NOT suggest new commands. Do NOT ask questions. Do NOT repeat the input.",
            "Your entire response should be a single, concise sentence or two at most."
        ])
        summary_prompt_text = "\n".join(prompt_parts)
        
    

        ai_engine_id_for_summary = self.app_settings.SECONDARY_AI_ENGINE
        ai_model_instance = self._instantiate_ai_engine_model(ai_engine_id_for_summary)
        
        
        with self.terminal_display.status("[bold yellow]Vigi is thinking (analyzing output)...[/bold yellow]", spinner="dots8"):
            try:
                generation_config = AIGenerationOptions(
                    temperature=0.1, # Lower temperature for more deterministic, factual summaries
                    max_output_tokens=150 # Restrict output length
                )
                
                response = ai_model_instance.generate_content(
                    summary_prompt_text,
                    generation_config=generation_config,
                    safety_settings=self.AI_CONTENT_SAFETY_CONFIGURATION
                )

                if response.parts:
                    summary_text = "".join(part.text for part in response.parts).strip()
                    if not summary_text and command_success and not has_stdout and not has_stderr:
                        # Fallback if AI still gives empty for "no output" successful commands
                        summary_text = f"The command `{executed_command.split()[0]}` completed successfully with no direct output."

                  
                    return summary_text if summary_text else "AI did not provide a specific summary for this output." # Ensure non-empty return
                elif response.prompt_feedback and response.prompt_feedback.block_reason:
                    block_msg = f"Summary generation blocked: {response.prompt_feedback.block_reason_message}"
                    return f"Error: AI summary blocked. ({block_msg})"
                else:
                    # Provide a generic message for successful "no output" commands if AI fails here
                    if command_success and not has_stdout and not has_stderr:
                        return f"The command `{executed_command.split()[0]}` completed successfully with no direct output."
                    return "AI analysis of output did not yield a specific summary."

            except Exception as e:
                error_msg = f"Error during AI call for summary: {e}"
                return f"Error: Could not get summary from AI. ({type(e).__name__})"

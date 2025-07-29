import os
import re
import json
import asyncio
import logging
from typing import List, Optional, Dict, Any, Callable
from collections.abc import Callable as CallableType
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_random_exponential

logger = logging.getLogger(__name__)

# Ensure API key is configured. Consider moving this to a central init if not already.
if os.getenv("GEMINI_API_KEY"):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
else:
    logger.warning("GEMINI_API_KEY environment variable not set. LLM calls will fail.")


VIGI_DEV_SYSTEM_PROMPT = """
You are a top tier AI developer writing a program based on user intent.
Fully implement every feature without TODOs. Add code comments explaining your implementation.
"""

CONVERSATION_PROMPT = """
You are maintaining a software project. Consider this conversation history:
{history}

Current project structure:
{file_tree}

Respond to the user's request while considering the existing codebase.
User: {input}
Assistant:
"""

MODIFICATION_PROMPT = """
Modify the existing codebase based on this request: {request}

Existing files:
{existing_files}

Provide ONLY a JSON object where:
- Keys are relative file paths (strings).
- Values are the **complete new content** for that file (strings).
Example: {{"src/app.js": "console.log(\\'Hello World!\\');\n// more code...", "public/index.html": "<!DOCTYPE html>..."}}
"""

QA_PROMPT = """
Answer this question about the codebase: {question}

Relevant code files:
{relevant_code}

Provide a concise technical answer:
"""

GENERATE_SLUG_PROMPT = """
Based on the following user prompt, suggest a short, descriptive, filesystem-friendly project name (slug).
The slug should be in kebab-case (all lowercase, words separated by hyphens).
It should not contain spaces or special characters other than hyphens. Aim for 2-5 words.
Examples:
User Prompt: "a simple pong game in javascript" -> Slug: "simple-pong-game"
User Prompt: "complex data analysis tool with python and pandas" -> Slug: "data-analysis-tool"
User Prompt: "My new web app" -> Slug: "my-new-web-app"

User Prompt: {user_prompt}

Return ONLY the slug:
"""

def generate_project_slug(user_prompt: str, model: str = 'gemini-1.5-pro-latest') -> str:
    """Generates a filesystem-friendly project slug from a user prompt."""
    
    prompt_text = GENERATE_SLUG_PROMPT.format(user_prompt=user_prompt)
    
    try:
        model_instance = genai.GenerativeModel(model)
        response = model_instance.generate_content(
            prompt_text,
            generation_config=genai.GenerationConfig(temperature=0.4, max_output_tokens=50))

        slug = response.text.strip().lower()
        # Basic sanitization, LLM should mostly follow kebab-case instruction
        slug = re.sub(r'\s+', '-', slug) # Replace spaces with hyphens
        slug = re.sub(r'[^a-z0-9-]', '', slug) # Remove non-alphanumeric or hyphen chars
        slug = re.sub(r'-+', '-', slug) # Replace multiple hyphens with single
        slug = slug.strip('-') # Remove leading/trailing hyphens

        if not slug: # Fallback if LLM fails or sanitization removes everything
            # Create a simple slug from the prompt directly if LLM fails
            slug = "-".join(user_prompt.lower().split()[:3])
            slug = re.sub(r'[^a-z0-9-]', '', slug)
            slug = re.sub(r'-+', '-', slug).strip('-')
            return slug if slug else "unnamed-project"
        return slug
    except Exception as e:
        logger.error(f"Error generating project slug: {e}")
        # Create a simple slug from the prompt directly if LLM fails
        slug = "-".join(user_prompt.lower().split()[:3])
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        slug = re.sub(r'-+', '-', slug).strip('-')
        return slug if slug else "error-unnamed-project"


def specify_file_paths(prompt: str, plan: str, model: str = 'gemini-1.5-pro-latest') -> List[str]:


    prompt_text = f"""
    {VIGI_DEV_SYSTEM_PROMPT}
    Generate a JSON array of **relative file paths** needed for this project.
    Paths should be relative to the project's root directory.
    Filenames should be appropriate for their content and OS-agnostic where possible.
    - DO NOT include absolute paths (e.g., paths starting with / or a drive letter like C:\\).
    - DO NOT use ".." to navigate to parent directories. All paths must be within the project.
    - Ensure paths are valid filenames or relative paths like "src/components/button.js".
    
    Example: ["index.html", "styles.css", "app.js", "src/components/button.js"]
    
    User Prompt: {prompt}
    Plan: {plan}
    
    Return ONLY a JSON array of strings representing relative file paths:
    """
    
    try:
        model_instance = genai.GenerativeModel(model)
        response = model_instance.generate_content(
            prompt_text,
            generation_config=genai.GenerationConfig(temperature=0.7))
        
        # Extract JSON array more robustly
        match = re.search(r'\[\s*(?:".*?"\s*,\s*)*".*?"\s*\]|\[\s*\]', response.text, re.DOTALL)
        if match:
            json_str = match.group(0)
            return json.loads(json_str)
        else:
            logger.error(f"Failed to find a valid JSON array in LLM response for file paths: {response.text}")
            # Attempt to extract paths if they are just listed without proper JSON array
            lines = [line.strip() for line in response.text.splitlines() if line.strip().endswith(('.html', '.css', '.js', '.py', '.md', '.json', '.txt'))] # common extensions
            if lines:
                 logger.warning(f"Attempting to use line-extracted paths: {lines}")
                 return lines
            return []
    except Exception as e:
        logger.error(f"Failed to parse file paths from LLM response '{response.text}': {e}")
        return []

def plan(prompt: str, 
         stream_handler: Optional[Callable[[bytes], None]] = None, 
         model: str = 'gemini-1.5-pro-latest', 
         extra_messages: List[Dict[str, str]] = []) -> str: # extra_messages not used currently
  

    full_prompt = f"""
    {VIGI_DEV_SYSTEM_PROMPT}
    Create a development plan using GitHub Markdown. Start with a YAML block describing files to create.
    Include for each file: variables, schemas, DOM IDs, and function names.
    
    App Prompt: {prompt}
    """
    
    try:
        model_instance = genai.GenerativeModel(model)
        response_stream = model_instance.generate_content(
            full_prompt,
            generation_config=genai.GenerationConfig(temperature=0.7),
            stream=True)
        
        collected = []
        for chunk in response_stream:
            text = chunk.text
            collected.append(text)
            if stream_handler and text: # Ensure text is not empty
                stream_handler(text.encode('utf-8')) # Explicitly encode
        
        return "".join(collected)
    except Exception as e:
        logger.error(f"Error in plan generation stream: {e}")
        return f"Error during plan generation: {e}"


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
async def generate_code(prompt: str, # prompt (original user prompt) is not directly used here, but kept for consistency
                       plan_details: str,  # Renamed from 'plan' to avoid conflict with the plan function
                       current_file: str,
                       stream_handler: Optional[Callable[[bytes], Any]] = None,
                       model_name: str = 'gemini-1.5-pro-latest') -> str:
   
    full_prompt = f"""
    {VIGI_DEV_SYSTEM_PROMPT}
    You are generating code for the file: {current_file}
    Follow this overall development plan:
    {plan_details}
    
    User's Original Goal (for context): {prompt}

    Instructions:
    1. Generate ONLY the complete, valid code for the file `{current_file}`.
    2. Ensure the code is fully functional and implements the requirements for this specific file as per the plan.
    3. Do not add any explanatory text, markdown, or comments *outside* the code block if one is used.
    4. If the file is a configuration file (e.g. JSON, YAML), just output the raw content.
    5. If the file is a script (e.g. Python, JavaScript), output the code, ideally within a ```<language_hint> ... ``` block if appropriate, but ensure ONLY code is present. If no language hint, just raw code.
    
    Code for {current_file}:
    """
    
    async def sync_generate() -> str: # Changed to async def for direct await
        model = genai.GenerativeModel(model_name)
        response_stream = model.generate_content( # Renamed variable to avoid conflict
            full_prompt,
            generation_config=genai.GenerationConfig(temperature=0.5, max_output_tokens=4096), # Adjusted temp
            stream=True)
        
        collected = []
        for chunk in response_stream:
            text = chunk.text
            collected.append(text)
            if stream_handler and text:
                stream_handler(text.encode('utf-8'))
        return "".join(collected)
    
    try:
        code_content = await sync_generate() # directly await the async function
        
        # Refined extraction: Prioritize fenced code blocks, then fallback to raw if no blocks
        # This regex looks for ``` followed by an optional language, then captures content, then ```
        code_blocks = re.findall(r"```(?:[a-zA-Z0-9_+\-]+)?\s*\n(.*?)\n```", code_content, re.DOTALL)
        if code_blocks:
            return code_blocks[0].strip() # Return the content of the first block
        else:
            # If no fenced blocks, assume the whole response is code (after stripping prompt remnants if any)
            # This is a basic fallback. More sophisticated stripping might be needed if LLM adds preamble.
            return code_content.strip() 
    except Exception as e:
        logger.error(f"Error generating code for {current_file}: {e}")
        return f"// Error generating code for {current_file}: {e}"


def generate_code_sync(prompt: str, 
                      plan_details: str, 
                      current_file: str,
                      stream_handler: Optional[Callable[[bytes], Any]] = None,
                      model: str = 'gemini-1.5-pro-latest') -> str:
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If in an async context already, create a task
            # This part is tricky without knowing the broader async setup.
            # For simplicity in a sync script, we run a new loop if needed.
            # However, if main.py is run by an async framework, this might cause issues.
            # A robust solution involves an async-to-sync bridge or running main.py's core logic in an async func.
            # For now, let's assume generate_code_sync is called from a purely synchronous context
            # or where a new event loop is acceptable for this specific task.
            # logger.warning("generate_code_sync called from a running event loop. This might be suboptimal.")
            # fut = asyncio.ensure_future(generate_code(prompt, plan_details, current_file, stream_handler, model))
            # return loop.run_until_complete(fut) # This can lead to "cannot be nested" errors
            # Simplest for now, but may need refinement based on how main.py is run:
            return asyncio.run(generate_code(prompt, plan_details, current_file, stream_handler, model))

        else:
            return loop.run_until_complete(
                generate_code(prompt, plan_details, current_file, stream_handler, model))
    except RuntimeError as e:
        if "cannot be nested" in str(e):
            logger.error("Asyncio event loop nesting error in generate_code_sync. "
                         "Consider restructuring async calls or using nest_asyncio if appropriate.")
            # Fallback to a very simple blocking call (less ideal as it bypasses retry and proper streaming logic)
            if genai.api_key:
                model_instance = genai.GenerativeModel(model)
                full_prompt_text = f"{VIGI_DEV_SYSTEM_PROMPT}\nGenerate ONLY valid code for {current_file} based on this plan:\n{plan_details}\nUser Prompt: {prompt}"
                response = model_instance.generate_content(full_prompt_text)
                code_blocks = re.findall(r"```(?:.*?)\n(.*?)```", response.text, re.DOTALL)
                return code_blocks[0] if code_blocks else response.text.strip()
            return f"// Error due to event loop nesting for {current_file}"
        raise e # Re-raise other RuntimeErrors

async def handle_conversation(context: Dict[str, Any], 
                            user_input: str,
                            model_name: str = 'gemini-1.5-pro-latest') -> str: # Renamed model to model_name
    

    prompt = CONVERSATION_PROMPT.format(
        history="\n".join([f"{msg['role']}: {msg['content']}" 
                          for msg in context.get('conversation_history', [])]),
        file_tree="\n".join(context.get('file_paths', [])), # This should be a proper file tree from utils
        input=user_input
    )
    
    try:
        model_instance = genai.GenerativeModel(model_name)
        response = await asyncio.to_thread(model_instance.generate_content, prompt) # Run blocking call in thread
        return response.text
    except Exception as e:
        logger.error(f"Error handling conversation: {e}")
        return f"Error during conversation: {e}"


def handle_conversation_sync(context: Dict[str, Any], 
                           user_input: str,
                           model: str = 'gemini-1.5-pro-latest') -> str:
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return asyncio.run(handle_conversation(context, user_input, model))
        else:
            return loop.run_until_complete(
                handle_conversation(context, user_input, model))
    except RuntimeError:
        # Fallback for nesting error, similar to generate_code_sync
        if genai.api_key:
            model_instance = genai.GenerativeModel(model)
            prompt_text = CONVERSATION_PROMPT.format(history="...", file_tree="...", input=user_input) # Simplified for fallback
            response = model_instance.generate_content(prompt_text)
            return response.text
        return "Error: Could not handle conversation due to event loop issue."

async def generate_modification(context: Dict[str, Any], 
                              request: str,
                              model_name: str = 'gemini-1.5-pro-latest') -> Dict[str, str]: # Renamed model
  

    existing_files_parts = []
    for path in context.get('file_paths', []):
        content = context['codebase'].get(path, f'// File {path} exists but no content loaded or available.')
        existing_files_parts.append(f"File: {path}\nContent:\n{content}")
    existing_files_str = "\n\n---\n\n".join(existing_files_parts)

    # The MODIFICATION_PROMPT itself implies JSON output.
    # We use generate_code which is general, but the prompt guides the LLM.
    # The `current_file` argument to `generate_code` here is a bit of a misnomer,
    # as we expect JSON output, not code for a single file.
    # We name it 'modifications.json' conceptually.
    
    # The prompt for modification needs to be very specific about JSON output.
    modification_prompt_text = MODIFICATION_PROMPT.format(request=request, existing_files=existing_files_str)
    
    # We are asking generate_code to produce JSON, not code for a "current_file"
    # So, the "plan_details" for generate_code will be this modification_prompt_text itself.
    # And "current_file" is just a conceptual name for the JSON output.
    try:
        json_response_str = await generate_code(
            prompt=request, # The user's overall modification request
            plan_details=modification_prompt_text, # The detailed prompt asking for JSON
            current_file="modifications.json", # Conceptual name for the JSON output
            model_name=model_name
        )
        
        # Try to find JSON within potential markdown code blocks
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', json_response_str, re.DOTALL | re.MULTILINE)
        if match:
            json_str_cleaned = match.group(1)
        else:
            # If no block, assume raw output is JSON or needs cleaning
            # This is risky if LLM doesn't strictly output JSON.
            # A more robust approach might be to find the first '{' and last '}'
            first_brace = json_response_str.find('{')
            last_brace = json_response_str.rfind('}')
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                json_str_cleaned = json_response_str[first_brace : last_brace+1]
            else: # Could not reliably find JSON structure
                logger.error(f"Could not find JSON structure in modification response: {json_response_str}")
                return {"error": "LLM response did not contain a recognizable JSON object for modifications."}


        return json.loads(json_str_cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON from modification response: '{json_str_cleaned}'. Error: {e}")
        return {"error": f"Failed to parse LLM JSON output for modifications. Content (cleaned): {json_str_cleaned[:200]}..."}
    except Exception as e:
        logger.error(f"Error generating modification: {e}")
        return {"error": f"General error during modification: {e}"}


def generate_modification_sync(context: Dict[str, Any], 
                             request: str,
                             model: str = 'gemini-1.5-pro-latest') -> Dict[str, str]:
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return asyncio.run(generate_modification(context, request, model))
        else:
            return loop.run_until_complete(
                generate_modification(context, request, model))
    except RuntimeError:
        # Simplified fallback
        return {"error": "Could not generate modification due to event loop issue."}


async def answer_question(context: Dict[str, Any],
                        question: str,
                        model_name: str = 'gemini-1.5-pro-latest') -> str: # Renamed model
  
    relevant_files = context.get('file_paths', []) # Or a smarter way to select relevant files
    relevant_code_parts = []
    for path in relevant_files: # Consider only showing a snippet or relevant functions
        code_snippet = context['codebase'].get(path, f'// Code for {path} not available.')
        # Truncate long files for the prompt
        if len(code_snippet) > 1500:
            code_snippet = code_snippet[:1500] + "\n... (file truncated)\n"
        relevant_code_parts.append(f"File: {path}\n{code_snippet}")
    relevant_code_str = "\n\n---\n\n".join(relevant_code_parts)
    
    try:
        model_instance = genai.GenerativeModel(model_name)
        response = await asyncio.to_thread( # Run blocking call in thread
            model_instance.generate_content,
            QA_PROMPT.format(question=question, relevant_code=relevant_code_str)
        )
        return response.text
    except Exception as e:
        logger.error(f"Error answering question: {e}")
        return f"Error during question answering: {e}"


def answer_question_sync(context: Dict[str, Any],
                        question: str,
                        model: str = 'gemini-1.5-pro-latest') -> str:
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return asyncio.run(answer_question(context, question, model))
        else:
            return loop.run_until_complete(
                answer_question(context, question, model))
    except RuntimeError:
         # Simplified fallback
        return "Error: Could not answer question due to event loop issue."
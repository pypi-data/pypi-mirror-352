import os
import traceback # Added for logging exception info
# import colorama # colorama will be initialized and used in main scripts primarily

# --- LLM Configurations ---
# API keys for LLMs are now expected to be set as environment variables.
# The `api_key_env_var` field in each configuration below specifies the
# name of the environment variable that should hold the API key.

LLM_CONFIGS = {
    "gemini": {
        "api_key_env_var": "GEMINI_API_KEY",  # Environment variable for Gemini API Key
        "model_name": "gemini-1.5-flash", # Updated to a common and recent model
        "temperature": 0.3,
        "description": "Google Gemini LLM. Good for a balance of capabilities and cost."
    },
    "groq": {
        "api_key_env_var": "GROQ_API_KEY",    # Environment variable for Groq API Key
        "model_name": "llama3-8b-8192",    # Groq hosted Llama3
        "temperature": 0.2,
        "description": "Groq hosted LLM (e.g., Llama3). Known for high speed."
    }
    # Add more providers here if needed
    # Ensure each provider has an "api_key_env_var" entry
    # pointing to the correct environment variable name.
}

# --- Verbose Printing ---
VERBOSE = False  # Set to False to reduce console output

# --- ANSI Color Definitions ---
class AnsiColors:
    # For foreground
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    GRAY = "\033[90m" # Bright black / Dark Gray

    # For bright foreground
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # Styles
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"

class Theme:
    USER_PROMPT = AnsiColors.BRIGHT_GREEN + AnsiColors.BOLD
    AI_PROMPT = AnsiColors.BRIGHT_CYAN + AnsiColors.BOLD
    SYSTEM_INFO = AnsiColors.BRIGHT_BLUE
    MUTED_SYSTEM_INFO = AnsiColors.BLUE 
    SUCCESS = AnsiColors.BRIGHT_GREEN
    ERROR = AnsiColors.BRIGHT_RED + AnsiColors.BOLD
    WARNING = AnsiColors.BRIGHT_YELLOW # No bold to make it softer than error
    COMMAND = AnsiColors.MAGENTA + AnsiColors.BOLD
    VERBOSE_PREFIX = AnsiColors.DIM + AnsiColors.GRAY 
    SECTION_HEADER = AnsiColors.BRIGHT_MAGENTA + AnsiColors.BOLD
    HIGHLIGHT = AnsiColors.BRIGHT_YELLOW # For highlighting parts of messages
    STATUS = AnsiColors.CYAN # For general status updates

    # Helper to ensure reset, useful if colorama's autoreset is not fully relied upon or for inline styling.
    @staticmethod
    def F(style, text): # Format
        return f"{style}{text}{AnsiColors.RESET}"
    
    @staticmethod
    def H_TEXT(text): # Header Text (from user prompts/content)
        return f"{AnsiColors.BOLD}{text}{AnsiColors.RESET}"


def v_print(message, **kwargs):
    """Prints a message if VERBOSE is True.
    Handles 'exc_info' kwarg to print traceback like logging.error.
    """
    if VERBOSE:
        exc_info_flag = kwargs.pop('exc_info', False)
        # Ensure Theme.VERBOSE_PREFIX and AnsiColors.RESET are applied correctly.
        # colorama.init(autoreset=True) should handle the final reset.
        print(f"{Theme.VERBOSE_PREFIX}[V] {message}{AnsiColors.RESET}", **kwargs)
        if exc_info_flag:
            # This mimics logging.error(..., exc_info=True)
            # Should be called from within an except block for traceback.print_exc() to work correctly.
            traceback.print_exc()

# Example of how to understand the new config structure:
# To use "gemini":
# 1. Set the environment variable GEMINI_API_KEY with your actual Gemini API key.
# 2. The application will read this environment variable when initializing Gemini.
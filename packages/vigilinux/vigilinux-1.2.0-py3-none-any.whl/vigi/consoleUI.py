# consoleUI.py
from typing import Callable, Generator
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
# from rich.panel import Panel # Panel will not be used to wrap the main content anymore
# from rich.rule import Rule # Rule will not be used to introduce the content anymore
from rich.text import Text
import time # Keep for the sleep, though we might adjust it

# This console can be shared if needed, but functions currently create their own.
# For now, we'll keep local console instances to minimize structural changes.

def render_markdown_in_real_time_by_accumulating_text_chunks(
    text_chunks_generator: Generator[str, None, None],
    code_theme_for_markdown: str
) -> str:
    complete_markdown_text_accumulated_from_chunks = ""
    rich_console_instance_for_output = Console()
    # The Live display will now update the Markdown object directly.
    # This means no extra panel or title around the AI's markdown response.
    with Live(console=rich_console_instance_for_output, refresh_per_second=12) as live_display_updater_for_real_time_rendering: 
        for individual_text_segment_from_generator in text_chunks_generator:
            # The original time.sleep(0.5) is very slow for a chat interface.
            # Reducing it significantly for a more responsive feel.
            # If the generator yields chunks at a good pace, this might even be removed or set smaller.
            time.sleep(0.02) # Reduced for better chat feel
            complete_markdown_text_accumulated_from_chunks += individual_text_segment_from_generator
            markdown_object_for_rendering = Markdown(
                markup=complete_markdown_text_accumulated_from_chunks,
                code_theme=code_theme_for_markdown
            )
            # REMOVED Panel wrapping. Update with the Markdown object directly.
            live_display_updater_for_real_time_rendering.update(markdown_object_for_rendering)
    # Ensure a newline after the live display finishes so the next prompt isn't on the same line.
    rich_console_instance_for_output.line()
    return complete_markdown_text_accumulated_from_chunks

def display_text_chunks_immediately_with_color(
    text_chunks_generator: Generator[str, None, None],
    text_color_for_display: str
) -> str:
    complete_text_accumulated_from_chunks = ""
    rich_console_instance_for_output = Console()
    # Live display will update the Text object directly.
    with Live(console=rich_console_instance_for_output, refresh_per_second=12) as live_display_updater_for_real_time_rendering:
        for individual_text_segment_from_generator in text_chunks_generator:
            # No explicit sleep here, assuming text chunks arrive at a reasonable rate
            # or the application's nature doesn't require artificial slowing for plain text.
            # If it's too fast, a small time.sleep(0.01) could be added.
            complete_text_accumulated_from_chunks += individual_text_segment_from_generator
            text_renderable = Text(complete_text_accumulated_from_chunks, style=text_color_for_display)
            # REMOVED Panel wrapping. Update with the Text object directly.
            live_display_updater_for_real_time_rendering.update(text_renderable)
    # Ensure a newline after the live display finishes
    rich_console_instance_for_output.line()
    return complete_text_accumulated_from_chunks

def choose_between_real_time_and_static_markdown_rendering(
    text_chunks_generator: Generator[str, None, None],
    flag_indicating_real_time_rendering: bool,
    code_theme_for_markdown: str
) -> str:
    if flag_indicating_real_time_rendering:
        return render_markdown_in_real_time_by_accumulating_text_chunks(
            text_chunks_generator,
            code_theme_for_markdown
        )
    else: # Static (non-streaming) Markdown
        rich_console_instance_for_output = Console()
        # The "Loading..." status is fine to keep.
        with rich_console_instance_for_output.status("[bold green]Loading..."):
            complete_markdown_text_for_static_rendering = "".join(text_chunks_generator)
        
        markdown_object_for_static_rendering = Markdown(
            markup=complete_markdown_text_for_static_rendering,
            code_theme=code_theme_for_markdown
        )
        # REMOVED Rule and Panel. Print the Markdown object directly.
        rich_console_instance_for_output.print(markdown_object_for_static_rendering)
        # Ensure a newline after the static output
        rich_console_instance_for_output.line()
        return complete_markdown_text_for_static_rendering

def choose_between_real_time_and_static_text_display(
    text_chunks_generator: Generator[str, None, None],
    flag_indicating_real_time_display: bool,
    text_color_for_display: str
) -> str:
    if flag_indicating_real_time_display:
        return display_text_chunks_immediately_with_color(
            text_chunks_generator,
            text_color_for_display
        )
    else: # Static (non-streaming) Text
        rich_console_instance_for_output = Console()
        # The "Loading..." status is fine to keep.
        with rich_console_instance_for_output.status("[bold green]Loading..."):
            complete_text_for_static_display = "".join(text_chunks_generator)
        
        text_renderable = Text(complete_text_for_static_display, style=text_color_for_display)
        # REMOVED Rule and Panel. Print the Text object directly.
        rich_console_instance_for_output.print(text_renderable)
        # Ensure a newline after the static output
        rich_console_instance_for_output.line()
        return complete_text_for_static_display

def select_appropriate_printing_function_based_on_markdown_flag(
    flag_indicating_markdown_usage: bool,
    code_theme_for_markdown: str,
    default_color_for_text: str
) -> Callable[[Generator[str, None, None], bool], str]:
    # This function's logic remains the same, it just returns one of the modified printers.
    if flag_indicating_markdown_usage:
        return lambda text_chunks_generator, flag_indicating_real_time_rendering: choose_between_real_time_and_static_markdown_rendering(
            text_chunks_generator,
            flag_indicating_real_time_rendering,
            code_theme_for_markdown
        )
    else:
        return lambda text_chunks_generator, flag_indicating_real_time_display: choose_between_real_time_and_static_text_display(
            text_chunks_generator,
            flag_indicating_real_time_display,
            default_color_for_text
        )
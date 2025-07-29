# fanficdownloader/cli.py
import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm

# Initialize Typer app
app = typer.Typer(
    no_args_is_help=True, # This will show help if no args are given, but we'll override it
    rich_markup_mode="rich",
    help="FanFic Downloader CLI - Download fan fiction stories from various sites"
)

# Initialize Rich console (main instance, though others are also initialized in modules)
console = Console()

# Import command functions from their respective modules
# Renamed command functions to avoid clashes with original script's local function names
from fanfic_downloader.commands.download import download_stories_command
from fanfic_downloader.commands.extract import extract_story_urls_command
from fanfic_downloader.commands.update import update_epub_files_command
from fanfic_downloader.commands.list import list_downloaded_files_command
from fanfic_downloader.commands.settings import manage_settings_command
from fanfic_downloader.commands.help import show_help_command

# Add commands to the Typer app instance
app.command(name="download", help="[bold blue]Download[/bold blue] fan fiction stories.")(download_stories_command)
app.command(name="extract", help="[bold blue]Extract[/bold blue] story URLs from a source.")(extract_story_urls_command)
app.command(name="update", help="[bold blue]Update[/bold blue] existing downloaded EPUB files.")(update_epub_files_command)
app.command(name="list", help="[bold blue]List[/bold blue] previously downloaded stories.")(list_downloaded_files_command)
app.command(name="settings", help="[bold blue]Manage[/bold blue] application settings.")(manage_settings_command)
app.command(name="help", help="[bold blue]Help[/bold blue] Get help Commands")(show_help_command) # The `help` command is often explicitly added

@app.callback()
def main_callback(ctx: typer.Context):
    """
    FanFic Downloader CLI tool.
    """
    pass
# --- Main Callback for Interactive Mode ---

def run():
    """Entry point for the application."""
    app()

if __name__ == "__main__":
    app()
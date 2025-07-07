import typer
from pathlib import Path
from rich.console import Console
from . import converter, mover, utils

app = typer.Typer(rich_markup_mode="markdown")
console = Console()

@app.command()
def convert(
    input_dir: Path = typer.Argument(..., help="Directory containing ProRes files to convert.", exists=True, file_okay=False, dir_okay=True, readable=True),
    output_dir: Path = typer.Argument(..., help="Directory to save converted H.264 files.", file_okay=False, dir_okay=True, writable=True),
    workers: int = typer.Option(4, "--workers", "-w", help="Number of videos to process in parallel.")
):
    """
    Converts all ProRes .mov files in a directory to H.264 format.
    """
    console.print(f"Starting conversion from [cyan]{input_dir}[/cyan] to [cyan]{output_dir}[/cyan]...")
    with console.status("[bold green]Processing videos...", spinner="dots") as status:
        for result in converter.run_conversion(input_dir, output_dir, workers):
            console.print(result)
    console.print("[bold green]Conversion process complete![/bold green]")

@app.command()
def move(
    source_dir: Path = typer.Argument(..., help="Directory containing original ProRes files to move.", exists=True, file_okay=False, dir_okay=True, readable=True),
    archive_dir: Path = typer.Argument(..., help="Directory to archive the ProRes files.", file_okay=False, dir_okay=True, writable=True)
):
    """
    Moves all ProRes .mov files from a source directory to an archive directory.
    """
    console.print(f"Archiving ProRes files from [cyan]{source_dir}[/cyan] to [cyan]{archive_dir}[/cyan]...")
    for result in mover.move_prores_files(source_dir, archive_dir):
        console.print(result)

@app.command()
def verify(
    video_path: Path = typer.Argument(..., help="Path to the video file to verify.", exists=True, file_okay=True, dir_okay=False, readable=True)
):
    """
    Verifies if a single video file is a ProRes file and checks for an alpha channel.
    """
    console.print(f"Verifying file: [cyan]{video_path}[/cyan]")
    is_prores_file = utils.is_prores(str(video_path))
    
    if not is_prores_file:
        console.print("[bold red]✗ The file is not a ProRes video.[/bold red]")
        return

    console.print("[bold green]✓ The file is a ProRes video.[/bold green]")
    
    has_alpha = utils.has_alpha_channel(str(video_path))
    if has_alpha:
        console.print("[bold yellow]  - It contains an alpha channel.[/bold yellow]")
    else:
        console.print("  - It does not contain an alpha channel.")

if __name__ == "__main__":
    app() 
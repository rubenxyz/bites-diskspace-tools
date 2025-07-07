import typer
from pathlib import Path
from rich.console import Console
from . import converter, utils, reporter, deleter

app = typer.Typer(rich_markup_mode="markdown")
console = Console()

@app.command()
def convert(
    scan_dir: Path = typer.Argument(..., help="Directory to scan for ProRes files to convert.", exists=True, file_okay=False, dir_okay=True, readable=True),
    workers: int = typer.Option(4, "--workers", "-w", help="Number of videos to process in parallel.")
):
    """
    Recursively converts ProRes files to H.264, managing originals in subfolders.
    """
    console.print(f"Starting recursive conversion scan in [cyan]{scan_dir}[/cyan]...")
    console.print("Originals will be moved to a [bold]_CONVERTED[/bold] subfolder in their respective directories.")
    with console.status("[bold green]Processing videos...", spinner="dots") as status:
        for result in converter.run_conversion(scan_dir, workers):
            console.print(result)
    console.print("[bold green]Conversion process complete![/bold green]")

@app.command(help="Moves ProRes files in folders ending with .PRV to the Trash.")
def remove_prv(
    scan_dir: Path = typer.Argument(..., help="Directory to scan for .PRV folders.", exists=True, file_okay=False, dir_okay=True, readable=True),
):
    """
    Finds and moves ProRes files (without alpha) in subfolders ending with .PRV to the Trash.
    """
    console.print(f"Scanning [cyan]{scan_dir}[/cyan] for ProRes files in .PRV folders...")
    with console.status("[bold green]Scanning files...", spinner="dots"):
        files_to_delete = deleter.remove_prv_files(scan_dir)

    if not files_to_delete:
        console.print("[bold green]No matching files found to move to Trash.[/bold green]")
        return

    console.print(f"[bold yellow]Found {len(files_to_delete)} file(s) to move to Trash:[/bold yellow]")
    for f in files_to_delete:
        console.print(f"- {f.relative_to(scan_dir)}")
    
    confirm = typer.confirm(
        "Are you sure you want to move these files to the Trash?", 
        abort=True
    )
    
    console.print("\n[bold]Moving files to Trash...[/bold]")
    for result in deleter.delete_files(files_to_delete):
        console.print(result)
    
    console.print("\n[bold green]Process complete![/bold green]")

@app.command()
def report(
    target_dir: Path = typer.Argument(..., help="Directory to scan for a ProRes report.", exists=True, file_okay=False, dir_okay=True, readable=True)
):
    """
    Generates a PDF report of all ProRes files in a directory tree.
    """
    console.print(f"Generating ProRes PDF report for [cyan]{target_dir}[/cyan]...")
    with console.status("[bold green]Scanning files and building report...", spinner="dots"):
        report_path = reporter.generate_report(target_dir)
    console.print(f"[bold green]✓ Report successfully created at:[/bold green] [cyan]{report_path}[/cyan]")

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
import subprocess
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from .utils import is_prores, has_alpha_channel

def convert_to_h264(video_path: Path, output_dir: Path):
    """Converts a single video file to H.264."""
    output_file = output_dir / video_path.name
    
    if output_file.exists() and output_file.stat().st_size > 0:
        return f"Skipped (already converted): {video_path.name}"

    command = [
        "ffmpeg",
        "-i", str(video_path),
        "-c:v", "libx264", "-crf", "23", "-preset", "medium",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        "-y", str(output_file)
    ]
    
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        if output_file.exists() and output_file.stat().st_size > 0:
            return f"Successfully converted: {video_path.name}"
        else:
            if output_file.exists():
                output_file.unlink() # Clean up empty file
            return f"Conversion failed (zero size output): {video_path.name}"
    except subprocess.CalledProcessError as e:
        if output_file.exists():
            output_file.unlink() # Clean up corrupt file
        return f"Conversion failed for {video_path.name}: {e.stderr}"

def run_conversion(input_dir: Path, output_dir: Path, max_workers: int = 4):
    """Scans a directory and converts all ProRes .mov files to H.264 in parallel."""
    if not shutil.which("ffmpeg"):
        raise FileNotFoundError("ffmpeg not found. Please install ffmpeg.")

    output_dir.mkdir(parents=True, exist_ok=True)
    
    prores_files = [
        f for f in input_dir.glob("*.mov") 
        if f.is_file() and is_prores(f)
    ]

    files_to_process = []
    for f in prores_files:
        if has_alpha_channel(f):
            yield f"Skipped (has alpha channel): {f.name}"
        else:
            files_to_process.append(f)

    if not files_to_process:
        if not prores_files: # Only show this if no prores files were found at all
            yield "No suitable ProRes .mov files found to convert."
        return

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(convert_to_h264, f, output_dir): f for f in files_to_process}
        for future in as_completed(futures):
            yield future.result() 
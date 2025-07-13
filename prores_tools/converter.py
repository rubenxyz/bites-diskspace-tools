import subprocess
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from .utils import find_prores_files_fast

def convert_to_h264(video_path: Path):
    """
    Moves a video to a processing folder within its own directory, converts it,
    and then moves the original to a converted folder.
    """
    original_path = video_path
    parent_dir = original_path.parent
    
    processing_dir = parent_dir / "_PROCESSING"
    converted_dir = parent_dir / "_SOURCE"
    
    processing_dir.mkdir(exist_ok=True)
    converted_dir.mkdir(exist_ok=True)

    processing_path = processing_dir / original_path.name
    output_path = original_path

    try:
        shutil.move(str(original_path), str(processing_path))

        command = [
            "ffmpeg", "-i", str(processing_path),
            "-c:v", "libx264", "-crf", "23", "-preset", "medium",
            "-pix_fmt", "yuv420p", "-c:a", "copy",
            "-movflags", "+faststart", "-y", str(output_path)
        ]
        subprocess.run(command, check=True, capture_output=True, text=True)

        if output_path.exists() and output_path.stat().st_size > 0:
            converted_path = converted_dir / original_path.name
            shutil.move(str(processing_path), str(converted_path))
            return f"Successfully converted: {original_path.relative_to(original_path.parents[2])}"
        else:
            shutil.move(str(processing_path), str(original_path))
            return f"Conversion failed (zero size output): {original_path.name}"
    except (subprocess.CalledProcessError, Exception) as e:
        if processing_path.exists():
            shutil.move(str(processing_path), str(original_path))
        error_message = e.stderr if isinstance(e, subprocess.CalledProcessError) else str(e)
        return f"Conversion failed for {original_path.name}: {error_message}"

def run_conversion(scan_dir: Path, max_workers: int = 4):
    """Scans a directory tree and converts all valid ProRes .mov files."""
    if not shutil.which("ffmpeg"):
        raise FileNotFoundError("ffmpeg not found. Please install ffmpeg.")

    folders_to_skip = ['_PROCESSING', '_SOURCE', '_ALPHA']
    all_prores_files = find_prores_files_fast(scan_dir, folders_to_ignore=folders_to_skip)

    if not all_prores_files:
        yield "No new ProRes .mov files found to convert."
        return

    files_to_process = []
    for file_info in all_prores_files:
        f = file_info['path']
        if file_info['alpha']:
            alpha_dir = f.parent / "_ALPHA"
            alpha_dir.mkdir(exist_ok=True)
            try:
                shutil.move(str(f), str(alpha_dir / f.name))
                yield f"Moved to _ALPHA: {f.relative_to(scan_dir)}"
            except Exception as e:
                yield f"Error moving {f.name} to _ALPHA: {e}"
        else:
            files_to_process.append(f)

    if not files_to_process:
        yield "No new suitable ProRes files (without alpha) found to convert."
        return

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(convert_to_h264, f): f for f in files_to_process}
        for future in as_completed(futures):
            yield future.result() 
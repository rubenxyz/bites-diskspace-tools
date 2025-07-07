import subprocess
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from .utils import is_prores, has_alpha_channel

def convert_to_h264(video_path: Path, processing_dir: Path, converted_dir: Path):
    """
    Moves a video to a processing folder, converts it to H.264 in the original location,
    and then moves the original to a converted folder.
    """
    original_path = video_path
    processing_path = processing_dir / original_path.name
    output_path = original_path  # The new h264 file will take the original's place

    try:
        # 1. Move original to _PROCESSING
        shutil.move(str(original_path), str(processing_path))

        # 2. Run ffmpeg conversion
        command = [
            "ffmpeg",
            "-i", str(processing_path),
            "-c:v", "libx264", "-crf", "23", "-preset", "medium",
            "-pix_fmt", "yuv420p",
            "-c:a", "copy",  # Copy the audio stream exactly
            "-movflags", "+faststart",
            "-y", str(output_path)
        ]
        subprocess.run(command, check=True, capture_output=True, text=True)

        # 3. Verify output and move original to _CONVERTED
        if output_path.exists() and output_path.stat().st_size > 0:
            converted_path = converted_dir / original_path.name
            shutil.move(str(processing_path), str(converted_path))
            return f"Successfully converted: {original_path.name}"
        else:
            # Move original back if conversion created an empty file
            shutil.move(str(processing_path), str(original_path))
            return f"Conversion failed (zero size output): {original_path.name}"

    except (subprocess.CalledProcessError, Exception) as e:
        # On any error, try to move the original back to its starting place
        if processing_path.exists():
            shutil.move(str(processing_path), str(original_path))
        
        error_message = e.stderr if isinstance(e, subprocess.CalledProcessError) else str(e)
        return f"Conversion failed for {original_path.name}: {error_message}"


def run_conversion(input_dir: Path, max_workers: int = 4):
    """Scans a directory and converts all valid ProRes .mov files to H.264."""
    if not shutil.which("ffmpeg"):
        raise FileNotFoundError("ffmpeg not found. Please install ffmpeg.")

    processing_dir = input_dir / "_PROCESSING"
    converted_dir = input_dir / "_CONVERTED"
    processing_dir.mkdir(exist_ok=True)
    converted_dir.mkdir(exist_ok=True)
    
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
        if not prores_files:
            yield "No suitable ProRes .mov files found to convert."
        return

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(convert_to_h264, f, processing_dir, converted_dir): f for f in files_to_process}
        for future in as_completed(futures):
            yield future.result() 
import subprocess
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from .utils import find_prores_files_fast, validate_video_file

def convert_to_h264(video_path: Path):
    """
    Moves a video to a processing folder within its own directory, converts it,
    and then moves the original to a converted folder.
    """
    original_path = video_path
    parent_dir = original_path.parent
    
    processing_dir = parent_dir / "_PROCESSING"
    source_dir = parent_dir / "_SOURCE"
    failed_dir = parent_dir / "_FAILED"
    
    processing_dir.mkdir(exist_ok=True)
    source_dir.mkdir(exist_ok=True)
    failed_dir.mkdir(exist_ok=True)

    processing_path = processing_dir / original_path.name
    output_path = original_path

    try:
        shutil.move(str(original_path), str(processing_path))

        # Validate input file before conversion
        if not validate_video_file(str(processing_path)):
            failed_path = failed_dir / original_path.name
            shutil.move(str(processing_path), str(failed_path))
            return f"[VALIDATION ERROR] Input file validation failed: {original_path.name} (moved to _FAILED)"

        command = [
            "ffmpeg", "-i", str(processing_path),
            "-c:v", "libx264", "-crf", "23", "-preset", "medium",
            "-pix_fmt", "yuv420p", "-c:a", "copy",
            "-movflags", "+faststart", "-y", str(output_path)
        ]
        try:
            subprocess.run(command, check=True, capture_output=True, text=True, timeout=300)
        except subprocess.TimeoutExpired:
            failed_path = failed_dir / original_path.name
            shutil.move(str(processing_path), str(failed_path))
            return f"[TIMEOUT ERROR] Conversion timed out for {original_path.name} (moved to _FAILED)"
        except subprocess.CalledProcessError as e:
            failed_path = failed_dir / original_path.name
            shutil.move(str(processing_path), str(failed_path))
            return f"[FFMPEG ERROR] Conversion failed for {original_path.name}: {e.stderr.strip()} (moved to _FAILED)"
        except Exception as e:
            failed_path = failed_dir / original_path.name
            shutil.move(str(processing_path), str(failed_path))
            return f"[UNEXPECTED ERROR] Conversion failed for {original_path.name}: {str(e)} (moved to _FAILED)"

        # Validate output file after conversion
        if output_path.exists() and output_path.stat().st_size > 0 and validate_video_file(str(output_path)):
            source_path = source_dir / original_path.name
            shutil.move(str(processing_path), str(source_path))
            return f"Successfully converted: {original_path.relative_to(original_path.parents[2])}"
        else:
            failed_path = failed_dir / original_path.name
            shutil.move(str(processing_path), str(failed_path))
            if not output_path.exists() or output_path.stat().st_size == 0:
                return f"[FFMPEG ERROR] Conversion failed (zero size output): {original_path.name} (moved to _FAILED)"
            else:
                return f"[VALIDATION ERROR] Output file validation failed: {original_path.name} (moved to _FAILED)"
    except (subprocess.CalledProcessError, Exception) as e:
        if processing_path.exists():
            failed_path = failed_dir / original_path.name
            shutil.move(str(processing_path), str(failed_path))
        error_message = e.stderr if isinstance(e, subprocess.CalledProcessError) else str(e)
        return f"Conversion failed for {original_path.name}: {error_message} (moved to _FAILED)"

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
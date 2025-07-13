import subprocess
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from .utils import find_prores_files_fast, validate_video_file

def convert_to_h264(video_path: Path, max_retries: int = 2):
    """
    Moves a video to a processing folder within its own directory, converts it,
    and then moves the original to a converted folder. Retries on transient errors.
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

    attempt = 0
    while attempt <= max_retries:
        try:
            shutil.move(str(original_path), str(processing_path))

            # Validate input file before conversion
            if not validate_video_file(str(processing_path)):
                failed_path = failed_dir / original_path.name
                shutil.move(str(processing_path), str(failed_path))
                return (
                    f"[VALIDATION ERROR] Input file validation failed: {processing_path} (moved to _FAILED)\n"
                    f"Suggestion: Check if the input file is a valid video."
                )

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
                return (
                    f"[TIMEOUT ERROR] Conversion timed out for {processing_path} (moved to _FAILED)\n"
                    f"Suggestion: Try increasing the timeout or check for system performance issues."
                )
            except subprocess.CalledProcessError as e:
                # Retry on transient errors (e.g., IO error, file lock)
                if attempt < max_retries and 'Resource temporarily unavailable' in (e.stderr or ''):
                    attempt += 1
                    continue
                failed_path = failed_dir / original_path.name
                shutil.move(str(processing_path), str(failed_path))
                return (
                    f"[FFMPEG ERROR] Conversion failed for {processing_path}: {e.stderr.strip()} (moved to _FAILED)\n"
                    f"Suggestion: Check ffmpeg logs and input file integrity."
                )
            except Exception as e:
                # Retry on transient IO errors
                if attempt < max_retries and 'temporarily unavailable' in str(e):
                    attempt += 1
                    continue
                failed_path = failed_dir / original_path.name
                shutil.move(str(processing_path), str(failed_path))
                return (
                    f"[UNEXPECTED ERROR] Conversion failed for {processing_path}: {str(e)} (moved to _FAILED)\n"
                    f"Suggestion: Investigate the error and check system resources."
                )

            # Validate output file after conversion
            if output_path.exists() and output_path.stat().st_size > 0 and validate_video_file(str(output_path)):
                source_path = source_dir / original_path.name
                shutil.move(str(processing_path), str(source_path))
                if attempt > 0:
                    return f"Successfully converted after {attempt+1} attempts: {original_path.relative_to(original_path.parents[2])}"
                return f"Successfully converted: {original_path.relative_to(original_path.parents[2])}"
            else:
                failed_path = failed_dir / original_path.name
                shutil.move(str(processing_path), str(failed_path))
                if not output_path.exists() or output_path.stat().st_size == 0:
                    msg = (
                        f"[FFMPEG ERROR] Conversion failed (zero size output): {output_path} (moved to _FAILED)\n"
                        f"Suggestion: Check ffmpeg command and input file."
                    )
                else:
                    msg = (
                        f"[VALIDATION ERROR] Output file validation failed: {output_path} (moved to _FAILED)\n"
                        f"Suggestion: Check if the output file is playable."
                    )
                if attempt < max_retries:
                    attempt += 1
                    continue
                return msg
        except Exception as e:
            # Retry on transient IO errors
            if attempt < max_retries and 'temporarily unavailable' in str(e):
                attempt += 1
                continue
            failed_path = failed_dir / original_path.name
            if processing_path.exists():
                shutil.move(str(processing_path), str(failed_path))
            return (
                f"[UNEXPECTED ERROR] Conversion failed for {processing_path}: {str(e)} (moved to _FAILED)\n"
                f"Suggestion: Investigate the error and check system resources."
            )
        break
    if attempt > max_retries:
        return f"[RETRY ERROR] Conversion failed after {max_retries+1} attempts: {original_path.name} (moved to _FAILED)"

def run_conversion(scan_dir: Path, max_workers: int = 4):
    """Scans a directory tree and converts all valid ProRes .mov files, with progress tracking."""
    import time
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

    total = len(files_to_process)
    processed = 0
    succeeded = 0
    failed = 0
    error_summary = []
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(convert_to_h264, f): f for f in files_to_process}
        for future in as_completed(futures):
            result = future.result()
            processed += 1
            if result.startswith("Successfully converted"):
                succeeded += 1
            elif result.startswith("Moved to _ALPHA"):
                pass
            else:
                failed += 1
                if result.startswith("["):
                    error_summary.append(result)
            elapsed = time.time() - start_time
            avg_time = elapsed / processed if processed else 0
            remaining = total - processed
            est_remaining = avg_time * remaining
            yield (f"Progress: {processed}/{total} | Succeeded: {succeeded} | Failed: {failed} | Remaining: {remaining} | "
                   f"Elapsed: {elapsed:.1f}s | Est. Remaining: {est_remaining:.1f}s")
            yield result
    if error_summary:
        yield "\n--- Conversion Error Summary ---"
        for err in error_summary:
            yield err 
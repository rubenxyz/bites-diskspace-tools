import subprocess
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

def is_prores(video_path: str) -> bool:
    """Check if a video file is encoded with ProRes."""
    if not shutil.which("ffprobe"):
        raise FileNotFoundError("ffprobe not found. Please install ffmpeg.")
    
    command = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=codec_name",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(video_path)
    ]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return "prores" in result.stdout.lower()
    except subprocess.CalledProcessError:
        # This could happen for various reasons, e.g., not a valid video file
        return False
    except FileNotFoundError:
        return False

def has_alpha_channel(video_path: str) -> bool:
    """Check if a video file's pixel format has an alpha channel."""
    if not shutil.which("ffprobe"):
        raise FileNotFoundError("ffprobe not found. Please install ffmpeg.")
    
    command = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=pix_fmt",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(video_path)
    ]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        pix_fmt = result.stdout.strip()
        # Pixel formats with alpha usually contain 'a' (e.g., yuva, rgba)
        return 'a' in pix_fmt
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def find_prores_files_fast(scan_dir: Path):
    """
    Scans a directory tree in parallel to quickly find all ProRes files,
    skipping special folders.
    """
    all_mov_files = [
        p for p in scan_dir.rglob("*.mov") 
        if p.is_file() and not any(part in p.parts for part in ['_PROCESSING', '_CONVERTED', '_ALPHA'])
    ]
    
    prores_files = []

    def _check_file(path):
        if is_prores(path):
            has_alpha = has_alpha_channel(path)
            return {"path": path, "alpha": has_alpha}
        return None

    with ThreadPoolExecutor() as executor:
        results = executor.map(_check_file, all_mov_files)
        for result in results:
            if result:
                prores_files.append(result)

    return prores_files 
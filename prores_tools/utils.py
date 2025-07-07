import subprocess
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

def format_size(size_bytes):
    """Converts bytes to a human-readable string (GB, MB, KB)."""
    if size_bytes >= 1024**3:
        return f"{size_bytes / 1024**3:.2f} GB"
    elif size_bytes >= 1024**2:
        return f"{size_bytes / 1024**2:.2f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes} Bytes"

def find_files_by_extension(scan_dir: Path, extension: str, folders_to_ignore: list[str] | None = None):
    """
    Scans a directory tree to find all files with a given extension,
    optionally skipping special folders.
    """
    if folders_to_ignore is None:
        folders_to_ignore = []

    found_files = []
    all_files = scan_dir.rglob(f'*{extension}')

    for p in all_files:
        if p.is_file() and not any(part in p.parts for part in folders_to_ignore):
            size = p.stat().st_size
            found_files.append({"path": p, "size": size, "type": extension})
    
    return found_files

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

def find_prores_files_fast(scan_dir: Path, folders_to_ignore: list[str] | None = None):
    """
    Scans a directory tree in parallel to quickly find all ProRes files,
    optionally skipping special folders.
    """
    if folders_to_ignore is None:
        folders_to_ignore = []

    all_mov_files = [
        p for p in scan_dir.rglob("*.mov") 
        if p.is_file() and not any(part in p.parts for part in folders_to_ignore)
    ]
    
    prores_files = []

    def _check_file(path):
        if is_prores(path):
            has_alpha = has_alpha_channel(path)
            size = path.stat().st_size
            return {"path": path, "alpha": has_alpha, "size": size, "type": "prores"}
        return None

    with ThreadPoolExecutor() as executor:
        results = executor.map(_check_file, all_mov_files)
        for result in results:
            if result:
                prores_files.append(result)

    return prores_files 
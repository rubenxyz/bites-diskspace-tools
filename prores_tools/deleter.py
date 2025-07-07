import os
from pathlib import Path
from send2trash import send2trash
from .utils import find_prores_files_fast

def remove_prv_files(scan_dir: Path):
    """
    Finds all ProRes files that meet the deletion criteria.
    """
    all_prores_files = find_prores_files_fast(scan_dir)
    files_to_delete = []

    for file_info in all_prores_files:
        path = file_info['path']
        if not file_info['alpha'] and path.parent.name.endswith('.PRV'):
            files_to_delete.append(path)
    
    return files_to_delete

def delete_files(files: list[Path]):
    """
    Moves a list of files to the system's Trash.
    """
    for f in files:
        try:
            send2trash(f)
            yield f"Moved to Trash: {f}"
        except OSError as e:
            yield f"Error moving {f} to Trash: {e}" 
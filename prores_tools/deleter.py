import os
from pathlib import Path
from send2trash import send2trash
from .utils import find_prores_files_fast

def find_files_to_cleanup(scan_dir: Path):
    """
    Finds all ProRes files that meet the cleanup criteria.
    """
    # Scan everywhere except the _PROCESSING folder to avoid touching active files
    folders_to_skip = ['_PROCESSING']
    all_prores_files = find_prores_files_fast(scan_dir, folders_to_ignore=folders_to_skip)
    
    files_to_trash = []

    for file_info in all_prores_files:
        path = file_info['path']
        
        # Criterion 1: Any ProRes file in a _CONVERTED folder
        if '_CONVERTED' in path.parts:
            files_to_trash.append(path)
            continue

        # Criterion 2: ProRes file without alpha in a .PRV folder
        if not file_info['alpha'] and path.parent.name.endswith('.PRV'):
            files_to_trash.append(path)
    
    # Return a unique list of files
    return list(set(files_to_trash))

def move_files_to_trash(files: list[Path]):
    """
    Moves a list of files to the system's Trash.
    """
    for f in files:
        try:
            send2trash(f)
            yield f"Moved to Trash: {f}"
        except OSError as e:
            yield f"Error moving {f} to Trash: {e}" 
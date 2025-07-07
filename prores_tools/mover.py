from pathlib import Path
import shutil
from .utils import is_prores, has_alpha_channel

def move_prores_files(source_dir: Path, archive_dir: Path):
    """Scans a source directory and moves all ProRes .mov files to an archive directory."""
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    moved_files_count = 0
    skipped_files_count = 0
    alpha_channel_skipped_count = 0

    files_to_check = list(source_dir.glob("*.mov"))

    if not files_to_check:
        yield "No .mov files found to process."
        return

    for f in files_to_check:
        if f.is_file() and is_prores(f):
            if has_alpha_channel(f):
                yield f"Skipped (has alpha channel): {f.name}"
                alpha_channel_skipped_count += 1
                continue

            destination = archive_dir / f.name
            try:
                shutil.move(str(f), str(destination))
                yield f"Moved: {f.name}"
                moved_files_count += 1
            except Exception as e:
                yield f"Error moving {f.name}: {e}"
        elif f.is_file():
            skipped_files_count += 1
    
    yield f"\nProcess complete. Moved {moved_files_count} file(s)."
    if alpha_channel_skipped_count > 0:
        yield f"Skipped {alpha_channel_skipped_count} file(s) with alpha channels."
    if skipped_files_count > 0:
        yield f"Skipped {skipped_files_count} non-ProRes file(s)." 
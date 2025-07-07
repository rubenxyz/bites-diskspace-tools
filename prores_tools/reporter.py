from pathlib import Path
from datetime import datetime
from .utils import is_prores, has_alpha_channel

def generate_report(target_dir: Path):
    """
    Scans a directory tree, finds all ProRes files, and generates a markdown report.
    """
    report_path = target_dir / "prores_report.md"
    prores_files = []

    # Use rglob to recursively find all .mov files
    for f in target_dir.rglob("*.mov"):
        if f.is_file() and is_prores(f):
            has_alpha = has_alpha_channel(f)
            prores_files.append({"path": f, "alpha": has_alpha})

    # Build the tree structure string
    tree_str = build_tree_string(target_dir, prores_files)
    
    # Generate the report content
    report_content = f"""# ProRes Video Report

**Source Directory:** `{target_dir.resolve()}`
**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

```
{tree_str}
```

---

**Summary:**
*   **Total ProRes Files Found:** {len(prores_files)}
*   **Files with Alpha Channel:** {sum(1 for f in prores_files if f['alpha'])}

"""

    with open(report_path, "w") as f:
        f.write(report_content)
    
    return report_path

def build_tree_string(root: Path, files: list) -> str:
    """Builds a string representation of the file tree with aligned tags."""
    tree = {}
    for file_info in files:
        path = file_info['path']
        parts = path.relative_to(root).parts
        current_level = tree
        for part in parts[:-1]:
            current_level = current_level.setdefault(part, {})
        current_level[parts[-1]] = file_info # Store the whole dict

    if not tree:
        return f"{root.name}/\n(No ProRes files found)"

    raw_lines = []

    def _generate_raw_lines(d, prefix=""):
        items = sorted(d.items())
        for i, (name, content) in enumerate(items):
            connector = "├── " if i < len(items) - 1 else "└── "
            if isinstance(content, dict) and 'path' not in content:
                raw_lines.append((f"{prefix}{connector}{name}/", None))
                _generate_raw_lines(content, prefix + ("│   " if i < len(items) - 1 else "    "))
            else:
                # It's a file
                tag = "[ProRes - Alpha Channel]" if content['alpha'] else "[ProRes]"
                raw_lines.append((f"{prefix}{connector}{name}", tag))

    _generate_raw_lines(tree)

    max_len = 0
    if any(tag for _, tag in raw_lines):
        # Only consider lines with files for max length calculation
        max_len = max(len(text) for text, tag in raw_lines if tag is not None)

    padding = 4
    
    output_lines = [f"{root.name}/"]
    for text, tag in raw_lines:
        if tag is not None:
            padded_text = text.ljust(max_len + padding)
            output_lines.append(f"{padded_text}{tag}")
        else:
            output_lines.append(text)
            
    return "\n".join(output_lines) 
from pathlib import Path
from datetime import datetime
from weasyprint import HTML, CSS
import pkg_resources
from .utils import is_prores, has_alpha_channel

def generate_report(target_dir: Path):
    """
    Scans a directory tree, finds all ProRes files, and generates a PDF report.
    """
    report_path = target_dir / "prores_report.pdf"
    prores_files = []

    for f in target_dir.rglob("*.mov"):
        if f.is_file() and is_prores(f):
            has_alpha = has_alpha_channel(f)
            prores_files.append({"path": f, "alpha": has_alpha})

    tree_html_content = build_tree_html(target_dir, prores_files)
    
    css_path = pkg_resources.resource_filename('prores_tools', 'report_style.css')
    stylesheet = CSS(css_path)

    html_content = f"""
    <html>
    <head>
    </head>
    <body>
        <h1>ProRes Video Report</h1>
        <p><strong>Source Directory:</strong> {target_dir.resolve()}</p>
        <p><strong>Report Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <div class="tree-container">
            <pre>{tree_html_content}</pre>
        </div>
        <div class="summary">
            <p><strong>Summary:</strong></p>
            <ul>
                <li>Total ProRes Files Found: {len(prores_files)}</li>
                <li>Files with Alpha Channel: {sum(1 for f in prores_files if f['alpha'])}</li>
            </ul>
        </div>
    </body>
    </html>
    """

    html_doc = HTML(string=html_content)
    html_doc.write_pdf(report_path, stylesheets=[stylesheet])
    
    return report_path

def build_tree_html(root: Path, files: list) -> str:
    """Builds a preformatted HTML string of the file tree with aligned tags."""
    tree = {}
    for file_info in files:
        path = file_info['path']
        parts = path.relative_to(root).parts
        current_level = tree
        for part in parts[:-1]:
            current_level = current_level.setdefault(part, {})
        current_level[parts[-1]] = file_info

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
                tag = "[ProRes - Alpha Channel]" if content['alpha'] else "[ProRes]"
                raw_lines.append((f"{prefix}{connector}{name}", tag))

    _generate_raw_lines(tree)

    max_len = 0
    if any(tag for _, tag in raw_lines if tag):
        max_len = max(len(text) for text, tag in raw_lines if tag)

    padding = 4
    total_width = max_len + padding
    
    output_lines = [f"{root.name}/"]
    for text, tag in raw_lines:
        if tag:
            line = text.ljust(total_width) + tag
            output_lines.append(line)
        else:
            output_lines.append(text)
            
    return "\n".join(output_lines)

def build_tree_string(root: Path, files: list) -> str:
    """This function is no longer used for PDF generation but kept for potential future use."""
    # ... previous implementation ...
    pass 
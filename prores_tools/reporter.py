from pathlib import Path
from datetime import datetime
from weasyprint import HTML, CSS
import pkg_resources
from .utils import find_prores_files_fast, format_size

def generate_report(target_dir: Path):
    """
    Scans a directory tree, finds all ProRes files, and generates a PDF report.
    """
    report_path = target_dir / "prores_report.pdf"
    
    folders_to_skip = ['_PROCESSING']
    prores_files = find_prores_files_fast(target_dir, folders_to_ignore=folders_to_skip)

    # Calculate size totals
    total_size = sum(f['size'] for f in prores_files)
    alpha_size = sum(f['size'] for f in prores_files if f['alpha'])
    no_alpha_size = total_size - alpha_size

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
                <li>Total ProRes Files: {len(prores_files)} ({format_size(total_size)})</li>
                <li>Files with Alpha Channel: {sum(1 for f in prores_files if f['alpha'])} ({format_size(alpha_size)})</li>
                <li>Files without Alpha Channel: {sum(1 for f in prores_files if not f['alpha'])} ({format_size(no_alpha_size)})</li>
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
                raw_lines.append((f"{prefix}{connector}{name}/", None, None))
                _generate_raw_lines(content, prefix + ("│   " if i < len(items) - 1 else "    "))
            else:
                tag = "[ProRes - Alpha Channel]" if content['alpha'] else "[ProRes]"
                size_str = format_size(content['size'])
                raw_lines.append((f"{prefix}{connector}{name}", tag, size_str))

    _generate_raw_lines(tree)

    max_len = 0
    if any(tag for _, tag, _ in raw_lines if tag):
        max_len = max(len(text) for text, _, _ in raw_lines if text)
    
    tag_width = 28 # Width for the codec tag column
    
    output_lines = [f"{root.name}/"]
    for text, tag, size in raw_lines:
        if tag:
            line_part1 = text.ljust(max_len + 4)
            line_part2 = tag.ljust(tag_width)
            line = f"{line_part1}{line_part2}{size}"
            output_lines.append(line)
        else:
            output_lines.append(text)
            
    return "\n".join(output_lines)

def build_tree_string(root: Path, files: list) -> str:
    """This function is no longer used for PDF generation but kept for potential future use."""
    # ... previous implementation ...
    pass 
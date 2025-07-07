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

    tree_html = build_tree_html(target_dir, prores_files)
    
    # Load the CSS stylesheet from the package
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
        <div class="tree-container">{tree_html}</div>
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
    """Builds an HTML table string representation of the file tree."""
    tree = {}
    for file_info in files:
        path = file_info['path']
        parts = path.relative_to(root).parts
        current_level = tree
        for part in parts[:-1]:
            current_level = current_level.setdefault(part, {})
        current_level[parts[-1]] = file_info

    if not tree:
        return f"<p>{root.name}/<br>(No ProRes files found)</p>"
    
    lines = [f'<tr><td colspan="2" style="font-weight: bold;">{root.name}/</td></tr>']
    
    def _generate_lines(d, prefix=""):
        items = sorted(d.items())
        for i, (name, content) in enumerate(items):
            # Use non-breaking spaces for indentation
            html_prefix = prefix.replace(" ", "&nbsp;")
            connector = "├── " if i < len(items) - 1 else "└── "
            
            if isinstance(content, dict) and 'path' not in content:
                lines.append(f'<tr><td colspan="2">{html_prefix}{connector}{name}/</td></tr>')
                _generate_lines(content, prefix + ("│   " if i < len(items) - 1 else "    "))
            else:
                tag = "[ProRes - Alpha Channel]" if content['alpha'] else "[ProRes]"
                lines.append(f'<tr><td>{html_prefix}{connector}{name}</td><td>{tag}</td></tr>')

    _generate_lines(tree)
    
    return f"<table>\n" + "\n".join(lines) + "\n</table>"

def build_tree_string(root: Path, files: list) -> str:
    """This function is no longer used for PDF generation but kept for potential future use."""
    # ... previous implementation ...
    pass 
from pathlib import Path
from datetime import datetime
from weasyprint import HTML, CSS
import pkg_resources
from .utils import find_prores_files_fast, find_files_by_extension, format_size

def generate_report(target_dir: Path):
    """
    Scans a directory tree, finds all ProRes and PSD files, and generates a PDF report.
    """
    report_path = target_dir / "prores_report.pdf"
    
    folders_to_skip = ['_PROCESSING']
    prores_files = find_prores_files_fast(target_dir, folders_to_ignore=folders_to_skip)
    psd_files = find_files_by_extension(target_dir, ".psd", folders_to_ignore=folders_to_skip)

    all_files = sorted(prores_files + psd_files, key=lambda x: x['path'])

    # Calculate size totals
    total_prores_size = sum(f['size'] for f in prores_files)
    alpha_size = sum(f['size'] for f in prores_files if f['alpha'])
    no_alpha_size = total_prores_size - alpha_size
    total_psd_size = sum(f['size'] for f in psd_files)
    grand_total_size = total_prores_size + total_psd_size

    tree_html_content = build_tree_html(target_dir, all_files)
    
    css_path = pkg_resources.resource_filename('prores_tools', 'report_style.css')
    stylesheet = CSS(css_path)

    html_content = f"""
    <html>
    <head>
    </head>
    <body>
        <h1>Project Asset Report</h1>
        <p><strong>Source Directory:</strong> {target_dir.resolve()}</p>
        <p><strong>Report Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <div class="summary">
            <p><strong>Summary:</strong></p>
            <ul>
                <li>Total ProRes Files: {len(prores_files)} ({format_size(total_prores_size)})</li>
                <li>  - With Alpha Channel: {sum(1 for f in prores_files if f['alpha'])} ({format_size(alpha_size)})</li>
                <li>  - Without Alpha Channel: {sum(1 for f in prores_files if not f['alpha'])} ({format_size(no_alpha_size)})</li>
                <li>Total PSD Files: {len(psd_files)} ({format_size(total_psd_size)})</li>
                <li style="border-top: 1px solid #ccc; padding-top: 5px; margin-top: 5px;"><strong>Grand Total: {len(all_files)} files ({format_size(grand_total_size)})</strong></li>
            </ul>
        </div>
        <div class="tree-container">
            <pre>{tree_html_content}</pre>
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
        return f"{root.name}/\n(No relevant files found)"
    
    raw_lines = []

    def _generate_raw_lines(d, prefix=""):
        items = sorted(d.items())
        for i, (name, content) in enumerate(items):
            connector = "├── " if i < len(items) - 1 else "└── "
            if isinstance(content, dict) and 'path' not in content:
                raw_lines.append((f"{prefix}{connector}{name}/", None, None))
                _generate_raw_lines(content, prefix + ("│   " if i < len(items) - 1 else "    "))
            else:
                if content['type'] == 'prores':
                    tag = "[ProRes - Alpha]" if content['alpha'] else "[ProRes]"
                else:
                    tag = f"[{content['type'].upper().replace('.', '')}]"
                
                size_str = format_size(content['size'])
                raw_lines.append((f"{prefix}{connector}{name}", tag, size_str))

    _generate_raw_lines(tree)

    max_len = 0
    if any(tag for _, tag, _ in raw_lines if tag):
        max_len = max(len(text) for text, _, _ in raw_lines if text)
    
    tag_width = 20
    
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
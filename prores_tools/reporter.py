from pathlib import Path
from datetime import datetime
from weasyprint import HTML, CSS
import pkg_resources
from .utils import find_prores_files_fast, find_files_by_extension, format_size

def generate_report(target_dir: Path):
    """
    Scans a directory tree, finds all ProRes and PSD files, and generates a PDF report.
    """
    report_path = target_dir / f"{target_dir.name}_report.pdf"
    
    folders_to_skip = ['_PROCESSING']
    prores_files = find_prores_files_fast(target_dir, folders_to_ignore=folders_to_skip)
    all_psd_files = find_files_by_extension(target_dir, ".psd", folders_to_ignore=folders_to_skip)
    
    # Filter for PSD files over 100MB
    large_psd_files = [psd for psd in all_psd_files if psd['size'] > 100 * 1024 * 1024]

    all_files = sorted(prores_files + large_psd_files, key=lambda x: x['path'])

    # Calculate size totals
    total_prores_size = sum(f['size'] for f in prores_files)
    alpha_size = sum(f['size'] for f in prores_files if f['alpha'])
    no_alpha_size = total_prores_size - alpha_size
    total_psd_size = sum(f['size'] for f in large_psd_files)
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
                <li>Total PSD Files (&gt;100MB): {len(large_psd_files)} ({format_size(total_psd_size)})</li>
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

def generate_conversion_report(target_dir: Path):
    """
    Scans a directory tree for _SOURCE, _FAILED, _ALPHA, and _PROCESSING folders and generates a PDF conversion report.
    """
    report_path = target_dir / f"{target_dir.name}_conversion_report.pdf"

    def gather_files(folder_name):
        return list(target_dir.rglob(f'{folder_name}/*'))

    source_files = gather_files('_SOURCE')
    failed_files = gather_files('_FAILED')
    alpha_files = gather_files('_ALPHA')
    processing_files = gather_files('_PROCESSING')

    def file_summary(files):
        return [(str(f.relative_to(target_dir)), f.stat().st_size) for f in files if f.is_file()]

    html_content = f"""
    <html>
    <head></head>
    <body>
        <h1>Conversion Report</h1>
        <p><strong>Source Directory:</strong> {target_dir.resolve()}</p>
        <p><strong>Report Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <div class="summary">
            <ul>
                <li><strong>Successfully Converted (_SOURCE):</strong> {len(source_files)}</li>
                <li><strong>Failed Conversions (_FAILED):</strong> {len(failed_files)}</li>
                <li><strong>Alpha Channel Files (_ALPHA):</strong> {len(alpha_files)}</li>
                <li><strong>Still in Processing (_PROCESSING):</strong> {len(processing_files)}</li>
            </ul>
        </div>
        <h2>Details</h2>
        <h3>_SOURCE</h3>
        <pre>{chr(10).join([f'{f[0]} ({format_size(f[1])})' for f in file_summary(source_files)]) or 'None'}</pre>
        <h3>_FAILED</h3>
        <pre>{chr(10).join([f'{f[0]} ({format_size(f[1])})' for f in file_summary(failed_files)]) or 'None'}</pre>
        <h3>_ALPHA</h3>
        <pre>{chr(10).join([f'{f[0]} ({format_size(f[1])})' for f in file_summary(alpha_files)]) or 'None'}</pre>
        <h3>_PROCESSING</h3>
        <pre>{chr(10).join([f'{f[0]} ({format_size(f[1])})' for f in file_summary(processing_files)]) or 'None'}</pre>
    </body>
    </html>
    """

    css_path = pkg_resources.resource_filename('prores_tools', 'report_style.css')
    stylesheet = CSS(css_path)
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
                    tag = "[PSD >100MB]"
                
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
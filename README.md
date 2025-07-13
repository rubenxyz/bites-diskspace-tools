# ProRes Tools

A collection of utilities for converting and managing ProRes video files.

## Installation

This project uses Python and requires `ffmpeg` to be installed and available in your system's PATH.

1.  **Install Dependencies:**
    If you don't have `ffmpeg` installed, you can use Homebrew on macOS:
    ```sh
    brew install ffmpeg
    ```

2.  **Set up a Virtual Environment:**
    It's highly recommended to use a virtual environment to manage dependencies.

    ```sh
    # Create the virtual environment
    python3 -m venv venv

    # Activate it
    source venv/bin/activate
    ```

3.  **Install the Tool:**
    With the virtual environment active, install the project and its dependencies:
    ```sh
    pip install .
    ```

## Usage

Once installed, you can use the `prores-tool` command from your terminal (ensure the virtual environment is active).

### Convert Videos

This command recursively scans a directory for ProRes `.mov` files and converts them to H.264.

```sh
prores-tool convert /path/to/your/videos
```

**Workflow:**
1.  The tool scans all folders within the given path for `.mov` files.
2.  For each folder containing a ProRes file, it creates up to three subfolders: `_PROCESSING`, `_SOURCE`, and `_ALPHA`.
3.  **ProRes files with an alpha channel** are moved directly into the `_ALPHA` subfolder. They are not converted.
4.  **ProRes files without an alpha channel** are moved to `_PROCESSING`, converted to H.264 (in-place), and then the original ProRes file is moved to `_SOURCE` for archival.

**Options:**
*   `--workers <number>` or `-w <number>`: Set the number of parallel conversion jobs (default is 4).

### Cleanup Project Files

This command recursively finds and moves specific types of files to the system's Trash to help clean up a project directory. It targets two specific sets of files:
1.  All ProRes files located inside any `_SOURCE` folder.
2.  ProRes files *without an alpha channel* that are inside any folder ending with the `.PRV` extension.

```sh
prores-tool cleanup /path/to/your/project_folder
```

> [!WARNING]
> This command is non-interactive and will immediately move all matching files to the Trash without a confirmation prompt. Use with caution.

### Generate a Report

This command recursively scans a directory and creates a detailed PDF report named `prores_report.pdf`. The report provides insights into both ProRes and Photoshop (`.psd`) assets.

```sh
prores-tool report /path/to/your/project_folder
```

**Report Contents:**
*   **File Tree:** A visual tree of all found ProRes and `.psd` files.
*   **Summary Breakdown:**
    *   Total count and size of all ProRes files.
    *   Separate counts and sizes for ProRes files with and without alpha channels.
    *   Total count and size of all `.psd` files.
    *   A grand total combining all analyzed assets.

### Verify a File

Checks if a single video file is encoded with the ProRes codec and whether it contains an alpha channel.

```sh
prores-tool verify /path/to/your/video.mov
```

---

## For Developers: Creating a New Feature

To add a new feature to `prores-tool`, follow these steps:

1.  **Create a New Command:** Add a function to `prores_tools/cli.py` and decorate it with `@app.command()`.
2.  **Add Core Logic:** Create a new Python file in the `prores_tools/` directory to house the feature's primary logic.
3.  **Import and Use:** Import your new module into `prores_tools/cli.py` and call it from your command function.
4.  **Add Tests (Recommended):** Create a corresponding test file in a `tests/` directory to ensure your feature works as expected.

By following this structure, you can extend the tool's functionality while maintaining a clean and organized codebase. 
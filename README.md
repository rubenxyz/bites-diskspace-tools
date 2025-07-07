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

This command recursively scans a directory for ProRes `.mov` files and converts them to H.264. It preserves the original audio and operates directly within the sub-directory where each video is found.

```sh
prores-tool convert /path/to/your/videos
```

**Workflow:**
1.  The tool scans all folders within the given path.
2.  In any folder containing a valid ProRes file, it creates the necessary subfolders (`_PROCESSING`, `_CONVERTED`, `_ALPHA`).
3.  A valid ProRes file (without alpha) is moved to `_PROCESSING`, converted, and then the original is archived to `_CONVERTED`.
4.  ProRes files with alpha channels are moved directly into the `_ALPHA` subfolder in their respective directory.

**Options:**
*   `--workers <number>` or `-w <number>`: Set the number of parallel conversion jobs (default is 4).

### Move Preview Files to Trash

This command recursively finds and moves ProRes files to the system's Trash if they meet a specific criteria:
1. The file must NOT have an alpha channel.
2. The folder containing the file must end with `.PRV`.

```sh
prores-tool remove-prv /path/to/your/project_folder
```

> [!WARNING]
> This command is non-interactive and will immediately move all matching files to the Trash without a confirmation prompt. Use with caution.

### Generate a Report

This command recursively scans a directory and creates a PDF file (`prores_report.pdf`) detailing all the ProRes files it finds.

```sh
prores-tool report /path/to/your/project_folder
```

### Verify a File

Checks if a single video file is encoded with the ProRes codec and whether it contains an alpha channel.

```sh
prores-tool verify /path/to/your/video.mov
``` 
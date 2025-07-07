# ProRes Tools

A collection of utilities for converting and managing ProRes video files.

## Installation

This project uses Python and requires `ffmpeg` to be installed and available in your system's PATH.

1.  **Install ffmpeg:**
    If you don't have ffmpeg installed, you can use Homebrew on macOS:
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

This command scans a directory for ProRes `.mov` files and converts them to H.264. It preserves the original audio (including multi-channel audio) and operates directly within the specified directory.

```sh
prores-tool convert /path/to/your/videos
```

**Workflow:**
1.  The tool creates two subfolders: `_PROCESSING` and `_CONVERTED`.
2.  A valid ProRes file (without an alpha channel) is moved into `_PROCESSING`.
3.  A new H.264 file is created in its original place.
4.  Upon successful conversion, the original file is moved from `_PROCESSING` to `_CONVERTED` for archival.
5.  ProRes files with alpha channels are skipped and left in their original location.

**Options:**
*   `--workers <number>` or `-w <number>`: Set the number of parallel conversion jobs (default is 4).

### Generate a Report

This command recursively scans a directory and creates a Markdown file (`prores_report.md`) detailing all the ProRes files it finds.

```sh
prores-tool report /path/to/your/project_folder
```

### Verify a File

Checks if a single video file is encoded with the ProRes codec and whether it contains an alpha channel.

```sh
prores-tool verify /path/to/your/video.mov
``` 
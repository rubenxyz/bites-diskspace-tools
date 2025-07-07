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

Converts all ProRes `.mov` files from an input directory to H.264 `.mov` files in an output directory. It uses parallel processing for speed.

```sh
prores-tool convert /path/to/your/videos /path/to/converted/output
```

**Options:**
*   `--workers <number>` or `-w <number>`: Set the number of parallel conversion jobs (default is 4).

### Archive Original Files

Moves all ProRes `.mov` files from a source directory to an archive directory.

```sh
prores-tool move /path/to/your/videos /path/to/your/archive
```

### Verify a File

Checks if a single video file is encoded with the ProRes codec.

```sh
prores-tool verify /path/to/your/video.mov
``` 
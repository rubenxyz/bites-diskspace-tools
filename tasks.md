# Task Manager - ProRes Tools Improvements

## To-Do List



### 1. Failed Conversion Handling
- **Goal**: If file fails to convert, move to `_FAILED`
- **Implementation**:
  - Create `_FAILED` folder structure
  - Move failed files to `_FAILED` instead of restoring to original location
  - Update conversion logic to handle various failure scenarios:
    - Corrupted output files
    - FFmpeg errors
    - Timeout errors
    - File validation failures

### 2. Conversion Report Script
- **Goal**: Create dedicated conversion report/log for the folder where conversion runs
- **Implementation**:
  - When running a conversion triggers  Scan for `_SOURCE`, `_FAILED`, `_ALPHA` folders
  - Generate detailed report showing:
    - Files successfully converted (moved to `_SOURCE`)
    - Files that failed conversion (moved to `_FAILED`)
    - Files with alpha channels (moved to `_ALPHA`)
    - Files still in `_PROCESSING` (if any)
    - Original vs converted file sizes
    - Error messages for failed conversions
    - Conversion timestamps
  - Output format: PDF report similar to existing report command

### 3. Enhanced Error Handling

#### 3.1 Add File Validation Function Using ffprobe
- **Goal**: Ensure both input and output video files are valid and playable
- **Implementation**:
  - Implement a function that uses ffprobe to check video integrity
  - Integrate validation before and after conversion
  - Log validation results for each file

#### 3.2 Implement Timeout Protection for Long-Running Conversions
- **Goal**: Prevent the conversion process from hanging indefinitely
- **Implementation**:
  - Set a reasonable timeout for ffmpeg subprocess calls
  - Handle timeout exceptions and move affected files to `_FAILED`
  - Log timeout events in the conversion report

#### 3.3 Add Detailed Error Logging and Categorization
- **Goal**: Provide actionable error information for each failed conversion
- **Implementation**:
  - Capture and categorize errors (e.g., ffmpeg error, validation error, timeout)
  - Store error messages and types in the conversion report/log
  - Optionally, write error logs to a separate file for debugging

#### 3.4 Improve Error Messages with Actionable Information
- **Goal**: Make error messages clear and helpful for troubleshooting
- **Implementation**:
  - Standardize error message format
  - Include file paths, error type, and suggested next steps
  - Display summary of errors at the end of the conversion process

#### 3.5 Add Retry Logic for Transient Failures
- **Goal**: Automatically retry conversions that fail due to temporary issues
- **Implementation**:
  - Identify transient errors (e.g., temporary file locks, IO errors)
  - Retry failed conversions a configurable number of times
  - Log each retry attempt and its outcome

#### 3.6 Implement Progress Tracking for Long Conversions
- **Goal**: Provide feedback on conversion progress
- **Implementation**:
  - Track and display the number of files processed, succeeded, failed, and remaining
  - Optionally, show estimated time remaining
  - Update progress in real-time in the CLI output and report

#### 3.7 Add File Integrity Checks Before and After Conversion
- **Goal**: Ensure files are not corrupted during processing
- **Implementation**:
  - Compute and compare checksums (e.g., MD5, SHA256) before and after conversion
  - Log any discrepancies and flag affected files
  - Optionally, skip conversion if input file is already corrupted


## Technical Considerations
- Maintain backward compatibility with existing folder structure
- Ensure thread safety for parallel processing
- Add proper logging for debugging
- Consider adding configuration options for timeouts and retries
- Update documentation to reflect new behavior
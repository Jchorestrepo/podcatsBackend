"""Service for audio manipulation using pydub."""
import os
from pydub import AudioSegment
from fastapi import HTTPException

def combine_audio_files(file_paths: list[str], output_path: str):
    """
    Combines multiple MP3 files into a single file.

    Args:
        file_paths: A list of paths to the MP3 files to combine.
        output_path: The path to save the final combined MP3 file.
    
    Raises:
        HTTPException: If an error occurs during audio processing.
    """
    try:
        combined_audio = AudioSegment.empty()
        for path in file_paths:
            if os.path.exists(path):
                segment = AudioSegment.from_mp3(path)
                combined_audio += segment
            else:
                # This can be a warning or an error depending on desired strictness
                print(f"Warning: Audio file not found at {path}, skipping.")

        # Export the combined audio file
        combined_audio.export(output_path, format="mp3")
    except Exception as e:
        # Catching a broad exception as pydub can raise various errors
        raise HTTPException(status_code=500, detail=f"Failed to combine audio files: {e}")

def cleanup_files(file_paths: list[str]):
    """
    Deletes a list of files.

    Args:
        file_paths: A list of file paths to delete.
    """
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError as e:
            # Log the error but don't interrupt the response to the user
            print(f"Error cleaning up file {path}: {e}")

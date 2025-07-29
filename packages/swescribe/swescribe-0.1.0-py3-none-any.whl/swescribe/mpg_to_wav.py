import logging
import subprocess
from pathlib import Path


def extract_audio(mpg_file_path: Path, wav_file_path: Path):
    logging.debug(f"Starting extraction for: {mpg_file_path.name}")

    if not mpg_file_path.exists():
        raise FileNotFoundError(f"The file {mpg_file_path} does not exist.")
    elif not wav_file_path.parent.exists():
        raise FileNotFoundError(
            f"The ouput directory {wav_file_path.parent} does not exist."
        )

    # Use ffmpeg to extract audio, targeting a sample rate of 16kHz and a single channel (mono)
    command = [
        "ffmpeg",
        "-y",  # Overwrite output files without asking
        "-i",
        str(mpg_file_path),  # Input file
        "-ar",
        "16000",  # Set audio sample rate to 16kHz
        "-ac",
        "1",  # Set audio channels to mono
        str(wav_file_path),
    ]

    subprocess.run(
        command,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    logging.debug(f"Successfully extracted audio to: {wav_file_path}\n")

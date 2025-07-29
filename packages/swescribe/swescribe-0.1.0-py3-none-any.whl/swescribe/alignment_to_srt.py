import logging
from typing import Generator, List

from swescribe.clean_whisper import clean_text


def format_timestamp(seconds):
    """Create srt-compliant timestamp

    Args:
        seconds (float): The time in seconds, with milisecond precision

    Returns:
        str: The formatted timestamp
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def cleaned_segments(
    segments: List[dict[str:any]],
) -> Generator[dict[str:str], None, None]:
    for segment in segments:
        text = clean_text(segment["text"].strip())

        if not text:
            logging.debug(f"Skipping empty segment {segment=}")
            continue

        yield {
            "start": format_timestamp(segment["start"]),
            "end": format_timestamp(segment["end"]),
            "text": text,
        }


def alignment_to_srt(aligned_result: List[dict]):
    """Convert aligned result to SRT format.

    Args:
        aligned_result List of (dict): The aligned result from the Whisperx library.

    Returns:
        str: The formatted SRT content.
    """
    srt_content = ""
    for idx, segment in enumerate(
        cleaned_segments(aligned_result["segments"]), start=1
    ):
        srt_content += f"{idx}\n{segment['start']} --> {segment['end']}\n{segment['text']}\n\n"

    return srt_content

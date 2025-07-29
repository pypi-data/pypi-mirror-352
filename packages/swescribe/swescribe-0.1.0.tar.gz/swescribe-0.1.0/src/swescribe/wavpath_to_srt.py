from pathlib import Path

from swescribe.alignment_to_srt import alignment_to_srt
from swescribe.transcribe import align_results, model_transcribe


def wavpath_to_srt(audio_file_path: Path):
    """Reads WAV file and generates a subtitle file in SRT format.

    Args:
        audio_file_path (Path): The path to the WAV file.

    Returns:
        str: The formatted SRT content.
    """
    transcription_result = model_transcribe(audio_file_path)

    aligned_result = align_results(audio_file_path, transcription_result)

    srt_content = alignment_to_srt(aligned_result)
    return srt_content

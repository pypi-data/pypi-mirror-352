import logging
import re
from pathlib import Path

import pandas as pd
from jiwer import wer

from swescribe import num_test_cases
from swescribe.paths import (
    ground_truth_dir,
    txt_output_dir,
    wer_results_file,
    wer_summary_file,
)


def read_transcript(transcript_path: Path) -> str:
    with transcript_path.open("r", encoding="utf-8") as file:
        raw_text = file.read()
    cleaned_text = raw_text.replace("xzy", " ").strip()
    if cleaned_text == "":
        raise ValueError(
            f"Error: The file '{transcript_path}' contains no text."
        )
    return cleaned_text


def homogenize_string(text: str) -> str:
    """Homogenize strings for comparison

    Args:
        text (str): The string to be homogenized.

    Removes multiple whitespaces and non-alphanumeric characters.

    Returns:
        str: The homogenized string.
    """
    words = re.findall(r"\b\S+\b", text)
    alnum_words = (re.sub(r"\W+", "", word) for word in words)
    alnum_string = " ".join(alnum_words)
    single_spaced = re.sub(r" +", " ", alnum_string)

    re_text = single_spaced.strip().lower()

    return re_text


def calculate_wer(ground_truth_path: Path, transcription_path: Path) -> float:
    if ground_truth_path.name != transcription_path.name:
        raise ValueError(
            f"Expected {ground_truth_path.name=} to equal {transcription_path.name=}"
        )
    ground_truth = read_transcript(ground_truth_path)

    transcription = read_transcript(transcription_path)

    cleaned_ground_truth = homogenize_string(ground_truth)
    cleaned_transcription = homogenize_string(transcription)

    wer_score = wer(cleaned_ground_truth, cleaned_transcription)
    logging.info(f"Calculated WER for '{transcription_path}': {wer_score:.4f}")
    return wer_score


def summarize_wer(wer_results_file, wer_summary_file):
    df = pd.read_csv(wer_results_file)

    if len(df) != num_test_cases:
        raise ValueError(f"Expected {num_test_cases} rows found {len(df)}")

    summary = df["WER"].describe()

    summary_df = summary.reset_index()
    summary_df.columns = ["Statistic", "WER"]

    summary_df.to_csv(wer_summary_file, index=False, float_format="%.4f")
    print(f"Summary statistics saved to {wer_summary_file}")


def perform_wer_analysis(
    transcription_dir: Path,
    ground_truth_dir: Path,
    output_csv_file: Path,
    summary_file: None | Path = None,
):
    if summary_file is None:
        summary_file = Path(output_csv_file.parent, "wer_summary.csv")
    elif not summary_file.parent.exists():
        raise FileNotFoundError(
            f"Parent directory of summary file does not exist: {summary_file.parent}"
        )

    transcription_paths = sorted(list(transcription_dir.glob("*.txt")))
    logging.info(
        f"Total files found in transcription directory: {len(transcription_paths)}"
    )
    groundtruth_paths = sorted(list(ground_truth_dir.glob("*.txt")))

    if (
        len(groundtruth_paths) != num_test_cases
        or len(transcription_paths) != num_test_cases
    ):
        raise ValueError(
            f"Expected {num_test_cases} input files in each directory found: "
            f"GT ({len(groundtruth_paths)}) and "
            f"Transcriptions ({len(transcription_paths)})."
        )

    wer_results = []
    for transcription_file, ground_truth_file in zip(
        *(transcription_paths, groundtruth_paths)
    ):
        wer_score = calculate_wer(ground_truth_file, transcription_file)

        wer_results.append((transcription_file.stem, wer_score))

    if not wer_results:
        raise ValueError("Error: No valid WER results to write. Exiting.")

    df = pd.DataFrame(wer_results, columns=["filename", "WER"])
    df.to_csv(output_csv_file, index=False, float_format="%.4f")
    logging.debug(
        f"\nWER results successfully written to '{output_csv_file}'."
    )
    summarize_wer(output_csv_file, summary_file)


if __name__ == "__main__":
    perform_wer_analysis(
        transcription_dir=txt_output_dir,
        ground_truth_dir=ground_truth_dir,
        output_csv_file=wer_results_file,
        summary_file=wer_summary_file,
    )  # pragma no cover

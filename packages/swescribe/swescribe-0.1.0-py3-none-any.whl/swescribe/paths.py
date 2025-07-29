from pathlib import Path

project_root = Path(__file__).parents[2]

data_dir = project_root / "data"

input_videos_dir = data_dir / "mpg_input"
ground_truth_dir = data_dir / "ground_truth"

wav_extracted_dir = data_dir / "wav_extracted"

txt_output_dir = data_dir / "txt_output"
srt_output_dir = data_dir / "srt_output"
txt_cleaned_dir = data_dir / "txt_cleaned"

wer_results_file = data_dir / "wer_results.csv"
wer_summary_file = data_dir / "wer_results_summary.csv"

from argparse import ArgumentParser
from collections import defaultdict
from pathlib import Path
from tempfile import mkdtemp

from tqdm import tqdm

from swescribe.mpg_to_wav import extract_audio
from swescribe.wavpath_to_srt import wavpath_to_srt


def pipeline(input_path: Path, output_path: Path, force=False):
    if input_path.suffix == ".wav":
        audio_path = input_path
    else:
        audio_path = Path(mkdtemp()) / input_path.with_suffix(".wav").name
        extract_audio(mpg_file_path=input_path, wav_file_path=audio_path)
    srt_content = wavpath_to_srt(audio_path)

    write_mode = "w" if force else "x"

    with open(output_path, write_mode, encoding="utf-8") as f:
        f.write(srt_content)


def cli(arg_list: list[str] | None = None):
    args = parse_args(arg_list)

    force = args.force

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {input_path}")

    output = args.output
    if output is not None:
        output = Path(output)
    elif input_path.is_file():
        output = Path(input_path).with_suffix(".srt")
    else:
        output = input_path

    if output.suffix == ".srt" and input_path.is_dir():
        raise ValueError("Output file is a file, but input is a directory.")

    if input_path.is_file():
        print(f"Converting {input_path} to {output}")
        pipeline(input_path, output)

    elif input_path.is_dir():
        audios = [
            (audio, output / audio.with_suffix(".srt").name)
            for extension in ["*.wav", "*.mpg"]
            for audio in input_path.glob(extension)
        ]
        inputs = [
            (audio, output)
            for audio, output in audios
            if force or not output.exists()
        ]
        check_for_duplicate_outputs(inputs)

        print(f"Converting {len(inputs)} audios in {input_path} to {output}")
        for audio, srt_path in tqdm(inputs, desc="Transcribing"):
            pipeline(audio, srt_path, force=force)


def check_for_duplicate_outputs(inputs: list[tuple[Path, Path]]):
    output_files = defaultdict(list)
    for in_file, out_file in inputs:
        output_files[out_file].append(in_file)

    if len(output_files) != len(inputs):
        raise FileExistsError(
            "Files with same output.srt detected: " + str(output_files)
        )


def parse_args(arg_list):
    parser = ArgumentParser(
        description="SweScribe: A WhisperX based transcription tool for historical swedish newsreels."
    )

    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        required=True,
        help="Input file. Or directory to browser for .wav and .mpg files.",
    )

    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output file or directory. Needs to be a directory or None if "
        "input is a directory. "
        "Will default to using the video name with an .srt"
        "extension if no value is supplied or directories are used.",
    )

    parser.add_argument(
        "-f",
        "--force",
        default=False,
        action="store_true",
        help="Write over .srt file if they exist.",
    )
    args = parser.parse_args(arg_list)
    return args


if __name__ == "__main__":
    cli()  # pragma no cover

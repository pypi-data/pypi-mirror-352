import logging

import torch
import whisperx

if not torch.cuda.is_available():
    raise Exception("No GPU available.")

device = "cuda"

language_code = "sv"

logging.info("Loading Whisper model...")
model = whisperx.load_model(
    "large",
    device,
    language=language_code,
    asr_options={
        "multilingual": False,
        "max_new_tokens": None,
        "clip_timestamps": None,
        "hallucination_silence_threshold": None,
        "hotwords": None,
    },
)

logging.info("\nLoading alignment model...")
alignment_model, metadata = whisperx.load_align_model(
    language_code=language_code,
    device=device,
    model_name="KBLab/wav2vec2-large-voxrex-swedish",
)


def align_results(audio_file_path, transcription_result):
    return whisperx.align(
        transcription_result["segments"],
        alignment_model,
        metadata,
        str(audio_file_path),
        device,
        preprocess=False,
    )


def model_transcribe(audio_file_path):
    return model.transcribe(str(audio_file_path))

"""Transcribe audio files using the OpenAI API."""

import os
import json
import subprocess  # noqa: S404
import logging
from openai import OpenAI
from pathlib import Path

logger = logging.getLogger(__name__)


def transcribe_audio(audio_file, language="en", whisper_cpp_model=None):
    """
    Transcribe an audio file using either OpenAI API or whisper.cpp.

    Parameters
    ----------
    audio_file : file-like object
        The audio file to transcribe.
    language : str, default="English"
        The language of the audio file.
    whisper_cpp_model : str
        The whisper.cpp model to use for transcription.

    Returns
    -------
    dict
        The transcription of the audio file in segments.
    """
    if whisper_cpp_model and "gpt" not in whisper_cpp_model:
        return _transcribe_audio_whisper_cpp(audio_file, language, whisper_cpp_model)

    return _transcribe_audio_openai(audio_file, language, whisper_cpp_model)


def _transcribe_audio_openai(audio_file, language, whisper_cpp_model):
    """Transcribe an audio file using the OpenAI API."""
    client = OpenAI()

    if "gpt" in whisper_cpp_model:
        response_format = "json"
    else:
        response_format = "verbose_json"

    try:
        # Transcribe the audio using OpenAI API
        transcript = client.audio.transcriptions.create(
            file=audio_file,
            model=whisper_cpp_model,
            response_format=response_format,
            timestamp_granularities=["segment"],
            language=language,
            temperature=0,
        )
    except Exception as e:
        logger.error(f"Failed to transcribe audio: {e}")
        return {}

    return transcript.to_dict()


def _transcribe_audio_whisper_cpp(audio_file, language, model):
    """
    Transcribe using whisper.cpp CLI.

    Converts whisper-cli output to resemble OpenAI verbose_json format
    {
        "timestamps": {
            "from": "00:00:00,000",
            "to": "00:00:02,440"
        },
        "offsets": {
            "from": 0,
            "to": 2440
        },
        "text": " Hello, Good"
    }
    to
    {
        "id": 0,
        "start": 0,
        "end": 2.44,
        "text": "Hello, Good"
    }
    """
    # Get absolute paths using Pathlib (works on both Windows & Linux)
    models_path = Path.cwd() / "models"
    audio_path = Path.cwd() / "data" / "audio"

    # Format Windows paths correctly for Docker (convert to raw string)
    models_path = models_path.resolve().as_posix()
    audio_path = audio_path.resolve().as_posix()

    # Whisper CPP docker image
    docker_image = "ghcr.io/ggerganov/whisper.cpp:main"

    commands = [
        ["rm", "-f", "data/audio/output.wav"],
        [
            "ffmpeg",
            "-i",
            str(audio_file.name),
            "-ar",
            "16000",
            "-ac",
            "1",
            "-c:a",
            "pcm_s16le",
            "data/audio/output.wav",
        ],
        ["rm", "-f", "data/audio/output.wav.json"],
        # Download model if not exists
        [
            "docker",
            "run",
            "-it",
            "--rm",
            "-v",
            f'"{models_path}":/models',
            f"{docker_image}",
            f'"./models/download-ggml-model.sh {model} /models"',
        ],
        # Run transcription
        [
            "docker",
            "run",
            "-it",
            "--rm",
            "-v",
            f'"{models_path}":/models',
            "-v",
            f'"{audio_path}":/audios',
            f"{docker_image}",
            f'"./build/bin/whisper-cli -m /models/ggml-{model}.bin -f /audios/output.wav -ml 16 -oj -l {language}"',
        ],
    ]

    try:
        for cmd in commands:
            command = " ".join(cmd)
            logger.info(f"Running: {command}")
            result = subprocess.run(
                command,
                shell=True,  # noqa: S602
                capture_output=True,
                text=True,
                check=True,
            )

            # Print output
            logger.info(f"STDOUT: {result.stdout}")
            logger.warning(f"STDERR: {result.stderr}")

            # If a command fails, stop execution
            if result.returncode != 0:
                logger.error(
                    f"Error: Command {cmd} failed with exit code {result.returncode}"
                )
                break

        # # Wanted real-time output, tried many, all garbled, disabled https://stackoverflow.com/questions/803265/getting-realtime-output-using-subprocess
        # process = subprocess.Popen(conmed, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', universal_newlines=True)

        # while process.poll() is None:
        #     line = process.stdout.readline()
        #     print(line)

        with open("data/audio/output.wav.json", "rb") as f:
            transcript = json.load(f)

        # return the transcript in the format expected by the OpenAI API
        adapted_transcript = {"segments": []}
        for idx, segment in enumerate(transcript["transcription"]):
            start = segment["offsets"]["from"] / 1000
            end = segment["offsets"]["to"] / 1000
            text = segment["text"]
            adapted_transcript["segments"].append(
                {"id": idx, "start": start, "end": end, "text": text}
            )

        return adapted_transcript
    except Exception as e:
        logger.error(f"Unexpected error with whisper.cpp: {e}")
        return {}


def transcribe_audio_and_write(audio_file, destination_path: str):
    """
    Transcribe an audio file using the OpenAI API and write the transcription to a file.

    Parameters
    ----------
    audio_file : file-like object
        The audio file to transcribe.
    destination_path : str
        The full path (including filename) where the transcription will be saved.
    """
    transcription = transcribe_audio(audio_file)

    # Extract the transcription text
    transcription_text = transcription.get("text", "")

    # Ensure the destination directory exists
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)

    # Write the transcription to the destination file
    with open(destination_path, "w", encoding="utf-8") as f:
        f.write(transcription_text)

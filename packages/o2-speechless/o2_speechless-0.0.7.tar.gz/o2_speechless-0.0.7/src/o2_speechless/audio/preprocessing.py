"""Preprocessing utilities for audio files."""

import os
from pydub import AudioSegment, silence

MIN_SILENCE_LEN = 500


def remove_silences(
    input_file: str,
    silence_thresh: float = -20.0,
    min_silence_len: int = MIN_SILENCE_LEN,
) -> str:
    """
    Remove silent portions from an audio file and export a new file.

    Parameters
    ----------
    input_file : str
        Path to the input audio file.
    silence_thresh : float
        Silence threshold in dBFS. Anything quieter than this will be considered silence.
    min_silence_len : int
        The minimum length of silence in milliseconds that will be removed.

    Returns
    -------
    str
        Path to the processed audio file (with silence removed).
    """
    audio = AudioSegment.from_file(input_file)
    # Split the audio into chunks based on silence
    chunks = silence.split_on_silence(
        audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh
    )

    # Concatenate all the non-silent chunks
    processed_audio = AudioSegment.empty()

    # Combine all non-silent chunks into a single AudioSegment object in one step
    processed_audio = sum(chunks, AudioSegment.empty())

    # Build a new file name
    base, _ext = os.path.splitext(input_file)
    output_file = f"{base}_nosilence.wav"
    processed_audio.export(output_file, format="wav")

    return output_file

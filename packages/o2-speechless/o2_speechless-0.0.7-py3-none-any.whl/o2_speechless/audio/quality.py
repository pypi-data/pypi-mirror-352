"""Audio quality analysis functions"""

import numpy as np

FUNDAMENTAL_FREQ = 1000


def compute_thd(audio: np.array, sr: int, fundamental_freq: float) -> float:
    """
    Compute the total harmonic distortion of an audio signal.

    Parameters
    ----------
    audio : np.array
        The input audio signal.
    sr : int
        The sample rate of the audio signal.
    fundamental_freq : float
        The fundamental frequency of the audio signal.

    Returns
    -------
    float
        The total harmonic distortion of the audio signal.
    """
    # Perform FFT
    fft_spectrum = np.fft.fft(audio)
    freqs = np.fft.fftfreq(len(audio), 1 / sr)

    # Identify fundamental and harmonics
    fundamental_idx = np.argmin(np.abs(freqs - fundamental_freq))
    harmonics_idx = [
        np.argmin(np.abs(freqs - fundamental_freq * (i + 1))) for i in range(1, 5)
    ]

    # Compute THD
    fundamental_power = np.abs(fft_spectrum[fundamental_idx]) ** 2
    harmonic_power = sum(np.abs(fft_spectrum[idx]) ** 2 for idx in harmonics_idx)
    thd = np.sqrt(harmonic_power) / fundamental_power

    # Return percentage THD
    return thd * 100


def compute_snr(signal: np.array, sr: int) -> float:
    """
    Compute the signal-to-noise ratio (SNR) in dB without manually specifying noise duration. Noise is estimated from the lowest-energy segments of the signal.

    Parameters
    ----------
    signal : np.array
        The entire input signal.
    sr : int
        The sampling rate in Hz.

    Returns
    -------
    float
        The Signal-to-Noise Ratio (SNR) in decibels (dB).
    """
    # Compute total signal power
    signal_power = np.mean(signal**2)

    # Estimate noise power from the quietest part of the signal
    frame_size = sr // 10  # 100ms frames
    num_frames = len(signal) // frame_size
    frame_powers = [
        np.mean(signal[i * frame_size : (i + 1) * frame_size] ** 2)
        for i in range(num_frames)
    ]

    # Estimate noise power as the 10th percentile of frame power (conservative estimate of background noise)
    noise_power = np.percentile(frame_powers, 10)

    # Avoid division by zero
    if noise_power == 0:
        return float("inf")

    # Compute SNR in decibels
    snr = 10 * np.log10(signal_power / noise_power)

    return snr


def interpret_snr(snr: float) -> tuple:
    """
    Interpret the Signal-to-Noise Ratio (SNR) value.

    Parameters:
        snr : float
            The SNR value in decibels (dB).

    Returns:
        tuple: (interpretation string, color code)
    """
    if snr < 10:
        return (
            f"SNR = {snr:.2f} dB → Very poor (high noise, low signal quality)",
            "#FF0000",  # Red
        )
    elif 10 <= snr < 20:  # noqa: WPS432
        return (
            f"SNR = {snr:.2f} dB → Poor (noticeable noise, subpar audio)",
            "#FF5722",  # Deep Orange
        )
    elif 20 <= snr < 30:  # noqa: WPS432
        return (
            f"SNR = {snr:.2f} dB → Acceptable (some noise, but tolerable)",
            "#FFC107",  # Yellow
        )
    elif 30 <= snr < 40:  # noqa: WPS432
        return (
            f"SNR = {snr:.2f} dB → Good (clean audio, minimal noise)",
            "#4CAF50",  # Green
        )
    return (
        f"SNR = {snr:.2f} dB → Excellent (very clean audio, almost no noise)",
        "#2196F3",  # Blue
    )


def interpret_thd(thd: float) -> tuple:
    """
    Interpret the Total Harmonic Distortion (THD) value.

    Parameters
    ----------
    thd : float
        The THD value in percentage (%).

    Returns
    -------
        tuple: (interpretation string, color code)
    """
    if thd > 1:
        return (
            f"THD = {thd:.2f}% → Poor (noticeable distortion, low-quality audio)",
            "#FF0000",  # Red
        )
    elif 0.3 <= thd <= 1:  # noqa: WPS432, WPS459
        return (
            f"THD = {thd:.2f}% → Fair (distortion, see if can be improved)",
            "#FFC107",  # Yellow
        )
    elif 0.1 <= thd < 0.3:  # noqa: WPS432, WPS459
        return (
            f"THD = {thd:.2f}% → Good (slightly perceptible distortion)",
            "#4CAF50",  # Green
        )
    return (
        f"THD = {thd:.2f}% → Excellent (very little distortion, high-quality audio)",
        "#2196F3",  # Blue
    )


def analyze_audio(
    signal: np.array, sr: int, fundamental_freq: float = FUNDAMENTAL_FREQ
) -> dict:
    """
    Compute and interpret the SNR and THD for an audio signal.

    Parameters
    ----------
    signal : np.array
        The input audio signal.
    sr : int
        The sample rate of the audio signal.
    fundamental_freq : float
        The fundamental frequency of the audio signal.

    Returns
    -------
    dict
        A dictionary containing the SNR and THD values, interpretations, and
    """
    # Compute values
    snr_value = compute_snr(signal, sr)
    thd_value = compute_thd(signal, sr, fundamental_freq)

    # Interpret values with colors
    snr_interpretation, snr_color = interpret_snr(snr_value)
    thd_interpretation, thd_color = interpret_thd(thd_value)

    # Return results as a dictionary
    return {
        "SNR": {
            "value": snr_value,
            "interpretation": snr_interpretation,
            "color": snr_color,
        },
        "THD": {
            "value": thd_value,
            "interpretation": thd_interpretation,
            "color": thd_color,
        },
    }

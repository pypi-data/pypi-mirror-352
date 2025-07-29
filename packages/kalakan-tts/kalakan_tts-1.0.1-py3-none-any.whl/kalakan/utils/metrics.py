"""
Evaluation metrics for Kalakan TTS.

This module provides evaluation metrics for TTS systems,
including MCD, F0 RMSE, and voicing error.
"""

from typing import Dict, Optional, Tuple, Union, Protocol

import numpy as np
import torch
import librosa
from scipy.spatial.distance import cdist


class AudioProcessor(Protocol):
    """Protocol for audio processor objects."""
    sample_rate: int
    n_fft: int
    hop_length: int
    win_length: int


def compute_mcd(
    reference_audio: Union[np.ndarray, torch.Tensor],
    synthesized_audio: Union[np.ndarray, torch.Tensor],
    audio_processor: Optional[AudioProcessor] = None,
    sample_rate: int = 22050,
    n_mfcc: int = 13,
    n_fft: int = 1024,
    hop_length: int = 256,
    win_length: Optional[int] = None,
) -> float:
    """
    Compute Mel Cepstral Distortion (MCD) between reference and synthesized audio.

    Args:
        reference_audio: Reference audio signal.
        synthesized_audio: Synthesized audio signal.
        audio_processor: Audio processor instance. If provided, uses its parameters.
        sample_rate: Audio sample rate.
        n_mfcc: Number of MFCCs to compute.
        n_fft: FFT size.
        hop_length: Hop length.
        win_length: Window length. If None, defaults to n_fft.

    Returns:
        MCD value in dB.
    """
    # Convert to numpy if needed
    if isinstance(reference_audio, torch.Tensor):
        reference_audio = reference_audio.cpu().numpy()
    if isinstance(synthesized_audio, torch.Tensor):
        synthesized_audio = synthesized_audio.cpu().numpy()

    # Ensure audio is 1D
    if reference_audio.ndim > 1:
        reference_audio = reference_audio.squeeze()
    if synthesized_audio.ndim > 1:
        synthesized_audio = synthesized_audio.squeeze()

    # Use audio processor parameters if provided
    if audio_processor is not None:
        sample_rate = audio_processor.sample_rate
        n_fft = audio_processor.n_fft
        hop_length = audio_processor.hop_length
        win_length = audio_processor.win_length

    # Set default win_length if not provided
    if win_length is None:
        win_length = n_fft

    # Compute MFCCs for reference audio
    ref_mfcc = librosa.feature.mfcc(
        y=reference_audio,
        sr=sample_rate,
        n_mfcc=n_mfcc,
        n_fft=n_fft,
        hop_length=hop_length,
        win_length=win_length,
    )

    # Compute MFCCs for synthesized audio
    syn_mfcc = librosa.feature.mfcc(
        y=synthesized_audio,
        sr=sample_rate,
        n_mfcc=n_mfcc,
        n_fft=n_fft,
        hop_length=hop_length,
        win_length=win_length,
    )

    # Dynamic time warping to align MFCCs
    D, wp = librosa.sequence.dtw(ref_mfcc, syn_mfcc, subseq=True)

    # Extract aligned frames
    ref_aligned = np.array([ref_mfcc[:, wp[i, 0]] for i in range(len(wp))])
    syn_aligned = np.array([syn_mfcc[:, wp[i, 1]] for i in range(len(wp))])

    # Compute Euclidean distance
    mcd = np.mean(np.sqrt(np.sum((ref_aligned - syn_aligned) ** 2, axis=1)))

    # Convert to dB
    mcd = 10 / np.log(10) * mcd

    return float(mcd)


def compute_f0_metrics(
    reference_audio: Union[np.ndarray, torch.Tensor],
    synthesized_audio: Union[np.ndarray, torch.Tensor],
    sample_rate: int = 22050,
    hop_length: int = 256,
    f0_min: float = 80.0,
    f0_max: float = 800.0,
) -> Dict[str, float]:
    """
    Compute F0 metrics between reference and synthesized audio.

    Args:
        reference_audio: Reference audio signal.
        synthesized_audio: Synthesized audio signal.
        sample_rate: Audio sample rate.
        hop_length: Hop length for F0 extraction.
        f0_min: Minimum F0 value.
        f0_max: Maximum F0 value.

    Returns:
        Dictionary containing F0 metrics:
            - f0_rmse: Root mean square error of F0.
            - f0_corr: Correlation coefficient of F0.
            - voicing_error: Voicing error rate.
    """
    # Convert to numpy if needed
    if isinstance(reference_audio, torch.Tensor):
        reference_audio = reference_audio.cpu().numpy()
    if isinstance(synthesized_audio, torch.Tensor):
        synthesized_audio = synthesized_audio.cpu().numpy()

    # Ensure audio is 1D
    if reference_audio.ndim > 1:
        reference_audio = reference_audio.squeeze()
    if synthesized_audio.ndim > 1:
        synthesized_audio = synthesized_audio.squeeze()

    # Extract F0 for reference audio
    ref_f0, ref_voiced_flag, _ = librosa.pyin(
        reference_audio,
        fmin=f0_min,
        fmax=f0_max,
        sr=sample_rate,
        hop_length=hop_length,
    )

    # Extract F0 for synthesized audio
    syn_f0, syn_voiced_flag, _ = librosa.pyin(
        synthesized_audio,
        fmin=f0_min,
        fmax=f0_max,
        sr=sample_rate,
        hop_length=hop_length,
    )

    # Dynamic time warping to align F0 sequences
    ref_f0_padded = np.pad(ref_f0, (0, max(0, len(syn_f0) - len(ref_f0))), mode='constant', constant_values=np.nan)
    syn_f0_padded = np.pad(syn_f0, (0, max(0, len(ref_f0) - len(syn_f0))), mode='constant', constant_values=np.nan)

    # Compute metrics only on frames where both are voiced
    ref_voiced = ~np.isnan(ref_f0_padded)
    syn_voiced = ~np.isnan(syn_f0_padded)
    both_voiced = ref_voiced & syn_voiced

    # Compute voicing error
    voicing_error = np.mean(ref_voiced != syn_voiced) * 100.0

    # Compute F0 RMSE and correlation
    if np.sum(both_voiced) > 0:
        f0_rmse = np.sqrt(np.mean((ref_f0_padded[both_voiced] - syn_f0_padded[both_voiced]) ** 2))
        f0_corr = np.corrcoef(ref_f0_padded[both_voiced], syn_f0_padded[both_voiced])[0, 1]
    else:
        f0_rmse = float('nan')
        f0_corr = float('nan')

    return {
        "f0_rmse": float(f0_rmse),
        "f0_corr": float(f0_corr),
        "voicing_error": float(voicing_error),
    }


def compute_word_error_rate(
    reference_text: str,
    recognized_text: str,
) -> float:
    """
    Compute Word Error Rate (WER) between reference and recognized text.

    Args:
        reference_text: Reference text.
        recognized_text: Recognized text.

    Returns:
        Word Error Rate.
    """
    # Tokenize text into words
    ref_words = reference_text.lower().split()
    hyp_words = recognized_text.lower().split()

    # Compute Levenshtein distance
    d = np.zeros((len(ref_words) + 1, len(hyp_words) + 1), dtype=np.int32)

    # Initialize first row and column
    for i in range(len(ref_words) + 1):
        d[i, 0] = i
    for j in range(len(hyp_words) + 1):
        d[0, j] = j

    # Compute distance
    for i in range(1, len(ref_words) + 1):
        for j in range(1, len(hyp_words) + 1):
            if ref_words[i-1] == hyp_words[j-1]:
                d[i, j] = d[i-1, j-1]
            else:
                d[i, j] = min(d[i-1, j], d[i, j-1], d[i-1, j-1]) + 1

    # Compute WER
    wer = d[len(ref_words), len(hyp_words)] / len(ref_words)

    return float(wer)


def compute_character_error_rate(
    reference_text: str,
    recognized_text: str,
) -> float:
    """
    Compute Character Error Rate (CER) between reference and recognized text.

    Args:
        reference_text: Reference text.
        recognized_text: Recognized text.

    Returns:
        Character Error Rate.
    """
    # Normalize text
    ref_chars = reference_text.lower()
    hyp_chars = recognized_text.lower()

    # Compute Levenshtein distance
    d = np.zeros((len(ref_chars) + 1, len(hyp_chars) + 1), dtype=np.int32)

    # Initialize first row and column
    for i in range(len(ref_chars) + 1):
        d[i, 0] = i
    for j in range(len(hyp_chars) + 1):
        d[0, j] = j

    # Compute distance
    for i in range(1, len(ref_chars) + 1):
        for j in range(1, len(hyp_chars) + 1):
            if ref_chars[i-1] == hyp_chars[j-1]:
                d[i, j] = d[i-1, j-1]
            else:
                d[i, j] = min(d[i-1, j], d[i, j-1], d[i-1, j-1]) + 1

    # Compute CER
    cer = d[len(ref_chars), len(hyp_chars)] / len(ref_chars)

    return float(cer)
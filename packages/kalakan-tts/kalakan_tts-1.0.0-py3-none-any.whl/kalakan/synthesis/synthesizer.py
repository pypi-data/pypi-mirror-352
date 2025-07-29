"""
Synthesizer for Kalakan TTS.

This module implements the main synthesizer interface for Kalakan TTS,
which combines the text processing, acoustic model, and vocoder to
generate speech from text.
"""

import logging
import os
from typing import Dict, List, Optional, Tuple, Union, Any

import numpy as np
import torch
import torchaudio

from kalakan.audio.utils import save_audio
from kalakan.models.acoustic.base_acoustic import BaseAcousticModel
from kalakan.models.vocoders.base_vocoder import BaseVocoder
from kalakan.text.normalizer import normalize_text
from kalakan.text.cleaner import clean_text
from kalakan.text.twi_g2p import TwiG2P
from kalakan.text.enhanced_g2p import EnhancedTwiG2P
from kalakan.utils.config import Config
from kalakan.utils.device import get_device
from kalakan.utils.model_factory import ModelFactory


logger = logging.getLogger(__name__)


class Synthesizer:
    """
    Synthesizer for Kalakan TTS.

    This class provides methods for generating speech from text using
    the Kalakan TTS system.
    """

    def __init__(
        self,
        acoustic_model: Optional[Union[BaseAcousticModel, str]] = None,
        vocoder: Optional[Union[BaseVocoder, str]] = None,
        g2p: Optional[TwiG2P] = None,
        device: Optional[torch.device] = None,
        config: Optional[Union[Dict, Config, str]] = None,
        acoustic_model_type: Optional[str] = None,
        vocoder_type: Optional[str] = None,
    ):
        """
        Initialize the synthesizer.

        Args:
            acoustic_model: Acoustic model to use, or path to a checkpoint file.
                If None, a default acoustic model is used based on configuration.
            vocoder: Vocoder to use, or path to a checkpoint file.
                If None, a default vocoder is used based on configuration.
            g2p: Grapheme-to-phoneme converter to use.
                If None, a default TwiG2P converter is used.
            device: Device to use for inference.
            config: Configuration for the synthesizer.
            acoustic_model_type: Type of acoustic model to use if creating a new one.
                If None, the type is determined from the configuration.
            vocoder_type: Type of vocoder to use if creating a new one.
                If None, the type is determined from the configuration.
        """
        # Set device
        self.device = device if device is not None else get_device()
        logger.info(f"Using device: {self.device}")

        # Set configuration
        if config is None:
            self.config = Config()
        elif isinstance(config, dict):
            self.config = Config(config)
        elif isinstance(config, str):
            self.config = Config(config)
        else:
            self.config = config

        # Set G2P converter
        self.g2p = g2p if g2p is not None else EnhancedTwiG2P()
        logger.info(f"Using G2P converter: {self.g2p.__class__.__name__}")

        # Set acoustic model
        if isinstance(acoustic_model, BaseAcousticModel):
            # Use provided acoustic model
            self.acoustic_model = acoustic_model.to(self.device)
        else:
            # Get default configuration path if needed
            if config is None:
                config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                          "configs", "models", "tacotron2_base.yaml")
                if os.path.exists(config_path):
                    logger.info(f"Loading default acoustic model configuration from {config_path}")
                    config = config_path

            # Create acoustic model using factory
            self.acoustic_model = ModelFactory.create_acoustic_model(
                model_type=acoustic_model_type,
                config=config,
                checkpoint_path=acoustic_model if isinstance(acoustic_model, str) else None,
                device=self.device,
            )

        # Set vocoder
        if isinstance(vocoder, BaseVocoder):
            # Use provided vocoder
            self.vocoder = vocoder.to(self.device)
        else:
            # Get default configuration path if needed
            if config is None:
                config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                          "configs", "models", "griffin_lim_base.yaml")
                if os.path.exists(config_path):
                    logger.info(f"Loading default vocoder configuration from {config_path}")
                    config = config_path

            # Create vocoder using factory
            self.vocoder = ModelFactory.create_vocoder(
                model_type=vocoder_type,
                config=config,
                checkpoint_path=vocoder if isinstance(vocoder, str) else None,
                device=self.device,
            )

        # Set models to evaluation mode
        self.acoustic_model.eval()
        self.vocoder.eval()

        logger.info(f"Initialized synthesizer with {self.acoustic_model.__class__.__name__} acoustic model and {self.vocoder.__class__.__name__} vocoder")



    def synthesize(
        self,
        text: str,
        normalize: bool = True,
        clean: bool = True,
        max_length: Optional[int] = None,
        speed: float = 1.0,
        pitch: float = 1.0,
        energy: float = 1.0,
    ) -> torch.Tensor:
        """
        Synthesize speech from text.

        Args:
            text: Input text.
            normalize: Whether to normalize the text.
            clean: Whether to clean the text.
            max_length: Maximum length of generated mel spectrograms.
            speed: Speech speed factor (1.0 = normal speed). Inversely affects duration.
            pitch: Pitch factor (1.0 = normal pitch).
            energy: Energy factor (1.0 = normal energy).

        Returns:
            Generated audio waveform.
        """
        # Preprocess text
        if clean:
            text = clean_text(text)
        if normalize:
            text = normalize_text(text)

        # Convert text to phoneme sequence
        phoneme_sequence = self.g2p.text_to_phoneme_sequence(text)

        # Convert to tensor
        phonemes = torch.tensor(phoneme_sequence, dtype=torch.long).unsqueeze(0).to(self.device)

        # Generate mel spectrogram
        with torch.no_grad():
            # Prepare base parameters for inference
            inference_kwargs = {}
            if max_length is not None:
                inference_kwargs["max_length"] = max_length

            # Add FastSpeech2-specific parameters if the model is FastSpeech2
            if self.acoustic_model.__class__.__name__ == "FastSpeech2":
                # For FastSpeech2 models, speed is inversely related to duration control
                inference_kwargs["p_control"] = pitch
                inference_kwargs["e_control"] = energy
                inference_kwargs["d_control"] = 1.0 / speed if speed > 0 else 1.0

            # Call inference with appropriate parameters
            mel, _ = self.acoustic_model.inference(phonemes, **inference_kwargs)

        # Generate audio
        with torch.no_grad():
            audio = self.vocoder.inference(mel)

        return audio.squeeze(0)

    def synthesize_batch(
        self,
        texts: List[str],
        normalize: bool = True,
        clean: bool = True,
        max_length: Optional[int] = None,
        batch_size: int = 8,
        speed: float = 1.0,
        pitch: float = 1.0,
        energy: float = 1.0,
    ) -> List[torch.Tensor]:
        """
        Synthesize speech from a batch of texts.

        Args:
            texts: List of input texts.
            normalize: Whether to normalize the texts.
            clean: Whether to clean the texts.
            max_length: Maximum length of generated mel spectrograms.
            batch_size: Batch size for inference.
            speed: Speech speed factor (1.0 = normal speed).
            pitch: Pitch factor (1.0 = normal pitch).
            energy: Energy factor (1.0 = normal energy).

        Returns:
            List of generated audio waveforms.
        """
        # Preprocess texts
        processed_texts = []
        for text in texts:
            if clean:
                text = clean_text(text)
            if normalize:
                text = normalize_text(text)
            processed_texts.append(text)

        # Convert texts to phoneme sequences
        phoneme_sequences = []
        for text in processed_texts:
            phoneme_sequence = self.g2p.text_to_phoneme_sequence(text)
            phoneme_sequences.append(phoneme_sequence)

        # Process in batches
        audio_list = []
        for i in range(0, len(phoneme_sequences), batch_size):
            # Get batch
            batch_sequences = phoneme_sequences[i:i+batch_size]

            # Pad sequences
            max_length_phonemes = max(len(seq) for seq in batch_sequences)
            padded_phonemes = []
            for seq in batch_sequences:
                padded_seq = seq + [0] * (max_length_phonemes - len(seq))
                padded_phonemes.append(padded_seq)

            # Convert to tensor
            phonemes = torch.tensor(padded_phonemes, dtype=torch.long).to(self.device)

            # Generate mel spectrograms
            with torch.no_grad():
                # Prepare base parameters for inference
                inference_kwargs = {}
                if max_length is not None:
                    inference_kwargs["max_length"] = max_length

                # Add FastSpeech2-specific parameters if the model is FastSpeech2
                if self.acoustic_model.__class__.__name__ == "FastSpeech2":
                    # For FastSpeech2 models, speed is inversely related to duration control
                    inference_kwargs["p_control"] = pitch
                    inference_kwargs["e_control"] = energy
                    inference_kwargs["d_control"] = 1.0 / speed if speed > 0 else 1.0

                # Call inference with appropriate parameters
                mels, _ = self.acoustic_model.inference(phonemes, **inference_kwargs)

            # Generate audio
            with torch.no_grad():
                audio = self.vocoder.inference(mels)

            # Add to list
            audio_list.extend(audio.cpu())

        return audio_list

    def save_audio(
        self,
        audio: torch.Tensor,
        file_path: str,
        sample_rate: Optional[int] = None,
    ) -> None:
        """
        Save audio to a file.

        Args:
            audio: Audio waveform.
            file_path: Path to save the audio file.
            sample_rate: Sample rate of the audio. If None, the vocoder's sample rate is used.
        """
        # Get sample rate
        if sample_rate is None:
            sample_rate = self.vocoder.sample_rate

        # Save audio
        save_audio(audio.cpu().numpy(), file_path, sample_rate=sample_rate)

    def text_to_speech(
        self,
        text: str,
        output_file: str,
        normalize: bool = True,
        clean: bool = True,
        max_length: Optional[int] = None,
        sample_rate: Optional[int] = None,
        speed: float = 1.0,
        pitch: float = 1.0,
        energy: float = 1.0,
    ) -> None:
        """
        Convert text to speech and save to a file.

        Args:
            text: Input text.
            output_file: Path to save the audio file.
            normalize: Whether to normalize the text.
            clean: Whether to clean the text.
            max_length: Maximum length of generated mel spectrograms.
            sample_rate: Sample rate of the audio. If None, the vocoder's sample rate is used.
            speed: Speech speed factor (1.0 = normal speed).
            pitch: Pitch factor (1.0 = normal pitch).
            energy: Energy factor (1.0 = normal energy).
        """
        # Synthesize speech
        audio = self.synthesize(
            text=text,
            normalize=normalize,
            clean=clean,
            max_length=max_length,
            speed=speed,
            pitch=pitch,
            energy=energy,
        )

        # Save audio
        self.save_audio(audio, output_file, sample_rate=sample_rate)
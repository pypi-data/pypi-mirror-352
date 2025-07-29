"""
FastSpeech2 model for Kalakan TTS.

This module implements the FastSpeech2 model for text-to-mel conversion,
as described in "FastSpeech 2: Fast and High-Quality End-to-End Text to Speech"
(Ren et al., 2020), with adaptations for the Twi language.
"""

from typing import Dict, List, Optional, Tuple, Union

import torch
import torch.nn as nn
import torch.nn.functional as F

from kalakan.models.acoustic.base_acoustic import BaseAcousticModel
from kalakan.models.components.encoders import TextEncoder
from kalakan.models.components.decoders import MelDecoder
from kalakan.models.components.layers import VarianceAdaptor
from kalakan.text.phonemes import TwiPhonemes


class FastSpeech2(BaseAcousticModel):
    """
    FastSpeech2 model for Kalakan TTS.
    
    This model converts phoneme sequences to mel spectrograms using
    a non-autoregressive encoder-decoder architecture with variance adapters.
    """
    
    def __init__(
        self,
        n_phonemes: Optional[int] = None,
        phoneme_dict: Optional[Dict[str, int]] = None,
        embedding_dim: int = 256,
        encoder_dim: int = 256,
        encoder_layers: int = 4,
        encoder_heads: int = 2,
        encoder_conv_filter_size: int = 1024,
        encoder_conv_kernel_size: int = 9,
        encoder_dropout: float = 0.2,
        variance_predictor_filter_size: int = 256,
        variance_predictor_kernel_size: int = 3,
        variance_predictor_dropout: float = 0.5,
        decoder_dim: int = 256,
        decoder_layers: int = 4,
        decoder_heads: int = 2,
        decoder_conv_filter_size: int = 1024,
        decoder_conv_kernel_size: int = 9,
        decoder_dropout: float = 0.2,
        n_mels: int = 80,
        max_seq_len: int = 1000,
        pitch_feature_level: str = "phoneme_level",
        energy_feature_level: str = "phoneme_level",
        pitch_quantization: str = "linear",
        energy_quantization: str = "linear",
        n_bins: int = 256,
    ):
        """
        Initialize the FastSpeech2 model.
        
        Args:
            n_phonemes: Number of phonemes in the vocabulary.
                If None, the number of phonemes is determined from phoneme_dict.
            phoneme_dict: Dictionary mapping phonemes to indices.
                If None, the default Twi phoneme dictionary is used.
            embedding_dim: Dimension of the phoneme embeddings.
            encoder_dim: Dimension of the encoder.
            encoder_layers: Number of transformer layers in the encoder.
            encoder_heads: Number of attention heads in the encoder.
            encoder_conv_filter_size: Size of the convolutional filter in the encoder.
            encoder_conv_kernel_size: Kernel size for the encoder convolutional layers.
            encoder_dropout: Dropout rate for the encoder.
            variance_predictor_filter_size: Size of the variance predictor filter.
            variance_predictor_kernel_size: Kernel size for the variance predictor.
            variance_predictor_dropout: Dropout rate for the variance predictor.
            decoder_dim: Dimension of the decoder.
            decoder_layers: Number of transformer layers in the decoder.
            decoder_heads: Number of attention heads in the decoder.
            decoder_conv_filter_size: Size of the convolutional filter in the decoder.
            decoder_conv_kernel_size: Kernel size for the decoder convolutional layers.
            decoder_dropout: Dropout rate for the decoder.
            n_mels: Number of mel bands.
            max_seq_len: Maximum sequence length.
            pitch_feature_level: Level of pitch features ("phoneme_level" or "frame_level").
            energy_feature_level: Level of energy features ("phoneme_level" or "frame_level").
            pitch_quantization: Type of pitch quantization ("linear" or "log").
            energy_quantization: Type of energy quantization ("linear" or "log").
            n_bins: Number of bins for quantization.
        """
        # Initialize base class
        super().__init__(phoneme_dict=phoneme_dict)
        
        # Set model name
        self.model_name = "fastspeech2"
        
        # Set number of phonemes
        if n_phonemes is not None:
            self.n_phonemes = n_phonemes
        
        # Set number of mel bands
        self.n_mels = n_mels
        
        # Set maximum sequence length
        self.max_seq_len = max_seq_len
        
        # Set feature levels
        self.pitch_feature_level = pitch_feature_level
        self.energy_feature_level = energy_feature_level
        
        # Create phoneme embedding
        self.phoneme_embedding = nn.Embedding(
            self.n_phonemes, embedding_dim, padding_idx=self.pad_id
        )
        
        # Create encoder
        self.encoder = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(
                d_model=encoder_dim,
                nhead=encoder_heads,
                dim_feedforward=encoder_conv_filter_size,
                dropout=encoder_dropout,
                activation="relu",
                batch_first=True,
            ),
            num_layers=encoder_layers,
            norm=nn.LayerNorm(encoder_dim),
        )
        
        # Create variance adaptor
        self.variance_adaptor = VarianceAdaptor(
            encoder_dim=encoder_dim,
            filter_size=variance_predictor_filter_size,
            kernel_size=variance_predictor_kernel_size,
            dropout=variance_predictor_dropout,
            n_bins=n_bins,
            pitch_feature_level=pitch_feature_level,
            energy_feature_level=energy_feature_level,
            pitch_quantization=pitch_quantization,
            energy_quantization=energy_quantization,
        )
        
        # Create decoder
        self.decoder = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(
                d_model=decoder_dim,
                nhead=decoder_heads,
                dim_feedforward=decoder_conv_filter_size,
                dropout=decoder_dropout,
                activation="relu",
                batch_first=True,
            ),
            num_layers=decoder_layers,
            norm=nn.LayerNorm(decoder_dim),
        )
        
        # Create mel linear layer
        self.mel_linear = nn.Linear(decoder_dim, n_mels)
        
        # Create length regulator
        self.length_regulator = LengthRegulator()
    
    def forward(
        self,
        phonemes: torch.Tensor,
        phoneme_lengths: torch.Tensor,
        max_length: Optional[int] = None,
        durations: Optional[torch.Tensor] = None,
        pitch: Optional[torch.Tensor] = None,
        energy: Optional[torch.Tensor] = None,
        p_control: float = 1.0,
        e_control: float = 1.0,
        d_control: float = 1.0,
    ) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
        """
        Forward pass of the FastSpeech2 model.
        
        Args:
            phonemes: Tensor of phoneme indices [batch_size, max_phoneme_length].
            phoneme_lengths: Tensor of phoneme sequence lengths [batch_size].
            max_length: Maximum length of generated mel spectrograms.
            durations: Ground truth durations for training [batch_size, max_phoneme_length].
            pitch: Ground truth pitch for training [batch_size, max_phoneme_length or max_mel_length].
            energy: Ground truth energy for training [batch_size, max_phoneme_length or max_mel_length].
            p_control: Pitch control factor.
            e_control: Energy control factor.
            d_control: Duration control factor.
                
        Returns:
            Tuple containing:
                - Predicted mel spectrograms [batch_size, n_mels, max_mel_length].
                - Dictionary of additional outputs (e.g., durations, pitch, energy).
        """
        # Get batch size and max length
        batch_size = phonemes.size(0)
        
        # Create masks
        src_masks = self._get_mask_from_lengths(phoneme_lengths)
        
        # Embed phonemes
        x = self.phoneme_embedding(phonemes)
        
        # Encode
        x = self.encoder(x, src_key_padding_mask=src_masks)
        
        # Apply variance adaptor
        (
            x,
            duration_predictions,
            pitch_predictions,
            energy_predictions,
            mel_lengths,
            mel_masks,
        ) = self.variance_adaptor(
            x,
            src_masks,
            phoneme_lengths,
            max_length,
            durations,
            pitch,
            energy,
            p_control,
            e_control,
            d_control,
        )
        
        # Decode
        x = self.decoder(x, src_key_padding_mask=mel_masks)
        
        # Generate mel spectrograms
        mel_outputs = self.mel_linear(x)
        
        # Transpose to match expected output shape [batch_size, n_mels, max_mel_length]
        mel_outputs = mel_outputs.transpose(1, 2)
        
        # Prepare outputs
        outputs = {
            "duration_predictions": duration_predictions,
            "pitch_predictions": pitch_predictions,
            "energy_predictions": energy_predictions,
            "mel_lengths": mel_lengths,
            "mel_masks": mel_masks,
        }
        
        return mel_outputs, outputs
    
    def inference(
        self,
        phonemes: torch.Tensor,
        max_length: Optional[int] = None,
        p_control: float = 1.0,
        e_control: float = 1.0,
        d_control: float = 1.0,
    ) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
        """
        Generate mel spectrograms from phonemes (inference mode).
        
        Args:
            phonemes: Tensor of phoneme indices [batch_size, max_phoneme_length].
            max_length: Maximum length of generated mel spectrograms.
            p_control: Pitch control factor.
            e_control: Energy control factor.
            d_control: Duration control factor.
                
        Returns:
            Tuple containing:
                - Predicted mel spectrograms [batch_size, n_mels, max_mel_length].
                - Dictionary of additional outputs (e.g., durations, pitch, energy).
        """
        # Set model to evaluation mode
        self.eval()
        
        # Compute phoneme lengths
        phoneme_lengths = torch.sum(phonemes != self.pad_id, dim=1)
        
        # Forward pass
        mel_outputs, outputs = self.forward(
            phonemes=phonemes,
            phoneme_lengths=phoneme_lengths,
            max_length=max_length,
            p_control=p_control,
            e_control=e_control,
            d_control=d_control,
        )
        
        return mel_outputs, outputs
    
    def _get_mask_from_lengths(self, lengths: torch.Tensor) -> torch.Tensor:
        """
        Create mask from sequence lengths.
        
        Args:
            lengths: Sequence lengths [batch_size].
                
        Returns:
            Mask tensor [batch_size, max_len].
        """
        batch_size = lengths.size(0)
        max_len = torch.max(lengths).item()
        mask = torch.arange(0, max_len).to(lengths.device).expand(batch_size, max_len) >= lengths.unsqueeze(1)
        return mask


class LengthRegulator(nn.Module):
    """
    Length regulator for FastSpeech2.
    
    This module expands the phoneme sequence according to the predicted durations.
    """
    
    def __init__(self):
        """Initialize the length regulator."""
        super().__init__()
    
    def forward(
        self,
        x: torch.Tensor,
        durations: torch.Tensor,
        max_length: Optional[int] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass of the length regulator.
        
        Args:
            x: Input tensor [batch_size, max_phoneme_length, encoder_dim].
            durations: Durations tensor [batch_size, max_phoneme_length].
            max_length: Maximum length of the output sequence.
                
        Returns:
            Tuple containing:
                - Expanded tensor [batch_size, max_mel_length, encoder_dim].
                - Output lengths [batch_size].
        """
        # Get batch size and input dimensions
        batch_size, max_phoneme_length, encoder_dim = x.size()
        
        # Calculate output lengths
        output_lengths = torch.sum(durations, dim=1).long()
        
        # Set maximum length if specified
        if max_length is not None:
            output_lengths = torch.clamp(output_lengths, max=max_length)
        
        # Get maximum output length
        max_mel_length = torch.max(output_lengths).item()
        
        # Initialize output tensor
        output = torch.zeros(batch_size, max_mel_length, encoder_dim).to(x.device)
        
        # Expand each phoneme according to its duration
        for i in range(batch_size):
            current_position = 0
            for j in range(max_phoneme_length):
                if durations[i, j] == 0:
                    # Skip padding
                    continue
                
                # Get current phoneme and its duration
                current_phoneme = x[i, j]
                current_duration = min(durations[i, j].item(), max_mel_length - current_position)
                
                # Expand the phoneme
                output[i, current_position:current_position + current_duration] = current_phoneme
                
                # Update position
                current_position += current_duration
                
                # Break if we've reached the maximum length
                if current_position >= max_mel_length:
                    break
        
        return output, output_lengths
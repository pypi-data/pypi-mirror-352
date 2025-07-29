"""
Tacotron2 model for Kalakan TTS.

This module implements the Tacotron2 model for text-to-mel conversion,
as described in "Natural TTS Synthesis by Conditioning WaveNet on Mel Spectrogram
Predictions" (Shen et al., 2018), with adaptations for the Twi language.
"""

from typing import Dict, List, Optional, Tuple, Union

import torch
import torch.nn as nn
import torch.nn.functional as F

from kalakan.models.acoustic.base_acoustic import BaseAcousticModel
from kalakan.models.components.decoders import MelDecoder
from kalakan.models.components.encoders import TextEncoder
from kalakan.text.phonemes import TwiPhonemes


class Tacotron2(BaseAcousticModel):
    """
    Tacotron2 model for Kalakan TTS.
    
    This model converts phoneme sequences to mel spectrograms using
    an encoder-decoder architecture with attention.
    """
    
    def __init__(
        self,
        n_phonemes: Optional[int] = None,
        phoneme_dict: Optional[Dict[str, int]] = None,
        embedding_dim: int = 512,
        encoder_dim: int = 512,
        encoder_conv_layers: int = 3,
        encoder_conv_kernel_size: int = 5,
        encoder_conv_dropout: float = 0.5,
        encoder_lstm_layers: int = 1,
        encoder_lstm_dropout: float = 0.1,
        decoder_dim: int = 1024,
        decoder_prenet_dim: List[int] = [256, 256],
        decoder_lstm_layers: int = 2,
        decoder_lstm_dropout: float = 0.1,
        decoder_zoneout: float = 0.1,
        attention_dim: int = 128,
        attention_location_features_dim: int = 32,
        attention_location_kernel_size: int = 31,
        postnet_dim: int = 512,
        postnet_kernel_size: int = 5,
        postnet_layers: int = 5,
        postnet_dropout: float = 0.5,
        n_mels: int = 80,
        stop_threshold: float = 0.5,
    ):
        """
        Initialize the Tacotron2 model.
        
        Args:
            n_phonemes: Number of phonemes in the vocabulary.
                If None, the number of phonemes is determined from phoneme_dict.
            phoneme_dict: Dictionary mapping phonemes to indices.
                If None, the default Twi phoneme dictionary is used.
            embedding_dim: Dimension of the phoneme embeddings.
            encoder_dim: Dimension of the encoder output.
            encoder_conv_layers: Number of convolutional layers in the encoder.
            encoder_conv_kernel_size: Kernel size for the encoder convolutional layers.
            encoder_conv_dropout: Dropout rate for the encoder convolutional layers.
            encoder_lstm_layers: Number of LSTM layers in the encoder.
            encoder_lstm_dropout: Dropout rate for the encoder LSTM layers.
            decoder_dim: Dimension of the decoder hidden state.
            decoder_prenet_dim: Dimensions of the decoder prenet layers.
            decoder_lstm_layers: Number of LSTM layers in the decoder.
            decoder_lstm_dropout: Dropout rate for the decoder LSTM layers.
            decoder_zoneout: Zoneout rate for the decoder LSTM layers.
            attention_dim: Dimension of the attention space.
            attention_location_features_dim: Dimension of the location features.
            attention_location_kernel_size: Kernel size for the location features convolution.
            postnet_dim: Dimension of the postnet.
            postnet_kernel_size: Kernel size for the postnet.
            postnet_layers: Number of postnet layers.
            postnet_dropout: Dropout rate for the postnet.
            n_mels: Number of mel bands.
            stop_threshold: Threshold for stop token prediction.
        """
        # Initialize base class
        super().__init__(phoneme_dict=phoneme_dict)
        
        # Set model name
        self.model_name = "tacotron2"
        
        # Set number of phonemes
        if n_phonemes is not None:
            self.n_phonemes = n_phonemes
        
        # Set number of mel bands
        self.n_mels = n_mels
        
        # Set stop threshold
        self.stop_threshold = stop_threshold
        
        # Create encoder
        self.encoder = TextEncoder(
            n_phonemes=self.n_phonemes,
            embedding_dim=embedding_dim,
            encoder_dim=encoder_dim,
            conv_layers=encoder_conv_layers,
            conv_kernel_size=encoder_conv_kernel_size,
            conv_dropout=encoder_conv_dropout,
            lstm_layers=encoder_lstm_layers,
            lstm_dropout=encoder_lstm_dropout,
        )
        
        # Create decoder
        self.decoder = MelDecoder(
            encoder_dim=encoder_dim,
            decoder_dim=decoder_dim,
            prenet_dim=decoder_prenet_dim,
            n_mels=n_mels,
            attention_dim=attention_dim,
            attention_location_features_dim=attention_location_features_dim,
            attention_location_kernel_size=attention_location_kernel_size,
            lstm_layers=decoder_lstm_layers,
            lstm_dropout=decoder_lstm_dropout,
            zoneout=decoder_zoneout,
            postnet_dim=postnet_dim,
            postnet_kernel_size=postnet_kernel_size,
            postnet_layers=postnet_layers,
            postnet_dropout=postnet_dropout,
        )
    
    def forward(
        self,
        phonemes: torch.Tensor,
        phoneme_lengths: torch.Tensor,
        mels: Optional[torch.Tensor] = None,
        mel_lengths: Optional[torch.Tensor] = None,
        max_length: Optional[int] = None,
    ) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
        """
        Forward pass of the Tacotron2 model.
        
        Args:
            phonemes: Tensor of phoneme indices [batch_size, max_phoneme_length].
            phoneme_lengths: Tensor of phoneme sequence lengths [batch_size].
            mels: Tensor of target mel spectrograms [batch_size, n_mels, max_mel_length].
                Required for training, optional for inference.
            mel_lengths: Tensor of mel spectrogram lengths [batch_size].
                Required for training, optional for inference.
            max_length: Maximum length of generated mel spectrograms.
                Only used during inference.
                
        Returns:
            Tuple containing:
                - Predicted mel spectrograms [batch_size, n_mels, max_mel_length].
                - Dictionary of additional outputs (e.g., alignments, stop tokens).
        """
        # Encode phonemes
        encoder_outputs, encoder_output_lengths = self.encoder(phonemes, phoneme_lengths)
        
        # Decode mel spectrograms
        mel_outputs, mel_outputs_postnet, stop_outputs, decoder_outputs = self.decoder(
            encoder_outputs=encoder_outputs,
            encoder_output_lengths=encoder_output_lengths,
            mels=mels,
            mel_lengths=mel_lengths,
            max_length=max_length,
        )
        
        # Prepare outputs
        outputs = {
            "mel_outputs": mel_outputs,
            "mel_outputs_postnet": mel_outputs_postnet,
            "stop_outputs": stop_outputs,
            "alignments": decoder_outputs["alignments"],
        }
        
        return mel_outputs_postnet, outputs
    
    def inference(
        self,
        phonemes: torch.Tensor,
        max_length: Optional[int] = None,
    ) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
        """
        Generate mel spectrograms from phonemes (inference mode).
        
        Args:
            phonemes: Tensor of phoneme indices [batch_size, max_phoneme_length].
            max_length: Maximum length of generated mel spectrograms.
                
        Returns:
            Tuple containing:
                - Predicted mel spectrograms [batch_size, n_mels, max_mel_length].
                - Dictionary of additional outputs (e.g., alignments, stop tokens).
        """
        # Set model to evaluation mode
        self.eval()
        
        # Compute phoneme lengths
        phoneme_lengths = torch.sum(phonemes != self.pad_id, dim=1)
        
        # Forward pass
        mel_outputs_postnet, outputs = self.forward(
            phonemes=phonemes,
            phoneme_lengths=phoneme_lengths,
            max_length=max_length,
        )
        
        # Apply stop token threshold
        if "stop_outputs" in outputs:
            stop_outputs = outputs["stop_outputs"]
            stop_indices = torch.argmax((stop_outputs > self.stop_threshold).float(), dim=1)
            
            # Trim mel spectrograms based on stop tokens
            for i in range(mel_outputs_postnet.size(0)):
                if stop_indices[i] > 0:
                    mel_outputs_postnet[i, :, stop_indices[i]:] = 0.0
        
        return mel_outputs_postnet, outputs
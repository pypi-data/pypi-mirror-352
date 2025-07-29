"""
Custom layers for Kalakan TTS models.

This module provides custom neural network layers used in Kalakan TTS models.
"""

from typing import Dict, List, Optional, Tuple, Union

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np


class LinearNorm(nn.Module):
    """
    Linear layer with weight normalization.
    
    This layer applies weight normalization to a linear layer,
    which can improve training stability and convergence.
    """
    
    def __init__(
        self,
        in_features: int,
        out_features: int,
        bias: bool = True,
        w_init_gain: str = 'linear',
    ):
        """
        Initialize the weight-normalized linear layer.
        
        Args:
            in_features: Size of each input sample.
            out_features: Size of each output sample.
            bias: If set to False, the layer will not learn an additive bias.
            w_init_gain: Gain for weight initialization (linear, relu, tanh, etc.).
        """
        super().__init__()
        
        self.linear = nn.Linear(in_features, out_features, bias=bias)
        
        # Initialize weights
        nn.init.xavier_uniform_(
            self.linear.weight,
            gain=nn.init.calculate_gain(w_init_gain)
        )
        
        if bias:
            nn.init.constant_(self.linear.bias, 0.0)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of the weight-normalized linear layer.
        
        Args:
            x: Input tensor [batch_size, ..., in_features].
                
        Returns:
            Output tensor [batch_size, ..., out_features].
        """
        return self.linear(x)


class ConvBlock(nn.Module):
    """
    Convolutional block with batch normalization and dropout.
    
    This block consists of a 1D convolutional layer followed by
    batch normalization, ReLU activation, and dropout.
    """
    
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int = 5,
        stride: int = 1,
        padding: Optional[int] = None,
        dilation: int = 1,
        bias: bool = True,
        dropout: float = 0.5,
        activation: str = 'relu',
    ):
        """
        Initialize the convolutional block.
        
        Args:
            in_channels: Number of input channels.
            out_channels: Number of output channels.
            kernel_size: Size of the convolving kernel.
            stride: Stride of the convolution.
            padding: Padding added to both sides of the input.
                If None, padding is (kernel_size - 1) // 2.
            dilation: Spacing between kernel elements.
            bias: If True, adds a learnable bias to the output.
            dropout: Dropout probability.
            activation: Activation function (relu, tanh, etc.).
        """
        super().__init__()
        
        # Set padding if not provided
        if padding is None:
            padding = (kernel_size - 1) // 2
        
        # Create convolutional layer
        self.conv = nn.Conv1d(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            stride=stride,
            padding=padding,
            dilation=dilation,
            bias=bias,
        )
        
        # Create batch normalization layer
        self.batch_norm = nn.BatchNorm1d(out_channels)
        
        # Set activation function
        if activation == 'relu':
            self.activation = nn.ReLU()
        elif activation == 'tanh':
            self.activation = nn.Tanh()
        elif activation == 'sigmoid':
            self.activation = nn.Sigmoid()
        else:
            raise ValueError(f"Unsupported activation: {activation}")
        
        # Create dropout layer
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of the convolutional block.
        
        Args:
            x: Input tensor [batch_size, in_channels, time].
                
        Returns:
            Output tensor [batch_size, out_channels, time].
        """
        x = self.conv(x)
        x = self.batch_norm(x)
        x = self.activation(x)
        x = self.dropout(x)
        return x


class ResidualBlock(nn.Module):
    """
    Residual block for FastSpeech2.
    
    This block consists of two convolutional layers with a residual connection.
    """
    
    def __init__(
        self,
        channels: int,
        kernel_size: int = 3,
        dropout: float = 0.1,
    ):
        """
        Initialize the residual block.
        
        Args:
            channels: Number of channels.
            kernel_size: Size of the convolving kernel.
            dropout: Dropout probability.
        """
        super().__init__()
        
        # Create convolutional layers
        self.conv1 = nn.Conv1d(
            in_channels=channels,
            out_channels=channels,
            kernel_size=kernel_size,
            padding=(kernel_size - 1) // 2,
        )
        self.conv2 = nn.Conv1d(
            in_channels=channels,
            out_channels=channels,
            kernel_size=kernel_size,
            padding=(kernel_size - 1) // 2,
        )
        
        # Create batch normalization layers
        self.batch_norm1 = nn.BatchNorm1d(channels)
        self.batch_norm2 = nn.BatchNorm1d(channels)
        
        # Create dropout layer
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of the residual block.
        
        Args:
            x: Input tensor [batch_size, channels, time].
                
        Returns:
            Output tensor [batch_size, channels, time].
        """
        residual = x
        
        # First convolutional layer
        x = self.conv1(x)
        x = self.batch_norm1(x)
        x = F.relu(x)
        x = self.dropout(x)
        
        # Second convolutional layer
        x = self.conv2(x)
        x = self.batch_norm2(x)
        
        # Residual connection
        x = x + residual
        
        # Apply ReLU
        x = F.relu(x)
        
        return x


class VariancePredictor(nn.Module):
    """
    Variance predictor for FastSpeech2.
    
    This module predicts variance information (duration, pitch, energy)
    from encoder outputs.
    """
    
    def __init__(
        self,
        input_dim: int,
        filter_size: int = 256,
        kernel_size: int = 3,
        dropout: float = 0.5,
    ):
        """
        Initialize the variance predictor.
        
        Args:
            input_dim: Dimension of the input.
            filter_size: Size of the convolutional filter.
            kernel_size: Size of the convolving kernel.
            dropout: Dropout probability.
        """
        super().__init__()
        
        # Create convolutional layers
        self.conv1 = nn.Conv1d(
            in_channels=input_dim,
            out_channels=filter_size,
            kernel_size=kernel_size,
            padding=(kernel_size - 1) // 2,
        )
        self.conv2 = nn.Conv1d(
            in_channels=filter_size,
            out_channels=filter_size,
            kernel_size=kernel_size,
            padding=(kernel_size - 1) // 2,
        )
        
        # Create batch normalization layers
        self.batch_norm1 = nn.BatchNorm1d(filter_size)
        self.batch_norm2 = nn.BatchNorm1d(filter_size)
        
        # Create dropout layer
        self.dropout = nn.Dropout(dropout)
        
        # Create projection layer
        self.proj = nn.Linear(filter_size, 1)
    
    def forward(
        self,
        x: torch.Tensor,
        mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Forward pass of the variance predictor.
        
        Args:
            x: Input tensor [batch_size, time, input_dim].
            mask: Mask tensor [batch_size, time].
                
        Returns:
            Output tensor [batch_size, time, 1].
        """
        # Transpose for 1D convolution
        x = x.transpose(1, 2)
        
        # First convolutional layer
        x = self.conv1(x)
        x = self.batch_norm1(x)
        x = F.relu(x)
        x = self.dropout(x)
        
        # Second convolutional layer
        x = self.conv2(x)
        x = self.batch_norm2(x)
        x = F.relu(x)
        x = self.dropout(x)
        
        # Transpose back
        x = x.transpose(1, 2)
        
        # Project to output
        x = self.proj(x)
        
        # Apply mask if provided
        if mask is not None:
            x = x.masked_fill(mask.unsqueeze(-1), 0.0)
        
        return x


class VarianceAdaptor(nn.Module):
    """
    Variance adaptor for FastSpeech2.
    
    This module adapts the encoder output based on predicted
    variance features (duration, pitch, energy).
    """
    
    def __init__(
        self,
        encoder_dim: int = 256,
        filter_size: int = 256,
        kernel_size: int = 3,
        dropout: float = 0.5,
        n_bins: int = 256,
        pitch_feature_level: str = "phoneme_level",
        energy_feature_level: str = "phoneme_level",
        pitch_quantization: str = "linear",
        energy_quantization: str = "linear",
    ):
        """
        Initialize the variance adaptor.
        
        Args:
            encoder_dim: Dimension of the encoder output.
            filter_size: Size of the convolutional filter.
            kernel_size: Size of the convolutional kernel.
            dropout: Dropout rate.
            n_bins: Number of bins for quantization.
            pitch_feature_level: Level of pitch features ("phoneme_level" or "frame_level").
            energy_feature_level: Level of energy features ("phoneme_level" or "frame_level").
            pitch_quantization: Type of pitch quantization ("linear" or "log").
            energy_quantization: Type of energy quantization ("linear" or "log").
        """
        super().__init__()
        
        self.duration_predictor = VariancePredictor(
            input_dim=encoder_dim,
            filter_size=filter_size,
            kernel_size=kernel_size,
            dropout=dropout,
        )
        
        self.pitch_predictor = VariancePredictor(
            input_dim=encoder_dim,
            filter_size=filter_size,
            kernel_size=kernel_size,
            dropout=dropout,
        )
        
        self.energy_predictor = VariancePredictor(
            input_dim=encoder_dim,
            filter_size=filter_size,
            kernel_size=kernel_size,
            dropout=dropout,
        )
        
        self.pitch_feature_level = pitch_feature_level
        self.energy_feature_level = energy_feature_level
        
        # Initialize pitch and energy bins
        self.pitch_bins = nn.Parameter(
            torch.linspace(0, 1, n_bins - 1),
            requires_grad=False,
        )
        self.energy_bins = nn.Parameter(
            torch.linspace(0, 1, n_bins - 1),
            requires_grad=False,
        )
        
        # Initialize pitch and energy embeddings
        self.pitch_embedding = nn.Embedding(n_bins, encoder_dim)
        self.energy_embedding = nn.Embedding(n_bins, encoder_dim)
        
        # Initialize length regulator
        self.length_regulator = LengthRegulator()
    
    def forward(
        self,
        x: torch.Tensor,
        src_mask: torch.Tensor,
        src_lengths: torch.Tensor,
        max_length: Optional[int] = None,
        durations: Optional[torch.Tensor] = None,
        pitch: Optional[torch.Tensor] = None,
        energy: Optional[torch.Tensor] = None,
        p_control: float = 1.0,
        e_control: float = 1.0,
        d_control: float = 1.0,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Forward pass of the variance adaptor.
        
        Args:
            x: Input tensor [batch_size, max_phoneme_length, encoder_dim].
            src_mask: Source mask tensor [batch_size, max_phoneme_length].
            src_lengths: Source lengths [batch_size].
            max_length: Maximum length of the output sequence.
            durations: Ground truth durations for training [batch_size, max_phoneme_length].
            pitch: Ground truth pitch for training [batch_size, max_phoneme_length or max_mel_length].
            energy: Ground truth energy for training [batch_size, max_phoneme_length or max_mel_length].
            p_control: Pitch control factor.
            e_control: Energy control factor.
            d_control: Duration control factor.
                
        Returns:
            Tuple containing:
                - Adapted tensor [batch_size, max_mel_length, encoder_dim].
                - Duration predictions [batch_size, max_phoneme_length].
                - Pitch predictions [batch_size, max_phoneme_length or max_mel_length].
                - Energy predictions [batch_size, max_phoneme_length or max_mel_length].
                - Output lengths [batch_size].
                - Output mask [batch_size, max_mel_length].
        """
        # Predict durations
        log_duration_predictions = self.duration_predictor(x, src_mask)
        duration_predictions = torch.exp(log_duration_predictions) - 1
        
        # Apply duration control
        duration_predictions = duration_predictions * d_control
        
        # Use ground truth durations during training
        if durations is not None:
            durations_rounded = torch.round(durations * d_control).long()
        else:
            durations_rounded = torch.round(duration_predictions).long()
        
        # Apply length regulator
        x_expanded, mel_lengths = self.length_regulator(x, durations_rounded, max_length)
        
        # Create mel mask
        mel_mask = self._get_mask_from_lengths(mel_lengths)
        
        # Predict and process pitch
        pitch_predictions = self.pitch_predictor(x, src_mask)
        
        # Apply pitch control
        pitch_predictions = pitch_predictions * p_control
        
        # Use ground truth pitch during training
        if pitch is not None:
            pitch_embeddings = self._add_pitch_embedding(
                x_expanded, pitch, mel_mask if self.pitch_feature_level == "frame_level" else src_mask
            )
        else:
            pitch_embeddings = self._add_pitch_embedding(
                x_expanded, pitch_predictions, mel_mask if self.pitch_feature_level == "frame_level" else src_mask
            )
        
        # Predict and process energy
        energy_predictions = self.energy_predictor(x, src_mask)
        
        # Apply energy control
        energy_predictions = energy_predictions * e_control
        
        # Use ground truth energy during training
        if energy is not None:
            energy_embeddings = self._add_energy_embedding(
                pitch_embeddings, energy, mel_mask if self.energy_feature_level == "frame_level" else src_mask
            )
        else:
            energy_embeddings = self._add_energy_embedding(
                pitch_embeddings, energy_predictions, mel_mask if self.energy_feature_level == "frame_level" else src_mask
            )
        
        return (
            energy_embeddings,
            duration_predictions,
            pitch_predictions,
            energy_predictions,
            mel_lengths,
            mel_mask,
        )
    
    def _add_pitch_embedding(
        self,
        x: torch.Tensor,
        pitch: torch.Tensor,
        mask: torch.Tensor,
    ) -> torch.Tensor:
        """
        Add pitch embedding to the input tensor.
        
        Args:
            x: Input tensor [batch_size, max_length, encoder_dim].
            pitch: Pitch tensor [batch_size, max_length, 1].
            mask: Mask tensor [batch_size, max_length].
                
        Returns:
            Tensor with pitch embedding added [batch_size, max_length, encoder_dim].
        """
        # Normalize pitch to [0, 1]
        pitch_min, pitch_max = 0.0, 1.0
        pitch_normalized = (pitch - pitch_min) / (pitch_max - pitch_min)
        
        # Quantize pitch
        pitch_buckets = torch.bucketize(pitch_normalized, self.pitch_bins)
        
        # Apply mask
        pitch_buckets = pitch_buckets.masked_fill(mask.unsqueeze(-1), 0)
        
        # Get pitch embeddings
        pitch_embeddings = self.pitch_embedding(pitch_buckets.squeeze(-1))
        
        # Add pitch embeddings to input
        return x + pitch_embeddings
    
    def _add_energy_embedding(
        self,
        x: torch.Tensor,
        energy: torch.Tensor,
        mask: torch.Tensor,
    ) -> torch.Tensor:
        """
        Add energy embedding to the input tensor.
        
        Args:
            x: Input tensor [batch_size, max_length, encoder_dim].
            energy: Energy tensor [batch_size, max_length, 1].
            mask: Mask tensor [batch_size, max_length].
                
        Returns:
            Tensor with energy embedding added [batch_size, max_length, encoder_dim].
        """
        # Normalize energy to [0, 1]
        energy_min, energy_max = 0.0, 1.0
        energy_normalized = (energy - energy_min) / (energy_max - energy_min)
        
        # Quantize energy
        energy_buckets = torch.bucketize(energy_normalized, self.energy_bins)
        
        # Apply mask
        energy_buckets = energy_buckets.masked_fill(mask.unsqueeze(-1), 0)
        
        # Get energy embeddings
        energy_embeddings = self.energy_embedding(energy_buckets.squeeze(-1))
        
        # Add energy embeddings to input
        return x + energy_embeddings
    
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
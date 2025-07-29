"""
Encoder architectures for Kalakan TTS models.

This module provides various encoder architectures used in Kalakan TTS models,
including the text encoder for Tacotron2.
"""

from typing import List, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

from kalakan.models.components.layers import ConvBlock, LinearNorm


class TextEncoder(nn.Module):
    """
    Text encoder for Tacotron2.
    
    This encoder converts phoneme embeddings to hidden representations
    using a stack of convolutional layers followed by a bidirectional LSTM.
    """
    
    def __init__(
        self,
        n_phonemes: int,
        embedding_dim: int = 512,
        encoder_dim: int = 512,
        conv_layers: int = 3,
        conv_kernel_size: int = 5,
        conv_dropout: float = 0.5,
        lstm_layers: int = 1,
        lstm_dropout: float = 0.1,
    ):
        """
        Initialize the text encoder.
        
        Args:
            n_phonemes: Number of phonemes in the vocabulary.
            embedding_dim: Dimension of the phoneme embeddings.
            encoder_dim: Dimension of the encoder output.
            conv_layers: Number of convolutional layers.
            conv_kernel_size: Kernel size for the convolutional layers.
            conv_dropout: Dropout rate for the convolutional layers.
            lstm_layers: Number of LSTM layers.
            lstm_dropout: Dropout rate for the LSTM layers.
        """
        super().__init__()
        
        # Dimensions
        self.n_phonemes = n_phonemes
        self.embedding_dim = embedding_dim
        self.encoder_dim = encoder_dim
        
        # Phoneme embedding
        self.embedding = nn.Embedding(n_phonemes, embedding_dim, padding_idx=0)
        
        # Convolutional layers
        self.convs = nn.ModuleList()
        for i in range(conv_layers):
            in_channels = embedding_dim if i == 0 else encoder_dim
            self.convs.append(
                ConvBlock(
                    in_channels=in_channels,
                    out_channels=encoder_dim,
                    kernel_size=conv_kernel_size,
                    dropout=conv_dropout,
                )
            )
        
        # Bidirectional LSTM
        self.lstm = nn.LSTM(
            input_size=encoder_dim,
            hidden_size=encoder_dim // 2,
            num_layers=lstm_layers,
            batch_first=True,
            bidirectional=True,
            dropout=lstm_dropout if lstm_layers > 1 else 0.0,
        )
    
    def forward(
        self,
        phonemes: torch.Tensor,
        phoneme_lengths: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass of the text encoder.
        
        Args:
            phonemes: Phoneme indices [batch_size, max_phoneme_length].
            phoneme_lengths: Phoneme sequence lengths [batch_size].
                
        Returns:
            Tuple containing:
                - Encoder outputs [batch_size, max_phoneme_length, encoder_dim].
                - Encoder output lengths [batch_size].
        """
        # Embed phonemes
        # [batch_size, max_phoneme_length, embedding_dim]
        x = self.embedding(phonemes)
        
        # Apply convolutional layers
        # [batch_size, max_phoneme_length, encoder_dim]
        for conv in self.convs:
            x = conv(x.transpose(1, 2)).transpose(1, 2)
        
        # Pack sequence for LSTM
        x_packed = nn.utils.rnn.pack_padded_sequence(
            x, phoneme_lengths.cpu(), batch_first=True, enforce_sorted=False
        )
        
        # Apply LSTM
        # [batch_size, max_phoneme_length, encoder_dim]
        outputs_packed, _ = self.lstm(x_packed)
        outputs, _ = nn.utils.rnn.pad_packed_sequence(outputs_packed, batch_first=True)
        
        return outputs, phoneme_lengths


class TransformerEncoder(nn.Module):
    """
    Transformer encoder for FastSpeech2.
    
    This encoder converts phoneme embeddings to hidden representations
    using a stack of Transformer encoder layers.
    """
    
    def __init__(
        self,
        n_phonemes: int,
        embedding_dim: int = 512,
        encoder_dim: int = 512,
        n_heads: int = 8,
        n_layers: int = 4,
        conv_filter_size: int = 1024,
        conv_kernel_size: List[int] = [9, 1],
        encoder_dropout: float = 0.1,
        max_seq_len: int = 2048,
    ):
        """
        Initialize the transformer encoder.
        
        Args:
            n_phonemes: Number of phonemes in the vocabulary.
            embedding_dim: Dimension of the phoneme embeddings.
            encoder_dim: Dimension of the encoder output.
            n_heads: Number of attention heads.
            n_layers: Number of transformer layers.
            conv_filter_size: Size of the convolutional filter.
            conv_kernel_size: Kernel sizes for the convolutional layers.
            encoder_dropout: Dropout rate for the encoder.
            max_seq_len: Maximum sequence length.
        """
        super().__init__()
        
        # Dimensions
        self.n_phonemes = n_phonemes
        self.embedding_dim = embedding_dim
        self.encoder_dim = encoder_dim
        
        # Phoneme embedding
        self.embedding = nn.Embedding(n_phonemes, embedding_dim, padding_idx=0)
        
        # Positional encoding
        self.positional_encoding = nn.Parameter(
            self._get_sinusoid_encoding_table(max_seq_len, embedding_dim),
            requires_grad=False,
        )
        
        # Transformer layers
        self.layers = nn.ModuleList()
        for _ in range(n_layers):
            self.layers.append(
                TransformerEncoderLayer(
                    encoder_dim=encoder_dim,
                    n_heads=n_heads,
                    conv_filter_size=conv_filter_size,
                    conv_kernel_size=conv_kernel_size,
                    dropout=encoder_dropout,
                )
            )
    
    def forward(
        self,
        phonemes: torch.Tensor,
        phoneme_lengths: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass of the transformer encoder.
        
        Args:
            phonemes: Phoneme indices [batch_size, max_phoneme_length].
            phoneme_lengths: Phoneme sequence lengths [batch_size].
                
        Returns:
            Tuple containing:
                - Encoder outputs [batch_size, max_phoneme_length, encoder_dim].
                - Encoder output lengths [batch_size].
        """
        # Create mask
        # [batch_size, max_phoneme_length]
        mask = self._get_mask_from_lengths(phoneme_lengths, phonemes.size(1))
        
        # Embed phonemes
        # [batch_size, max_phoneme_length, embedding_dim]
        x = self.embedding(phonemes)
        
        # Add positional encoding
        # [batch_size, max_phoneme_length, embedding_dim]
        x = x + self.positional_encoding[:phonemes.size(1), :].unsqueeze(0)
        
        # Apply transformer layers
        # [batch_size, max_phoneme_length, encoder_dim]
        for layer in self.layers:
            x = layer(x, mask)
        
        return x, phoneme_lengths
    
    def _get_mask_from_lengths(
        self,
        lengths: torch.Tensor,
        max_len: int,
    ) -> torch.Tensor:
        """
        Create mask from sequence lengths.
        
        Args:
            lengths: Sequence lengths [batch_size].
            max_len: Maximum sequence length.
                
        Returns:
            Mask tensor [batch_size, max_len].
        """
        batch_size = lengths.size(0)
        mask = torch.arange(0, max_len).to(lengths.device).expand(batch_size, max_len) >= lengths.unsqueeze(1)
        return mask
    
    def _get_sinusoid_encoding_table(
        self,
        max_seq_len: int,
        embedding_dim: int,
    ) -> torch.Tensor:
        """
        Create sinusoidal positional encoding table.
        
        Args:
            max_seq_len: Maximum sequence length.
            embedding_dim: Dimension of the embeddings.
                
        Returns:
            Positional encoding table [max_seq_len, embedding_dim].
        """
        # Create position indices
        position = torch.arange(0, max_seq_len, dtype=torch.float).unsqueeze(1)
        
        # Create dimension indices
        div_term = torch.exp(
            torch.arange(0, embedding_dim, 2).float() * (-torch.log(torch.tensor(10000.0)) / embedding_dim)
        )
        
        # Create positional encoding table
        pos_table = torch.zeros(max_seq_len, embedding_dim)
        pos_table[:, 0::2] = torch.sin(position * div_term)
        pos_table[:, 1::2] = torch.cos(position * div_term)
        
        return pos_table


class TransformerEncoderLayer(nn.Module):
    """
    Transformer encoder layer for FastSpeech2.
    
    This layer consists of a multi-head self-attention module and a
    position-wise feed-forward network.
    """
    
    def __init__(
        self,
        encoder_dim: int,
        n_heads: int,
        conv_filter_size: int,
        conv_kernel_size: List[int],
        dropout: float,
    ):
        """
        Initialize the transformer encoder layer.
        
        Args:
            encoder_dim: Dimension of the encoder.
            n_heads: Number of attention heads.
            conv_filter_size: Size of the convolutional filter.
            conv_kernel_size: Kernel sizes for the convolutional layers.
            dropout: Dropout rate.
        """
        super().__init__()
        
        # Multi-head self-attention
        self.self_attn = nn.MultiheadAttention(
            embed_dim=encoder_dim,
            num_heads=n_heads,
            dropout=dropout,
            batch_first=True,
        )
        
        # Position-wise feed-forward network
        self.conv1 = nn.Conv1d(
            in_channels=encoder_dim,
            out_channels=conv_filter_size,
            kernel_size=conv_kernel_size[0],
            padding=(conv_kernel_size[0] - 1) // 2,
        )
        self.conv2 = nn.Conv1d(
            in_channels=conv_filter_size,
            out_channels=encoder_dim,
            kernel_size=conv_kernel_size[1],
            padding=(conv_kernel_size[1] - 1) // 2,
        )
        
        # Layer normalization
        self.norm1 = nn.LayerNorm(encoder_dim)
        self.norm2 = nn.LayerNorm(encoder_dim)
        
        # Dropout
        self.dropout = nn.Dropout(dropout)
    
    def forward(
        self,
        x: torch.Tensor,
        mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Forward pass of the transformer encoder layer.
        
        Args:
            x: Input tensor [batch_size, max_seq_len, encoder_dim].
            mask: Mask tensor [batch_size, max_seq_len].
                
        Returns:
            Output tensor [batch_size, max_seq_len, encoder_dim].
        """
        # Self-attention
        # [batch_size, max_seq_len, encoder_dim]
        attn_mask = mask.unsqueeze(1).expand(-1, mask.size(1), -1) if mask is not None else None
        attn_output, _ = self.self_attn(x, x, x, key_padding_mask=mask)
        
        # Residual connection and layer normalization
        # [batch_size, max_seq_len, encoder_dim]
        x = self.norm1(x + self.dropout(attn_output))
        
        # Position-wise feed-forward network
        # [batch_size, encoder_dim, max_seq_len]
        ff_output = self.conv1(x.transpose(1, 2))
        ff_output = F.relu(ff_output)
        ff_output = self.conv2(ff_output).transpose(1, 2)
        
        # Residual connection and layer normalization
        # [batch_size, max_seq_len, encoder_dim]
        x = self.norm2(x + self.dropout(ff_output))
        
        return x
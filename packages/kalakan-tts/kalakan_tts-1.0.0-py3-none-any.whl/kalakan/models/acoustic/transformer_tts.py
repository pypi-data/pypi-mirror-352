"""
Transformer-TTS model for Kalakan TTS.

This module implements the Transformer-TTS model for text-to-mel conversion,
as described in "Neural Speech Synthesis with Transformer Network"
(Li et al., 2019), with adaptations for the Twi language.
"""

from typing import Dict, List, Optional, Tuple, Union

import torch
import torch.nn as nn
import torch.nn.functional as F

from kalakan.models.acoustic.base_acoustic import BaseAcousticModel
from kalakan.models.components.layers import LinearNorm
from kalakan.text.phonemes import TwiPhonemes


class TransformerTTS(BaseAcousticModel):
    """
    Transformer-TTS model for Kalakan TTS.
    
    This model converts phoneme sequences to mel spectrograms using
    a transformer-based encoder-decoder architecture with attention.
    """
    
    def __init__(
        self,
        n_phonemes: Optional[int] = None,
        phoneme_dict: Optional[Dict[str, int]] = None,
        embedding_dim: int = 512,
        encoder_layers: int = 6,
        encoder_heads: int = 8,
        encoder_dim: int = 512,
        encoder_conv_filter_size: int = 2048,
        encoder_conv_kernel_size: int = 9,
        encoder_dropout: float = 0.1,
        decoder_layers: int = 6,
        decoder_heads: int = 8,
        decoder_dim: int = 512,
        decoder_conv_filter_size: int = 2048,
        decoder_conv_kernel_size: int = 9,
        decoder_dropout: float = 0.1,
        n_mels: int = 80,
        max_seq_len: int = 1000,
        stop_threshold: float = 0.5,
    ):
        """
        Initialize the Transformer-TTS model.
        
        Args:
            n_phonemes: Number of phonemes in the vocabulary.
                If None, the number of phonemes is determined from phoneme_dict.
            phoneme_dict: Dictionary mapping phonemes to indices.
                If None, the default Twi phoneme dictionary is used.
            embedding_dim: Dimension of the phoneme embeddings.
            encoder_layers: Number of transformer layers in the encoder.
            encoder_heads: Number of attention heads in the encoder.
            encoder_dim: Dimension of the encoder.
            encoder_conv_filter_size: Size of the convolutional filter in the encoder.
            encoder_conv_kernel_size: Kernel size for the encoder convolutional layers.
            encoder_dropout: Dropout rate for the encoder.
            decoder_layers: Number of transformer layers in the decoder.
            decoder_heads: Number of attention heads in the decoder.
            decoder_dim: Dimension of the decoder.
            decoder_conv_filter_size: Size of the convolutional filter in the decoder.
            decoder_conv_kernel_size: Kernel size for the decoder convolutional layers.
            decoder_dropout: Dropout rate for the decoder.
            n_mels: Number of mel bands.
            max_seq_len: Maximum sequence length.
            stop_threshold: Threshold for stop token prediction.
        """
        # Initialize base class
        super().__init__(phoneme_dict=phoneme_dict)
        
        # Set model name
        self.model_name = "transformer_tts"
        
        # Set number of phonemes
        if n_phonemes is not None:
            self.n_phonemes = n_phonemes
        
        # Set number of mel bands
        self.n_mels = n_mels
        
        # Set maximum sequence length
        self.max_seq_len = max_seq_len
        
        # Set stop threshold
        self.stop_threshold = stop_threshold
        
        # Create phoneme embedding
        self.phoneme_embedding = nn.Embedding(
            self.n_phonemes, embedding_dim, padding_idx=self.pad_id
        )
        
        # Create positional encoding
        self.positional_encoding = PositionalEncoding(
            embedding_dim, max_seq_len=max_seq_len
        )
        
        # Create encoder
        self.encoder = TransformerEncoder(
            embedding_dim=embedding_dim,
            num_layers=encoder_layers,
            num_heads=encoder_heads,
            hidden_dim=encoder_dim,
            conv_filter_size=encoder_conv_filter_size,
            conv_kernel_size=encoder_conv_kernel_size,
            dropout=encoder_dropout,
        )
        
        # Create decoder
        self.decoder = TransformerDecoder(
            embedding_dim=embedding_dim,
            num_layers=decoder_layers,
            num_heads=decoder_heads,
            hidden_dim=decoder_dim,
            conv_filter_size=decoder_conv_filter_size,
            conv_kernel_size=decoder_conv_kernel_size,
            dropout=decoder_dropout,
        )
        
        # Create mel linear layer
        self.mel_linear = LinearNorm(
            decoder_dim, n_mels, bias=True, w_init_gain='linear'
        )
        
        # Create stop token layer
        self.stop_linear = LinearNorm(
            decoder_dim, 1, bias=True, w_init_gain='sigmoid'
        )
        
        # Create prenet
        self.prenet = Prenet(
            n_mels, [256, 256], dropout=0.5
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
        Forward pass of the Transformer-TTS model.
        
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
        # Get batch size
        batch_size = phonemes.size(0)
        
        # Create masks
        src_mask = self._get_mask_from_lengths(phoneme_lengths)
        
        # Embed phonemes
        x = self.phoneme_embedding(phonemes)
        
        # Add positional encoding
        x = self.positional_encoding(x)
        
        # Encode
        encoder_outputs = self.encoder(x, src_mask)
        
        # Check if we're in training or inference mode
        if mels is not None:
            # Training mode
            
            # Create target mask
            tgt_mask = self._get_mask_from_lengths(mel_lengths)
            
            # Prepare decoder inputs (shift mel spectrograms)
            decoder_inputs = mels.transpose(1, 2)[:, :-1, :]  # [batch_size, max_mel_length-1, n_mels]
            
            # Add zero frame at the beginning
            zero_frame = torch.zeros(batch_size, 1, self.n_mels).to(decoder_inputs.device)
            decoder_inputs = torch.cat([zero_frame, decoder_inputs], dim=1)  # [batch_size, max_mel_length, n_mels]
            
            # Apply prenet
            decoder_inputs = self.prenet(decoder_inputs)
            
            # Add positional encoding
            decoder_inputs = self.positional_encoding(decoder_inputs)
            
            # Decode
            decoder_outputs, attention_weights = self.decoder(
                decoder_inputs, encoder_outputs, src_mask, tgt_mask
            )
            
            # Generate mel spectrograms
            mel_outputs = self.mel_linear(decoder_outputs)
            
            # Generate stop tokens
            stop_outputs = self.stop_linear(decoder_outputs).squeeze(-1)
            
            # Transpose mel outputs to match expected shape [batch_size, n_mels, max_mel_length]
            mel_outputs = mel_outputs.transpose(1, 2)
            
            # Prepare outputs
            outputs = {
                "mel_outputs": mel_outputs,
                "stop_outputs": stop_outputs,
                "attention_weights": attention_weights,
            }
            
            return mel_outputs, outputs
        else:
            # Inference mode
            
            # Set maximum length if not specified
            if max_length is None:
                max_length = self.max_seq_len
            
            # Initialize decoder inputs with zero frame
            decoder_inputs = torch.zeros(batch_size, 1, self.n_mels).to(phonemes.device)
            
            # Initialize output tensors
            mel_outputs = []
            stop_outputs = []
            attention_weights_list = []
            
            # Generate mel frames auto-regressively
            for i in range(max_length):
                # Apply prenet
                decoder_inputs_processed = self.prenet(decoder_inputs)
                
                # Add positional encoding
                decoder_inputs_processed = self.positional_encoding(decoder_inputs_processed)
                
                # Create target mask (all False for inference)
                tgt_mask = torch.zeros(batch_size, decoder_inputs_processed.size(1)).bool().to(phonemes.device)
                
                # Decode
                decoder_outputs, attention_weights = self.decoder(
                    decoder_inputs_processed, encoder_outputs, src_mask, tgt_mask
                )
                
                # Generate mel frame
                mel_output = self.mel_linear(decoder_outputs[:, -1:, :])
                
                # Generate stop token
                stop_output = self.stop_linear(decoder_outputs[:, -1:, :]).squeeze(-1)
                
                # Append to outputs
                mel_outputs.append(mel_output)
                stop_outputs.append(stop_output)
                attention_weights_list.append(attention_weights[:, :, -1:, :])
                
                # Update decoder inputs
                decoder_inputs = torch.cat([decoder_inputs, mel_output.transpose(1, 2)], dim=1)
                
                # Check if we should stop
                if torch.sigmoid(stop_output).item() > self.stop_threshold:
                    break
            
            # Concatenate outputs
            mel_outputs = torch.cat(mel_outputs, dim=1).transpose(1, 2)  # [batch_size, n_mels, max_mel_length]
            stop_outputs = torch.cat(stop_outputs, dim=1)  # [batch_size, max_mel_length]
            attention_weights = torch.cat(attention_weights_list, dim=2)  # [batch_size, n_layers, max_mel_length, max_phoneme_length]
            
            # Prepare outputs
            outputs = {
                "mel_outputs": mel_outputs,
                "stop_outputs": stop_outputs,
                "attention_weights": attention_weights,
            }
            
            return mel_outputs, outputs
    
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
        mel_outputs, outputs = self.forward(
            phonemes=phonemes,
            phoneme_lengths=phoneme_lengths,
            max_length=max_length,
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


class PositionalEncoding(nn.Module):
    """
    Positional encoding for transformer models.
    
    This module adds positional information to the input embeddings.
    """
    
    def __init__(
        self,
        d_model: int,
        max_seq_len: int = 1000,
        dropout: float = 0.1,
    ):
        """
        Initialize the positional encoding.
        
        Args:
            d_model: Dimension of the model.
            max_seq_len: Maximum sequence length.
            dropout: Dropout rate.
        """
        super().__init__()
        
        self.dropout = nn.Dropout(p=dropout)
        
        # Create positional encoding
        pe = torch.zeros(max_seq_len, d_model)
        position = torch.arange(0, max_seq_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-torch.log(torch.tensor(10000.0)) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        
        self.register_buffer('pe', pe.unsqueeze(0))
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of the positional encoding.
        
        Args:
            x: Input tensor [batch_size, seq_len, d_model].
                
        Returns:
            Output tensor with positional encoding added [batch_size, seq_len, d_model].
        """
        x = x + self.pe[:, :x.size(1), :]
        return self.dropout(x)


class Prenet(nn.Module):
    """
    Prenet for Transformer-TTS.
    
    This module processes the mel spectrogram inputs before feeding them to the decoder.
    """
    
    def __init__(
        self,
        in_dim: int,
        sizes: List[int],
        dropout: float = 0.5,
    ):
        """
        Initialize the prenet.
        
        Args:
            in_dim: Input dimension.
            sizes: List of hidden layer sizes.
            dropout: Dropout rate.
        """
        super().__init__()
        
        # Create layers
        self.layers = nn.ModuleList()
        
        # Input layer
        self.layers.append(
            nn.Sequential(
                LinearNorm(in_dim, sizes[0], bias=False),
                nn.ReLU(),
                nn.Dropout(dropout)
            )
        )
        
        # Hidden layers
        for i in range(len(sizes) - 1):
            self.layers.append(
                nn.Sequential(
                    LinearNorm(sizes[i], sizes[i+1], bias=False),
                    nn.ReLU(),
                    nn.Dropout(dropout)
                )
            )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of the prenet.
        
        Args:
            x: Input tensor [batch_size, seq_len, in_dim].
                
        Returns:
            Output tensor [batch_size, seq_len, sizes[-1]].
        """
        for layer in self.layers:
            x = layer(x)
        return x


class TransformerEncoder(nn.Module):
    """
    Transformer encoder for Transformer-TTS.
    
    This module encodes the phoneme sequence using a transformer architecture.
    """
    
    def __init__(
        self,
        embedding_dim: int,
        num_layers: int,
        num_heads: int,
        hidden_dim: int,
        conv_filter_size: int,
        conv_kernel_size: int,
        dropout: float,
    ):
        """
        Initialize the transformer encoder.
        
        Args:
            embedding_dim: Dimension of the input embeddings.
            num_layers: Number of transformer layers.
            num_heads: Number of attention heads.
            hidden_dim: Dimension of the hidden layers.
            conv_filter_size: Size of the convolutional filter.
            conv_kernel_size: Size of the convolutional kernel.
            dropout: Dropout rate.
        """
        super().__init__()
        
        # Create transformer encoder layers
        self.layers = nn.ModuleList([
            TransformerEncoderLayer(
                embedding_dim=embedding_dim,
                num_heads=num_heads,
                hidden_dim=hidden_dim,
                conv_filter_size=conv_filter_size,
                conv_kernel_size=conv_kernel_size,
                dropout=dropout,
            )
            for _ in range(num_layers)
        ])
        
        # Create layer normalization
        self.layer_norm = nn.LayerNorm(embedding_dim)
    
    def forward(
        self,
        x: torch.Tensor,
        mask: torch.Tensor,
    ) -> torch.Tensor:
        """
        Forward pass of the transformer encoder.
        
        Args:
            x: Input tensor [batch_size, max_phoneme_length, embedding_dim].
            mask: Mask tensor [batch_size, max_phoneme_length].
                
        Returns:
            Output tensor [batch_size, max_phoneme_length, embedding_dim].
        """
        # Apply transformer encoder layers
        for layer in self.layers:
            x = layer(x, mask)
        
        # Apply layer normalization
        x = self.layer_norm(x)
        
        return x


class TransformerEncoderLayer(nn.Module):
    """
    Transformer encoder layer for Transformer-TTS.
    
    This module implements a single layer of the transformer encoder.
    """
    
    def __init__(
        self,
        embedding_dim: int,
        num_heads: int,
        hidden_dim: int,
        conv_filter_size: int,
        conv_kernel_size: int,
        dropout: float,
    ):
        """
        Initialize the transformer encoder layer.
        
        Args:
            embedding_dim: Dimension of the input embeddings.
            num_heads: Number of attention heads.
            hidden_dim: Dimension of the hidden layers.
            conv_filter_size: Size of the convolutional filter.
            conv_kernel_size: Size of the convolutional kernel.
            dropout: Dropout rate.
        """
        super().__init__()
        
        # Create multi-head attention
        self.self_attention = nn.MultiheadAttention(
            embed_dim=embedding_dim,
            num_heads=num_heads,
            dropout=dropout,
            batch_first=True,
        )
        
        # Create feed-forward network
        self.feed_forward = nn.Sequential(
            nn.Linear(embedding_dim, conv_filter_size),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(conv_filter_size, embedding_dim),
            nn.Dropout(dropout),
        )
        
        # Create layer normalization
        self.norm1 = nn.LayerNorm(embedding_dim)
        self.norm2 = nn.LayerNorm(embedding_dim)
        
        # Create dropout
        self.dropout = nn.Dropout(dropout)
    
    def forward(
        self,
        x: torch.Tensor,
        mask: torch.Tensor,
    ) -> torch.Tensor:
        """
        Forward pass of the transformer encoder layer.
        
        Args:
            x: Input tensor [batch_size, max_phoneme_length, embedding_dim].
            mask: Mask tensor [batch_size, max_phoneme_length].
                
        Returns:
            Output tensor [batch_size, max_phoneme_length, embedding_dim].
        """
        # Apply self-attention
        residual = x
        x = self.norm1(x)
        x, _ = self.self_attention(
            query=x,
            key=x,
            value=x,
            key_padding_mask=mask,
        )
        x = self.dropout(x)
        x = residual + x
        
        # Apply feed-forward network
        residual = x
        x = self.norm2(x)
        x = self.feed_forward(x)
        x = residual + x
        
        return x


class TransformerDecoder(nn.Module):
    """
    Transformer decoder for Transformer-TTS.
    
    This module decodes the encoder outputs to generate mel spectrograms.
    """
    
    def __init__(
        self,
        embedding_dim: int,
        num_layers: int,
        num_heads: int,
        hidden_dim: int,
        conv_filter_size: int,
        conv_kernel_size: int,
        dropout: float,
    ):
        """
        Initialize the transformer decoder.
        
        Args:
            embedding_dim: Dimension of the input embeddings.
            num_layers: Number of transformer layers.
            num_heads: Number of attention heads.
            hidden_dim: Dimension of the hidden layers.
            conv_filter_size: Size of the convolutional filter.
            conv_kernel_size: Size of the convolutional kernel.
            dropout: Dropout rate.
        """
        super().__init__()
        
        # Create transformer decoder layers
        self.layers = nn.ModuleList([
            TransformerDecoderLayer(
                embedding_dim=embedding_dim,
                num_heads=num_heads,
                hidden_dim=hidden_dim,
                conv_filter_size=conv_filter_size,
                conv_kernel_size=conv_kernel_size,
                dropout=dropout,
            )
            for _ in range(num_layers)
        ])
        
        # Create layer normalization
        self.layer_norm = nn.LayerNorm(embedding_dim)
    
    def forward(
        self,
        x: torch.Tensor,
        memory: torch.Tensor,
        memory_mask: torch.Tensor,
        tgt_mask: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass of the transformer decoder.
        
        Args:
            x: Input tensor [batch_size, max_mel_length, embedding_dim].
            memory: Encoder outputs [batch_size, max_phoneme_length, embedding_dim].
            memory_mask: Encoder mask [batch_size, max_phoneme_length].
            tgt_mask: Target mask [batch_size, max_mel_length].
                
        Returns:
            Tuple containing:
                - Output tensor [batch_size, max_mel_length, embedding_dim].
                - Attention weights [batch_size, num_layers, max_mel_length, max_phoneme_length].
        """
        # Initialize attention weights
        attention_weights = []
        
        # Apply transformer decoder layers
        for layer in self.layers:
            x, attn = layer(x, memory, memory_mask, tgt_mask)
            attention_weights.append(attn)
        
        # Apply layer normalization
        x = self.layer_norm(x)
        
        # Stack attention weights
        attention_weights = torch.stack(attention_weights, dim=1)
        
        return x, attention_weights


class TransformerDecoderLayer(nn.Module):
    """
    Transformer decoder layer for Transformer-TTS.
    
    This module implements a single layer of the transformer decoder.
    """
    
    def __init__(
        self,
        embedding_dim: int,
        num_heads: int,
        hidden_dim: int,
        conv_filter_size: int,
        conv_kernel_size: int,
        dropout: float,
    ):
        """
        Initialize the transformer decoder layer.
        
        Args:
            embedding_dim: Dimension of the input embeddings.
            num_heads: Number of attention heads.
            hidden_dim: Dimension of the hidden layers.
            conv_filter_size: Size of the convolutional filter.
            conv_kernel_size: Size of the convolutional kernel.
            dropout: Dropout rate.
        """
        super().__init__()
        
        # Create multi-head attention
        self.self_attention = nn.MultiheadAttention(
            embed_dim=embedding_dim,
            num_heads=num_heads,
            dropout=dropout,
            batch_first=True,
        )
        
        self.cross_attention = nn.MultiheadAttention(
            embed_dim=embedding_dim,
            num_heads=num_heads,
            dropout=dropout,
            batch_first=True,
        )
        
        # Create feed-forward network
        self.feed_forward = nn.Sequential(
            nn.Linear(embedding_dim, conv_filter_size),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(conv_filter_size, embedding_dim),
            nn.Dropout(dropout),
        )
        
        # Create layer normalization
        self.norm1 = nn.LayerNorm(embedding_dim)
        self.norm2 = nn.LayerNorm(embedding_dim)
        self.norm3 = nn.LayerNorm(embedding_dim)
        
        # Create dropout
        self.dropout = nn.Dropout(dropout)
    
    def forward(
        self,
        x: torch.Tensor,
        memory: torch.Tensor,
        memory_mask: torch.Tensor,
        tgt_mask: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass of the transformer decoder layer.
        
        Args:
            x: Input tensor [batch_size, max_mel_length, embedding_dim].
            memory: Encoder outputs [batch_size, max_phoneme_length, embedding_dim].
            memory_mask: Encoder mask [batch_size, max_phoneme_length].
            tgt_mask: Target mask [batch_size, max_mel_length].
                
        Returns:
            Tuple containing:
                - Output tensor [batch_size, max_mel_length, embedding_dim].
                - Attention weights [batch_size, max_mel_length, max_phoneme_length].
        """
        # Apply self-attention
        residual = x
        x = self.norm1(x)
        x, _ = self.self_attention(
            query=x,
            key=x,
            value=x,
            key_padding_mask=tgt_mask,
        )
        x = self.dropout(x)
        x = residual + x
        
        # Apply cross-attention
        residual = x
        x = self.norm2(x)
        x, attn_weights = self.cross_attention(
            query=x,
            key=memory,
            value=memory,
            key_padding_mask=memory_mask,
        )
        x = self.dropout(x)
        x = residual + x
        
        # Apply feed-forward network
        residual = x
        x = self.norm3(x)
        x = self.feed_forward(x)
        x = residual + x
        
        return x, attn_weights
"""
Decoder architectures for Kalakan TTS models.

This module provides various decoder architectures used in Kalakan TTS models,
including the mel decoder for Tacotron2.
"""

from typing import Dict, List, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

from kalakan.models.components.attention import LocationSensitiveAttention
from kalakan.models.components.layers import ConvBlock, LinearNorm


class MelDecoder(nn.Module):
    """
    Mel decoder for Tacotron2.
    
    This decoder generates mel spectrograms from encoder outputs using
    an attention mechanism and a stack of LSTM layers.
    """
    
    def __init__(
        self,
        encoder_dim: int,
        decoder_dim: int = 1024,
        prenet_dim: List[int] = [256, 256],
        n_mels: int = 80,
        attention_dim: int = 128,
        attention_location_features_dim: int = 32,
        attention_location_kernel_size: int = 31,
        lstm_layers: int = 2,
        lstm_dropout: float = 0.1,
        zoneout: float = 0.1,
        postnet_dim: int = 512,
        postnet_kernel_size: int = 5,
        postnet_layers: int = 5,
        postnet_dropout: float = 0.5,
    ):
        """
        Initialize the mel decoder.
        
        Args:
            encoder_dim: Dimension of the encoder outputs.
            decoder_dim: Dimension of the decoder hidden state.
            prenet_dim: Dimensions of the prenet layers.
            n_mels: Number of mel bands.
            attention_dim: Dimension of the attention space.
            attention_location_features_dim: Dimension of the location features.
            attention_location_kernel_size: Kernel size for the location features convolution.
            lstm_layers: Number of LSTM layers.
            lstm_dropout: Dropout rate for the LSTM layers.
            zoneout: Zoneout rate for the LSTM layers.
            postnet_dim: Dimension of the postnet.
            postnet_kernel_size: Kernel size for the postnet.
            postnet_layers: Number of postnet layers.
            postnet_dropout: Dropout rate for the postnet.
        """
        super().__init__()
        
        # Dimensions
        self.encoder_dim = encoder_dim
        self.decoder_dim = decoder_dim
        self.prenet_dim = prenet_dim
        self.n_mels = n_mels
        
        # Prenet
        self.prenet = Prenet(n_mels, prenet_dim)
        
        # Attention
        self.attention = LocationSensitiveAttention(
            query_dim=decoder_dim,
            key_dim=encoder_dim,
            attention_dim=attention_dim,
            location_features_dim=attention_location_features_dim,
            location_kernel_size=attention_location_kernel_size,
        )
        
        # Decoder LSTM
        # The first LSTM layer takes the prenet output (prenet_dim[-1]) and context vector (encoder_dim)
        self.lstm_input_dim = prenet_dim[-1] + encoder_dim
        self.lstm = nn.ModuleList()
        for i in range(lstm_layers):
            input_size = self.lstm_input_dim if i == 0 else decoder_dim
            lstm_layer = nn.LSTMCell(
                input_size=input_size,
                hidden_size=decoder_dim,
            )
            self.lstm.append(ZoneoutLSTMCell(lstm_layer, zoneout))
        
        # Projection layers
        self.mel_proj = LinearNorm(decoder_dim + encoder_dim, n_mels)
        self.stop_proj = LinearNorm(decoder_dim + encoder_dim, 1)
        
        # Postnet
        self.postnet = Postnet(
            n_mels=n_mels,
            postnet_dim=postnet_dim,
            kernel_size=postnet_kernel_size,
            n_layers=postnet_layers,
            dropout=postnet_dropout,
        )
    
    def forward(
        self,
        encoder_outputs: torch.Tensor,
        encoder_output_lengths: torch.Tensor,
        mels: Optional[torch.Tensor] = None,
        mel_lengths: Optional[torch.Tensor] = None,
        max_length: Optional[int] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, Dict[str, torch.Tensor]]:
        """
        Forward pass of the mel decoder.
        
        Args:
            encoder_outputs: Encoder outputs [batch_size, max_encoder_length, encoder_dim].
            encoder_output_lengths: Encoder output lengths [batch_size].
            mels: Target mel spectrograms [batch_size, n_mels, max_mel_length].
                Required for training, optional for inference.
            mel_lengths: Mel spectrogram lengths [batch_size].
                Required for training, optional for inference.
            max_length: Maximum length of generated mel spectrograms.
                Only used during inference.
                
        Returns:
            Tuple containing:
                - Predicted mel spectrograms before postnet [batch_size, n_mels, max_mel_length].
                - Predicted mel spectrograms after postnet [batch_size, n_mels, max_mel_length].
                - Stop tokens [batch_size, max_mel_length].
                - Dictionary of additional outputs (e.g., alignments).
        """
        # Determine batch size and device
        batch_size = encoder_outputs.size(0)
        device = encoder_outputs.device
        
        # Determine maximum length
        if mels is not None:
            max_mel_length = mels.size(2)
        else:
            if max_length is None:
                max_mel_length = encoder_outputs.size(1) * 10  # Heuristic
            else:
                max_mel_length = max_length
        
        # Initialize decoder states
        decoder_states = self._init_decoder_states(batch_size, device)
        
        # Initialize outputs
        mel_outputs = []
        stop_outputs = []
        alignments = []
        
        # Initialize attention weights
        attention_weights = torch.zeros(
            batch_size, encoder_outputs.size(1), device=device
        )
        
        # Create attention mask
        attention_mask = self._get_mask_from_lengths(
            encoder_output_lengths, encoder_outputs.size(1)
        )
        
        # Initialize decoder input
        decoder_input = torch.zeros(batch_size, self.n_mels, device=device)
        
        # Teacher forcing (training) or autoregressive (inference)
        for t in range(max_mel_length):
            # Get decoder input for current time step
            if mels is not None and t < mels.size(2):
                # Teacher forcing
                decoder_input = mels[:, :, t]
            
            # Run decoder for one step
            mel_output, stop_output, attention_weights, decoder_states = self._decoder_step(
                decoder_input, encoder_outputs, attention_weights, attention_mask, decoder_states
            )
            
            # Store outputs
            mel_outputs.append(mel_output)
            stop_outputs.append(stop_output)
            alignments.append(attention_weights)
            
            # Update decoder input for next time step
            decoder_input = mel_output
        
        # Stack outputs
        mel_outputs = torch.stack(mel_outputs, dim=2)  # [batch_size, n_mels, max_mel_length]
        stop_outputs = torch.stack(stop_outputs, dim=1)  # [batch_size, max_mel_length]
        alignments = torch.stack(alignments, dim=1)  # [batch_size, max_mel_length, max_encoder_length]
        
        # Apply postnet
        mel_outputs_postnet = self.postnet(mel_outputs) + mel_outputs
        
        # Return outputs
        outputs = {
            "alignments": alignments,
        }
        
        return mel_outputs, mel_outputs_postnet, stop_outputs, outputs
    
    def _decoder_step(
        self,
        decoder_input: torch.Tensor,
        encoder_outputs: torch.Tensor,
        prev_attention_weights: torch.Tensor,
        attention_mask: torch.Tensor,
        decoder_states: Dict[str, torch.Tensor],
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, Dict[str, torch.Tensor]]:
        """
        Run the decoder for one step.
        
        Args:
            decoder_input: Decoder input for current time step [batch_size, n_mels].
            encoder_outputs: Encoder outputs [batch_size, max_encoder_length, encoder_dim].
            prev_attention_weights: Previous attention weights [batch_size, max_encoder_length].
            attention_mask: Attention mask [batch_size, max_encoder_length].
            decoder_states: Dictionary of decoder states.
                
        Returns:
            Tuple containing:
                - Mel output for current time step [batch_size, n_mels].
                - Stop token for current time step [batch_size, 1].
                - Attention weights for current time step [batch_size, max_encoder_length].
                - Updated decoder states.
        """
        # Apply prenet
        prenet_output = self.prenet(decoder_input)
        
        # Apply attention to get context vector
        context, attention_weights = self.attention(
            query=decoder_states["hidden_0"],  # Use the first hidden state as query
            keys=encoder_outputs,
            values=encoder_outputs,
            prev_attention_weights=prev_attention_weights,
            mask=attention_mask,
        )
        
        # Store context in decoder states for next step
        decoder_states["context"] = context
        
        # Initialize LSTM inputs - first layer takes prenet output concatenated with context
        lstm_input = torch.cat([prenet_output, context], dim=1)
        
        # Run LSTM layers
        for i, lstm_layer in enumerate(self.lstm):
            # Get hidden state and cell state
            hidden_state = decoder_states[f"hidden_{i}"]
            cell_state = decoder_states[f"cell_{i}"]
            
            # Run LSTM cell
            hidden_state, cell_state = lstm_layer(lstm_input, (hidden_state, cell_state))
            
            # Update decoder states
            decoder_states[f"hidden_{i}"] = hidden_state
            decoder_states[f"cell_{i}"] = cell_state
            
            # Update LSTM input for next layer - subsequent layers take only the hidden state
            lstm_input = hidden_state
        
        # Get decoder output from the last LSTM layer
        decoder_output = hidden_state
        
        # Concatenate decoder output and context
        concat_output = torch.cat([decoder_output, context], dim=1)
        
        # Project to mel output and stop token
        mel_output = self.mel_proj(concat_output)
        stop_output = self.stop_proj(concat_output)
        
        return mel_output, stop_output, attention_weights, decoder_states
    
    def _init_decoder_states(
        self,
        batch_size: int,
        device: torch.device,
    ) -> Dict[str, torch.Tensor]:
        """
        Initialize decoder states.
        
        Args:
            batch_size: Batch size.
            device: Device to create tensors on.
                
        Returns:
            Dictionary of decoder states.
        """
        decoder_states = {}
        
        # Initialize hidden and cell states for each LSTM layer
        for i in range(len(self.lstm)):
            decoder_states[f"hidden_{i}"] = torch.zeros(batch_size, self.decoder_dim, device=device)
            decoder_states[f"cell_{i}"] = torch.zeros(batch_size, self.decoder_dim, device=device)
            
        # Initialize context vector (needed for the first decoder step)
        decoder_states["context"] = torch.zeros(batch_size, self.encoder_dim, device=device)
        
        return decoder_states
    
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
        mask = torch.arange(0, max_len).to(lengths.device).expand(batch_size, max_len) < lengths.unsqueeze(1)
        return mask


class Prenet(nn.Module):
    """
    Prenet for Tacotron2.
    
    This module consists of a stack of fully-connected layers with ReLU activations
    and dropout, used to process the previous mel frame before feeding it to the decoder.
    """
    
    def __init__(
        self,
        input_dim: int,
        layer_dims: List[int],
        dropout: float = 0.5,
    ):
        """
        Initialize the prenet.
        
        Args:
            input_dim: Dimension of the input.
            layer_dims: Dimensions of the prenet layers.
            dropout: Dropout rate.
        """
        super().__init__()
        
        # Create layers
        self.layers = nn.ModuleList()
        in_dim = input_dim
        for layer_dim in layer_dims:
            self.layers.append(
                nn.Sequential(
                    LinearNorm(in_dim, layer_dim),
                    nn.ReLU(),
                    nn.Dropout(dropout),
                )
            )
            in_dim = layer_dim
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of the prenet.
        
        Args:
            x: Input tensor [batch_size, input_dim].
                
        Returns:
            Output tensor [batch_size, layer_dims[-1]].
        """
        for layer in self.layers:
            x = layer(x)
        return x


class Postnet(nn.Module):
    """
    Postnet for Tacotron2.
    
    This module consists of a stack of 1D convolutional layers with tanh activations
    and dropout, used to refine the mel spectrogram generated by the decoder.
    """
    
    def __init__(
        self,
        n_mels: int,
        postnet_dim: int = 512,
        kernel_size: int = 5,
        n_layers: int = 5,
        dropout: float = 0.5,
    ):
        """
        Initialize the postnet.
        
        Args:
            n_mels: Number of mel bands.
            postnet_dim: Dimension of the postnet.
            kernel_size: Kernel size for the convolutional layers.
            n_layers: Number of convolutional layers.
            dropout: Dropout rate.
        """
        super().__init__()
        
        # Create layers
        self.layers = nn.ModuleList()
        
        # First layer
        self.layers.append(
            nn.Sequential(
                nn.Conv1d(
                    in_channels=n_mels,
                    out_channels=postnet_dim,
                    kernel_size=kernel_size,
                    padding=(kernel_size - 1) // 2,
                ),
                nn.BatchNorm1d(postnet_dim),
                nn.Tanh(),
                nn.Dropout(dropout),
            )
        )
        
        # Hidden layers
        for i in range(1, n_layers - 1):
            self.layers.append(
                nn.Sequential(
                    nn.Conv1d(
                        in_channels=postnet_dim,
                        out_channels=postnet_dim,
                        kernel_size=kernel_size,
                        padding=(kernel_size - 1) // 2,
                    ),
                    nn.BatchNorm1d(postnet_dim),
                    nn.Tanh(),
                    nn.Dropout(dropout),
                )
            )
        
        # Last layer
        self.layers.append(
            nn.Sequential(
                nn.Conv1d(
                    in_channels=postnet_dim,
                    out_channels=n_mels,
                    kernel_size=kernel_size,
                    padding=(kernel_size - 1) // 2,
                ),
                nn.BatchNorm1d(n_mels),
                nn.Dropout(dropout),
            )
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of the postnet.
        
        Args:
            x: Input tensor [batch_size, n_mels, time].
                
        Returns:
            Output tensor [batch_size, n_mels, time].
        """
        for layer in self.layers:
            x = layer(x)
        return x


class ZoneoutLSTMCell(nn.Module):
    """
    LSTM cell with zoneout regularization.
    
    This module implements zoneout regularization for LSTM cells,
    as described in "Zoneout: Regularizing RNNs by Randomly Preserving Hidden Activations"
    (Krueger et al., 2016).
    """
    
    def __init__(
        self,
        lstm_cell: nn.LSTMCell,
        zoneout_prob: float = 0.1,
    ):
        """
        Initialize the zoneout LSTM cell.
        
        Args:
            lstm_cell: LSTM cell to apply zoneout to.
            zoneout_prob: Probability of applying zoneout.
        """
        super().__init__()
        
        self.lstm_cell = lstm_cell
        self.zoneout_prob = zoneout_prob
        self.hidden_size = lstm_cell.hidden_size
    
    def forward(
        self,
        x: torch.Tensor,
        states: Tuple[torch.Tensor, torch.Tensor],
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass of the zoneout LSTM cell.
        
        Args:
            x: Input tensor [batch_size, input_size].
            states: Tuple of (hidden_state, cell_state).
                
        Returns:
            Tuple of (new_hidden_state, new_cell_state).
        """
        # Unpack states
        h_prev, c_prev = states
        
        # Run LSTM cell
        h, c = self.lstm_cell(x, states)
        
        # Apply zoneout
        if self.training:
            # Create binary mask
            mask_h = torch.bernoulli(
                torch.ones_like(h) * (1 - self.zoneout_prob)
            ).to(h.device)
            mask_c = torch.bernoulli(
                torch.ones_like(c) * (1 - self.zoneout_prob)
            ).to(c.device)
            
            # Apply mask
            h = mask_h * h + (1 - mask_h) * h_prev
            c = mask_c * c + (1 - mask_c) * c_prev
        
        return h, c
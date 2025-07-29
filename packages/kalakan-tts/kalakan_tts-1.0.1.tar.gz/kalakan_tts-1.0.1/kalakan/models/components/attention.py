"""
Attention mechanisms for Kalakan TTS models.

This module provides various attention mechanisms used in Kalakan TTS models,
including location-sensitive attention for Tacotron2.
"""

from typing import Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F


class LocationSensitiveAttention(nn.Module):
    """
    Location-sensitive attention for Tacotron2.
    
    This attention mechanism extends the additive attention by considering
    the attention weights from the previous time step, as described in
    "Attention-Based Models for Speech Recognition" (Chorowski et al., 2015).
    """
    
    def __init__(
        self,
        query_dim: int,
        key_dim: int,
        attention_dim: int = 128,
        location_features_dim: int = 32,
        location_kernel_size: int = 31,
        attention_temperature: float = 1.0,
    ):
        """
        Initialize the location-sensitive attention.
        
        Args:
            query_dim: Dimension of the query vectors.
            key_dim: Dimension of the key vectors.
            attention_dim: Dimension of the attention space.
            location_features_dim: Dimension of the location features.
            location_kernel_size: Kernel size for the location features convolution.
            attention_temperature: Temperature for the softmax.
        """
        super().__init__()
        
        # Dimensions
        self.query_dim = query_dim
        self.key_dim = key_dim
        self.attention_dim = attention_dim
        self.location_features_dim = location_features_dim
        self.location_kernel_size = location_kernel_size
        self.attention_temperature = attention_temperature
        
        # Query projection
        self.query_proj = nn.Linear(query_dim, attention_dim, bias=False)
        
        # Key projection
        self.key_proj = nn.Linear(key_dim, attention_dim, bias=False)
        
        # Location features
        self.location_conv = nn.Conv1d(
            in_channels=1,
            out_channels=location_features_dim,
            kernel_size=location_kernel_size,
            padding=(location_kernel_size - 1) // 2,
            bias=False,
        )
        self.location_proj = nn.Linear(location_features_dim, attention_dim, bias=False)
        
        # Energy projection
        self.energy_proj = nn.Linear(attention_dim, 1, bias=False)
        
        # Mask value
        self.mask_value = -float("inf")
    
    def forward(
        self,
        query: torch.Tensor,
        keys: torch.Tensor,
        values: torch.Tensor,
        prev_attention_weights: torch.Tensor,
        mask: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass of the location-sensitive attention.
        
        Args:
            query: Query tensor [batch_size, query_dim].
            keys: Key tensor [batch_size, max_time, key_dim].
            values: Value tensor [batch_size, max_time, value_dim].
            prev_attention_weights: Previous attention weights [batch_size, max_time].
            mask: Mask tensor [batch_size, max_time].
                
        Returns:
            Tuple containing:
                - Context vector [batch_size, value_dim].
                - Attention weights [batch_size, max_time].
        """
        # Project query
        # [batch_size, attention_dim]
        query_proj = self.query_proj(query.unsqueeze(1))
        
        # Project keys
        # [batch_size, max_time, attention_dim]
        key_proj = self.key_proj(keys)
        
        # Process location features
        # [batch_size, 1, max_time]
        prev_attention_weights = prev_attention_weights.unsqueeze(1)
        
        # [batch_size, location_features_dim, max_time]
        location_features = self.location_conv(prev_attention_weights)
        
        # [batch_size, max_time, location_features_dim]
        location_features = location_features.transpose(1, 2)
        
        # [batch_size, max_time, attention_dim]
        location_proj = self.location_proj(location_features)
        
        # Compute energy
        # [batch_size, max_time, attention_dim]
        energy = key_proj + query_proj + location_proj
        
        # Apply tanh
        energy = torch.tanh(energy)
        
        # [batch_size, max_time, 1]
        energy = self.energy_proj(energy)
        
        # [batch_size, max_time]
        energy = energy.squeeze(-1)
        
        # Apply mask if provided
        if mask is not None:
            energy = energy.masked_fill(mask == 0, self.mask_value)
        
        # Apply temperature
        energy = energy / self.attention_temperature
        
        # Compute attention weights
        # [batch_size, max_time]
        attention_weights = F.softmax(energy, dim=1)
        
        # Compute context vector
        # [batch_size, value_dim]
        context = torch.bmm(attention_weights.unsqueeze(1), values).squeeze(1)
        
        return context, attention_weights


class ForwardAttention(nn.Module):
    """
    Forward attention for FastSpeech2.
    
    This attention mechanism enforces a monotonic attention by considering
    only the forward direction, as described in "Forward Attention in
    Sequence-to-Sequence Acoustic Modeling for Speech Synthesis" (Zhang et al., 2018).
    """
    
    def __init__(
        self,
        query_dim: int,
        key_dim: int,
        attention_dim: int = 128,
        attention_temperature: float = 1.0,
    ):
        """
        Initialize the forward attention.
        
        Args:
            query_dim: Dimension of the query vectors.
            key_dim: Dimension of the key vectors.
            attention_dim: Dimension of the attention space.
            attention_temperature: Temperature for the softmax.
        """
        super().__init__()
        
        # Dimensions
        self.query_dim = query_dim
        self.key_dim = key_dim
        self.attention_dim = attention_dim
        self.attention_temperature = attention_temperature
        
        # Query projection
        self.query_proj = nn.Linear(query_dim, attention_dim, bias=False)
        
        # Key projection
        self.key_proj = nn.Linear(key_dim, attention_dim, bias=False)
        
        # Energy projection
        self.energy_proj = nn.Linear(attention_dim, 1, bias=False)
        
        # Mask value
        self.mask_value = -float("inf")
    
    def forward(
        self,
        query: torch.Tensor,
        keys: torch.Tensor,
        values: torch.Tensor,
        prev_attention_weights: torch.Tensor,
        mask: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass of the forward attention.
        
        Args:
            query: Query tensor [batch_size, query_dim].
            keys: Key tensor [batch_size, max_time, key_dim].
            values: Value tensor [batch_size, max_time, value_dim].
            prev_attention_weights: Previous attention weights [batch_size, max_time].
            mask: Mask tensor [batch_size, max_time].
                
        Returns:
            Tuple containing:
                - Context vector [batch_size, value_dim].
                - Attention weights [batch_size, max_time].
        """
        # Project query
        # [batch_size, attention_dim]
        query_proj = self.query_proj(query.unsqueeze(1))
        
        # Project keys
        # [batch_size, max_time, attention_dim]
        key_proj = self.key_proj(keys)
        
        # Compute energy
        # [batch_size, max_time, attention_dim]
        energy = key_proj + query_proj
        
        # Apply tanh
        energy = torch.tanh(energy)
        
        # [batch_size, max_time, 1]
        energy = self.energy_proj(energy)
        
        # [batch_size, max_time]
        energy = energy.squeeze(-1)
        
        # Apply mask if provided
        if mask is not None:
            energy = energy.masked_fill(mask == 0, self.mask_value)
        
        # Apply temperature
        energy = energy / self.attention_temperature
        
        # Compute attention weights
        # [batch_size, max_time]
        attention_weights_raw = F.softmax(energy, dim=1)
        
        # Apply forward attention
        # [batch_size, max_time]
        attention_weights = self._apply_forward_attention(attention_weights_raw, prev_attention_weights)
        
        # Compute context vector
        # [batch_size, value_dim]
        context = torch.bmm(attention_weights.unsqueeze(1), values).squeeze(1)
        
        return context, attention_weights
    
    def _apply_forward_attention(
        self,
        attention_weights_raw: torch.Tensor,
        prev_attention_weights: torch.Tensor,
    ) -> torch.Tensor:
        """
        Apply forward attention mechanism.
        
        Args:
            attention_weights_raw: Raw attention weights [batch_size, max_time].
            prev_attention_weights: Previous attention weights [batch_size, max_time].
                
        Returns:
            Forward attention weights [batch_size, max_time].
        """
        # Compute forward attention
        # [batch_size, max_time]
        batch_size, max_time = attention_weights_raw.size()
        
        # Initialize forward attention weights
        forward_attention_weights = torch.zeros_like(attention_weights_raw)
        
        # First time step
        forward_attention_weights[:, 0] = attention_weights_raw[:, 0]
        
        # Remaining time steps
        for t in range(1, max_time):
            # Previous forward attention
            prev_forward = prev_attention_weights[:, t-1:t+1]
            
            # Current raw attention
            current_raw = attention_weights_raw[:, t].unsqueeze(1)
            
            # Compute forward attention
            forward_attention_weights[:, t] = (prev_forward * current_raw).sum(dim=1)
        
        # Normalize
        forward_attention_weights = forward_attention_weights / (forward_attention_weights.sum(dim=1, keepdim=True) + 1e-8)
        
        return forward_attention_weights
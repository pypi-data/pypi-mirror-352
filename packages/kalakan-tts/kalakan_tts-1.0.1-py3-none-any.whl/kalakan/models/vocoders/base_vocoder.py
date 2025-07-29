"""
Base vocoder model for Kalakan TTS.

This module defines the base class for vocoder models (mel-to-audio) in Kalakan TTS.
"""

import os
from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple, Union

import numpy as np
import torch
import torch.nn as nn


class BaseVocoder(nn.Module, ABC):
    """
    Base class for vocoder models in Kalakan TTS.
    
    This abstract class defines the interface for vocoder models (mel-to-audio)
    in Kalakan TTS. All vocoder models should inherit from this class and
    implement its abstract methods.
    """
    
    def __init__(
        self,
        n_mels: int = 80,
        sample_rate: int = 22050,
        hop_length: int = 256,
    ):
        """
        Initialize the base vocoder model.
        
        Args:
            n_mels: Number of mel bands in the input mel spectrogram.
            sample_rate: Audio sample rate.
            hop_length: Hop length between frames.
        """
        super().__init__()
        
        self.n_mels = n_mels
        self.sample_rate = sample_rate
        self.hop_length = hop_length
        
        # Model name
        self.model_name = "base_vocoder"
    
    @abstractmethod
    def forward(self, mels: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of the vocoder model.
        
        Args:
            mels: Mel spectrograms [batch_size, n_mels, time].
                
        Returns:
            Generated audio waveforms [batch_size, time*hop_length].
        """
        pass
    
    @abstractmethod
    def inference(self, mels: torch.Tensor) -> torch.Tensor:
        """
        Generate audio from mel spectrograms (inference mode).
        
        Args:
            mels: Mel spectrograms [batch_size, n_mels, time].
                
        Returns:
            Generated audio waveforms [batch_size, time*hop_length].
        """
        pass
    
    def generate(
        self,
        mels: Union[np.ndarray, torch.Tensor],
        device: Optional[torch.device] = None,
    ) -> torch.Tensor:
        """
        Generate audio from mel spectrograms.
        
        Args:
            mels: Mel spectrograms as numpy array or torch tensor.
            device: Device to use for inference.
                
        Returns:
            Generated audio waveforms [batch_size, time*hop_length].
        """
        # Convert to tensor if needed
        if isinstance(mels, np.ndarray):
            mels = torch.from_numpy(mels).float()
        
        # Add batch dimension if needed
        if mels.dim() == 2:
            mels = mels.unsqueeze(0)
        
        # Move to device if specified
        if device is not None:
            mels = mels.to(device)
        else:
            mels = mels.to(next(self.parameters()).device)
        
        # Generate audio
        with torch.no_grad():
            audio = self.inference(mels)
        
        return audio
    
    def save_checkpoint(self, checkpoint_path: str, optimizer: Optional[torch.optim.Optimizer] = None) -> None:
        """
        Save model checkpoint.
        
        Args:
            checkpoint_path: Path to save the checkpoint.
            optimizer: Optimizer to save. If None, only the model is saved.
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(checkpoint_path)), exist_ok=True)
        
        # Prepare checkpoint
        checkpoint = {
            "model_state_dict": self.state_dict(),
            "model_name": self.model_name,
            "n_mels": self.n_mels,
            "sample_rate": self.sample_rate,
            "hop_length": self.hop_length,
        }
        
        # Add optimizer if provided
        if optimizer is not None:
            checkpoint["optimizer_state_dict"] = optimizer.state_dict()
        
        # Save checkpoint
        torch.save(checkpoint, checkpoint_path)
    
    @classmethod
    def load_checkpoint(
        cls,
        checkpoint_path: str,
        device: Optional[torch.device] = None,
        optimizer: Optional[torch.optim.Optimizer] = None,
    ) -> Tuple["BaseVocoder", Optional[torch.optim.Optimizer]]:
        """
        Load model checkpoint.
        
        Args:
            checkpoint_path: Path to the checkpoint.
            device: Device to load the model on.
            optimizer: Optimizer to load state into. If None, optimizer state is not loaded.
            
        Returns:
            Tuple containing:
                - Loaded model.
                - Loaded optimizer (if provided, otherwise None).
        """
        # Set device
        if device is None:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load checkpoint
        checkpoint = torch.load(checkpoint_path, map_location=device)
        
        # Check model name
        model_name = checkpoint.get("model_name", cls.__name__)
        if model_name != cls.__name__:
            print(f"Warning: Checkpoint is for model {model_name}, but loading into {cls.__name__}")
        
        # Create model instance
        model = cls(
            n_mels=checkpoint.get("n_mels", 80),
            sample_rate=checkpoint.get("sample_rate", 22050),
            hop_length=checkpoint.get("hop_length", 256),
        )
        
        # Load model state
        model.load_state_dict(checkpoint["model_state_dict"])
        model.to(device)
        
        # Load optimizer state if provided
        if optimizer is not None and "optimizer_state_dict" in checkpoint:
            optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        
        return model, optimizer
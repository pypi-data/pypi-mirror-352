"""
Base acoustic model for Kalakan TTS.

This module defines the base class for acoustic models (text-to-mel) in Kalakan TTS.
"""

import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import torch
import torch.nn as nn

from kalakan.text.phonemes import TwiPhonemes


class BaseAcousticModel(nn.Module, ABC):
    """
    Base class for acoustic models in Kalakan TTS.
    
    This abstract class defines the interface for acoustic models (text-to-mel)
    in Kalakan TTS. All acoustic models should inherit from this class and
    implement its abstract methods.
    """
    
    def __init__(self, phoneme_dict: Optional[Dict[str, int]] = None):
        """
        Initialize the base acoustic model.
        
        Args:
            phoneme_dict: Dictionary mapping phonemes to indices.
                If None, the default Twi phoneme dictionary is used.
        """
        super().__init__()
        
        # Set phoneme dictionary
        self.phoneme_dict = phoneme_dict if phoneme_dict is not None else TwiPhonemes.SYMBOL_TO_ID
        self.id_to_phoneme = {v: k for k, v in self.phoneme_dict.items()}
        
        # Number of phonemes
        self.n_phonemes = len(self.phoneme_dict)
        
        # Special token IDs
        self.pad_id = self.phoneme_dict.get(TwiPhonemes.PAD, 0)
        self.eos_id = self.phoneme_dict.get(TwiPhonemes.EOS, 0)
        
        # Model name
        self.model_name = "base_acoustic_model"
    
    @abstractmethod
    def forward(
        self,
        phonemes: torch.Tensor,
        phoneme_lengths: torch.Tensor,
        mels: Optional[torch.Tensor] = None,
        mel_lengths: Optional[torch.Tensor] = None,
        max_length: Optional[int] = None,
    ) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
        """
        Forward pass of the acoustic model.
        
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
        pass
    
    @abstractmethod
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
        pass
    
    def generate(
        self,
        text: Union[str, List[str]],
        max_length: Optional[int] = None,
        device: Optional[torch.device] = None,
    ) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
        """
        Generate mel spectrograms from text.
        
        Args:
            text: Input text or list of texts.
            max_length: Maximum length of generated mel spectrograms.
            device: Device to use for inference.
                
        Returns:
            Tuple containing:
                - Predicted mel spectrograms [batch_size, n_mels, max_mel_length].
                - Dictionary of additional outputs (e.g., alignments, stop tokens).
        """
        # Convert to list if single string
        if isinstance(text, str):
            text = [text]
        
        # Convert text to phoneme sequences
        phoneme_sequences = []
        for t in text:
            # In a real implementation, this would use the G2P converter
            # For now, we'll just use a simple placeholder
            phoneme_sequence = TwiPhonemes.text_to_sequence(t)
            phoneme_sequences.append(phoneme_sequence)
        
        # Pad sequences
        max_length_phonemes = max(len(seq) for seq in phoneme_sequences)
        padded_phonemes = []
        for seq in phoneme_sequences:
            padded_seq = seq + [self.pad_id] * (max_length_phonemes - len(seq))
            padded_phonemes.append(padded_seq)
        
        # Convert to tensor
        phonemes = torch.tensor(padded_phonemes, dtype=torch.long)
        
        # Move to device if specified
        if device is not None:
            phonemes = phonemes.to(device)
        else:
            phonemes = phonemes.to(next(self.parameters()).device)
        
        # Generate mel spectrograms
        with torch.no_grad():
            mels, outputs = self.inference(phonemes, max_length=max_length)
        
        return mels, outputs
    
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
            "phoneme_dict": self.phoneme_dict,
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
    ) -> Tuple["BaseAcousticModel", Optional[torch.optim.Optimizer]]:
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
        model = cls(phoneme_dict=checkpoint.get("phoneme_dict"))
        
        # Load model state
        model.load_state_dict(checkpoint["model_state_dict"])
        model.to(device)
        
        # Load optimizer state if provided
        if optimizer is not None and "optimizer_state_dict" in checkpoint:
            optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        
        return model, optimizer
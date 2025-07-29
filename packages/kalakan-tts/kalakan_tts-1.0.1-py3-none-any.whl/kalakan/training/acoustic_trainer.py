"""
Acoustic model trainer for Kalakan TTS.

This module implements the trainer for acoustic models (text-to-mel)
in Kalakan TTS.
"""

import os
from typing import Any, Dict, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader

from kalakan.models.acoustic.base_acoustic import BaseAcousticModel
from kalakan.training.trainer import Trainer
from kalakan.utils.config import Config


class AcousticTrainer(Trainer):
    """
    Trainer for acoustic models in Kalakan TTS.
    
    This trainer handles the training of acoustic models (text-to-mel)
    in Kalakan TTS.
    """
    
    def __init__(
        self,
        model: BaseAcousticModel,
        train_dataloader: DataLoader,
        val_dataloader: Optional[DataLoader] = None,
        config: Optional[Union[Dict, Config]] = None,
        device: Optional[torch.device] = None,
        output_dir: str = "models",
        experiment_name: Optional[str] = None,
        tensorboard_dir: Optional[str] = None,
    ):
        """
        Initialize the acoustic model trainer.
        
        Args:
            model: Acoustic model to train.
            train_dataloader: DataLoader for training data.
            val_dataloader: DataLoader for validation data.
            config: Training configuration.
            device: Device to use for training.
            output_dir: Directory to save model checkpoints.
            experiment_name: Name of the experiment.
            tensorboard_dir: Directory to save TensorBoard logs.
        """
        super().__init__(
            model=model,
            train_dataloader=train_dataloader,
            val_dataloader=val_dataloader,
            config=config,
            device=device,
            output_dir=output_dir,
            experiment_name=experiment_name,
            tensorboard_dir=tensorboard_dir,
        )
        
        # Set loss weights
        self.mel_loss_weight = self.config.get("training.loss_weights.mel_loss", 1.0)
        self.mel_postnet_loss_weight = self.config.get("training.loss_weights.mel_postnet_loss", 1.0)
        self.stop_loss_weight = self.config.get("training.loss_weights.stop_loss", 0.5)
    
    def _compute_loss(self, batch: Dict[str, torch.Tensor]) -> Tuple[torch.Tensor, Dict[str, Any]]:
        """
        Compute loss for a batch.
        
        Args:
            batch: Batch of data containing:
                - phonemes: Tensor of phoneme indices [batch_size, max_phoneme_length].
                - phoneme_lengths: Tensor of phoneme sequence lengths [batch_size].
                - mels: Tensor of target mel spectrograms [batch_size, n_mels, max_mel_length].
                - mel_lengths: Tensor of mel spectrogram lengths [batch_size].
            
        Returns:
            Tuple containing:
                - Loss tensor.
                - Dictionary of outputs.
        """
        # Extract batch data
        phonemes = batch["phonemes"]
        phoneme_lengths = batch["phoneme_lengths"]
        mels = batch["mels"]
        mel_lengths = batch["mel_lengths"]
        
        # Forward pass
        mel_outputs_postnet, outputs = self.model(
            phonemes=phonemes,
            phoneme_lengths=phoneme_lengths,
            mels=mels,
            mel_lengths=mel_lengths,
        )
        
        # Extract model outputs
        mel_outputs = outputs["mel_outputs"]
        stop_outputs = outputs["stop_outputs"]
        
        # Create target stop tokens
        # [batch_size, max_mel_length]
        stop_targets = torch.zeros_like(stop_outputs)
        for i, length in enumerate(mel_lengths):
            stop_targets[i, length-1:] = 1.0
        
        # Create mel mask
        # [batch_size, max_mel_length]
        mel_mask = self._get_mask_from_lengths(mel_lengths, mel_outputs.size(2))
        
        # Compute masked loss
        mel_loss = F.mse_loss(mel_outputs, mels) * self.mel_loss_weight
        mel_postnet_loss = F.mse_loss(mel_outputs_postnet, mels) * self.mel_postnet_loss_weight
        
        # Compute stop loss
        stop_loss = F.binary_cross_entropy_with_logits(
            stop_outputs, stop_targets, reduction="none"
        )
        stop_loss = (stop_loss * mel_mask).sum() / mel_mask.sum() * self.stop_loss_weight
        
        # Compute total loss
        loss = mel_loss + mel_postnet_loss + stop_loss
        
        # Prepare outputs
        outputs.update({
            "loss": loss.item(),
            "mel_loss": mel_loss.item(),
            "mel_postnet_loss": mel_postnet_loss.item(),
            "stop_loss": stop_loss.item(),
        })
        
        return loss, outputs
    
    def _log_batch(self, batch: Dict[str, torch.Tensor], outputs: Dict[str, Any]) -> None:
        """
        Log batch results.
        
        Args:
            batch: Batch of data.
            outputs: Dictionary of outputs.
        """
        # Log losses
        self.writer.add_scalar("Loss/mel", outputs["mel_loss"], self.global_step)
        self.writer.add_scalar("Loss/mel_postnet", outputs["mel_postnet_loss"], self.global_step)
        self.writer.add_scalar("Loss/stop", outputs["stop_loss"], self.global_step)
        
        # Log alignments
        if "alignments" in outputs and self.global_step % (self.log_interval * 10) == 0:
            alignments = outputs["alignments"][0].detach().cpu().numpy()
            self._log_alignment(alignments, self.global_step)
    
    def _log_validation(self, val_loss: float) -> None:
        """
        Log validation results.
        
        Args:
            val_loss: Validation loss.
        """
        # Log validation loss
        self.writer.add_scalar("Loss/validation", val_loss, self.global_step)
        
        # Generate validation samples
        if self.val_dataloader is not None:
            # Get a batch from the validation set
            batch = next(iter(self.val_dataloader))
            batch = self._move_batch_to_device(batch)
            
            # Extract batch data
            phonemes = batch["phonemes"]
            phoneme_lengths = batch["phoneme_lengths"]
            
            # Generate mel spectrograms
            with torch.no_grad():
                mel_outputs_postnet, outputs = self.model.inference(
                    phonemes=phonemes,
                    max_length=1000,
                )
            
            # Log generated mel spectrograms
            for i in range(min(3, mel_outputs_postnet.size(0))):
                mel = mel_outputs_postnet[i].detach().cpu().numpy()
                self._log_mel_spectrogram(mel, f"validation_{i}", self.global_step)
                
                # Log alignments
                if "alignments" in outputs:
                    alignments = outputs["alignments"][i].detach().cpu().numpy()
                    self._log_alignment(alignments, self.global_step, prefix=f"validation_{i}")
    
    def _log_mel_spectrogram(self, mel: np.ndarray, prefix: str, step: int) -> None:
        """
        Log mel spectrogram to TensorBoard.
        
        Args:
            mel: Mel spectrogram [n_mels, time].
            prefix: Prefix for the image name.
            step: Global step.
        """
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 4))
        im = ax.imshow(mel, aspect="auto", origin="lower", interpolation="none")
        plt.colorbar(im, ax=ax)
        plt.tight_layout()
        
        # Log to TensorBoard
        self.writer.add_figure(f"Mel/{prefix}", fig, step)
        plt.close(fig)
    
    def _log_alignment(self, alignment: np.ndarray, step: int, prefix: str = "train") -> None:
        """
        Log alignment to TensorBoard.
        
        Args:
            alignment: Alignment matrix [time, max_phoneme_length].
            step: Global step.
            prefix: Prefix for the image name.
        """
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 4))
        im = ax.imshow(alignment.T, aspect="auto", origin="lower", interpolation="none")
        plt.colorbar(im, ax=ax)
        plt.tight_layout()
        
        # Log to TensorBoard
        self.writer.add_figure(f"Alignment/{prefix}", fig, step)
        plt.close(fig)
    
    def _get_mask_from_lengths(self, lengths: torch.Tensor, max_len: int) -> torch.Tensor:
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
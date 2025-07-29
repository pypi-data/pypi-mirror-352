"""
Vocoder trainer for Kalakan TTS.

This module implements the trainer for vocoder models (mel-to-audio)
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
import torchaudio

from kalakan.models.vocoders.base_vocoder import BaseVocoder
from kalakan.training.trainer import Trainer
from kalakan.utils.config import Config


class VocoderTrainer(Trainer):
    """
    Trainer for vocoder models in Kalakan TTS.
    
    This trainer handles the training of vocoder models (mel-to-audio)
    in Kalakan TTS.
    """
    
    def __init__(
        self,
        model: BaseVocoder,
        train_dataloader: DataLoader,
        val_dataloader: Optional[DataLoader] = None,
        config: Optional[Union[Dict, Config]] = None,
        device: Optional[torch.device] = None,
        output_dir: str = "models",
        experiment_name: Optional[str] = None,
        tensorboard_dir: Optional[str] = None,
    ):
        """
        Initialize the vocoder trainer.
        
        Args:
            model: Vocoder model to train.
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
        self.mel_loss_weight = self.config.get("training.loss_weights.mel_loss", 45.0)
        self.feature_loss_weight = self.config.get("training.loss_weights.feature_loss", 1.0)
        self.adversarial_loss_weight = self.config.get("training.loss_weights.adversarial_loss", 1.0)
        
        # Set sample rate
        self.sample_rate = self.model.sample_rate
    
    def _compute_loss(self, batch: Dict[str, torch.Tensor]) -> Tuple[torch.Tensor, Dict[str, Any]]:
        """
        Compute loss for a batch.
        
        Args:
            batch: Batch of data containing:
                - mels: Tensor of mel spectrograms [batch_size, n_mels, time].
                - audio: Tensor of audio waveforms [batch_size, time*hop_length].
            
        Returns:
            Tuple containing:
                - Loss tensor.
                - Dictionary of outputs.
        """
        # Extract batch data
        mels = batch["mels"]
        audio = batch["audio"]
        
        # Forward pass
        pred_audio = self.model(mels)
        
        # Compute loss
        if isinstance(self.model, nn.DataParallel):
            hop_length = self.model.module.hop_length
        else:
            hop_length = self.model.hop_length
        
        # Ensure audio and pred_audio have the same length
        min_length = min(audio.size(-1), pred_audio.size(-1))
        audio = audio[..., :min_length]
        pred_audio = pred_audio[..., :min_length]
        
        # Compute waveform loss
        audio_loss = F.l1_loss(pred_audio, audio) * self.mel_loss_weight
        
        # Compute total loss
        loss = audio_loss
        
        # Prepare outputs
        outputs = {
            "pred_audio": pred_audio,
            "loss": loss.item(),
            "audio_loss": audio_loss.item(),
        }
        
        return loss, outputs
    
    def _log_batch(self, batch: Dict[str, torch.Tensor], outputs: Dict[str, Any]) -> None:
        """
        Log batch results.
        
        Args:
            batch: Batch of data.
            outputs: Dictionary of outputs.
        """
        # Log losses
        self.writer.add_scalar("Loss/audio", outputs["audio_loss"], self.global_step)
        
        # Log audio samples
        if self.global_step % (self.log_interval * 10) == 0:
            # Extract audio
            audio = batch["audio"][0].detach().cpu()
            pred_audio = outputs["pred_audio"][0].detach().cpu()
            
            # Log audio
            self.writer.add_audio("Audio/target", audio, self.global_step, sample_rate=self.sample_rate)
            self.writer.add_audio("Audio/predicted", pred_audio, self.global_step, sample_rate=self.sample_rate)
            
            # Log waveform
            self._log_waveform(audio, pred_audio, self.global_step)
    
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
            mels = batch["mels"]
            audio = batch["audio"]
            
            # Generate audio
            with torch.no_grad():
                pred_audio = self.model.inference(mels)
            
            # Log audio samples
            for i in range(min(3, mels.size(0))):
                # Extract audio
                audio_i = audio[i].detach().cpu()
                pred_audio_i = pred_audio[i].detach().cpu()
                
                # Log audio
                self.writer.add_audio(f"Validation/target_{i}", audio_i, self.global_step, sample_rate=self.sample_rate)
                self.writer.add_audio(f"Validation/predicted_{i}", pred_audio_i, self.global_step, sample_rate=self.sample_rate)
                
                # Log waveform
                self._log_waveform(audio_i, pred_audio_i, self.global_step, prefix=f"validation_{i}")
    
    def _log_waveform(self, audio: torch.Tensor, pred_audio: torch.Tensor, step: int, prefix: str = "train") -> None:
        """
        Log waveform to TensorBoard.
        
        Args:
            audio: Target audio waveform.
            pred_audio: Predicted audio waveform.
            step: Global step.
            prefix: Prefix for the image name.
        """
        # Create figure
        fig, ax = plt.subplots(2, 1, figsize=(10, 6))
        
        # Plot target waveform
        ax[0].plot(audio.numpy())
        ax[0].set_title("Target")
        ax[0].set_ylim([-1, 1])
        
        # Plot predicted waveform
        ax[1].plot(pred_audio.numpy())
        ax[1].set_title("Predicted")
        ax[1].set_ylim([-1, 1])
        
        plt.tight_layout()
        
        # Log to TensorBoard
        self.writer.add_figure(f"Waveform/{prefix}", fig, step)
        plt.close(fig)
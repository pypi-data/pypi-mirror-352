"""
Enhanced acoustic model trainer for Kalakan TTS.

This module implements an improved trainer for acoustic models (text-to-mel)
in Kalakan TTS, with support for modern training techniques.
"""

import os
import time
import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter

from kalakan.models.acoustic.base_acoustic import BaseAcousticModel
from kalakan.training.trainer import Trainer
from kalakan.utils.config import Config


class EnhancedAcousticTrainer(Trainer):
    """
    Enhanced trainer for acoustic models in Kalakan TTS.

    This trainer provides improved training for acoustic models with support for:
    - Mixed precision training
    - Gradient accumulation
    - Learning rate scheduling
    - Phoneme-level attention visualization
    - Pitch and energy prediction (for models that support it)
    - Guided attention loss
    - Adversarial training
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
        Initialize the enhanced acoustic model trainer.

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
        self.pitch_loss_weight = self.config.get("training.loss_weights.pitch_loss", 0.5)
        self.energy_loss_weight = self.config.get("training.loss_weights.energy_loss", 0.5)
        self.duration_loss_weight = self.config.get("training.loss_weights.duration_loss", 0.5)
        self.guided_attention_loss_weight = self.config.get("training.loss_weights.guided_attention_loss", 0.5)

        # Set up mixed precision training
        self.use_fp16 = self.config.get("training.fp16", False)
        if self.use_fp16:
            self.scaler = torch.cuda.amp.GradScaler()

        # Set up gradient accumulation
        self.grad_accumulation_steps = self.config.get("training.grad_accumulation_steps", 1)

        # Set up guided attention loss
        self.use_guided_attention = self.config.get("training.use_guided_attention", False)
        if self.use_guided_attention:
            self.guided_attention_sigma = self.config.get("training.guided_attention_sigma", 0.4)
            self.guided_attention_decay_steps = self.config.get("training.guided_attention_decay_steps", 20000)

        # Set up adversarial training
        self.use_adversarial_training = self.config.get("training.use_adversarial_training", False)
        if self.use_adversarial_training:
            self.discriminator = self._create_discriminator()
            self.discriminator_optimizer = self._create_optimizer(
                self.discriminator.parameters(),
                self.config.get("training.discriminator_optimizer", {})
            )
            self.adversarial_loss_weight = self.config.get("training.loss_weights.adversarial_loss", 0.1)

    def _create_optimizer(self, parameters, config: Dict) -> torch.optim.Optimizer:
        """
        Create an optimizer for the given parameters.

        Args:
            parameters: Model parameters to optimize.
            config: Optimizer configuration.

        Returns:
            Optimizer instance.
        """
        optimizer_name = config.get("name", "Adam")
        lr = config.get("lr", 0.001)
        betas = config.get("betas", (0.9, 0.999))
        eps = config.get("eps", 1e-8)
        weight_decay = config.get("weight_decay", 0.0)

        if optimizer_name == "Adam":
            return torch.optim.Adam(
                parameters,
                lr=lr,
                betas=betas,
                eps=eps,
                weight_decay=weight_decay,
            )
        elif optimizer_name == "AdamW":
            return torch.optim.AdamW(
                parameters,
                lr=lr,
                betas=betas,
                eps=eps,
                weight_decay=weight_decay,
            )
        elif optimizer_name == "SGD":
            return torch.optim.SGD(
                parameters,
                lr=lr,
                momentum=config.get("momentum", 0.9),
                weight_decay=weight_decay,
            )
        else:
            raise ValueError(f"Unsupported optimizer: {optimizer_name}")

    def _create_discriminator(self) -> nn.Module:
        """
        Create a discriminator model for adversarial training.

        Returns:
            Discriminator model.
        """
        # Simple discriminator that takes mel spectrograms as input
        # and outputs a probability of being real
        discriminator = nn.Sequential(
            nn.Conv1d(self.config.get("model.n_mels", 80), 32, kernel_size=3, stride=1, padding=1),
            nn.LeakyReLU(0.2),
            nn.Conv1d(32, 64, kernel_size=3, stride=2, padding=1),
            nn.LeakyReLU(0.2),
            nn.Conv1d(64, 128, kernel_size=3, stride=2, padding=1),
            nn.LeakyReLU(0.2),
            nn.Conv1d(128, 256, kernel_size=3, stride=2, padding=1),
            nn.LeakyReLU(0.2),
            nn.Conv1d(256, 512, kernel_size=3, stride=2, padding=1),
            nn.LeakyReLU(0.2),
            nn.Conv1d(512, 1, kernel_size=3, stride=1, padding=1),
        )

        return discriminator.to(self.device)

    def _compute_guided_attention_loss(
        self,
        attention_weights: torch.Tensor,
        phoneme_lengths: torch.Tensor,
        mel_lengths: torch.Tensor
    ) -> torch.Tensor:
        """
        Compute guided attention loss.

        Args:
            attention_weights: Attention weights [batch_size, max_mel_length, max_phoneme_length].
            phoneme_lengths: Phoneme sequence lengths [batch_size].
            mel_lengths: Mel spectrogram lengths [batch_size].

        Returns:
            Guided attention loss.
        """
        batch_size = attention_weights.size(0)
        max_phoneme_length = attention_weights.size(2)
        max_mel_length = attention_weights.size(1)

        # Create target attention matrix
        # The target is a diagonal matrix, where the diagonal represents
        # the ideal alignment between phonemes and mel frames
        target = torch.zeros_like(attention_weights)

        for i in range(batch_size):
            phoneme_length = phoneme_lengths[i].item()
            mel_length = mel_lengths[i].item()

            # Create diagonal target for this sample
            # The diagonal represents the ideal alignment
            # between phonemes and mel frames
            for j in range(int(mel_length)):
                # Calculate the ideal phoneme position for this mel frame
                # This creates a diagonal alignment
                ideal_pos = int(j * phoneme_length / mel_length)

                # Set a Gaussian distribution centered at the ideal position
                for k in range(int(phoneme_length)):
                    # Calculate distance from ideal position
                    dist = abs(k - ideal_pos)

                    # Set Gaussian value
                    target[i, j, k] = torch.exp(-dist ** 2 / (2 * self.guided_attention_sigma ** 2))

        # Compute loss
        # We use binary cross-entropy loss between the attention weights
        # and the target attention matrix
        loss = F.binary_cross_entropy(attention_weights, target)

        # Apply decay to the loss weight based on the current step
        if self.global_step < self.guided_attention_decay_steps:
            weight = 1.0 - (self.global_step / self.guided_attention_decay_steps)
        else:
            weight = 0.0

        return loss * weight * self.guided_attention_loss_weight

    def _compute_loss(self, batch: Dict[str, torch.Tensor]) -> Tuple[torch.Tensor, Dict[str, Any]]:
        """
        Compute loss for a batch.

        Args:
            batch: Batch of data containing:
                - phonemes: Tensor of phoneme indices [batch_size, max_phoneme_length].
                - phoneme_lengths: Tensor of phoneme sequence lengths [batch_size].
                - mels: Tensor of target mel spectrograms [batch_size, n_mels, max_mel_length].
                - mel_lengths: Tensor of mel spectrogram lengths [batch_size].
                - pitch: Tensor of pitch contours [batch_size, max_mel_length] (optional).
                - energy: Tensor of energy contours [batch_size, max_mel_length] (optional).
                - alignment: Tensor of phoneme-level alignments [batch_size, max_phoneme_length, max_mel_length] (optional).

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

        # Optional inputs
        pitch = batch.get("pitch", None)
        energy = batch.get("energy", None)
        alignment = batch.get("alignment", None)

        # Forward pass
        if self.use_fp16:
            with torch.cuda.amp.autocast():
                mel_outputs_postnet, outputs = self.model(
                    phonemes=phonemes,
                    phoneme_lengths=phoneme_lengths,
                    mels=mels,
                    mel_lengths=mel_lengths,
                    pitch=pitch,
                    energy=energy,
                    alignment=alignment,
                )
        else:
            mel_outputs_postnet, outputs = self.model(
                phonemes=phonemes,
                phoneme_lengths=phoneme_lengths,
                mels=mels,
                mel_lengths=mel_lengths,
                pitch=pitch,
                energy=energy,
                alignment=alignment,
            )

        # Extract model outputs
        mel_outputs = outputs["mel_outputs"]
        stop_outputs = outputs.get("stop_outputs", None)
        attention_weights = outputs.get("attention_weights", None)
        pitch_outputs = outputs.get("pitch_outputs", None)
        energy_outputs = outputs.get("energy_outputs", None)
        duration_outputs = outputs.get("duration_outputs", None)

        # Create target stop tokens if needed
        if stop_outputs is not None:
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

        # Initialize total loss
        loss = mel_loss + mel_postnet_loss

        # Compute stop loss if needed
        if stop_outputs is not None:
            stop_loss = F.binary_cross_entropy_with_logits(
                stop_outputs, stop_targets, reduction="none"
            )
            stop_loss = (stop_loss * mel_mask).sum() / mel_mask.sum() * self.stop_loss_weight
            loss = loss + stop_loss
        else:
            stop_loss = torch.tensor(0.0, device=self.device)

        # Compute pitch loss if needed
        if pitch_outputs is not None and pitch is not None:
            pitch_loss = F.mse_loss(pitch_outputs, pitch) * self.pitch_loss_weight
            loss = loss + pitch_loss
        else:
            pitch_loss = torch.tensor(0.0, device=self.device)

        # Compute energy loss if needed
        if energy_outputs is not None and energy is not None:
            energy_loss = F.mse_loss(energy_outputs, energy) * self.energy_loss_weight
            loss = loss + energy_loss
        else:
            energy_loss = torch.tensor(0.0, device=self.device)

        # Compute duration loss if needed
        if duration_outputs is not None and alignment is not None:
            # Extract target durations from alignment
            target_durations = alignment.sum(dim=1)
            duration_loss = F.mse_loss(duration_outputs, target_durations) * self.duration_loss_weight
            loss = loss + duration_loss
        else:
            duration_loss = torch.tensor(0.0, device=self.device)

        # Compute guided attention loss if needed
        if self.use_guided_attention and attention_weights is not None:
            guided_attention_loss = self._compute_guided_attention_loss(
                attention_weights, phoneme_lengths, mel_lengths
            )
            loss = loss + guided_attention_loss
        else:
            guided_attention_loss = torch.tensor(0.0, device=self.device)

        # Compute adversarial loss if needed
        if self.use_adversarial_training:
            # Train discriminator
            real_loss = F.binary_cross_entropy_with_logits(
                self.discriminator(mels),
                torch.ones(mels.size(0), 1, mels.size(2), device=self.device)
            )
            fake_loss = F.binary_cross_entropy_with_logits(
                self.discriminator(mel_outputs_postnet.detach()),
                torch.zeros(mel_outputs_postnet.size(0), 1, mel_outputs_postnet.size(2), device=self.device)
            )
            discriminator_loss = real_loss + fake_loss

            # Train generator (model)
            adversarial_loss = F.binary_cross_entropy_with_logits(
                self.discriminator(mel_outputs_postnet),
                torch.ones(mel_outputs_postnet.size(0), 1, mel_outputs_postnet.size(2), device=self.device)
            ) * self.adversarial_loss_weight

            loss = loss + adversarial_loss
        else:
            discriminator_loss = torch.tensor(0.0, device=self.device)
            adversarial_loss = torch.tensor(0.0, device=self.device)

        # Prepare outputs
        outputs.update({
            "loss": loss.item(),
            "mel_loss": mel_loss.item(),
            "mel_postnet_loss": mel_postnet_loss.item(),
            "stop_loss": stop_loss.item(),
            "pitch_loss": pitch_loss.item(),
            "energy_loss": energy_loss.item(),
            "duration_loss": duration_loss.item(),
            "guided_attention_loss": guided_attention_loss.item(),
            "discriminator_loss": discriminator_loss.item(),
            "adversarial_loss": adversarial_loss.item(),
        })

        return loss, outputs

    def _train_step(self, batch: Dict[str, torch.Tensor]) -> Dict[str, Any]:
        """
        Perform a single training step.

        Args:
            batch: Batch of data.

        Returns:
            Dictionary of outputs.
        """
        # Move batch to device
        batch = self._move_batch_to_device(batch)

        # Zero gradients
        if self.global_step % self.grad_accumulation_steps == 0:
            self.optimizer.zero_grad()

        # Compute loss
        loss, outputs = self._compute_loss(batch)

        # Scale loss for gradient accumulation
        loss = loss / self.grad_accumulation_steps

        # Backward pass
        if self.use_fp16:
            self.scaler.scale(loss).backward()
        else:
            loss.backward()

        # Update weights
        if (self.global_step + 1) % self.grad_accumulation_steps == 0:
            # Clip gradients
            if self.grad_clip_thresh > 0:
                if self.use_fp16:
                    self.scaler.unscale_(self.optimizer)

                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(), self.grad_clip_thresh
                )

            # Update weights
            if self.use_fp16:
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                self.optimizer.step()

            # Update discriminator if using adversarial training
            if self.use_adversarial_training:
                self.discriminator_optimizer.step()
                self.discriminator_optimizer.zero_grad()

        # Update learning rate
        if self.lr_scheduler is not None:
            self.lr_scheduler.step()

        return outputs

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
        self.writer.add_scalar("Loss/pitch", outputs["pitch_loss"], self.global_step)
        self.writer.add_scalar("Loss/energy", outputs["energy_loss"], self.global_step)
        self.writer.add_scalar("Loss/duration", outputs["duration_loss"], self.global_step)
        self.writer.add_scalar("Loss/guided_attention", outputs["guided_attention_loss"], self.global_step)
        self.writer.add_scalar("Loss/discriminator", outputs["discriminator_loss"], self.global_step)
        self.writer.add_scalar("Loss/adversarial", outputs["adversarial_loss"], self.global_step)

        # Log learning rate
        if self.optimizer is not None:
            self.writer.add_scalar(
                "Training/learning_rate",
                self.optimizer.param_groups[0]["lr"],
                self.global_step
            )

        # Log alignments
        if "attention_weights" in outputs and self.global_step % (self.log_interval * 10) == 0:
            attention_weights = outputs["attention_weights"][0].detach().cpu().numpy()
            self._log_alignment(attention_weights, self.global_step)

        # Log pitch and energy
        if "pitch_outputs" in outputs and self.global_step % (self.log_interval * 10) == 0:
            pitch = outputs["pitch_outputs"][0].detach().cpu().numpy()
            self._log_pitch(pitch, self.global_step)

        if "energy_outputs" in outputs and self.global_step % (self.log_interval * 10) == 0:
            energy = outputs["energy_outputs"][0].detach().cpu().numpy()
            self._log_energy(energy, self.global_step)

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
                if self.use_fp16:
                    with torch.cuda.amp.autocast():
                        # Call the model's inference method
                        # Use getattr to explicitly get the inference method
                        inference_method = getattr(self.model, "inference")
                        mel_outputs_postnet, outputs = inference_method(
                            phonemes=phonemes,
                            phoneme_lengths=phoneme_lengths,
                            max_length=1000
                        )
                else:
                    # Call the model's inference method
                    # Use getattr to explicitly get the inference method
                    inference_method = getattr(self.model, "inference")
                    mel_outputs_postnet, outputs = inference_method(
                        phonemes=phonemes,
                        phoneme_lengths=phoneme_lengths,
                        max_length=1000
                    )

            # Log generated mel spectrograms
            for i in range(min(3, mel_outputs_postnet.size(0))):
                mel = mel_outputs_postnet[i].detach().cpu().numpy()
                self._log_mel_spectrogram(mel, f"validation_{i}", self.global_step)

                # Log alignments
                if "attention_weights" in outputs:
                    attention_weights = outputs["attention_weights"][i].detach().cpu().numpy()
                    self._log_alignment(attention_weights, self.global_step, prefix=f"validation_{i}")

                # Log pitch and energy
                if "pitch_outputs" in outputs:
                    pitch = outputs["pitch_outputs"][i].detach().cpu().numpy()
                    self._log_pitch(pitch, self.global_step, prefix=f"validation_{i}")

                if "energy_outputs" in outputs:
                    energy = outputs["energy_outputs"][i].detach().cpu().numpy()
                    self._log_energy(energy, self.global_step, prefix=f"validation_{i}")

    def _log_mel_spectrogram(self, mel: np.ndarray, prefix: str, step: int) -> None:
        """
        Log mel spectrogram to TensorBoard.

        Args:
            mel: Mel spectrogram [n_mels, time].
            prefix: Prefix for the image name.
            step: Global step.
        """
        fig, ax = plt.subplots(figsize=(10, 4))
        im = ax.imshow(mel, aspect="auto", origin="lower", interpolation="none")
        plt.colorbar(im, ax=ax)
        plt.title(f"{prefix} Mel Spectrogram")
        plt.tight_layout()

        self.writer.add_figure(f"Mel/{prefix}", fig, step)
        plt.close(fig)

    def _log_alignment(self, alignment: np.ndarray, step: int, prefix: str = "train") -> None:
        """
        Log alignment to TensorBoard.

        Args:
            alignment: Alignment matrix [time, phoneme_length].
            step: Global step.
            prefix: Prefix for the image name.
        """
        fig, ax = plt.subplots(figsize=(10, 4))
        im = ax.imshow(alignment, aspect="auto", origin="lower", interpolation="none")
        plt.colorbar(im, ax=ax)
        plt.title(f"{prefix} Alignment")
        plt.tight_layout()

        self.writer.add_figure(f"Alignment/{prefix}", fig, step)
        plt.close(fig)

    def _log_pitch(self, pitch: np.ndarray, step: int, prefix: str = "train") -> None:
        """
        Log pitch contour to TensorBoard.

        Args:
            pitch: Pitch contour [time].
            step: Global step.
            prefix: Prefix for the image name.
        """
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(pitch)
        plt.title(f"{prefix} Pitch Contour")
        plt.tight_layout()

        self.writer.add_figure(f"Pitch/{prefix}", fig, step)
        plt.close(fig)

    def _log_energy(self, energy: np.ndarray, step: int, prefix: str = "train") -> None:
        """
        Log energy contour to TensorBoard.

        Args:
            energy: Energy contour [time].
            step: Global step.
            prefix: Prefix for the image name.
        """
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(energy)
        plt.title(f"{prefix} Energy Contour")
        plt.tight_layout()

        self.writer.add_figure(f"Energy/{prefix}", fig, step)
        plt.close(fig)

    def _get_mask_from_lengths(self, lengths: torch.Tensor, max_len: Optional[int] = None) -> torch.Tensor:
        """
        Get mask tensor from lengths.

        Args:
            lengths: Tensor of sequence lengths.
            max_len: Maximum length. If None, use max of lengths.

        Returns:
            Mask tensor.
        """
        if max_len is None:
            max_len = int(torch.max(lengths).item())

        ids = torch.arange(0, max_len, device=lengths.device)
        mask = (ids < lengths.unsqueeze(1)).float()

        return mask
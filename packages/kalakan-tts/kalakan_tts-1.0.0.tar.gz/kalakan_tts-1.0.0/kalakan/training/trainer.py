"""
Base trainer for Kalakan TTS models.

This module defines the base trainer class for Kalakan TTS models,
which handles common training functionality like logging, checkpointing,
and validation.
"""

import os
import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm

from kalakan.utils.config import Config
from kalakan.utils.device import get_device


class Trainer(ABC):
    """
    Base trainer for Kalakan TTS models.
    
    This abstract class defines the interface for trainers in Kalakan TTS.
    All trainers should inherit from this class and implement its abstract methods.
    """
    
    def __init__(
        self,
        model: nn.Module,
        train_dataloader: DataLoader,
        val_dataloader: Optional[DataLoader] = None,
        config: Optional[Union[Dict, Config]] = None,
        device: Optional[torch.device] = None,
        output_dir: str = "models",
        experiment_name: Optional[str] = None,
        tensorboard_dir: Optional[str] = None,
    ):
        """
        Initialize the trainer.
        
        Args:
            model: Model to train.
            train_dataloader: DataLoader for training data.
            val_dataloader: DataLoader for validation data.
            config: Training configuration.
            device: Device to use for training.
            output_dir: Directory to save model checkpoints.
            experiment_name: Name of the experiment.
            tensorboard_dir: Directory to save TensorBoard logs.
        """
        # Set model
        self.model = model
        
        # Set dataloaders
        self.train_dataloader = train_dataloader
        self.val_dataloader = val_dataloader
        
        # Set configuration
        if config is None:
            config = {}
        self.config = Config(config) if not isinstance(config, Config) else config
        
        # Set device
        self.device = device if device is not None else get_device()
        
        # Move model to device
        self.model = self.model.to(self.device)
        
        # Set output directory
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Set experiment name
        if experiment_name is None:
            experiment_name = f"{model.__class__.__name__}_{time.strftime('%Y%m%d_%H%M%S')}"
        self.experiment_name = experiment_name
        
        # Set TensorBoard directory
        if tensorboard_dir is None:
            tensorboard_dir = os.path.join(self.output_dir, "tensorboard", self.experiment_name)
        self.tensorboard_dir = tensorboard_dir
        os.makedirs(self.tensorboard_dir, exist_ok=True)
        
        # Create TensorBoard writer
        self.writer = SummaryWriter(self.tensorboard_dir)
        
        # Set training parameters
        self.batch_size = self.config.get("training.batch_size", 32)
        self.epochs = self.config.get("training.epochs", 1000)
        self.grad_clip_thresh = self.config.get("training.grad_clip_thresh", 1.0)
        self.seed = self.config.get("training.seed", 1234)
        
        # Set validation parameters
        self.validation_interval = self.config.get("training.validation_interval", 1000)
        
        # Set checkpointing parameters
        self.checkpoint_interval = self.config.get("training.checkpoint_interval", 5000)
        self.keep_top_k = self.config.get("training.keep_top_k", 5)
        
        # Set logging parameters
        self.log_interval = self.config.get("training.log_interval", 100)
        
        # Set early stopping parameters
        self.early_stopping_enabled = self.config.get("training.early_stopping.enabled", True)
        self.early_stopping_patience = self.config.get("training.early_stopping.patience", 10)
        self.early_stopping_min_delta = self.config.get("training.early_stopping.min_delta", 0.0001)
        
        # Set mixed precision parameters
        self.fp16 = self.config.get("training.fp16", False)
        
        # Set gradient accumulation parameters
        self.grad_accumulation_steps = self.config.get("training.grad_accumulation_steps", 1)
        
        # Initialize optimizer
        self.optimizer = self._init_optimizer()
        
        # Initialize learning rate scheduler
        self.lr_scheduler = self._init_lr_scheduler()
        
        # Initialize training state
        self.global_step = 0
        self.epoch = 0
        self.best_val_loss = float("inf")
        self.early_stopping_counter = 0
        
        # Set random seed
        torch.manual_seed(self.seed)
        np.random.seed(self.seed)
        
        # Initialize scaler for mixed precision training
        self.scaler = torch.cuda.amp.GradScaler() if self.fp16 else None
        
        # Initialize best checkpoints
        self.best_checkpoints = []
    
    def _init_optimizer(self) -> optim.Optimizer:
        """
        Initialize the optimizer.
        
        Returns:
            Optimizer instance.
        """
        # Get optimizer parameters
        optimizer_name = self.config.get("training.optimizer.name", "Adam")
        lr = self.config.get("training.optimizer.lr", 0.001)
        betas = self.config.get("training.optimizer.betas", (0.9, 0.999))
        eps = self.config.get("training.optimizer.eps", 1e-8)
        weight_decay = self.config.get("training.optimizer.weight_decay", 0.0)
        
        # Create optimizer
        if optimizer_name == "Adam":
            return optim.Adam(
                self.model.parameters(),
                lr=lr,
                betas=betas,
                eps=eps,
                weight_decay=weight_decay,
            )
        elif optimizer_name == "AdamW":
            return optim.AdamW(
                self.model.parameters(),
                lr=lr,
                betas=betas,
                eps=eps,
                weight_decay=weight_decay,
            )
        elif optimizer_name == "SGD":
            return optim.SGD(
                self.model.parameters(),
                lr=lr,
                momentum=self.config.get("training.optimizer.momentum", 0.9),
                weight_decay=weight_decay,
            )
        else:
            raise ValueError(f"Unsupported optimizer: {optimizer_name}")
    
    def _init_lr_scheduler(self) -> Optional[optim.lr_scheduler._LRScheduler]:
        """
        Initialize the learning rate scheduler.
        
        Returns:
            Learning rate scheduler instance, or None if not used.
        """
        # Get scheduler parameters
        scheduler_name = self.config.get("training.lr_scheduler.name", None)
        
        # Create scheduler
        if scheduler_name is None:
            return None
        elif scheduler_name == "StepLR":
            return optim.lr_scheduler.StepLR(
                self.optimizer,
                step_size=self.config.get("training.lr_scheduler.step_size", 50000),
                gamma=self.config.get("training.lr_scheduler.gamma", 0.5),
            )
        elif scheduler_name == "ExponentialLR":
            return optim.lr_scheduler.ExponentialLR(
                self.optimizer,
                gamma=self.config.get("training.lr_scheduler.gamma", 0.99),
            )
        elif scheduler_name == "ReduceLROnPlateau":
            return optim.lr_scheduler.ReduceLROnPlateau(
                self.optimizer,
                mode=self.config.get("training.lr_scheduler.mode", "min"),
                factor=self.config.get("training.lr_scheduler.factor", 0.5),
                patience=self.config.get("training.lr_scheduler.patience", 5),
                threshold=self.config.get("training.lr_scheduler.threshold", 0.001),
                threshold_mode=self.config.get("training.lr_scheduler.threshold_mode", "rel"),
                cooldown=self.config.get("training.lr_scheduler.cooldown", 0),
                min_lr=self.config.get("training.lr_scheduler.min_lr", 0.00001),
                eps=self.config.get("training.lr_scheduler.eps", 1e-8),
            )
        elif scheduler_name == "NoamLR":
            # Custom Noam learning rate scheduler (from Transformer paper)
            warmup_steps = self.config.get("training.lr_scheduler.warmup_steps", 4000)
            return NoamLR(
                self.optimizer,
                model_size=self.model.encoder.encoder_dim,
                warmup_steps=warmup_steps,
            )
        else:
            raise ValueError(f"Unsupported scheduler: {scheduler_name}")
    
    def train(self) -> None:
        """
        Train the model.
        """
        # Print training information
        print(f"Training {self.model.__class__.__name__} on {self.device}")
        print(f"Experiment name: {self.experiment_name}")
        print(f"Output directory: {self.output_dir}")
        print(f"TensorBoard directory: {self.tensorboard_dir}")
        print(f"Batch size: {self.batch_size}")
        print(f"Epochs: {self.epochs}")
        print(f"Training samples: {len(self.train_dataloader.dataset)}")
        if self.val_dataloader is not None:
            print(f"Validation samples: {len(self.val_dataloader.dataset)}")
        print(f"Mixed precision: {self.fp16}")
        print(f"Gradient accumulation steps: {self.grad_accumulation_steps}")
        print(f"Optimizer: {self.optimizer.__class__.__name__}")
        if self.lr_scheduler is not None:
            print(f"Learning rate scheduler: {self.lr_scheduler.__class__.__name__}")
        print(f"Early stopping: {self.early_stopping_enabled}")
        print(f"Device: {self.device}")
        print()
        
        # Training loop
        for epoch in range(self.epoch, self.epochs):
            self.epoch = epoch
            
            # Train for one epoch
            train_loss = self._train_epoch()
            
            # Log epoch results
            print(f"Epoch {epoch+1}/{self.epochs} - Train loss: {train_loss:.4f}")
            self.writer.add_scalar("Loss/train_epoch", train_loss, epoch)
            
            # Validate if needed
            if self.val_dataloader is not None and epoch % self.validation_interval == 0:
                val_loss = self._validate()
                print(f"Epoch {epoch+1}/{self.epochs} - Validation loss: {val_loss:.4f}")
                self.writer.add_scalar("Loss/validation_epoch", val_loss, epoch)
                
                # Save checkpoint if it's the best so far
                if val_loss < self.best_val_loss:
                    self.best_val_loss = val_loss
                    self._save_checkpoint(f"best_model_{epoch+1}.pt", val_loss=val_loss)
                    self.early_stopping_counter = 0
                else:
                    self.early_stopping_counter += 1
                
                # Early stopping
                if self.early_stopping_enabled and self.early_stopping_counter >= self.early_stopping_patience:
                    print(f"Early stopping after {epoch+1} epochs")
                    break
            
            # Save checkpoint
            if (epoch + 1) % self.checkpoint_interval == 0:
                self._save_checkpoint(f"model_{epoch+1}.pt")
        
        # Save final model
        self._save_checkpoint("final_model.pt")
        
        # Close TensorBoard writer
        self.writer.close()
    
    def _train_epoch(self) -> float:
        """
        Train the model for one epoch.
        
        Returns:
            Average training loss for the epoch.
        """
        # Set model to training mode
        self.model.train()
        
        # Initialize loss accumulator
        epoch_loss = 0.0
        
        # Create progress bar
        pbar = tqdm(self.train_dataloader, desc=f"Epoch {self.epoch+1}/{self.epochs}")
        
        # Iterate over batches
        for batch_idx, batch in enumerate(pbar):
            # Move batch to device
            batch = self._move_batch_to_device(batch)
            
            # Forward pass with mixed precision if enabled
            if self.fp16:
                with torch.cuda.amp.autocast():
                    loss, outputs = self._compute_loss(batch)
                    loss = loss / self.grad_accumulation_steps
            else:
                loss, outputs = self._compute_loss(batch)
                loss = loss / self.grad_accumulation_steps
            
            # Backward pass with mixed precision if enabled
            if self.fp16:
                self.scaler.scale(loss).backward()
            else:
                loss.backward()
            
            # Update weights if gradient accumulation is complete
            if (batch_idx + 1) % self.grad_accumulation_steps == 0:
                # Clip gradients
                if self.grad_clip_thresh > 0:
                    if self.fp16:
                        self.scaler.unscale_(self.optimizer)
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.grad_clip_thresh)
                
                # Update weights with mixed precision if enabled
                if self.fp16:
                    self.scaler.step(self.optimizer)
                    self.scaler.update()
                else:
                    self.optimizer.step()
                
                # Zero gradients
                self.optimizer.zero_grad()
                
                # Update learning rate
                if self.lr_scheduler is not None:
                    if isinstance(self.lr_scheduler, optim.lr_scheduler.ReduceLROnPlateau):
                        pass  # Updated after validation
                    else:
                        self.lr_scheduler.step()
            
            # Accumulate loss
            epoch_loss += loss.item() * self.grad_accumulation_steps
            
            # Update progress bar
            pbar.set_postfix({"loss": loss.item() * self.grad_accumulation_steps})
            
            # Log batch results
            if self.global_step % self.log_interval == 0:
                self.writer.add_scalar("Loss/train", loss.item() * self.grad_accumulation_steps, self.global_step)
                self.writer.add_scalar("LearningRate", self.optimizer.param_groups[0]["lr"], self.global_step)
                self._log_batch(batch, outputs)
            
            # Increment global step
            self.global_step += 1
        
        # Compute average loss
        epoch_loss /= len(self.train_dataloader)
        
        return epoch_loss
    
    def _validate(self) -> float:
        """
        Validate the model.
        
        Returns:
            Average validation loss.
        """
        # Set model to evaluation mode
        self.model.eval()
        
        # Initialize loss accumulator
        val_loss = 0.0
        
        # Iterate over batches
        with torch.no_grad():
            for batch in tqdm(self.val_dataloader, desc="Validation"):
                # Move batch to device
                batch = self._move_batch_to_device(batch)
                
                # Forward pass
                loss, outputs = self._compute_loss(batch)
                
                # Accumulate loss
                val_loss += loss.item()
        
        # Compute average loss
        val_loss /= len(self.val_dataloader)
        
        # Update learning rate if using ReduceLROnPlateau
        if isinstance(self.lr_scheduler, optim.lr_scheduler.ReduceLROnPlateau):
            self.lr_scheduler.step(val_loss)
        
        # Log validation results
        self._log_validation(val_loss)
        
        return val_loss
    
    def _save_checkpoint(self, filename: str, val_loss: Optional[float] = None) -> None:
        """
        Save model checkpoint.
        
        Args:
            filename: Name of the checkpoint file.
            val_loss: Validation loss for the checkpoint.
        """
        # Create checkpoint directory
        checkpoint_dir = os.path.join(self.output_dir, self.experiment_name)
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        # Create checkpoint path
        checkpoint_path = os.path.join(checkpoint_dir, filename)
        
        # Prepare checkpoint
        checkpoint = {
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "global_step": self.global_step,
            "epoch": self.epoch,
            "best_val_loss": self.best_val_loss,
            "config": self.config.to_dict(),
        }
        
        # Add learning rate scheduler if exists
        if self.lr_scheduler is not None:
            checkpoint["lr_scheduler_state_dict"] = self.lr_scheduler.state_dict()
        
        # Save checkpoint
        torch.save(checkpoint, checkpoint_path)
        
        # Add to best checkpoints if validation loss is provided
        if val_loss is not None:
            self.best_checkpoints.append((checkpoint_path, val_loss))
            self.best_checkpoints.sort(key=lambda x: x[1])
            
            # Keep only top K checkpoints
            if len(self.best_checkpoints) > self.keep_top_k:
                _, worst_checkpoint = self.best_checkpoints.pop()
                if os.path.exists(worst_checkpoint):
                    os.remove(worst_checkpoint)
        
        print(f"Saved checkpoint: {checkpoint_path}")
    
    def load_checkpoint(self, checkpoint_path: str) -> None:
        """
        Load model checkpoint.
        
        Args:
            checkpoint_path: Path to the checkpoint file.
        """
        # Load checkpoint
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        
        # Load model state
        self.model.load_state_dict(checkpoint["model_state_dict"])
        
        # Load optimizer state
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        
        # Load learning rate scheduler if exists
        if self.lr_scheduler is not None and "lr_scheduler_state_dict" in checkpoint:
            self.lr_scheduler.load_state_dict(checkpoint["lr_scheduler_state_dict"])
        
        # Load training state
        self.global_step = checkpoint.get("global_step", 0)
        self.epoch = checkpoint.get("epoch", 0)
        self.best_val_loss = checkpoint.get("best_val_loss", float("inf"))
        
        print(f"Loaded checkpoint: {checkpoint_path}")
    
    def _move_batch_to_device(self, batch: Any) -> Any:
        """
        Move batch to device.
        
        Args:
            batch: Batch to move to device.
            
        Returns:
            Batch on device.
        """
        if isinstance(batch, torch.Tensor):
            return batch.to(self.device)
        elif isinstance(batch, dict):
            return {k: self._move_batch_to_device(v) for k, v in batch.items()}
        elif isinstance(batch, list):
            return [self._move_batch_to_device(v) for v in batch]
        elif isinstance(batch, tuple):
            return tuple(self._move_batch_to_device(v) for v in batch)
        else:
            return batch
    
    @abstractmethod
    def _compute_loss(self, batch: Any) -> Tuple[torch.Tensor, Dict[str, Any]]:
        """
        Compute loss for a batch.
        
        Args:
            batch: Batch of data.
            
        Returns:
            Tuple containing:
                - Loss tensor.
                - Dictionary of outputs.
        """
        pass
    
    @abstractmethod
    def _log_batch(self, batch: Any, outputs: Dict[str, Any]) -> None:
        """
        Log batch results.
        
        Args:
            batch: Batch of data.
            outputs: Dictionary of outputs.
        """
        pass
    
    @abstractmethod
    def _log_validation(self, val_loss: float) -> None:
        """
        Log validation results.
        
        Args:
            val_loss: Validation loss.
        """
        pass


class NoamLR(optim.lr_scheduler._LRScheduler):
    """
    Learning rate scheduler from the Transformer paper.
    
    This scheduler increases the learning rate linearly for the first warmup_steps
    training steps, and decreases it thereafter proportionally to the inverse
    square root of the step number.
    """
    
    def __init__(
        self,
        optimizer: optim.Optimizer,
        model_size: int,
        warmup_steps: int,
        last_epoch: int = -1,
    ):
        """
        Initialize the Noam learning rate scheduler.
        
        Args:
            optimizer: Optimizer to schedule.
            model_size: Size of the model (typically the hidden size).
            warmup_steps: Number of warmup steps.
            last_epoch: The index of the last epoch.
        """
        self.model_size = model_size
        self.warmup_steps = warmup_steps
        super().__init__(optimizer, last_epoch)
    
    def get_lr(self) -> List[float]:
        """
        Get learning rate.
        
        Returns:
            List of learning rates for each parameter group.
        """
        step = max(1, self._step_count)
        scale = self.model_size ** (-0.5) * min(
            step ** (-0.5), step * self.warmup_steps ** (-1.5)
        )
        return [base_lr * scale for base_lr in self.base_lrs]
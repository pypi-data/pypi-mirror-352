"""
Model configuration utilities for Kalakan TTS.

This module provides utilities for managing model configurations,
including parameter validation, schema definition, and configuration loading.
"""

import os
from typing import Any, Dict, List, Optional, Type, Union

import yaml
from pydantic import BaseModel, Field, validator

from kalakan.utils.config import Config


class ModelConfig(BaseModel):
    """Base model configuration class."""
    name: str


class Tacotron2Config(ModelConfig):
    """Configuration for Tacotron2 model."""
    name: str = "tacotron2"
    
    # Phoneme embedding
    embedding_dim: int = 512
    n_phonemes: Optional[int] = None
    
    # Encoder
    encoder_dim: int = 512
    encoder_conv_layers: int = 3
    encoder_conv_kernel_size: int = 5
    encoder_conv_dropout: float = 0.5
    encoder_lstm_layers: int = 1
    encoder_lstm_dropout: float = 0.1
    
    # Decoder
    decoder_dim: int = 1024
    decoder_prenet_dim: List[int] = Field(default_factory=lambda: [256, 256])
    decoder_lstm_layers: int = 2
    decoder_lstm_dropout: float = 0.1
    decoder_zoneout: float = 0.1
    
    # Attention
    attention_dim: int = 128
    attention_location_features_dim: int = 32
    attention_location_kernel_size: int = 31
    
    # Postnet
    postnet_dim: int = 512
    postnet_kernel_size: int = 5
    postnet_layers: int = 5
    postnet_dropout: float = 0.5
    
    # Other parameters
    n_mels: int = 80
    stop_threshold: float = 0.5
    
    @validator('decoder_prenet_dim')
    def validate_prenet_dim(cls, v):
        """Validate prenet dimensions."""
        if len(v) < 1:
            raise ValueError("decoder_prenet_dim must have at least one layer")
        return v


class GriffinLimConfig(ModelConfig):
    """Configuration for Griffin-Lim vocoder."""
    name: str = "griffin_lim"
    
    # STFT parameters
    n_fft: int = 1024
    hop_length: int = 256
    win_length: int = 1024
    window: str = "hann"
    
    # Griffin-Lim parameters
    n_iter: int = 60
    power: float = 1.0
    momentum: float = 0.99
    
    # Audio parameters
    sample_rate: int = 22050
    
    @validator('window')
    def validate_window(cls, v):
        """Validate window function."""
        valid_windows = ["hann", "hamming", "blackman", "bartlett", "boxcar"]
        if v not in valid_windows:
            raise ValueError(f"window must be one of {valid_windows}")
        return v


def load_model_config(
    config_path: str,
    model_type: Optional[str] = None,
) -> Dict:
    """
    Load model configuration from a YAML file.
    
    Args:
        config_path: Path to the YAML configuration file.
        model_type: Type of model to load configuration for.
            If None, the model type is determined from the configuration.
            
    Returns:
        Model configuration dictionary.
    """
    # Load configuration
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)
    
    # Extract model configuration if it's under a 'model' key
    if isinstance(config_data, dict) and "model" in config_data:
        model_config = config_data["model"]
    else:
        model_config = config_data
    
    # Get model type from configuration if not provided
    if model_type is None and "name" in model_config:
        model_type = model_config["name"]
    
    # Validate configuration based on model type
    if model_type == "tacotron2":
        config_model = Tacotron2Config(**model_config)
    elif model_type == "griffin_lim":
        config_model = GriffinLimConfig(**model_config)
    else:
        # Just return the raw configuration if model type is unknown
        return model_config
    
    # Return validated configuration as dictionary
    return config_model.dict()


def save_model_config(
    config: Dict,
    config_path: str,
    model_type: Optional[str] = None,
) -> None:
    """
    Save model configuration to a YAML file.
    
    Args:
        config: Model configuration dictionary.
        config_path: Path to save the YAML configuration file.
        model_type: Type of model to save configuration for.
            If None, the model type is determined from the configuration.
    """
    # Get model type from configuration if not provided
    if model_type is None and "name" in config:
        model_type = config["name"]
    
    # Validate configuration based on model type
    if model_type == "tacotron2":
        config_model = Tacotron2Config(**config)
        config = config_model.dict()
    elif model_type == "griffin_lim":
        config_model = GriffinLimConfig(**config)
        config = config_model.dict()
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)
    
    # Save configuration
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump({"model": config}, f, default_flow_style=False)
"""
Model factory for Kalakan TTS.

This module provides a factory for creating models with proper configuration
handling, parameter validation, and automatic parameter mapping between
configuration files and model implementations.
"""

import inspect
import logging
import os
from typing import Any, Dict, List, Optional, Type, Union

import torch
import yaml

from kalakan.models.acoustic.base_acoustic import BaseAcousticModel
from kalakan.models.acoustic.tacotron2 import Tacotron2
from kalakan.models.vocoders.base_vocoder import BaseVocoder
from kalakan.models.vocoders.griffin_lim import GriffinLim
from kalakan.utils.config import Config
from kalakan.utils.model_config import load_model_config


logger = logging.getLogger(__name__)


class ModelFactory:
    """
    Factory for creating models with proper configuration handling.
    
    This class provides methods for creating models with proper configuration
    handling, parameter validation, and automatic parameter mapping between
    configuration files and model implementations.
    """
    
    # Registry of available models
    ACOUSTIC_MODELS = {
        "tacotron2": Tacotron2,
    }
    
    VOCODERS = {
        "griffin_lim": GriffinLim,
    }
    
    @classmethod
    def create_acoustic_model(
        cls,
        model_type: Optional[str] = None,
        config: Optional[Union[Dict, Config, str]] = None,
        checkpoint_path: Optional[str] = None,
        device: Optional[torch.device] = None,
    ) -> BaseAcousticModel:
        """
        Create an acoustic model with proper configuration handling.
        
        Args:
            model_type: Type of acoustic model to create.
                If None, the model type is determined from the configuration.
            config: Configuration for the model.
                Can be a dictionary, Config object, or path to a YAML file.
            checkpoint_path: Path to a checkpoint file to load.
            device: Device to place the model on.
                
        Returns:
            Created acoustic model.
        """
        # Get model type from configuration if not provided
        if model_type is None and isinstance(config, dict) and "name" in config:
            model_type = config["name"]
        elif model_type is None:
            model_type = "tacotron2"
            
        # Load configuration with model type
        model_config = cls._load_config(config, model_type)
        
        # Get model class
        if model_type not in cls.ACOUSTIC_MODELS:
            raise ValueError(f"Unsupported acoustic model: {model_type}")
        model_class = cls.ACOUSTIC_MODELS[model_type]
        
        # Create model with filtered parameters
        filtered_params = cls._filter_params(model_class, model_config)
        model = model_class(**filtered_params)
        
        # Load checkpoint if provided
        if checkpoint_path is not None:
            cls._load_checkpoint(model, checkpoint_path, device)
        
        # Move model to device
        if device is not None:
            model = model.to(device)
        
        return model
    
    @classmethod
    def create_vocoder(
        cls,
        model_type: Optional[str] = None,
        config: Optional[Union[Dict, Config, str]] = None,
        checkpoint_path: Optional[str] = None,
        device: Optional[torch.device] = None,
    ) -> BaseVocoder:
        """
        Create a vocoder with proper configuration handling.
        
        Args:
            model_type: Type of vocoder to create.
                If None, the model type is determined from the configuration.
            config: Configuration for the model.
                Can be a dictionary, Config object, or path to a YAML file.
            checkpoint_path: Path to a checkpoint file to load.
            device: Device to place the model on.
                
        Returns:
            Created vocoder.
        """
        # Get model type from configuration if not provided
        if model_type is None and isinstance(config, dict) and "name" in config:
            model_type = config["name"]
        elif model_type is None:
            model_type = "griffin_lim"
            
        # Load configuration with model type
        model_config = cls._load_config(config, model_type)
        
        # Get model class
        if model_type not in cls.VOCODERS:
            raise ValueError(f"Unsupported vocoder: {model_type}")
        model_class = cls.VOCODERS[model_type]
        
        # Create model with filtered parameters
        filtered_params = cls._filter_params(model_class, model_config)
        model = model_class(**filtered_params)
        
        # Load checkpoint if provided
        if checkpoint_path is not None:
            cls._load_checkpoint(model, checkpoint_path, device)
        
        # Move model to device
        if device is not None:
            model = model.to(device)
        
        return model
    
    @staticmethod
    def _load_config(config: Optional[Union[Dict, Config, str]], model_type: Optional[str] = None) -> Dict:
        """
        Load configuration from various sources.
        
        Args:
            config: Configuration source.
                Can be a dictionary, Config object, or path to a YAML file.
            model_type: Type of model to load configuration for.
                If None, the model type is determined from the configuration.
                
        Returns:
            Configuration dictionary.
        """
        if config is None:
            return {}
        elif isinstance(config, dict):
            return config
        elif isinstance(config, Config):
            return config.to_dict()
        elif isinstance(config, str) and os.path.exists(config):
            try:
                # Use the model_config module to load and validate the configuration
                return load_model_config(config, model_type)
            except Exception as e:
                logger.warning(f"Error loading model configuration: {e}")
                # Fall back to simple YAML loading
                with open(config, "r", encoding="utf-8") as f:
                    config_data = yaml.safe_load(f)
                    # Extract model configuration if it's under a 'model' key
                    if isinstance(config_data, dict) and "model" in config_data:
                        return config_data["model"]
                    return config_data
        else:
            logger.warning(f"Invalid configuration source: {config}")
            return {}
    
    @staticmethod
    def _filter_params(model_class: Type, config: Dict) -> Dict:
        """
        Filter configuration parameters to match model constructor parameters.
        
        Args:
            model_class: Model class to filter parameters for.
            config: Configuration dictionary.
                
        Returns:
            Filtered configuration dictionary.
        """
        # Get model constructor parameters
        signature = inspect.signature(model_class.__init__)
        valid_params = {
            param.name for param in signature.parameters.values()
            if param.name != "self"
        }
        
        # Filter configuration parameters
        filtered_params = {}
        for key, value in config.items():
            if key in valid_params:
                filtered_params[key] = value
            else:
                logger.debug(f"Ignoring parameter '{key}' for {model_class.__name__}")
        
        return filtered_params
    
    @staticmethod
    def _load_checkpoint(
        model: torch.nn.Module,
        checkpoint_path: str,
        device: Optional[torch.device] = None,
    ) -> None:
        """
        Load model checkpoint.
        
        Args:
            model: Model to load checkpoint into.
            checkpoint_path: Path to the checkpoint file.
            device: Device to load the checkpoint on.
        """
        # Determine device
        if device is None:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load checkpoint
        checkpoint = torch.load(checkpoint_path, map_location=device)
        
        # Load model state
        if "model_state_dict" in checkpoint:
            model.load_state_dict(checkpoint["model_state_dict"])
        else:
            logger.warning(f"No model state found in checkpoint: {checkpoint_path}")
        
        # Set model to evaluation mode
        model.eval()
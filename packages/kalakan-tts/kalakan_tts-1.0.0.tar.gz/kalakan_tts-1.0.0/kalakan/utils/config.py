"""
Configuration management for Kalakan TTS.

This module provides functionality for managing configuration settings
in Kalakan TTS, including loading and validating configuration files.
"""

import os
from typing import Any, Dict, List, Optional, Union

import yaml
from pydantic import BaseModel, Field, ValidationError


class Config:
    """
    Configuration manager for Kalakan TTS.
    
    This class provides methods for loading, validating, and accessing
    configuration settings in Kalakan TTS.
    """
    
    def __init__(self, config: Union[Dict, str, None] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config: Configuration dictionary, path to a YAML configuration file,
                or None to create an empty configuration.
        """
        # Initialize configuration
        self.config = {}
        
        # Load configuration if provided
        if config is not None:
            if isinstance(config, dict):
                self.config = config
            elif isinstance(config, str) and os.path.exists(config):
                self.load_yaml(config)
            else:
                raise ValueError(f"Invalid configuration: {config}")
    
    def load_yaml(self, yaml_path: str) -> None:
        """
        Load configuration from a YAML file.
        
        Args:
            yaml_path: Path to the YAML configuration file.
        """
        with open(yaml_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        # Update configuration
        self.config.update(config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key (can be nested using dot notation).
            default: Default value to return if the key is not found.
            
        Returns:
            Configuration value, or default if not found.
        """
        # Split key into parts
        parts = key.split(".")
        
        # Traverse configuration
        value = self.config
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key (can be nested using dot notation).
            value: Configuration value to set.
        """
        # Split key into parts
        parts = key.split(".")
        
        # Traverse configuration
        config = self.config
        for i, part in enumerate(parts[:-1]):
            if part not in config:
                config[part] = {}
            config = config[part]
        
        # Set value
        config[parts[-1]] = value
    
    def update(self, config: Dict) -> None:
        """
        Update configuration with another dictionary.
        
        Args:
            config: Configuration dictionary to update with.
        """
        self.config.update(config)
    
    def to_dict(self) -> Dict:
        """
        Convert configuration to a dictionary.
        
        Returns:
            Configuration dictionary.
        """
        return self.config
    
    def save_yaml(self, yaml_path: str) -> None:
        """
        Save configuration to a YAML file.
        
        Args:
            yaml_path: Path to save the YAML configuration file.
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(yaml_path)), exist_ok=True)
        
        # Save configuration
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(self.config, f, default_flow_style=False)
    
    def validate(self, model: BaseModel) -> None:
        """
        Validate configuration against a Pydantic model.
        
        Args:
            model: Pydantic model to validate against.
            
        Raises:
            ValidationError: If the configuration is invalid.
        """
        try:
            model(**self.config)
        except ValidationError as e:
            raise ValidationError(f"Invalid configuration: {e}")
    
    def __getitem__(self, key: str) -> Any:
        """
        Get a configuration value using dictionary syntax.
        
        Args:
            key: Configuration key.
            
        Returns:
            Configuration value.
            
        Raises:
            KeyError: If the key is not found.
        """
        value = self.get(key)
        if value is None:
            raise KeyError(f"Configuration key not found: {key}")
        return value
    
    def __setitem__(self, key: str, value: Any) -> None:
        """
        Set a configuration value using dictionary syntax.
        
        Args:
            key: Configuration key.
            value: Configuration value to set.
        """
        self.set(key, value)
    
    def __contains__(self, key: str) -> bool:
        """
        Check if a configuration key exists.
        
        Args:
            key: Configuration key.
            
        Returns:
            True if the key exists, False otherwise.
        """
        return self.get(key) is not None
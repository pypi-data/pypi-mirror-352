"""
Device management for Kalakan TTS.

This module provides functionality for managing devices (CPU/GPU)
in Kalakan TTS.
"""

from typing import Optional, Union

import torch


def get_device(device_id: Optional[Union[int, str]] = None) -> torch.device:
    """
    Get the device to use for computation.
    
    Args:
        device_id: Device ID to use. If None, the best available device is used.
            If "cpu", CPU is used. If an integer, the specified GPU is used.
            
    Returns:
        Device to use for computation.
    """
    # Use CPU if specified
    if device_id == "cpu":
        return torch.device("cpu")
    
    # Use CUDA if available
    if torch.cuda.is_available():
        if device_id is None:
            # Use the first available GPU
            return torch.device("cuda:0")
        elif isinstance(device_id, int):
            # Use the specified GPU
            if device_id < torch.cuda.device_count():
                return torch.device(f"cuda:{device_id}")
            else:
                print(f"Warning: GPU {device_id} not found, using CPU instead")
                return torch.device("cpu")
        else:
            # Use the specified device
            return torch.device(device_id)
    
    # Use CPU if CUDA is not available
    print("Warning: CUDA not available, using CPU instead")
    return torch.device("cpu")


def get_available_memory(device: Optional[torch.device] = None) -> int:
    """
    Get the amount of available memory on the device.
    
    Args:
        device: Device to check. If None, the current device is used.
            
    Returns:
        Amount of available memory in bytes.
    """
    # Use current device if not specified
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Check if device is CPU
    if device.type == "cpu":
        # Not implemented for CPU
        return 0
    
    # Get device index
    device_idx = device.index if device.index is not None else 0
    
    # Get memory usage
    torch.cuda.synchronize(device)
    total_memory = torch.cuda.get_device_properties(device_idx).total_memory
    allocated_memory = torch.cuda.memory_allocated(device_idx)
    reserved_memory = torch.cuda.memory_reserved(device_idx)
    
    # Calculate available memory
    available_memory = total_memory - allocated_memory - reserved_memory
    
    return available_memory


def clear_cuda_cache() -> None:
    """
    Clear the CUDA cache.
    """
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
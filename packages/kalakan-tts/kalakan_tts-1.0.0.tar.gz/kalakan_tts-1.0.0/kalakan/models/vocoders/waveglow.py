"""
WaveGlow vocoder for Kalakan TTS.

This module implements the WaveGlow model for converting mel spectrograms
to audio waveforms, as described in "WaveGlow: A Flow-based Generative
Network for Speech Synthesis" (Prenger et al., 2019).
"""

from typing import Dict, List, Optional, Tuple, Union

import torch
import torch.nn as nn
import torch.nn.functional as F

from kalakan.models.vocoders.base_vocoder import BaseVocoder


class WaveGlow(BaseVocoder):
    """
    WaveGlow vocoder for Kalakan TTS.
    
    This vocoder converts mel spectrograms to audio waveforms using
    a flow-based generative model.
    """
    
    def __init__(
        self,
        n_mels: int = 80,
        sample_rate: int = 22050,
        hop_length: int = 256,
        n_flows: int = 12,
        n_group: int = 8,
        n_early_every: int = 4,
        n_early_size: int = 2,
        n_layers: int = 8,
        n_channels: int = 256,
        kernel_size: int = 3,
        sigma: float = 1.0,
    ):
        """
        Initialize the WaveGlow vocoder.
        
        Args:
            n_mels: Number of mel bands in the input mel spectrogram.
            sample_rate: Audio sample rate.
            hop_length: Hop length between frames.
            n_flows: Number of flow steps.
            n_group: Number of samples in a group.
            n_early_every: Number of flows between early outputs.
            n_early_size: Size of early outputs.
            n_layers: Number of layers in each WaveNet.
            n_channels: Number of channels in the WaveNet.
            kernel_size: Kernel size for the WaveNet.
            sigma: Standard deviation of the Gaussian prior.
        """
        super().__init__(n_mels=n_mels, sample_rate=sample_rate, hop_length=hop_length)
        
        # Set model name
        self.model_name = "waveglow"
        
        # Set parameters
        self.n_flows = n_flows
        self.n_group = n_group
        self.n_early_every = n_early_every
        self.n_early_size = n_early_size
        self.sigma = sigma
        
        # Calculate remaining channels at the output of the last coupling layer
        self.n_remaining_channels = n_group
        for i in range(n_flows):
            if i % n_early_every == 0 and i > 0:
                self.n_remaining_channels -= n_early_size
        
        # Create upsample network
        self.upsample = nn.ConvTranspose1d(
            n_mels,
            n_mels,
            kernel_size=hop_length * 2,
            stride=hop_length,
            padding=hop_length // 2 + hop_length % 2,
            output_padding=hop_length % 2,
        )
        
        # Create WaveNet and Invertible 1x1 Conv layers
        self.WN = nn.ModuleList()
        self.convinv = nn.ModuleList()
        
        # Set up the flows
        for i in range(n_flows):
            # Check if we need to output channels
            if i % n_early_every == 0 and i > 0:
                n_half = n_group - n_early_size
            else:
                n_half = n_group // 2
            
            # Create invertible 1x1 convolution
            self.convinv.append(Invertible1x1Conv(n_group))
            
            # Create affine coupling layer (WaveNet)
            self.WN.append(WaveNet(
                n_half=n_half,
                n_mels=n_mels,
                n_layers=n_layers,
                n_channels=n_channels,
                kernel_size=kernel_size,
            ))
    
    def forward(
        self,
        mels: torch.Tensor,
        audio: Optional[torch.Tensor] = None,
        sigma: Optional[float] = None,
    ) -> Union[torch.Tensor, Tuple[torch.Tensor, List[torch.Tensor]]]:
        """
        Forward pass of the WaveGlow vocoder.
        
        Args:
            mels: Mel spectrograms [batch_size, n_mels, time].
            audio: Audio waveforms for training [batch_size, time*hop_length].
            sigma: Standard deviation of the Gaussian prior.
                
        Returns:
            If audio is provided (training mode):
                Tuple containing:
                    - Negative log-likelihood [batch_size].
                    - List of z tensors.
            If audio is not provided (inference mode):
                Generated audio waveforms [batch_size, time*hop_length].
        """
        if audio is not None:
            # Training mode
            return self._forward_training(mels, audio)
        else:
            # Inference mode
            return self._forward_inference(mels, sigma)
    
    def _forward_training(
        self,
        mels: torch.Tensor,
        audio: torch.Tensor,
    ) -> Tuple[torch.Tensor, List[torch.Tensor]]:
        """
        Forward pass for training.
        
        Args:
            mels: Mel spectrograms [batch_size, n_mels, time].
            audio: Audio waveforms [batch_size, time*hop_length].
                
        Returns:
            Tuple containing:
                - Negative log-likelihood [batch_size].
                - List of z tensors.
        """
        # Upsample mel spectrograms
        mels = self.upsample(mels)
        
        # Adjust audio and mel lengths
        if mels.size(2) > audio.size(1):
            mels = mels[:, :, :audio.size(1)]
        elif mels.size(2) < audio.size(1):
            audio = audio[:, :mels.size(2)]
        
        # Group audio
        batch_size, n_mels_channels, n_mels_steps = mels.size()
        audio = audio.unfold(1, self.n_group, self.n_group).permute(0, 2, 1)
        output_audio = []
        
        # Initialize log determinant
        log_det_W = 0
        
        # Initialize z
        z = []
        
        # Forward pass through flows
        for i in range(self.n_flows):
            # Split audio into two parts
            if i % self.n_early_every == 0 and i > 0:
                # Split off early outputs
                early_output = audio[:, :self.n_early_size, :]
                audio = audio[:, self.n_early_size:, :]
                z.append(early_output)
            else:
                # Split in half
                audio, log_det = self.convinv[i](audio)
                log_det_W = log_det_W + log_det
                
                # Split audio
                audio_0, audio_1 = audio.chunk(2, dim=1)
                
                # Compute WaveNet output
                output = self.WN[i](audio_0, mels)
                
                # Compute log determinant
                log_s = output[:, :audio_0.size(1), :]
                b = output[:, audio_0.size(1):, :]
                
                # Affine transformation
                audio_1 = torch.exp(log_s) * audio_1 + b
                
                # Concatenate audio
                audio = torch.cat([audio_0, audio_1], dim=1)
        
        # Add remaining channels to z
        z.append(audio)
        
        # Compute negative log-likelihood
        nll = 0.5 * torch.sum(torch.cat([torch.sum(z_i ** 2, [1, 2]) for z_i in z], dim=0))
        nll = nll - log_det_W
        
        return nll, z
    
    def _forward_inference(
        self,
        mels: torch.Tensor,
        sigma: Optional[float] = None,
    ) -> torch.Tensor:
        """
        Forward pass for inference.
        
        Args:
            mels: Mel spectrograms [batch_size, n_mels, time].
            sigma: Standard deviation of the Gaussian prior.
                
        Returns:
            Generated audio waveforms [batch_size, time*hop_length].
        """
        # Set sigma
        if sigma is None:
            sigma = self.sigma
        
        # Upsample mel spectrograms
        mels = self.upsample(mels)
        
        # Get batch size and number of steps
        batch_size, n_mels_channels, n_mels_steps = mels.size()
        
        # Generate Gaussian noise
        z = []
        
        # Generate remaining channels
        remaining_channels = self.n_remaining_channels
        audio = torch.randn(batch_size, remaining_channels, n_mels_steps, device=mels.device) * sigma
        
        # Backward pass through flows
        for i in reversed(range(self.n_flows)):
            # Check if we need to add early outputs
            if i % self.n_early_every == 0 and i > 0:
                # Add early outputs
                z_i = torch.randn(batch_size, self.n_early_size, n_mels_steps, device=mels.device) * sigma
                audio = torch.cat([z_i, audio], dim=1)
            
            # Split audio
            audio_0, audio_1 = audio.chunk(2, dim=1)
            
            # Compute WaveNet output
            output = self.WN[i](audio_0, mels)
            
            # Compute log_s and b
            log_s = output[:, :audio_0.size(1), :]
            b = output[:, audio_0.size(1):, :]
            
            # Inverse affine transformation
            audio_1 = (audio_1 - b) / torch.exp(log_s)
            
            # Concatenate audio
            audio = torch.cat([audio_0, audio_1], dim=1)
            
            # Inverse 1x1 convolution
            audio = self.convinv[i].inverse(audio)
        
        # Reshape audio
        audio = audio.permute(0, 2, 1).contiguous().view(batch_size, -1)
        
        return audio
    
    def inference(self, mels: torch.Tensor) -> torch.Tensor:
        """
        Generate audio from mel spectrograms (inference mode).
        
        Args:
            mels: Mel spectrograms [batch_size, n_mels, time].
                
        Returns:
            Generated audio waveforms [batch_size, time*hop_length].
        """
        # Set model to evaluation mode
        self.eval()
        
        # Forward pass
        with torch.no_grad():
            audio = self._forward_inference(mels)
        
        return audio


class Invertible1x1Conv(nn.Module):
    """
    Invertible 1x1 convolution for WaveGlow.
    
    This module implements a 1x1 convolution with a weight matrix that
    can be inverted.
    """
    
    def __init__(self, c: int):
        """
        Initialize the invertible 1x1 convolution.
        
        Args:
            c: Number of channels.
        """
        super().__init__()
        
        # Initialize weight matrix
        W = torch.qr(torch.randn(c, c))[0]
        
        # Register weight as parameter
        self.W = nn.Parameter(W)
        self.c = c
    
    def forward(self, z: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass of the invertible 1x1 convolution.
        
        Args:
            z: Input tensor [batch_size, channels, time].
                
        Returns:
            Tuple containing:
                - Output tensor [batch_size, channels, time].
                - Log determinant of the weight matrix.
        """
        # Compute log determinant
        log_det_W = torch.logdet(self.W) * z.size(2)
        
        # Reshape weight matrix
        W = self.W.view(self.c, self.c, 1)
        
        # Apply convolution
        z = F.conv1d(z, W)
        
        return z, log_det_W
    
    def inverse(self, z: torch.Tensor) -> torch.Tensor:
        """
        Inverse pass of the invertible 1x1 convolution.
        
        Args:
            z: Input tensor [batch_size, channels, time].
                
        Returns:
            Output tensor [batch_size, channels, time].
        """
        # Compute inverse weight matrix
        W_inverse = torch.inverse(self.W)
        
        # Reshape inverse weight matrix
        W_inverse = W_inverse.view(self.c, self.c, 1)
        
        # Apply inverse convolution
        z = F.conv1d(z, W_inverse)
        
        return z


class WaveNet(nn.Module):
    """
    WaveNet for WaveGlow.
    
    This module implements the WaveNet used in the affine coupling layers
    of WaveGlow.
    """
    
    def __init__(
        self,
        n_half: int,
        n_mels: int,
        n_layers: int = 8,
        n_channels: int = 256,
        kernel_size: int = 3,
    ):
        """
        Initialize the WaveNet.
        
        Args:
            n_half: Number of channels in the input.
            n_mels: Number of mel bands.
            n_layers: Number of layers in the WaveNet.
            n_channels: Number of channels in the WaveNet.
            kernel_size: Kernel size for the WaveNet.
        """
        super().__init__()
        
        # Create initial convolution
        self.in_layers = nn.ModuleList()
        self.res_skip_layers = nn.ModuleList()
        self.cond_layers = nn.ModuleList()
        
        # Initial convolution
        self.start = nn.Conv1d(n_half, n_channels, 1)
        
        # Create dilated convolutions
        for i in range(n_layers):
            dilation = 2 ** i
            padding = int((kernel_size * dilation - dilation) / 2)
            
            # Create in layer (dilated convolution)
            self.in_layers.append(nn.Conv1d(
                n_channels,
                n_channels * 2,
                kernel_size,
                dilation=dilation,
                padding=padding,
            ))
            
            # Create conditioning layer
            self.cond_layers.append(nn.Conv1d(
                n_mels,
                n_channels * 2,
                1,
            ))
            
            # Create residual and skip connections
            self.res_skip_layers.append(nn.Conv1d(
                n_channels,
                n_channels + n_half,
                1,
            ))
        
        # Create final convolution
        self.end = nn.Conv1d(n_channels, n_half * 2, 1)
    
    def forward(self, audio: torch.Tensor, mels: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of the WaveNet.
        
        Args:
            audio: Audio input [batch_size, n_half, time].
            mels: Mel spectrogram [batch_size, n_mels, time].
                
        Returns:
            Output tensor [batch_size, n_half*2, time].
        """
        # Initial convolution
        audio = self.start(audio)
        
        # Initialize skip connection
        output = torch.zeros_like(audio)
        n_channels_tensor = torch.IntTensor([self.in_layers[0].out_channels // 2])
        
        # Apply dilated convolutions
        for i, (in_layer, cond_layer, res_skip_layer) in enumerate(zip(
            self.in_layers, self.cond_layers, self.res_skip_layers
        )):
            # Apply dilated convolution
            acts = in_layer(audio)
            
            # Apply conditioning
            cond_acts = cond_layer(mels)
            
            # Add conditioning
            acts = acts + cond_acts
            
            # Split into gate and filter
            audio_filter, audio_gate = acts.chunk(2, dim=1)
            
            # Apply gated activation
            acts = torch.tanh(audio_filter) * torch.sigmoid(audio_gate)
            
            # Apply residual and skip connections
            res_skip_acts = res_skip_layer(acts)
            skip_acts = res_skip_acts[:, n_channels_tensor[0]:, :]
            res_acts = res_skip_acts[:, :n_channels_tensor[0], :]
            
            # Add residual connection
            audio = audio + res_acts
            
            # Add skip connection
            output = output + skip_acts
        
        # Final convolution
        output = self.end(F.relu(output))
        
        return output
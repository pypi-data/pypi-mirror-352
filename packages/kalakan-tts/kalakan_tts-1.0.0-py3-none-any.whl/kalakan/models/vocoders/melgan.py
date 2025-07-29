"""
MelGAN vocoder for Kalakan TTS.

This module implements the MelGAN model for converting mel spectrograms
to audio waveforms, as described in "MelGAN: Generative Adversarial Networks
for Conditional Waveform Synthesis" (Kumar et al., 2019).
"""

from typing import Dict, List, Optional, Tuple, Union

import torch
import torch.nn as nn
import torch.nn.functional as F

from kalakan.models.vocoders.base_vocoder import BaseVocoder


class MelGAN(BaseVocoder):
    """
    MelGAN vocoder for Kalakan TTS.
    
    This vocoder converts mel spectrograms to audio waveforms using
    a generative adversarial network with multi-scale discriminators.
    """
    
    def __init__(
        self,
        n_mels: int = 80,
        sample_rate: int = 22050,
        hop_length: int = 256,
        ngf: int = 32,
        n_residual_layers: int = 3,
        ratios: List[int] = [8, 8, 2, 2],
        use_weight_norm: bool = True,
    ):
        """
        Initialize the MelGAN vocoder.
        
        Args:
            n_mels: Number of mel bands in the input mel spectrogram.
            sample_rate: Audio sample rate.
            hop_length: Hop length between frames.
            ngf: Number of generator filters in the first convolutional layer.
            n_residual_layers: Number of residual layers in each upsampling block.
            ratios: List of upsampling ratios.
            use_weight_norm: Whether to use weight normalization.
        """
        super().__init__(n_mels=n_mels, sample_rate=sample_rate, hop_length=hop_length)
        
        # Set model name
        self.model_name = "melgan"
        
        # Set parameters
        self.ngf = ngf
        self.n_residual_layers = n_residual_layers
        self.ratios = ratios
        self.use_weight_norm = use_weight_norm
        
        # Calculate total upsampling factor
        self.total_upsampling = 1
        for ratio in ratios:
            self.total_upsampling *= ratio
        
        # Check if total upsampling matches hop length
        if self.total_upsampling != self.hop_length:
            raise ValueError(f"Total upsampling factor {self.total_upsampling} must match hop length {self.hop_length}")
        
        # Create generator
        self.generator = Generator(
            n_mels=n_mels,
            ngf=ngf,
            n_residual_layers=n_residual_layers,
            ratios=ratios,
            use_weight_norm=use_weight_norm,
        )
    
    def forward(self, mels: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of the MelGAN vocoder.
        
        Args:
            mels: Mel spectrograms [batch_size, n_mels, time].
                
        Returns:
            Generated audio waveforms [batch_size, time*hop_length].
        """
        return self.generator(mels)
    
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
            audio = self.forward(mels)
        
        return audio


class ResidualStack(nn.Module):
    """
    Residual stack for MelGAN.
    
    This module consists of a stack of residual blocks with dilated convolutions.
    """
    
    def __init__(
        self,
        channels: int,
        dilation: int = 1,
        use_weight_norm: bool = True,
    ):
        """
        Initialize the residual stack.
        
        Args:
            channels: Number of channels.
            dilation: Dilation factor.
            use_weight_norm: Whether to use weight normalization.
        """
        super().__init__()
        
        # Create residual block
        self.block = nn.Sequential(
            nn.LeakyReLU(0.2),
            nn.ReflectionPad1d(dilation),
            nn.utils.weight_norm(nn.Conv1d(channels, channels, kernel_size=3, dilation=dilation))
            if use_weight_norm else nn.Conv1d(channels, channels, kernel_size=3, dilation=dilation),
            nn.LeakyReLU(0.2),
            nn.utils.weight_norm(nn.Conv1d(channels, channels, kernel_size=1))
            if use_weight_norm else nn.Conv1d(channels, channels, kernel_size=1),
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of the residual stack.
        
        Args:
            x: Input tensor [batch_size, channels, time].
                
        Returns:
            Output tensor [batch_size, channels, time].
        """
        return x + self.block(x)


class Generator(nn.Module):
    """
    Generator for MelGAN.
    
    This module converts mel spectrograms to audio waveforms.
    """
    
    def __init__(
        self,
        n_mels: int = 80,
        ngf: int = 32,
        n_residual_layers: int = 3,
        ratios: List[int] = [8, 8, 2, 2],
        use_weight_norm: bool = True,
    ):
        """
        Initialize the generator.
        
        Args:
            n_mels: Number of mel bands in the input mel spectrogram.
            ngf: Number of generator filters in the first convolutional layer.
            n_residual_layers: Number of residual layers in each upsampling block.
            ratios: List of upsampling ratios.
            use_weight_norm: Whether to use weight normalization.
        """
        super().__init__()
        
        # Create initial convolution
        self.initial = nn.Sequential(
            nn.ReflectionPad1d(3),
            nn.utils.weight_norm(nn.Conv1d(n_mels, ngf * 2, kernel_size=7))
            if use_weight_norm else nn.Conv1d(n_mels, ngf * 2, kernel_size=7),
        )
        
        # Create upsampling blocks
        self.upsample_blocks = nn.ModuleList()
        current_channels = ngf * 2
        
        for i, ratio in enumerate(ratios):
            out_channels = ngf * 2 // (2 ** (i + 1))
            
            # Create upsampling block
            block = nn.ModuleList([
                nn.LeakyReLU(0.2),
                nn.utils.weight_norm(
                    nn.ConvTranspose1d(
                        current_channels,
                        out_channels,
                        kernel_size=ratio * 2,
                        stride=ratio,
                        padding=ratio // 2 + ratio % 2,
                        output_padding=ratio % 2,
                    )
                ) if use_weight_norm else nn.ConvTranspose1d(
                    current_channels,
                    out_channels,
                    kernel_size=ratio * 2,
                    stride=ratio,
                    padding=ratio // 2 + ratio % 2,
                    output_padding=ratio % 2,
                ),
            ])
            
            # Add residual stacks
            for j in range(n_residual_layers):
                block.append(ResidualStack(out_channels, dilation=3 ** j, use_weight_norm=use_weight_norm))
            
            self.upsample_blocks.append(nn.Sequential(*block))
            current_channels = out_channels
        
        # Create output convolution
        self.output = nn.Sequential(
            nn.LeakyReLU(0.2),
            nn.ReflectionPad1d(3),
            nn.utils.weight_norm(nn.Conv1d(current_channels, 1, kernel_size=7))
            if use_weight_norm else nn.Conv1d(current_channels, 1, kernel_size=7),
            nn.Tanh(),
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of the generator.
        
        Args:
            x: Mel spectrogram [batch_size, n_mels, time].
                
        Returns:
            Generated audio waveform [batch_size, 1, time*hop_length].
        """
        # Initial convolution
        x = self.initial(x)
        
        # Apply upsampling blocks
        for block in self.upsample_blocks:
            x = block(x)
        
        # Output convolution
        x = self.output(x)
        
        return x


class Discriminator(nn.Module):
    """
    Discriminator for MelGAN.
    
    This module consists of multiple sub-discriminators operating at
    different scales.
    """
    
    def __init__(
        self,
        scales: int = 3,
        ndf: int = 16,
        n_layers: int = 4,
        downsampling_factor: int = 4,
        use_weight_norm: bool = True,
    ):
        """
        Initialize the discriminator.
        
        Args:
            scales: Number of sub-discriminators at different scales.
            ndf: Number of discriminator filters in the first convolutional layer.
            n_layers: Number of convolutional layers in each sub-discriminator.
            downsampling_factor: Downsampling factor for each scale.
            use_weight_norm: Whether to use weight normalization.
        """
        super().__init__()
        
        # Create sub-discriminators
        self.sub_discriminators = nn.ModuleList()
        
        for i in range(scales):
            self.sub_discriminators.append(
                SubDiscriminator(
                    ndf=ndf,
                    n_layers=n_layers,
                    use_weight_norm=use_weight_norm,
                )
            )
        
        # Create downsampling layers
        self.downsample = nn.AvgPool1d(
            kernel_size=downsampling_factor,
            stride=downsampling_factor,
            padding=downsampling_factor // 2,
            count_include_pad=False,
        )
    
    def forward(self, x: torch.Tensor) -> List[List[torch.Tensor]]:
        """
        Forward pass of the discriminator.
        
        Args:
            x: Audio waveform [batch_size, 1, time].
                
        Returns:
            List of outputs from each sub-discriminator, where each output is a list
            of feature maps from each layer.
        """
        results = []
        
        for i, discriminator in enumerate(self.sub_discriminators):
            if i > 0:
                x = self.downsample(x)
            
            results.append(discriminator(x))
        
        return results


class SubDiscriminator(nn.Module):
    """
    Sub-discriminator for MelGAN.
    
    This module is a convolutional discriminator operating at a specific scale.
    """
    
    def __init__(
        self,
        ndf: int = 16,
        n_layers: int = 4,
        use_weight_norm: bool = True,
    ):
        """
        Initialize the sub-discriminator.
        
        Args:
            ndf: Number of discriminator filters in the first convolutional layer.
            n_layers: Number of convolutional layers.
            use_weight_norm: Whether to use weight normalization.
        """
        super().__init__()
        
        # Create convolutional layers
        self.layers = nn.ModuleList()
        
        # Initial convolution
        self.layers.append(
            nn.Sequential(
                nn.ReflectionPad1d(7),
                nn.utils.weight_norm(nn.Conv1d(1, ndf, kernel_size=15))
                if use_weight_norm else nn.Conv1d(1, ndf, kernel_size=15),
                nn.LeakyReLU(0.2, True),
            )
        )
        
        # Additional convolutional layers
        nf = ndf
        stride = 1
        for i in range(n_layers):
            nf_prev = nf
            nf = min(nf * 2, 1024)
            stride = 2 if i < n_layers - 1 else 1
            
            self.layers.append(
                nn.Sequential(
                    nn.utils.weight_norm(nn.Conv1d(
                        nf_prev,
                        nf,
                        kernel_size=stride * 10 + 1,
                        stride=stride,
                        padding=stride * 5,
                        groups=nf_prev // 4,
                    )) if use_weight_norm else nn.Conv1d(
                        nf_prev,
                        nf,
                        kernel_size=stride * 10 + 1,
                        stride=stride,
                        padding=stride * 5,
                        groups=nf_prev // 4,
                    ),
                    nn.LeakyReLU(0.2, True),
                )
            )
        
        # Output convolution
        self.layers.append(
            nn.Sequential(
                nn.utils.weight_norm(nn.Conv1d(nf, 1, kernel_size=3, padding=1))
                if use_weight_norm else nn.Conv1d(nf, 1, kernel_size=3, padding=1),
            )
        )
    
    def forward(self, x: torch.Tensor) -> List[torch.Tensor]:
        """
        Forward pass of the sub-discriminator.
        
        Args:
            x: Audio waveform [batch_size, 1, time].
                
        Returns:
            List of feature maps from each layer.
        """
        results = []
        
        for layer in self.layers:
            x = layer(x)
            results.append(x)
        
        return results
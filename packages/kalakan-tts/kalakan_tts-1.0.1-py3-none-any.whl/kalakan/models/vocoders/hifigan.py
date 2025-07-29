"""
HiFi-GAN vocoder for Kalakan TTS.

This module implements the HiFi-GAN model for converting mel spectrograms
to audio waveforms, as described in "HiFi-GAN: Generative Adversarial Networks
for Efficient and High Fidelity Speech Synthesis" (Kong et al., 2020).
"""

from typing import Dict, List, Optional, Tuple, Union

import torch
import torch.nn as nn
import torch.nn.functional as F

from kalakan.models.vocoders.base_vocoder import BaseVocoder


class HiFiGAN(BaseVocoder):
    """
    HiFi-GAN vocoder for Kalakan TTS.

    This vocoder converts mel spectrograms to audio waveforms using
    a generative adversarial network with multi-period and multi-scale
    discriminators.
    """

    def __init__(
        self,
        n_mels: int = 80,
        sample_rate: int = 22050,
        hop_length: int = 256,
        upsample_rates: List[int] = [8, 8, 2, 2],
        upsample_kernel_sizes: List[int] = [16, 16, 4, 4],
        upsample_initial_channel: int = 512,
        resblock_kernel_sizes: List[int] = [3, 7, 11],
        resblock_dilation_sizes: List[List[int]] = [[1, 3, 5], [1, 3, 5], [1, 3, 5]],
        leaky_relu_slope: float = 0.1,
    ):
        """
        Initialize the HiFi-GAN vocoder.

        Args:
            n_mels: Number of mel bands in the input mel spectrogram.
            sample_rate: Audio sample rate.
            hop_length: Hop length between frames.
            upsample_rates: List of upsampling rates.
            upsample_kernel_sizes: List of kernel sizes for upsampling.
            upsample_initial_channel: Initial number of channels for upsampling.
            resblock_kernel_sizes: List of kernel sizes for resblocks.
            resblock_dilation_sizes: List of dilation sizes for resblocks.
            leaky_relu_slope: Slope for leaky ReLU.
        """
        super().__init__(n_mels=n_mels, sample_rate=sample_rate, hop_length=hop_length)

        # Set model name
        self.model_name = "hifigan"

        # Set parameters
        self.upsample_rates = upsample_rates
        self.upsample_kernel_sizes = upsample_kernel_sizes
        self.upsample_initial_channel = upsample_initial_channel
        self.resblock_kernel_sizes = resblock_kernel_sizes
        self.resblock_dilation_sizes = resblock_dilation_sizes
        self.leaky_relu_slope = leaky_relu_slope

        # Calculate total upsampling factor
        self.total_upsampling = 1
        for rate in upsample_rates:
            self.total_upsampling *= rate

        # Check if total upsampling matches hop length
        if self.total_upsampling != self.hop_length:
            raise ValueError(f"Total upsampling factor {self.total_upsampling} must match hop length {self.hop_length}")

        # Create initial convolution
        self.conv_pre = nn.utils.weight_norm(nn.Conv1d(
            n_mels, upsample_initial_channel, kernel_size=7, stride=1, padding=3
        ))

        # Create upsampling layers
        self.ups = nn.ModuleList()
        in_channels = upsample_initial_channel
        for i, (u_rate, u_kernel) in enumerate(zip(upsample_rates, upsample_kernel_sizes)):
            out_channels = in_channels // 2
            self.ups.append(
                nn.utils.weight_norm(nn.ConvTranspose1d(
                    in_channels,
                    out_channels,
                    kernel_size=u_kernel,
                    stride=u_rate,
                    padding=(u_kernel - u_rate) // 2,
                ))
            )
            in_channels = out_channels

        # Create resblocks
        self.resblocks = nn.ModuleList()
        for i in range(len(self.ups)):
            ch = in_channels
            for k, d in zip(resblock_kernel_sizes, resblock_dilation_sizes):
                self.resblocks.append(ResBlock(ch, k, d, leaky_relu_slope))

        # Create final convolution
        self.conv_post = nn.utils.weight_norm(nn.Conv1d(ch, 1, kernel_size=7, stride=1, padding=3))

    def forward(self, mels: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of the HiFi-GAN vocoder.

        Args:
            mels: Mel spectrograms [batch_size, n_mels, time].

        Returns:
            Generated audio waveforms [batch_size, time*hop_length].
        """
        # Initial convolution
        x = self.conv_pre(mels)

        # Apply upsampling and resblocks
        for i, up in enumerate(self.ups):
            x = F.leaky_relu(x, self.leaky_relu_slope)
            x = up(x)

            # Apply resblocks
            xs = None
            for j, resblock in enumerate(self.resblocks):
                if xs is None:
                    xs = resblock(x)
                else:
                    xs = xs + resblock(x)
            # Ensure xs is not None before division
            if xs is not None:
                x = xs / len(self.resblocks)
            else:
                # This should not happen if there's at least one resblock
                x = x  # Keep x unchanged if no resblocks were processed

        # Final convolution
        x = F.leaky_relu(x, self.leaky_relu_slope)
        x = self.conv_post(x)
        x = torch.tanh(x)

        return x

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

    def remove_weight_norm(self):
        """
        Remove weight normalization from all convolutional layers.

        This is important for inference as it can improve performance.
        Should be called after loading the model for inference.
        """
        import torch.nn.utils as nn_utils

        # Remove weight norm from convolutional layers
        if hasattr(self, 'conv_pre'):
            if hasattr(self.conv_pre, 'weight_g'):
                nn_utils.remove_weight_norm(self.conv_pre)

        # Remove from upsampling layers
        for layer in self.ups:
            if hasattr(layer, 'weight_g'):
                nn_utils.remove_weight_norm(layer)

        # Remove from final convolution
        if hasattr(self.conv_post, 'weight_g'):
            nn_utils.remove_weight_norm(self.conv_post)

        # Remove from resblocks
        for i, resblock in enumerate(self.resblocks):
            # Call the remove_weight_norm method on each ResBlock instance
            # We know these are ResBlock instances from our initialization
            if isinstance(resblock, ResBlock):
                resblock.remove_weight_norm()


class ResBlock(nn.Module):
    """
    Residual block for HiFi-GAN.

    This block consists of a stack of dilated convolutions with residual connections.
    """

    def __init__(
        self,
        channels: int,
        kernel_size: int,
        dilations: List[int],
        leaky_relu_slope: float = 0.1,
    ):
        """
        Initialize the residual block.

        Args:
            channels: Number of channels.
            kernel_size: Kernel size for convolutions.
            dilations: List of dilation factors.
            leaky_relu_slope: Slope for leaky ReLU.
        """
        super().__init__()

        self.leaky_relu_slope = leaky_relu_slope

        # Create dilated convolutions
        self.convs = nn.ModuleList()
        for dilation in dilations:
            self.convs.append(
                nn.utils.weight_norm(nn.Conv1d(
                    channels,
                    channels,
                    kernel_size,
                    stride=1,
                    padding=dilation * (kernel_size - 1) // 2,
                    dilation=dilation,
                ))
            )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of the residual block.

        Args:
            x: Input tensor [batch_size, channels, time].

        Returns:
            Output tensor [batch_size, channels, time].
        """
        for conv in self.convs:
            residual = x
            x = F.leaky_relu(x, self.leaky_relu_slope)
            x = conv(x)
            x = x + residual
        return x

    def remove_weight_norm(self):
        """
        Remove weight normalization from all convolutional layers in the resblock.
        """
        import torch.nn.utils as nn_utils

        for layer in self.convs:
            if hasattr(layer, 'weight_g'):
                nn_utils.remove_weight_norm(layer)


class MultiPeriodDiscriminator(nn.Module):
    """
    Multi-period discriminator for HiFi-GAN.

    This discriminator analyzes the audio at different periods to capture
    various aspects of the signal.
    """

    def __init__(
        self,
        periods: List[int] = [2, 3, 5, 7, 11],
        leaky_relu_slope: float = 0.1,
    ):
        """
        Initialize the multi-period discriminator.

        Args:
            periods: List of periods to analyze.
            leaky_relu_slope: Slope for leaky ReLU.
        """
        super().__init__()

        # Create period discriminators
        self.discriminators = nn.ModuleList([
            PeriodDiscriminator(period, leaky_relu_slope)
            for period in periods
        ])

    def forward(
        self,
        y: torch.Tensor,
        y_hat: torch.Tensor,
    ) -> Tuple[List[torch.Tensor], List[torch.Tensor], List[List[torch.Tensor]], List[List[torch.Tensor]]]:
        """
        Forward pass of the multi-period discriminator.

        Args:
            y: Real audio waveform [batch_size, 1, time].
            y_hat: Generated audio waveform [batch_size, 1, time].

        Returns:
            Tuple containing:
                - List of real outputs from each discriminator.
                - List of fake outputs from each discriminator.
                - List of lists of real feature maps from each discriminator.
                - List of lists of fake feature maps from each discriminator.
        """
        y_d_rs = []
        y_d_gs = []
        fmap_rs = []
        fmap_gs = []

        for discriminator in self.discriminators:
            y_d_r, fmap_r = discriminator(y)
            y_d_g, fmap_g = discriminator(y_hat)

            y_d_rs.append(y_d_r)
            y_d_gs.append(y_d_g)
            fmap_rs.append(fmap_r)
            fmap_gs.append(fmap_g)

        return y_d_rs, y_d_gs, fmap_rs, fmap_gs


class PeriodDiscriminator(nn.Module):
    """
    Period discriminator for HiFi-GAN.

    This discriminator analyzes the audio at a specific period.
    """

    def __init__(
        self,
        period: int,
        leaky_relu_slope: float = 0.1,
        kernel_size: int = 5,
        stride: int = 3,
        channels: List[int] = [32, 128, 512, 1024, 1024],
    ):
        """
        Initialize the period discriminator.

        Args:
            period: Period to analyze.
            leaky_relu_slope: Slope for leaky ReLU.
            kernel_size: Kernel size for convolutions.
            stride: Stride for convolutions.
            channels: List of channel sizes for convolutions.
        """
        super().__init__()

        self.period = period
        self.leaky_relu_slope = leaky_relu_slope

        # Create convolutional layers
        self.convs = nn.ModuleList()
        in_channels = 1
        for out_channels in channels:
            self.convs.append(
                nn.Conv2d(
                    in_channels,
                    out_channels,
                    kernel_size=(kernel_size, 1),
                    stride=(stride, 1),
                    padding=((kernel_size - 1) // 2, 0),
                )
            )
            in_channels = out_channels

        # Create final convolutional layer
        self.conv_post = nn.Conv2d(
            in_channels,
            1,
            kernel_size=(3, 1),
            stride=1,
            padding=(1, 0),
        )

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, List[torch.Tensor]]:
        """
        Forward pass of the period discriminator.

        Args:
            x: Audio waveform [batch_size, 1, time].

        Returns:
            Tuple containing:
                - Discriminator output [batch_size, 1, time'].
                - List of feature maps from each layer.
        """
        # Reshape input for 2D convolution
        batch_size, _, time = x.shape

        # Pad if needed
        if time % self.period != 0:
            pad_size = self.period - (time % self.period)
            x = F.pad(x, (0, pad_size))
            time = time + pad_size

        # Reshape to [batch_size, 1, time/period, period]
        x = x.view(batch_size, 1, time // self.period, self.period)

        # Apply convolutional layers
        feature_maps = []
        for conv in self.convs:
            x = conv(x)
            x = F.leaky_relu(x, self.leaky_relu_slope)
            feature_maps.append(x)

        # Apply final convolutional layer
        x = self.conv_post(x)
        feature_maps.append(x)

        # Reshape output
        x = x.flatten(1, -1)

        return x, feature_maps


class MultiScaleDiscriminator(nn.Module):
    """
    Multi-scale discriminator for HiFi-GAN.

    This discriminator analyzes the audio at different scales to capture
    both fine and coarse features.
    """

    def __init__(
        self,
        scales: int = 3,
        leaky_relu_slope: float = 0.1,
    ):
        """
        Initialize the multi-scale discriminator.

        Args:
            scales: Number of scales to analyze.
            leaky_relu_slope: Slope for leaky ReLU.
        """
        super().__init__()

        # Create scale discriminators
        self.discriminators = nn.ModuleList([
            ScaleDiscriminator(leaky_relu_slope)
            for _ in range(scales)
        ])

        # Create downsampling layers
        self.downsample = nn.AvgPool1d(kernel_size=4, stride=2, padding=1)

    def forward(
        self,
        y: torch.Tensor,
        y_hat: torch.Tensor,
    ) -> Tuple[List[torch.Tensor], List[torch.Tensor], List[List[torch.Tensor]], List[List[torch.Tensor]]]:
        """
        Forward pass of the multi-scale discriminator.

        Args:
            y: Real audio waveform [batch_size, 1, time].
            y_hat: Generated audio waveform [batch_size, 1, time].

        Returns:
            Tuple containing:
                - List of real outputs from each discriminator.
                - List of fake outputs from each discriminator.
                - List of lists of real feature maps from each discriminator.
                - List of lists of fake feature maps from each discriminator.
        """
        y_d_rs = []
        y_d_gs = []
        fmap_rs = []
        fmap_gs = []

        for i, discriminator in enumerate(self.discriminators):
            if i > 0:
                y = self.downsample(y)
                y_hat = self.downsample(y_hat)

            y_d_r, fmap_r = discriminator(y)
            y_d_g, fmap_g = discriminator(y_hat)

            y_d_rs.append(y_d_r)
            y_d_gs.append(y_d_g)
            fmap_rs.append(fmap_r)
            fmap_gs.append(fmap_g)

        return y_d_rs, y_d_gs, fmap_rs, fmap_gs


class ScaleDiscriminator(nn.Module):
    """
    Scale discriminator for HiFi-GAN.

    This discriminator analyzes the audio at a specific scale.
    """

    def __init__(
        self,
        leaky_relu_slope: float = 0.1,
        kernel_size: int = 15,
        stride: int = 1,
        channels: List[int] = [16, 64, 256, 1024, 1024],
        groups: List[int] = [1, 4, 16, 64, 256],
    ):
        """
        Initialize the scale discriminator.

        Args:
            leaky_relu_slope: Slope for leaky ReLU.
            kernel_size: Kernel size for convolutions.
            stride: Stride for convolutions.
            channels: List of channel sizes for convolutions.
            groups: List of group sizes for convolutions.
        """
        super().__init__()

        self.leaky_relu_slope = leaky_relu_slope

        # Create convolutional layers
        self.convs = nn.ModuleList()
        in_channels = 1
        for i, (out_channels, group) in enumerate(zip(channels, groups)):
            self.convs.append(
                nn.Conv1d(
                    in_channels,
                    out_channels,
                    kernel_size=kernel_size,
                    stride=stride,
                    padding=(kernel_size - 1) // 2,
                    groups=group if i > 0 else 1,
                )
            )
            in_channels = out_channels

        # Create final convolutional layer
        self.conv_post = nn.Conv1d(
            in_channels,
            1,
            kernel_size=3,
            stride=1,
            padding=1,
        )

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, List[torch.Tensor]]:
        """
        Forward pass of the scale discriminator.

        Args:
            x: Audio waveform [batch_size, 1, time].

        Returns:
            Tuple containing:
                - Discriminator output [batch_size, 1, time'].
                - List of feature maps from each layer.
        """
        # Apply convolutional layers
        feature_maps = []
        for conv in self.convs:
            x = conv(x)
            x = F.leaky_relu(x, self.leaky_relu_slope)
            feature_maps.append(x)

        # Apply final convolutional layer
        x = self.conv_post(x)
        feature_maps.append(x)

        # Reshape output
        x = x.flatten(1, -1)

        return x, feature_maps
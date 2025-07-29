# Kalakan TTS API Reference

This document provides a comprehensive reference for the Kalakan TTS API, including all public classes, methods, and functions.

## Table of Contents

1. [Synthesizer](#synthesizer)
2. [Text Processing](#text-processing)
3. [Acoustic Models](#acoustic-models)
4. [Vocoders](#vocoders)
5. [Audio Processing](#audio-processing)
6. [Configuration](#configuration)
7. [Model Factory](#model-factory)
8. [CLI Tools](#cli-tools)
9. [REST API](#rest-api)
10. [gRPC API](#grpc-api)

## Synthesizer

The `Synthesizer` class is the main interface for text-to-speech synthesis in Kalakan.

### `kalakan.synthesis.synthesizer.Synthesizer`

```python
class Synthesizer:
    def __init__(
        self,
        acoustic_model: Optional[Union[BaseAcousticModel, str]] = None,
        vocoder: Optional[Union[BaseVocoder, str]] = None,
        g2p: Optional[TwiG2P] = None,
        device: Optional[torch.device] = None,
        config: Optional[Union[Dict, Config, str]] = None,
        acoustic_model_type: Optional[str] = None,
        vocoder_type: Optional[str] = None,
    )
```

Initialize the synthesizer with the specified models and configuration.

**Parameters:**
- `acoustic_model`: Acoustic model to use, or path to a checkpoint file. If None, a default acoustic model is used based on configuration.
- `vocoder`: Vocoder to use, or path to a checkpoint file. If None, a default vocoder is used based on configuration.
- `g2p`: Grapheme-to-phoneme converter to use. If None, a default TwiG2P converter is used.
- `device`: Device to use for inference.
- `config`: Configuration for the synthesizer.
- `acoustic_model_type`: Type of acoustic model to use if creating a new one. If None, the type is determined from the configuration.
- `vocoder_type`: Type of vocoder to use if creating a new one. If None, the type is determined from the configuration.

### Methods

#### `synthesize`

```python
def synthesize(
    self,
    text: str,
    normalize: bool = True,
    clean: bool = True,
    max_length: Optional[int] = None,
) -> torch.Tensor
```

Synthesize speech from text.

**Parameters:**
- `text`: Input text.
- `normalize`: Whether to normalize the text.
- `clean`: Whether to clean the text.
- `max_length`: Maximum length of generated mel spectrograms.

**Returns:**
- Generated audio waveform as a PyTorch tensor.

#### `synthesize_batch`

```python
def synthesize_batch(
    self,
    texts: List[str],
    normalize: bool = True,
    clean: bool = True,
    max_length: Optional[int] = None,
    batch_size: int = 8,
) -> List[torch.Tensor]
```

Synthesize speech from a batch of texts.

**Parameters:**
- `texts`: List of input texts.
- `normalize`: Whether to normalize the texts.
- `clean`: Whether to clean the texts.
- `max_length`: Maximum length of generated mel spectrograms.
- `batch_size`: Batch size for inference.

**Returns:**
- List of generated audio waveforms as PyTorch tensors.

#### `save_audio`

```python
def save_audio(
    self,
    audio: torch.Tensor,
    file_path: str,
    sample_rate: Optional[int] = None,
) -> None
```

Save audio to a file.

**Parameters:**
- `audio`: Audio waveform.
- `file_path`: Path to save the audio file.
- `sample_rate`: Sample rate of the audio. If None, the vocoder's sample rate is used.

#### `text_to_speech`

```python
def text_to_speech(
    self,
    text: str,
    output_file: str,
    normalize: bool = True,
    clean: bool = True,
    max_length: Optional[int] = None,
    sample_rate: Optional[int] = None,
) -> None
```

Convert text to speech and save to a file.

**Parameters:**
- `text`: Input text.
- `output_file`: Path to save the audio file.
- `normalize`: Whether to normalize the text.
- `clean`: Whether to clean the text.
- `max_length`: Maximum length of generated mel spectrograms.
- `sample_rate`: Sample rate of the audio. If None, the vocoder's sample rate is used.

## Text Processing

### `kalakan.text.twi_g2p.TwiG2P`

```python
class TwiG2P:
    def __init__(self, pronunciation_dict_path: Optional[str] = None)
```

Grapheme-to-Phoneme (G2P) converter for Twi language.

**Parameters:**
- `pronunciation_dict_path`: Path to a pronunciation dictionary file. If provided, the dictionary will be loaded and used for G2P conversion.

#### Methods

##### `word_to_phonemes`

```python
def word_to_phonemes(self, word: str) -> List[str]
```

Convert a Twi word to phonemes.

**Parameters:**
- `word`: The Twi word to convert.

**Returns:**
- A list of phonemes.

##### `text_to_phonemes`

```python
def text_to_phonemes(self, text: str) -> List[str]
```

Convert Twi text to phonemes.

**Parameters:**
- `text`: The Twi text to convert.

**Returns:**
- A list of phonemes.

##### `text_to_phoneme_sequence`

```python
def text_to_phoneme_sequence(self, text: str) -> List[int]
```

Convert Twi text to a sequence of phoneme IDs.

**Parameters:**
- `text`: The Twi text to convert.

**Returns:**
- A list of phoneme IDs.

### `kalakan.text.enhanced_g2p.EnhancedTwiG2P`

An enhanced version of the TwiG2P converter with additional features for handling complex Twi text.

### `kalakan.text.normalizer.normalize_text`

```python
def normalize_text(text: str) -> str
```

Normalize Twi text by expanding abbreviations, converting numbers to words, etc.

**Parameters:**
- `text`: The text to normalize.

**Returns:**
- Normalized text.

### `kalakan.text.cleaner.clean_text`

```python
def clean_text(text: str) -> str
```

Clean Twi text by removing unnecessary characters, fixing common errors, etc.

**Parameters:**
- `text`: The text to clean.

**Returns:**
- Cleaned text.

### `kalakan.text.tokenizer.TwiTokenizer`

```python
class TwiTokenizer:
    def __init__(self)
```

Tokenizer for Twi text.

#### Methods

##### `tokenize`

```python
def tokenize(self, text: str) -> List[str]
```

Tokenize Twi text into words.

**Parameters:**
- `text`: The text to tokenize.

**Returns:**
- A list of tokens.

##### `word_to_phonemes`

```python
def word_to_phonemes(self, word: str) -> List[str]
```

Convert a Twi word to phonemes based on tokenization rules.

**Parameters:**
- `word`: The word to convert.

**Returns:**
- A list of phonemes.

## Acoustic Models

### `kalakan.models.acoustic.base_acoustic.BaseAcousticModel`

```python
class BaseAcousticModel(nn.Module):
    def __init__(self)
```

Base class for all acoustic models in Kalakan TTS.

#### Methods

##### `forward`

```python
def forward(
    self,
    phonemes: torch.Tensor,
    phoneme_lengths: torch.Tensor,
    mels: Optional[torch.Tensor] = None,
    mel_lengths: Optional[torch.Tensor] = None,
) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]
```

Forward pass of the acoustic model.

**Parameters:**
- `phonemes`: Batch of phoneme sequences.
- `phoneme_lengths`: Lengths of phoneme sequences.
- `mels`: Batch of target mel spectrograms (for training).
- `mel_lengths`: Lengths of target mel spectrograms.

**Returns:**
- Predicted mel spectrograms and additional outputs.

##### `inference`

```python
def inference(
    self,
    phonemes: torch.Tensor,
    max_length: Optional[int] = None,
) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]
```

Generate mel spectrograms from phoneme sequences.

**Parameters:**
- `phonemes`: Batch of phoneme sequences.
- `max_length`: Maximum length of generated mel spectrograms.

**Returns:**
- Generated mel spectrograms and additional outputs.

### `kalakan.models.acoustic.tacotron2.Tacotron2`

```python
class Tacotron2(BaseAcousticModel):
    def __init__(
        self,
        n_phonemes: Optional[int] = None,
        phoneme_dict: Optional[Dict[str, int]] = None,
        embedding_dim: int = 512,
        encoder_dim: int = 512,
        encoder_conv_layers: int = 3,
        encoder_conv_kernel_size: int = 5,
        encoder_conv_dropout: float = 0.5,
        encoder_lstm_layers: int = 1,
        encoder_lstm_dropout: float = 0.1,
        decoder_dim: int = 1024,
        decoder_prenet_dim: List[int] = [256, 256],
        decoder_lstm_layers: int = 2,
        decoder_lstm_dropout: float = 0.1,
        decoder_zoneout: float = 0.1,
        attention_dim: int = 128,
        attention_location_features_dim: int = 32,
        attention_location_kernel_size: int = 31,
        postnet_dim: int = 512,
        postnet_kernel_size: int = 5,
        postnet_layers: int = 5,
        postnet_dropout: float = 0.5,
        mel_channels: int = 80,
        gate_threshold: float = 0.5,
        max_decoder_steps: int = 1000,
        stop_threshold: float = 0.5,
    )
```

Tacotron2 model for Kalakan TTS.

**Parameters:**
- `n_phonemes`: Number of phonemes in the vocabulary.
- `phoneme_dict`: Dictionary mapping phonemes to indices.
- `embedding_dim`: Dimension of the phoneme embedding.
- `encoder_dim`: Dimension of the encoder output.
- `encoder_conv_layers`: Number of convolutional layers in the encoder.
- `encoder_conv_kernel_size`: Kernel size of the convolutional layers in the encoder.
- `encoder_conv_dropout`: Dropout rate for the convolutional layers in the encoder.
- `encoder_lstm_layers`: Number of LSTM layers in the encoder.
- `encoder_lstm_dropout`: Dropout rate for the LSTM layers in the encoder.
- `decoder_dim`: Dimension of the decoder output.
- `decoder_prenet_dim`: Dimensions of the decoder prenet layers.
- `decoder_lstm_layers`: Number of LSTM layers in the decoder.
- `decoder_lstm_dropout`: Dropout rate for the LSTM layers in the decoder.
- `decoder_zoneout`: Zoneout rate for the LSTM layers in the decoder.
- `attention_dim`: Dimension of the attention mechanism.
- `attention_location_features_dim`: Dimension of the location features in the attention mechanism.
- `attention_location_kernel_size`: Kernel size of the location features in the attention mechanism.
- `postnet_dim`: Dimension of the postnet output.
- `postnet_kernel_size`: Kernel size of the convolutional layers in the postnet.
- `postnet_layers`: Number of convolutional layers in the postnet.
- `postnet_dropout`: Dropout rate for the convolutional layers in the postnet.
- `mel_channels`: Number of mel spectrogram channels.
- `gate_threshold`: Threshold for the gate output.
- `max_decoder_steps`: Maximum number of decoder steps.
- `stop_threshold`: Threshold for stopping the decoder.

### `kalakan.models.acoustic.fastspeech2.FastSpeech2`

```python
class FastSpeech2(BaseAcousticModel):
    def __init__(
        self,
        n_phonemes: Optional[int] = None,
        phoneme_dict: Optional[Dict[str, int]] = None,
        embedding_dim: int = 256,
        encoder_layers: int = 4,
        encoder_attention_heads: int = 2,
        encoder_ffn_dim: int = 1024,
        encoder_dropout: float = 0.1,
        decoder_layers: int = 4,
        decoder_attention_heads: int = 2,
        decoder_ffn_dim: int = 1024,
        decoder_dropout: float = 0.1,
        variance_predictor_filter_size: int = 256,
        variance_predictor_kernel_size: int = 3,
        variance_predictor_dropout: float = 0.5,
        mel_channels: int = 80,
        max_seq_len: int = 1000,
    )
```

FastSpeech2 model for Kalakan TTS.

## Vocoders

### `kalakan.models.vocoders.base_vocoder.BaseVocoder`

```python
class BaseVocoder(nn.Module):
    def __init__(self, sample_rate: int = 22050)
```

Base class for all vocoders in Kalakan TTS.

**Parameters:**
- `sample_rate`: Sample rate of the generated audio.

#### Methods

##### `forward`

```python
def forward(
    self,
    mels: torch.Tensor,
) -> torch.Tensor
```

Forward pass of the vocoder.

**Parameters:**
- `mels`: Batch of mel spectrograms.

**Returns:**
- Generated audio waveforms.

##### `inference`

```python
def inference(
    self,
    mels: torch.Tensor,
) -> torch.Tensor
```

Generate audio waveforms from mel spectrograms.

**Parameters:**
- `mels`: Batch of mel spectrograms.

**Returns:**
- Generated audio waveforms.

### `kalakan.models.vocoders.hifigan.HiFiGAN`

```python
class HiFiGAN(BaseVocoder):
    def __init__(
        self,
        sample_rate: int = 22050,
        mel_channels: int = 80,
        upsample_rates: List[int] = [8, 8, 2, 2],
        upsample_kernel_sizes: List[int] = [16, 16, 4, 4],
        upsample_initial_channel: int = 512,
        resblock_kernel_sizes: List[int] = [3, 7, 11],
        resblock_dilation_sizes: List[List[int]] = [[1, 3, 5], [1, 3, 5], [1, 3, 5]],
        leaky_relu_slope: float = 0.1,
    )
```

HiFi-GAN vocoder for Kalakan TTS.

**Parameters:**
- `sample_rate`: Sample rate of the generated audio.
- `mel_channels`: Number of mel spectrogram channels.
- `upsample_rates`: Upsampling rates for each upsampling layer.
- `upsample_kernel_sizes`: Kernel sizes for each upsampling layer.
- `upsample_initial_channel`: Initial channel count for the upsampling layers.
- `resblock_kernel_sizes`: Kernel sizes for each residual block.
- `resblock_dilation_sizes`: Dilation sizes for each residual block.
- `leaky_relu_slope`: Slope of the leaky ReLU activation.

### `kalakan.models.vocoders.griffin_lim.GriffinLim`

```python
class GriffinLim(BaseVocoder):
    def __init__(
        self,
        sample_rate: int = 22050,
        n_fft: int = 1024,
        hop_length: int = 256,
        win_length: int = 1024,
        power: float = 1.5,
        n_iter: int = 60,
        mel_channels: int = 80,
        mel_fmin: float = 0.0,
        mel_fmax: Optional[float] = None,
    )
```

Griffin-Lim vocoder for Kalakan TTS.

**Parameters:**
- `sample_rate`: Sample rate of the generated audio.
- `n_fft`: Size of the FFT.
- `hop_length`: Hop length for the STFT.
- `win_length`: Window length for the STFT.
- `power`: Power of the magnitude spectrogram.
- `n_iter`: Number of iterations for the Griffin-Lim algorithm.
- `mel_channels`: Number of mel spectrogram channels.
- `mel_fmin`: Minimum frequency for the mel filterbank.
- `mel_fmax`: Maximum frequency for the mel filterbank.

## Audio Processing

### `kalakan.audio.features.mel_spectrogram`

```python
def mel_spectrogram(
    audio: torch.Tensor,
    n_fft: int = 1024,
    hop_length: int = 256,
    win_length: int = 1024,
    sample_rate: int = 22050,
    n_mels: int = 80,
    fmin: float = 0.0,
    fmax: Optional[float] = None,
    center: bool = True,
    power: float = 1.0,
    norm: Optional[str] = None,
    mel_scale: str = "htk",
) -> torch.Tensor
```

Convert audio waveform to mel spectrogram.

**Parameters:**
- `audio`: Audio waveform.
- `n_fft`: Size of the FFT.
- `hop_length`: Hop length for the STFT.
- `win_length`: Window length for the STFT.
- `sample_rate`: Sample rate of the audio.
- `n_mels`: Number of mel spectrogram channels.
- `fmin`: Minimum frequency for the mel filterbank.
- `fmax`: Maximum frequency for the mel filterbank.
- `center`: Whether to pad the signal at the beginning and end.
- `power`: Power of the magnitude spectrogram.
- `norm`: Normalization method for the mel filterbank.
- `mel_scale`: Scale for the mel filterbank.

**Returns:**
- Mel spectrogram.

### `kalakan.audio.preprocessing.preprocess_audio`

```python
def preprocess_audio(
    audio_path: str,
    target_sr: int = 22050,
    trim_silence: bool = True,
    trim_threshold_db: float = 60.0,
    normalize: bool = True,
) -> Tuple[np.ndarray, int]
```

Preprocess audio for TTS training.

**Parameters:**
- `audio_path`: Path to the audio file.
- `target_sr`: Target sample rate.
- `trim_silence`: Whether to trim silence from the beginning and end.
- `trim_threshold_db`: Threshold for silence trimming.
- `normalize`: Whether to normalize the audio.

**Returns:**
- Preprocessed audio waveform and sample rate.

### `kalakan.audio.utils.save_audio`

```python
def save_audio(
    audio: Union[np.ndarray, torch.Tensor],
    file_path: str,
    sample_rate: int = 22050,
    normalize: bool = True,
) -> None
```

Save audio to a file.

**Parameters:**
- `audio`: Audio waveform.
- `file_path`: Path to save the audio file.
- `sample_rate`: Sample rate of the audio.
- `normalize`: Whether to normalize the audio before saving.

## Configuration

### `kalakan.utils.config.Config`

```python
class Config:
    def __init__(
        self,
        config: Optional[Union[Dict, str]] = None,
    )
```

Configuration manager for Kalakan TTS.

**Parameters:**
- `config`: Configuration dictionary or path to a YAML configuration file.

#### Methods

##### `get`

```python
def get(
    self,
    key: str,
    default: Any = None,
) -> Any
```

Get a configuration value.

**Parameters:**
- `key`: Configuration key.
- `default`: Default value if the key is not found.

**Returns:**
- Configuration value.

##### `set`

```python
def set(
    self,
    key: str,
    value: Any,
) -> None
```

Set a configuration value.

**Parameters:**
- `key`: Configuration key.
- `value`: Configuration value.

##### `save`

```python
def save(
    self,
    file_path: str,
) -> None
```

Save the configuration to a YAML file.

**Parameters:**
- `file_path`: Path to save the configuration file.

## Model Factory

### `kalakan.utils.model_factory.ModelFactory`

```python
class ModelFactory:
    @staticmethod
    def create_acoustic_model(
        model_type: Optional[str] = None,
        config: Optional[Union[Dict, Config, str]] = None,
        checkpoint_path: Optional[str] = None,
        device: Optional[torch.device] = None,
    ) -> BaseAcousticModel
```

Create an acoustic model.

**Parameters:**
- `model_type`: Type of acoustic model to create.
- `config`: Configuration for the model.
- `checkpoint_path`: Path to a checkpoint file.
- `device`: Device to use for the model.

**Returns:**
- Acoustic model.

```python
@staticmethod
def create_vocoder(
    model_type: Optional[str] = None,
    config: Optional[Union[Dict, Config, str]] = None,
    checkpoint_path: Optional[str] = None,
    device: Optional[torch.device] = None,
) -> BaseVocoder
```

Create a vocoder.

**Parameters:**
- `model_type`: Type of vocoder to create.
- `config`: Configuration for the model.
- `checkpoint_path`: Path to a checkpoint file.
- `device`: Device to use for the model.

**Returns:**
- Vocoder.

## CLI Tools

### `kalakan.cli.synthesize`

```python
def synthesize(
    text: str,
    output_file: str,
    acoustic_model: Optional[str] = None,
    vocoder: Optional[str] = None,
    acoustic_model_type: Optional[str] = None,
    vocoder_type: Optional[str] = None,
    device: Optional[str] = None,
    config: Optional[str] = None,
    normalize: bool = True,
    clean: bool = True,
) -> None
```

Synthesize speech from text using the command line.

**Parameters:**
- `text`: Input text.
- `output_file`: Path to save the audio file.
- `acoustic_model`: Path to an acoustic model checkpoint.
- `vocoder`: Path to a vocoder checkpoint.
- `acoustic_model_type`: Type of acoustic model to use.
- `vocoder_type`: Type of vocoder to use.
- `device`: Device to use for inference.
- `config`: Path to a configuration file.
- `normalize`: Whether to normalize the text.
- `clean`: Whether to clean the text.

### `kalakan.cli.train`

```python
def train(
    model_type: str,
    data_dir: str,
    output_dir: str,
    config: Optional[str] = None,
    checkpoint: Optional[str] = None,
    device: Optional[str] = None,
    batch_size: Optional[int] = None,
    epochs: Optional[int] = None,
    learning_rate: Optional[float] = None,
    resume: bool = False,
) -> None
```

Train a model using the command line.

**Parameters:**
- `model_type`: Type of model to train.
- `data_dir`: Directory containing the training data.
- `output_dir`: Directory to save the trained model.
- `config`: Path to a configuration file.
- `checkpoint`: Path to a checkpoint file for resuming training.
- `device`: Device to use for training.
- `batch_size`: Batch size for training.
- `epochs`: Number of epochs to train.
- `learning_rate`: Learning rate for training.
- `resume`: Whether to resume training from a checkpoint.

## REST API

### `kalakan.api.server.app`

FastAPI application for the Kalakan TTS REST API.

#### Endpoints

##### `POST /synthesize`

Synthesize speech from text.

**Request Body:**
- `text`: Input text.
- `normalize`: Whether to normalize the text.
- `clean`: Whether to clean the text.

**Response:**
- Audio file in WAV format.

##### `GET /models`

Get a list of available models.

**Response:**
- List of available acoustic models and vocoders.

##### `GET /health`

Check the health of the API.

**Response:**
- Status of the API.

## gRPC API

### `kalakan.api.grpc_api.TwiTTSServicer`

gRPC servicer for the Kalakan TTS gRPC API.

#### Methods

##### `Synthesize`

```python
def Synthesize(
    self,
    request: SynthesizeRequest,
    context: grpc.ServicerContext,
) -> SynthesizeResponse
```

Synthesize speech from text.

**Request:**
- `text`: Input text.
- `normalize`: Whether to normalize the text.
- `clean`: Whether to clean the text.

**Response:**
- Audio data in WAV format.
- Sample rate of the audio.
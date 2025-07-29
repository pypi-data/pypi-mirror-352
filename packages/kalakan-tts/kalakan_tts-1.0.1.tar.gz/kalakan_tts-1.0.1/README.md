# Kalakan TTS

A fully custom, offline Text-to-Speech system for the Twi language.

## Features

- Specialized for Twi language with proper handling of special characters (ɛ, ɔ, Ɔ, tonal markers)
- Complete text processing pipeline with Twi-specific tokenization and phoneme mapping
- High-quality acoustic models:
  - Tacotron2: Attention-based sequence-to-sequence model
  - FastSpeech2: Non-autoregressive model with explicit duration modeling
  - Transformer-TTS: Transformer-based sequence-to-sequence model
- Multiple vocoders:
  - Griffin-Lim: Simple phase reconstruction algorithm
  - HiFi-GAN: High-fidelity GAN-based vocoder
  - MelGAN: Fast GAN-based vocoder
  - WaveGlow: Flow-based generative model
- Production-ready API with REST and gRPC interfaces
- Comprehensive training infrastructure with experiment tracking and data augmentation
- Advanced dataset preparation with metadata generation, phoneme conversion, and quality control
- Optimized for both cloud and edge deployment

## Installation

### Basic Installation

```bash
pip install kalakan-tts
```

### Development Installation

```bash
git clone https://github.com/kalakan-ai/kalakan-tts.git
cd kalakan-tts
pip install -e ".[dev,api,training]"
```

## Quick Start

### Text-to-Speech Synthesis

```python
from kalakan.synthesis.synthesizer import Synthesizer

# Initialize the synthesizer with specific models
synthesizer = Synthesizer(
    acoustic_model="/path/to/acoustic_model.pt",  # or use a model name like "tacotron2", "fastspeech2", "transformer_tts"
    vocoder="/path/to/vocoder.pt",  # or use a model name like "griffin_lim", "hifigan", "melgan", "waveglow"
    device="cuda:0",  # or "cpu"
)

# Generate audio from Twi text
audio = synthesizer.synthesize(
    text="Akwaaba! Wo ho te sɛn?",
    normalize=True,
    clean=True,
    speed=1.0,  # Control speech speed (for FastSpeech2)
    pitch=1.0,  # Control pitch (for FastSpeech2)
    energy=1.0,  # Control energy/volume (for FastSpeech2)
)

# Save the audio to a file
synthesizer.save_audio(audio, "output.wav")
```

### Command Line Interface

```bash
# Using the demo script
python demo.py --text "Akwaaba! Wo ho te sɛn?" --output output.wav --acoustic_model /path/to/acoustic_model.pt --vocoder /path/to/vocoder.pt

# Start the REST API server
python -m kalakan.api.server --host 0.0.0.0 --port 8000 --acoustic_model /path/to/acoustic_model.pt --vocoder /path/to/vocoder.pt

# Start the gRPC API server
python -m kalakan.api.grpc_api --host 0.0.0.0 --port 50051 --acoustic_model /path/to/acoustic_model.pt --vocoder /path/to/vocoder.pt
```

### API Clients

```bash
# REST API client
python rest_client.py --text "Akwaaba! Wo ho te sɛn?" --output output.wav --host localhost --port 8000

# gRPC API client
python grpc_client.py --text "Akwaaba! Wo ho te sɛn?" --output output.wav --host localhost --port 50051
```

## Dataset Preparation

Kalakan TTS includes a comprehensive metadata generation tool for preparing TTS datasets:

### Basic Metadata Generation

```bash
# Generate basic metadata for a dataset
kalakan gen-metadata --input-dir /path/to/dataset --verbose
```

### Advanced Features

```bash
# Generate metadata with phonemes, dataset splitting, and quality control
kalakan gen-metadata \
    --input-dir /path/to/dataset \
    --generate-phonemes \
    --split-dataset \
    --val-ratio 0.2 \
    --test-ratio 0.1 \
    --output-format both \
    --include-stats \
    --check-duplicates \
    --remove-duplicates \
    --normalize-text \
    --clean-text \
    --speaker-id "speaker_001" \
    --verbose
```

### Key Features

- **Phoneme Generation**: Automatic G2P conversion for Twi text
- **Text Normalization**: Cleaning and standardization of text content
- **Dataset Splitting**: Automatic train/validation/test splits
- **Quality Control**: Duration filtering, duplicate detection, and validation
- **Multiple Formats**: CSV and JSON output support
- **Comprehensive Statistics**: Detailed dataset analytics

For detailed documentation, see [docs/metadata_generation_guide.md](docs/metadata_generation_guide.md).

## Text Normalization

Kalakan TTS includes a powerful text normalization tool for preparing Twi text:

### Basic Text Normalization

```bash
# Normalize Twi text directly
kalakan norm --text "Dr. Kwame na Prof. Ama bɛba ha 25 mu."
```

### File Processing

```bash
# Normalize text from files with various options
kalakan norm \
    --file input.txt \
    --output normalized.txt \
    --format json \
    --show-diff \
    --verbose
```

### Key Features

- **Abbreviation Expansion**: "Dr." → "doctor", "Prof." → "professor"
- **Number Conversion**: "25" → text representation
- **Special Character Normalization**: Proper handling of Twi characters (ɛ, ɔ)
- **Multiple Output Formats**: Text, JSON, CSV
- **Batch Processing**: Process multiple files at once
- **Interactive File Selection**: GUI file picker
- **Difference Visualization**: See what changed during normalization

## Documentation

For detailed documentation, visit [docs/](docs/).

## License

Apache License 2.0
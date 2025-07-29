# Custom Twi TTS Model Training Guide

This guide provides instructions for developers who want to train their own custom Twi TTS models using the Kalakan framework. While we provide pre-trained models, custom training allows you to create models with specific voices, dialects, or domains.

## Table of Contents

1. [Why Train Custom Models](#why-train-custom-models)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Dataset Preparation](#dataset-preparation)
5. [Training Process](#training-process)
6. [Hyperparameter Tuning](#hyperparameter-tuning)
7. [Evaluation](#evaluation)
8. [Model Export](#model-export)
9. [Integration](#integration)
10. [Troubleshooting](#troubleshooting)

## Why Train Custom Models

While our pre-trained models work well for general purposes, you might want to train custom models for:

- **Specific Voice**: Train with a different speaker's voice
- **Dialect Adaptation**: Optimize for Asante, Akuapem, or Fante dialects
- **Domain-Specific**: Better pronunciation for medical, technical, or other specialized domains
- **Performance Optimization**: Train smaller models for specific deployment targets
- **Data Privacy**: Keep sensitive training data within your organization

## Prerequisites

Before starting, ensure you have:

- Python 3.7+ and PyTorch 1.7+
- CUDA-compatible GPU with 8GB+ VRAM (recommended)
- 16GB+ RAM
- 100GB+ free disk space
- Basic understanding of deep learning concepts
- Twi speech dataset (see [Dataset Preparation](#dataset-preparation))

## Installation

Install the Kalakan training package:

```bash
# Install from PyPI
pip install kalakan-tts-trainer

# Or install from source
git clone https://github.com/yourusername/kalakan.git
cd kalakan
pip install -e ".[training]"
```

## Dataset Preparation

### Option 1: Use an Existing Dataset

If you have access to a Twi speech dataset:

```bash
# Prepare the dataset
kalakan-prepare-dataset \
    --input-dir /path/to/raw/dataset \
    --output-dir data/twi_dataset \
    --language twi \
    --split 0.9,0.05,0.05
```

### Option 2: Record Your Own Dataset

For a custom voice, record your own dataset:

1. Follow our [Twi Dataset Collection Guide](twi_dataset_guide.md)
2. Ensure you have at least 5 hours of clean recordings (10+ hours recommended)
3. Prepare the dataset as in Option 1

### Option 3: Adapt an Existing Dataset

Start with our base dataset and add your custom recordings:

```bash
# Download our base dataset
kalakan-download-dataset --language twi --output-dir data/base_twi_dataset

# Add your custom recordings
kalakan-extend-dataset \
    --base-dir data/base_twi_dataset \
    --custom-dir /path/to/your/recordings \
    --output-dir data/extended_twi_dataset
```

## Training Process

### 1. Configuration

Create a training configuration file:

```bash
# Generate a default config
kalakan-generate-config \
    --model tacotron2 \
    --output configs/my_twi_tts.yaml
```

Edit the configuration file to customize:
- Model architecture
- Training parameters
- Data augmentation
- Optimization settings

Example configuration:

```yaml
# my_twi_tts.yaml
training:
  batch_size: 16
  epochs: 1000
  learning_rate: 0.001
  weight_decay: 0.0001
  grad_clip: 1.0
  save_interval: 10
  eval_interval: 5

model:
  type: "tacotron2"
  embedding_dim: 512
  encoder_dim: 512
  decoder_dim: 1024
  attention_dim: 128
  postnet_dim: 512

data:
  max_mel_length: 1000
  max_text_length: 200
  mel_channels: 80
  sampling_rate: 22050
  augmentation: true
  
optimizer:
  type: "adam"
  scheduler: "plateau"
  patience: 5
  factor: 0.5
```

### 2. Training the Acoustic Model

Train the Tacotron2 model:

```bash
kalakan-train \
    --config configs/my_twi_tts.yaml \
    --data-dir data/twi_dataset \
    --output-dir models/my_tacotron2_twi \
    --model tacotron2
```

Monitor training with TensorBoard:

```bash
tensorboard --logdir models/my_tacotron2_twi/logs
```

### 3. Training the Vocoder

Train a HiFi-GAN vocoder:

```bash
kalakan-train \
    --config configs/my_twi_tts.yaml \
    --data-dir data/twi_dataset \
    --output-dir models/my_hifigan_twi \
    --model hifigan
```

### 4. Fine-tuning (Optional)

Fine-tune on a smaller, high-quality dataset:

```bash
kalakan-train \
    --config configs/my_twi_tts.yaml \
    --data-dir data/twi_dataset_clean \
    --output-dir models/my_tacotron2_twi_ft \
    --model tacotron2 \
    --checkpoint models/my_tacotron2_twi/best_model.pt \
    --learning-rate 0.0001 \
    --epochs 100
```

## Hyperparameter Tuning

Optimize your model with hyperparameter tuning:

```bash
kalakan-tune \
    --config configs/my_twi_tts.yaml \
    --data-dir data/twi_dataset \
    --output-dir tuning_results \
    --model tacotron2 \
    --trials 20
```

Key parameters to tune:
- Learning rate
- Batch size
- Model dimensions
- Attention parameters
- Dropout rates

## Evaluation

Evaluate your trained model:

```bash
kalakan-evaluate \
    --acoustic-model models/my_tacotron2_twi/best_model.pt \
    --vocoder models/my_hifigan_twi/best_model.pt \
    --test-metadata data/twi_dataset/test_metadata.csv \
    --output-dir evaluation_results
```

The evaluation will provide:
- Objective metrics (MCD, WER, etc.)
- Sample audio files
- Comparative visualizations
- HTML report with results

## Model Export

Export your models for deployment:

```bash
kalakan-export \
    --acoustic-model models/my_tacotron2_twi/best_model.pt \
    --vocoder models/my_hifigan_twi/best_model.pt \
    --output-dir exported_models \
    --format pytorch \
    --quantize
```

Available export formats:
- PyTorch (default)
- ONNX
- TorchScript
- TensorFlow SavedModel

## Integration

### Using Your Custom Models

```python
from kalakan_twi_tts import TwiSynthesizer

# Initialize with custom models
synthesizer = TwiSynthesizer(
    acoustic_model="path/to/exported_models/acoustic_model.pt",
    vocoder="path/to/exported_models/vocoder.pt"
)

# Generate speech
audio = synthesizer.synthesize("Akwaaba! Wo ho te sɛn?")
synthesizer.save_audio(audio, "output.wav")
```

### Sharing Your Models

Create a model card with:
- Model architecture
- Training data description
- Performance metrics
- Usage examples
- Limitations

## Troubleshooting

### Common Issues and Solutions

#### 1. Out of Memory Errors
- Reduce batch size
- Use gradient accumulation
- Try mixed precision training

```bash
kalakan-train \
    --config configs/my_twi_tts.yaml \
    --data-dir data/twi_dataset \
    --output-dir models/my_tacotron2_twi \
    --model tacotron2 \
    --batch-size 8 \
    --grad-accumulation 2 \
    --mixed-precision
```

#### 2. Poor Alignment
- Check your phoneme dictionary
- Increase attention constraint weight
- Use guided attention loss

#### 3. Robotic Speech
- Train longer
- Use a more powerful vocoder
- Check audio preprocessing settings

#### 4. Slow Convergence
- Adjust learning rate
- Try different optimizers
- Check data quality

#### 5. Overfitting
- Add more data
- Increase dropout
- Use data augmentation

## Advanced Topics

### Multi-Speaker Training

Train a model that can synthesize multiple voices:

```bash
kalakan-train \
    --config configs/multi_speaker.yaml \
    --data-dir data/multi_speaker_dataset \
    --output-dir models/multi_speaker_twi \
    --model tacotron2_multi
```

### Transfer Learning

Start from an English model and adapt to Twi:

```bash
kalakan-train \
    --config configs/transfer_learning.yaml \
    --data-dir data/twi_dataset \
    --output-dir models/transfer_twi \
    --model tacotron2 \
    --pretrained models/english_tacotron2/model.pt \
    --freeze-encoder
```

### Low-Resource Training

Train with limited data:

```bash
kalakan-train \
    --config configs/low_resource.yaml \
    --data-dir data/small_twi_dataset \
    --output-dir models/low_resource_twi \
    --model tacotron2 \
    --data-augmentation high
```

---

By following this guide, you'll be able to train your own custom Twi TTS models tailored to your specific needs. For additional support, refer to our [community forum](https://github.com/yourusername/kalakan/discussions) or [open an issue](https://github.com/yourusername/kalakan/issues) on our GitHub repository.
# Kalakan TTS Training Guide for Twi Language

This guide provides detailed instructions for training the Kalakan TTS system specifically for the Twi language. Follow these steps to create a high-quality Twi text-to-speech system.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Dataset Preparation](#dataset-preparation)
3. [Training the Acoustic Model](#training-the-acoustic-model)
4. [Training the Vocoder](#training-the-vocoder)
5. [Fine-tuning](#fine-tuning)
6. [Evaluation](#evaluation)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

Before starting the training process, ensure you have:

- Python 3.7 or higher
- PyTorch 1.7 or higher
- CUDA-compatible GPU (recommended for faster training)
- At least 16GB of RAM
- At least 50GB of free disk space
- Twi speech dataset (see below)

## Dataset Preparation

### 1. Collecting a Twi Speech Dataset

For optimal results, you need a high-quality Twi speech dataset:

- **Size**: At least 10 hours of speech (20+ hours recommended)
- **Speaker**: Single speaker for best results
- **Quality**: Clean recordings with minimal background noise
- **Content**: Diverse text covering various phonetic contexts
- **Format**: WAV files (16-bit, 22050Hz or 44100Hz)

Sources for Twi speech data:
- [Common Voice](https://commonvoice.mozilla.org/) (if available for Twi)
- [ALFFA](https://github.com/besacier/ALFFA_PUBLIC) project
- Record your own dataset with a native Twi speaker
- National media archives or radio broadcasts

### 2. Preparing the Dataset

Use our dataset preparation script:

```bash
python scripts/prepare_dataset.py \
    --input-dir /path/to/raw/dataset \
    --output-dir data/twi_dataset \
    --max-duration 10.0 \
    --min-duration 1.0
```

This script will:
1. Clean and normalize the audio files
2. Process the text using our enhanced Twi G2P converter
3. Split the dataset into training, validation, and test sets
4. Generate metadata files for training

### 3. Computing Mel Spectrograms

Precompute mel spectrograms to speed up training:

```bash
python scripts/train_tacotron2.py \
    --data-dir data/twi_dataset \
    --output-dir models/tacotron2_twi \
    --compute-mels
```

## Training the Acoustic Model

### 1. Configuring the Model

Create a custom configuration for Twi:

```bash
cp configs/models/tacotron2_base.yaml configs/models/tacotron2_twi.yaml
```

Edit the configuration file to optimize for Twi:

```yaml
# Tacotron2 model configuration for Twi

model:
  name: "tacotron2"
  
  # Phoneme embedding
  embedding_dim: 512
  
  # Encoder
  encoder_dim: 512
  encoder_conv_layers: 3
  encoder_conv_kernel_size: 5
  encoder_conv_dropout: 0.5
  encoder_lstm_layers: 1
  encoder_lstm_dropout: 0.1
  
  # Decoder
  decoder_dim: 1024
  decoder_prenet_dim: [256, 256]
  decoder_lstm_layers: 2
  decoder_lstm_dropout: 0.1
  decoder_zoneout: 0.1
  
  # Attention
  attention_dim: 128
  attention_location_features_dim: 32
  attention_location_kernel_size: 31
  
  # Postnet
  postnet_dim: 512
  postnet_kernel_size: 5
  postnet_layers: 5
  postnet_dropout: 0.5
  
  # Other parameters
  n_mels: 80
  stop_threshold: 0.5
```

### 2. Training the Model

Train the Tacotron2 model:

```bash
python scripts/train_tacotron2.py \
    --config configs/models/tacotron2_twi.yaml \
    --data-dir data/twi_dataset \
    --output-dir models/tacotron2_twi \
    --batch-size 16 \
    --num-epochs 1000 \
    --learning-rate 1e-3
```

Training tips:
- Start with a smaller batch size if you encounter memory issues
- Use a learning rate scheduler to improve convergence
- Monitor validation loss to prevent overfitting
- Train for at least 100K steps for good results
- Save checkpoints regularly

### 3. Monitoring Training

Monitor the training progress:
- Check the loss curves (training and validation)
- Listen to samples generated during training
- Adjust hyperparameters if necessary

## Training the Vocoder

### 1. Configuring the Vocoder

For better quality, train a neural vocoder (e.g., WaveGlow or HiFi-GAN) instead of using Griffin-Lim:

```bash
cp configs/models/hifi_gan_base.yaml configs/models/hifi_gan_twi.yaml
```

Edit the configuration file as needed.

### 2. Training the Vocoder

Train the vocoder:

```bash
python scripts/train_vocoder.py \
    --config configs/models/hifi_gan_twi.yaml \
    --data-dir data/twi_dataset \
    --output-dir models/hifi_gan_twi \
    --batch-size 16 \
    --num-epochs 500
```

## Fine-tuning

After initial training, fine-tune the models:

1. **Acoustic Model Fine-tuning**:
   ```bash
   python scripts/train_tacotron2.py \
       --config configs/models/tacotron2_twi.yaml \
       --data-dir data/twi_dataset \
       --output-dir models/tacotron2_twi_ft \
       --checkpoint models/tacotron2_twi/tacotron2_best.pt \
       --learning-rate 1e-4 \
       --num-epochs 100
   ```

2. **Vocoder Fine-tuning**:
   ```bash
   python scripts/train_vocoder.py \
       --config configs/models/hifi_gan_twi.yaml \
       --data-dir data/twi_dataset \
       --output-dir models/hifi_gan_twi_ft \
       --checkpoint models/hifi_gan_twi/hifi_gan_best.pt \
       --learning-rate 1e-4 \
       --num-epochs 50
   ```

## Evaluation

Evaluate your trained models:

```bash
python scripts/evaluate_tts.py \
    --acoustic-model models/tacotron2_twi_ft/tacotron2_best.pt \
    --vocoder models/hifi_gan_twi_ft/hifi_gan_best.pt \
    --test-metadata data/twi_dataset/test_metadata.csv \
    --output-dir evaluation_results
```

Metrics to consider:
- Mean Opinion Score (MOS)
- Word Error Rate (WER) using ASR
- Character Error Rate (CER)
- Mel Cepstral Distortion (MCD)

## Troubleshooting

### Common Issues and Solutions

1. **Poor Phoneme Conversion**:
   - Enhance the G2P converter with more Twi-specific rules
   - Add more entries to the pronunciation dictionary

2. **Robotic Speech**:
   - Train for more epochs
   - Use a more powerful vocoder
   - Increase the dataset size

3. **Mispronunciations**:
   - Check the phoneme inventory for completeness
   - Ensure proper handling of Twi-specific characters (ɛ, ɔ)
   - Add tone information if needed

4. **Training Instability**:
   - Reduce learning rate
   - Apply gradient clipping
   - Use batch normalization

5. **Slow Inference**:
   - Export to ONNX format
   - Optimize decoder with techniques like guided attention

## Additional Resources

- [Twi Phonology Guide](https://en.wikipedia.org/wiki/Akan_language#Phonology)
- [Kalakan TTS Documentation](https://github.com/your-repo/kalakan)
- [Tacotron2 Paper](https://arxiv.org/abs/1712.05884)
- [HiFi-GAN Paper](https://arxiv.org/abs/2010.05646)

---

For additional support, please open an issue on the GitHub repository or contact the maintainers.
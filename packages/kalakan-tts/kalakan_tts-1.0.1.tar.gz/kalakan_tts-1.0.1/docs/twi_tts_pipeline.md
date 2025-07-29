# Twi TTS Pipeline

This document describes the improved Twi Text-to-Speech (TTS) pipeline for the Kalakan project.

## Overview

The Twi TTS pipeline consists of the following components:

1. **Data Preprocessing**: Prepare and normalize Twi text and audio data for training.
2. **Phoneme Alignment**: Generate phoneme-level alignments for improved training.
3. **Acoustic Model Training**: Train a Tacotron2 model to convert text to mel spectrograms.
4. **Vocoder Training**: Train a HiFi-GAN model to convert mel spectrograms to audio.
5. **Model Validation**: Validate the trained models with test utterances.
6. **Speech Synthesis**: Use the trained models to synthesize speech from text.

## Prerequisites

- Python 3.8 or higher
- PyTorch 1.10 or higher
- CUDA-compatible GPU (recommended)
- Montreal Forced Aligner (for phoneme alignment)

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Install Montreal Forced Aligner (for phoneme alignment):

```bash
pip install montreal-forced-aligner
```

## Data Preparation

1. Prepare your Twi dataset with audio files and transcripts.
2. Create a transcript file with the following format:

```
audio_file_name.wav    Twi text
```

3. Preprocess the dataset:

```bash
python scripts/preprocess_twi_dataset.py \
    --input_dir /path/to/raw/dataset \
    --output_dir /path/to/processed/dataset \
    --transcript_path /path/to/transcript.txt \
    --sample_rate 22050 \
    --trim_silence \
    --normalize_audio \
    --clean_text \
    --normalize_text \
    --augment \
    --augment_factor 2
```

## Phoneme Alignment

Generate phoneme-level alignments for improved training:

```bash
python scripts/align_twi_dataset.py \
    --metadata /path/to/processed/dataset/train_metadata.json \
    --audio_dir /path/to/processed/dataset/wavs \
    --output_dir /path/to/processed/dataset/alignments \
    --dict_path /path/to/pronunciation_dict.txt \
    --num_jobs 4
```

## Acoustic Model Training

Train the Tacotron2 acoustic model:

```bash
python scripts/train_enhanced_tacotron2.py \
    --train_metadata /path/to/processed/dataset/train_metadata.json \
    --val_metadata /path/to/processed/dataset/val_metadata.json \
    --audio_dir /path/to/processed/dataset/wavs \
    --alignment_path /path/to/processed/dataset/alignments/alignments.json \
    --model_config configs/models/tacotron2_twi.yaml \
    --training_config configs/training/acoustic_training_twi.yaml \
    --output_dir models/twi_tts/acoustic \
    --experiment_name Tacotron2_Twi
```

## Vocoder Training

Train the HiFi-GAN vocoder:

```bash
python scripts/train_hifigan.py \
    --train_metadata /path/to/processed/dataset/train_metadata.json \
    --val_metadata /path/to/processed/dataset/val_metadata.json \
    --audio_dir /path/to/processed/dataset/wavs \
    --model_config configs/models/hifigan_twi.yaml \
    --training_config configs/training/vocoder_training_twi.yaml \
    --output_dir models/twi_tts/vocoder \
    --experiment_name HiFiGAN_Twi
```

## Model Validation

Validate the trained models with test utterances:

```bash
python scripts/validate_twi_tts.py \
    --acoustic_model models/twi_tts/acoustic/Tacotron2_Twi/best_model.pt \
    --vocoder_model models/twi_tts/vocoder/HiFiGAN_Twi/best_model.pt \
    --acoustic_config configs/models/tacotron2_twi.yaml \
    --vocoder_config configs/models/hifigan_twi.yaml \
    --test_utterances resources/test_utterances_twi.json \
    --output_dir validation_results \
    --sample_rate 22050
```

## Speech Synthesis

Use the trained models to synthesize speech from text:

```bash
python examples/test-synthesis/synthesize_twi.py \
    --text "Akwaaba" \
    --model_path models/twi_tts/acoustic/Tacotron2_Twi/best_model.pt \
    --vocoder_path models/twi_tts/vocoder/HiFiGAN_Twi/best_model.pt \
    --config_path configs/models/tacotron2_twi.yaml \
    --vocoder_config configs/models/hifigan_twi.yaml \
    --output_dir synthesized_audio
```

## Key Improvements

The improved Twi TTS pipeline includes the following key enhancements:

1. **Enhanced G2P Conversion**: Better handling of Twi phonology, including tone markers and vowel lengthening.
2. **Phoneme-Level Alignment**: Using Montreal Forced Aligner for accurate phoneme-to-frame mapping.
3. **Data Augmentation**: Pitch shifting and time stretching to increase dataset size and diversity.
4. **Advanced Training Techniques**: Mixed precision training, gradient accumulation, and learning rate scheduling.
5. **HiFi-GAN Vocoder**: High-quality neural vocoder for more natural speech synthesis.
6. **Comprehensive Validation**: Objective metrics and subjective evaluation of synthesized speech.

## Best Practices

For optimal results, follow these best practices:

1. **Data Quality**: Use high-quality recordings with clear pronunciation and minimal background noise.
2. **Balanced Dataset**: Ensure a balanced distribution of phonemes, words, and sentence structures.
3. **Pronunciation Dictionary**: Create a comprehensive pronunciation dictionary for common Twi words.
4. **Hyperparameter Tuning**: Experiment with different hyperparameters to find the optimal configuration.
5. **Regular Validation**: Regularly validate the model during training to catch issues early.
6. **Multiple Dialects**: Include samples from different Twi dialects for better generalization.

## Troubleshooting

If you encounter issues, try the following:

1. **Alignment Failures**: If phoneme alignment fails, try increasing the beam size or using a better pronunciation dictionary.
2. **Training Instability**: Reduce the learning rate or batch size if training is unstable.
3. **Poor Audio Quality**: Increase the vocoder training duration or try different vocoder architectures.
4. **Mispronunciations**: Improve the pronunciation dictionary or add more examples of problematic words.
5. **Slow Inference**: Use mixed precision inference or optimize the model for deployment.

## References

- [Tacotron 2: Natural TTS Synthesis by Conditioning WaveNet on Mel Spectrogram Predictions](https://arxiv.org/abs/1712.05884)
- [HiFi-GAN: Generative Adversarial Networks for Efficient and High Fidelity Speech Synthesis](https://arxiv.org/abs/2010.05646)
- [Montreal Forced Aligner: Robust Phoneme Alignment](https://montreal-forced-aligner.readthedocs.io/)
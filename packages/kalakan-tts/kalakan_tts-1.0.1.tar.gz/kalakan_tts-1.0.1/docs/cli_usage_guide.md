# Kalakan TTS Command Line Interface Guide

This guide provides comprehensive documentation for using the Kalakan TTS system through its command line interface (CLI). The CLI provides access to key functionality including text-to-speech synthesis, model training, and evaluation.

## Table of Contents

1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Text-to-Speech Synthesis](#text-to-speech-synthesis)
4. [Model Training](#model-training)
5. [Interactive Demo](#interactive-demo)
6. [Dataset Preparation and Metadata Generation](#dataset-preparation-and-metadata-generation)
7. [Text Normalization](#text-normalization)
8. [API Server](#api-server)
9. [Advanced Usage](#advanced-usage)
10. [Environment Variables](#environment-variables)
11. [Troubleshooting](#troubleshooting)

## Installation

Before using the CLI, ensure that Kalakan TTS is properly installed:

```bash
# Install from PyPI
pip install kalakan-tts

# Or install from source
git clone https://github.com/kalakan-ai/kalakan-tts.git
cd kalakan-tts
pip install -e .
```

After installation, the following CLI commands will be available:

- `kalakan synthesize`: Generate speech from text
- `kalakan train`: Train acoustic models and vocoders
- `kalakan demo`: Run interactive TTS demo
- `kalakan gen-metadata`: Generate comprehensive dataset metadata with phonemes
- `kalakan norm`: Normalize Twi text for TTS processing
- `kalakan api`: Start the API server

## Basic Usage

To get help for any command, use the `--help` flag:

```bash
kalakan synthesize --help
kalakan train --help
kalakan demo --help
kalakan gen-metadata --help
kalakan norm --help
kalakan api --help
```

## Text-to-Speech Synthesis

The `kalakan synthesize` command converts text to speech and saves the result to an audio file.

### Basic Synthesis

```bash
kalakan synthesize \
    --text "Akwaaba! Wo ho te sɛn?" \
    --output output.wav
```

This uses the default models to synthesize the provided text and save it to `output.wav`.

### Using Specific Models

```bash
kalakan-synthesize \
    --text "Akwaaba! Wo ho te sɛn?" \
    --output output.wav \
    --acoustic-model /path/to/acoustic_model.pt \
    --vocoder /path/to/vocoder.pt
```

### Specifying Model Types

```bash
kalakan-synthesize \
    --text "Akwaaba! Wo ho te sɛn?" \
    --output output.wav \
    --acoustic-model-type tacotron2 \
    --vocoder-type hifigan
```

This uses the default Tacotron2 acoustic model and HiFi-GAN vocoder.

### Using a Configuration File

```bash
kalakan-synthesize \
    --text "Akwaaba! Wo ho te sɛn?" \
    --output output.wav \
    --config /path/to/config.yaml
```

### Batch Synthesis

```bash
kalakan-synthesize \
    --input texts.txt \
    --output-dir output_directory \
    --acoustic-model /path/to/acoustic_model.pt \
    --vocoder /path/to/vocoder.pt
```

Where `texts.txt` contains one text per line.

### Advanced Options

```bash
kalakan-synthesize \
    --text "Akwaaba! Wo ho te sɛn?" \
    --output output.wav \
    --acoustic-model /path/to/acoustic_model.pt \
    --vocoder /path/to/vocoder.pt \
    --device cuda:0 \
    --no-normalize \
    --no-clean \
    --sample-rate 22050
```

### Full Command Reference

```
Usage: kalakan-synthesize [OPTIONS]

Options:
  --text TEXT                     Input text to synthesize
  --input FILE                    Input file containing texts (one per line)
  --output FILE                   Output audio file
  --output-dir DIRECTORY          Output directory for batch synthesis
  --acoustic-model FILE           Path to acoustic model checkpoint
  --vocoder FILE                  Path to vocoder checkpoint
  --acoustic-model-type TEXT      Type of acoustic model (tacotron2, fastspeech2, transformer_tts)
  --vocoder-type TEXT             Type of vocoder (griffin_lim, hifigan, melgan, waveglow)
  --config FILE                   Path to configuration file
  --device TEXT                   Device to use (cpu, cuda, cuda:0, etc.)
  --normalize / --no-normalize    Whether to normalize text (default: normalize)
  --clean / --no-clean            Whether to clean text (default: clean)
  --sample-rate INTEGER           Sample rate of output audio
  --help                          Show this message and exit
```

## Model Training

The `kalakan-train` command trains acoustic models and vocoders.

### Training an Acoustic Model

```bash
kalakan-train \
    --model-type tacotron2 \
    --data-dir /path/to/dataset \
    --output-dir /path/to/output \
    --config configs/training/acoustic_training.yaml
```

### Training a Vocoder

```bash
kalakan-train \
    --model-type hifigan \
    --data-dir /path/to/dataset \
    --output-dir /path/to/output \
    --config configs/training/vocoder_training.yaml
```

### Resuming Training

```bash
kalakan-train \
    --model-type tacotron2 \
    --data-dir /path/to/dataset \
    --output-dir /path/to/output \
    --config configs/training/acoustic_training.yaml \
    --checkpoint /path/to/checkpoint.pt \
    --resume
```

### Distributed Training

```bash
kalakan-train \
    --model-type tacotron2 \
    --data-dir /path/to/dataset \
    --output-dir /path/to/output \
    --config configs/training/acoustic_training.yaml \
    --distributed \
    --world-size 4 \
    --rank 0
```

### Fine-tuning

```bash
kalakan-train \
    --model-type tacotron2 \
    --data-dir /path/to/dataset \
    --output-dir /path/to/output \
    --config configs/training/acoustic_training.yaml \
    --checkpoint /path/to/pretrained_model.pt \
    --learning-rate 0.0001 \
    --epochs 100
```

### Full Command Reference

```
Usage: kalakan-train [OPTIONS]

Options:
  --model-type TEXT               Type of model to train (tacotron2, fastspeech2, hifigan, etc.)
  --data-dir DIRECTORY            Directory containing the training data
  --output-dir DIRECTORY          Directory to save the trained model
  --config FILE                   Path to configuration file
  --checkpoint FILE               Path to checkpoint file for resuming training
  --resume                        Resume training from checkpoint
  --device TEXT                   Device to use (cpu, cuda, cuda:0, etc.)
  --batch-size INTEGER            Batch size for training
  --epochs INTEGER                Number of epochs to train
  --learning-rate FLOAT           Learning rate for training
  --distributed                   Use distributed training
  --world-size INTEGER            Number of processes for distributed training
  --rank INTEGER                  Rank of the current process for distributed training
  --seed INTEGER                  Random seed for reproducibility
  --help                          Show this message and exit
```

## Interactive Demo

The `kalakan demo` command provides a simple way to test TTS synthesis with custom text input.

### Basic Demo

```bash
kalakan demo \
    --text "Akwaaba! Wo ho te sɛn?" \
    --output demo.wav \
    --acoustic_model /path/to/acoustic_model.pt \
    --vocoder /path/to/vocoder.pt
```

### Demo with Text Processing

```bash
kalakan demo \
    --text "Dr. Kwame bɛba ha 25 mu" \
    --output demo.wav \
    --acoustic_model /path/to/acoustic_model.pt \
    --vocoder /path/to/vocoder.pt \
    --normalize \
    --clean
```

### Demo with Speech Control

```bash
kalakan demo \
    --text "Akwaaba! Wo ho te sɛn?" \
    --output demo.wav \
    --acoustic_model /path/to/acoustic_model.pt \
    --vocoder /path/to/vocoder.pt \
    --speed 1.2 \
    --pitch 0.9 \
    --energy 1.1
```

### Using Environment Variables

```bash
# Set environment variables
export KALAKAN_ACOUSTIC_MODEL=/path/to/acoustic_model.pt
export KALAKAN_VOCODER=/path/to/vocoder.pt

# Run demo without specifying models
kalakan demo --text "Akwaaba! Wo ho te sɛn?" --output demo.wav
```

### Full Command Reference

```
Usage: kalakan demo [OPTIONS]

Required Arguments:
  --text, -t TEXT                 Text to synthesize [required]

Output Options:
  --output, -o TEXT               Output audio file (default: output.wav)

Model Options:
  --acoustic_model, -a TEXT       Path to acoustic model checkpoint or model name
  --vocoder, -v TEXT              Path to vocoder checkpoint or model name

Text Processing Options:
  --normalize                     Normalize text before synthesis
  --clean                         Clean text before synthesis

Synthesis Control:
  --speed FLOAT                   Speech speed factor (default: 1.0)
  --pitch FLOAT                   Pitch factor (default: 1.0)
  --energy FLOAT                  Energy factor (default: 1.0)

Device Options:
  --device TEXT                   Device to use for inference (e.g., 'cuda:0', 'cpu')

  --help                          Show this message and exit
```

### Environment Variables

The demo command supports the following environment variables:

- `KALAKAN_ACOUSTIC_MODEL`: Default acoustic model path
- `KALAKAN_VOCODER`: Default vocoder path

This allows you to set up your environment once and run demos without specifying model paths each time.

## Dataset Preparation and Metadata Generation

The `kalakan gen-metadata` command generates comprehensive metadata for TTS datasets, including phoneme generation, text normalization, dataset splitting, and quality validation.

### Basic Metadata Generation

```bash
kalakan gen-metadata \
    --input-dir /path/to/dataset \
    --verbose
```

This will:
- Discover audio files in the `wavs/` subdirectory
- Load transcripts from `transcript.txt` or `metadata.csv`
- Generate normalized metadata with duration information
- Save results to `metadata.csv`

### Advanced Metadata Generation with Phonemes

```bash
kalakan gen-metadata \
    --input-dir /path/to/dataset \
    --generate-phonemes \
    --split-dataset \
    --val-ratio 0.2 \
    --test-ratio 0.2 \
    --output-format both \
    --include-stats \
    --verbose
```

This generates:
- Phoneme sequences using the Twi G2P model
- Train/validation/test splits
- Both CSV and JSON output formats
- Comprehensive dataset statistics

### Working with Different Transcript Formats

#### CSV Transcripts
```bash
kalakan gen-metadata \
    --input-dir /path/to/dataset \
    --transcript-file dataset/transcripts.csv \
    --transcript-format csv \
    --transcript-delimiter "," \
    --text-column 2 \
    --id-column 0 \
    --verbose
```

#### JSON Transcripts
```bash
kalakan gen-metadata \
    --input-dir /path/to/dataset \
    --transcript-file dataset/transcripts.json \
    --transcript-format json \
    --text-field "text" \
    --id-field "id" \
    --verbose
```

### Quality Control and Validation

```bash
kalakan gen-metadata \
    --input-dir /path/to/dataset \
    --min-duration 0.5 \
    --max-duration 10.0 \
    --min-text-length 5 \
    --max-text-length 200 \
    --check-duplicates \
    --remove-duplicates \
    --verbose
```

### Text Processing Options

```bash
kalakan gen-metadata \
    --input-dir /path/to/dataset \
    --normalize-text \
    --clean-text \
    --expand-abbreviations \
    --convert-numbers \
    --verbose
```

### Multi-Speaker Dataset Support

```bash
kalakan gen-metadata \
    --input-dir /path/to/dataset \
    --speaker-id "speaker_001" \
    --language "twi" \
    --generate-phonemes \
    --verbose
```

### Comprehensive Example

```bash
kalakan gen-metadata \
    --input-dir /path/to/twi_dataset \
    --transcript-file dataset/transcripts.csv \
    --transcript-format csv \
    --transcript-delimiter "," \
    --text-column 1 \
    --id-column 0 \
    --generate-phonemes \
    --split-dataset \
    --val-ratio 0.15 \
    --test-ratio 0.15 \
    --output-format both \
    --include-stats \
    --check-duplicates \
    --remove-duplicates \
    --speaker-id "twi_speaker_001" \
    --language "twi" \
    --min-duration 0.5 \
    --max-duration 10.0 \
    --min-text-length 10 \
    --max-text-length 150 \
    --normalize-text \
    --clean-text \
    --audio-ext "wav" \
    --verbose
```

### Output Files

The metadata generation creates several output files:

#### Single Dataset (no splitting)
- `metadata.csv` - Main metadata file
- `metadata.json` - JSON format (if `--output-format both`)
- `dataset_stats.json` - Dataset statistics (if `--include-stats`)

#### Split Dataset
- `train.csv` / `train.json` - Training set
- `val.csv` / `val.json` - Validation set
- `test.csv` / `test.json` - Test set (if test ratio > 0)
- `dataset_stats.json` - Comprehensive statistics

### Metadata File Format

#### CSV Format
```csv
id|audio_path|duration|text|phonemes|speaker_id|language
demo_001|wavs\demo_001.wav|2.50|agoo kalculus, mepa wo kyɛw|a g o o k a l k u l u s m e p a w o ky ɛ w|speaker_001|twi
```

#### JSON Format
```json
[
  {
    "id": "demo_001",
    "audio_path": "wavs\\demo_001.wav",
    "duration": 2.5,
    "text": "agoo kalculus, mepa wo kyɛw",
    "original_text": "Agoo Kalculus, mepa wo kyɛw",
    "phonemes": ["a", "g", "o", "o", "k", "a", "l", "k", "u", "l", "u", "s", "m", "e", "p", "a", "w", "o", "ky", "ɛ", "w"],
    "speaker_id": "speaker_001",
    "language": "twi"
  }
]
```

### Full Command Reference

```
Usage: kalakan gen-metadata [OPTIONS]

Input/Output Options:
  --input-dir DIRECTORY           Directory containing the dataset
  --output-dir DIRECTORY          Output directory (default: same as input-dir)
  --transcript-file FILE          Path to transcript file (auto-detected if not specified)

Transcript Format Options:
  --transcript-format TEXT        Format: txt, csv, json (default: auto-detect)
  --transcript-delimiter TEXT     CSV delimiter (default: |)
  --text-column INTEGER           CSV text column index (0-based, default: 1)
  --id-column INTEGER             CSV ID column index (0-based, default: 0)
  --text-field TEXT               JSON text field name (default: text)
  --id-field TEXT                 JSON ID field name (default: id)

Audio Processing Options:
  --audio-ext TEXT                Audio file extension (default: wav)
  --min-duration FLOAT            Minimum audio duration in seconds (default: 0.5)
  --max-duration FLOAT            Maximum audio duration in seconds (default: 10.0)

Text Processing Options:
  --normalize-text                Normalize text (lowercase, expand abbreviations)
  --clean-text                    Clean text (remove extra whitespace, punctuation)
  --expand-abbreviations          Expand abbreviations (Dr. -> doctor)
  --convert-numbers               Convert numbers to words
  --min-text-length INTEGER       Minimum text length in characters (default: 1)
  --max-text-length INTEGER       Maximum text length in characters (default: 500)

Phoneme Generation:
  --generate-phonemes             Generate phoneme sequences using G2P

Dataset Splitting:
  --split-dataset                 Split dataset into train/val/test
  --val-ratio FLOAT               Validation set ratio (default: 0.1)
  --test-ratio FLOAT              Test set ratio (default: 0.1)
  --random-seed INTEGER           Random seed for splitting (default: 42)

Output Format:
  --output-format TEXT            Output format: csv, json, both (default: csv)
  --include-stats                 Generate dataset statistics

Quality Control:
  --check-duplicates              Check for duplicate texts
  --remove-duplicates             Remove duplicate texts (keep first occurrence)

Metadata Options:
  --speaker-id TEXT               Speaker ID to add to metadata
  --language TEXT                 Language code (default: twi)

Logging:
  --verbose                       Enable verbose logging
  --quiet                         Suppress all output except errors

  --help                          Show this message and exit
```

### Dataset Statistics

When using `--include-stats`, a comprehensive statistics file is generated:

```json
{
  "total_entries": 100,
  "skipped_entries": 5,
  "total_duration": 450.5,
  "avg_duration": 4.5,
  "min_duration": 1.2,
  "max_duration": 9.8,
  "avg_text_length": 45.2,
  "min_text_length": 15,
  "max_text_length": 120,
  "train_size": 70,
  "val_size": 15,
  "test_size": 15,
  "duplicate_texts": 2,
  "processing_time": 125.3
}
```

## Text Normalization

The `kalakan norm` command provides comprehensive text normalization capabilities specifically designed for Twi text processing. This is essential for preparing text for TTS synthesis and ensuring consistent text representation.

### Basic Text Normalization

```bash
# Normalize text directly from command line
kalakan norm --text "Dr. Kwame na Prof. Ama bɛba ha 25 mu."
```

Output:
```
dr. kwame na prof. ama bɛba ha 25 mu.
```

### File-Based Normalization

```bash
# Normalize text from a file
kalakan norm --file input.txt --output normalized.txt
```

### Interactive File Selection

```bash
# Open file dialog to select text file
kalakan norm --select
```

### Batch Processing

```bash
# Process multiple files with file dialog
kalakan norm --select --batch --output-dir ./normalized_texts
```

### Advanced Normalization Options

```bash
# Customize normalization behavior
kalakan norm \
    --file input.txt \
    --output normalized.txt \
    --no-numbers \
    --no-abbreviations \
    --preserve-case \
    --show-diff \
    --format json \
    --verbose
```

### Normalization Features

#### Default Normalization Process:
1. **Abbreviation Expansion**: "Dr." → "doctor", "Prof." → "professor"
2. **Case Conversion**: Convert to lowercase
3. **Punctuation Normalization**: Standardize punctuation marks
4. **Number Processing**: Convert numbers to text representation
5. **Special Character Normalization**:
   - 'ε' → 'ɛ' (epsilon normalization)
   - 'Ε' → 'Ɛ' (capital epsilon)
   - 'ο' → 'ɔ' (open o normalization)
   - 'Ο' → 'Ɔ' (capital open o)

#### Customization Options:
- `--no-numbers`: Skip number normalization
- `--no-abbreviations`: Skip abbreviation expansion
- `--no-punctuation`: Skip punctuation normalization
- `--preserve-case`: Keep original case (don't convert to lowercase)

### Output Formats

#### Text Format (Default)
```bash
kalakan norm --text "Dr. Kwame bɛba ha 25 mu." --format text
```
Output:
```
dr. kwame bɛba ha 25 mu.
```

#### JSON Format
```bash
kalakan norm --text "Dr. Kwame bɛba ha 25 mu." --format json
```
Output:
```json
{
  "original": "Dr. Kwame bɛba ha 25 mu.",
  "normalized": "dr. kwame bɛba ha 25 mu."
}
```

#### CSV Format
```bash
kalakan norm --text "Dr. Kwame bɛba ha 25 mu." --format csv
```
Output:
```csv
Original,Normalized
"Dr. Kwame bɛba ha 25 mu.","dr. kwame bɛba ha 25 mu."
```

### Difference Visualization

```bash
# Show differences between original and normalized text
kalakan norm --text "Dr. Kwame bɛba ha 25 mu." --show-diff
```
Output:
```
Original:   Dr. Kwame bɛba ha 25 mu.
Normalized: dr. kwame bɛba ha 25 mu.
```

### Recursive Directory Processing

```bash
# Process all .txt files in a directory recursively
kalakan norm \
    --file ./text_directory \
    --recursive \
    --output-dir ./normalized_output \
    --format json \
    --verbose
```

### Encoding Support

```bash
# Specify file encoding for non-UTF-8 files
kalakan norm \
    --file legacy_text.txt \
    --encoding latin-1 \
    --output normalized.txt
```

### Full Command Reference

```
Usage: kalakan norm [OPTIONS]

Input Options (mutually exclusive):
  -T, --text TEXT                 Direct Twi text input to normalize
  -S, --select                    Open file dialog to select Twi text file
  -f, --file TEXT                 Path to text file to normalize

Output Options:
  -o, --output TEXT               Output file path (default: print to stdout)
  --output-dir TEXT               Output directory for batch processing

Processing Options:
  --no-numbers                    Skip number normalization
  --no-abbreviations              Skip abbreviation expansion
  --no-punctuation                Skip punctuation normalization
  --preserve-case                 Preserve original case (don't convert to lowercase)

Format Options:
  --format {text,json,csv}        Output format (default: text)
  --encoding TEXT                 File encoding (default: utf-8)

Batch Processing:
  --batch                         Process multiple files (when using --select)
  --recursive                     Process files recursively in directories

Display Options:
  --verbose, -v                   Verbose output
  --quiet, -q                     Quiet mode (minimal output)
  --show-diff                     Show differences between original and normalized text

  --help                          Show this message and exit
```

### Use Cases

#### 1. Preparing Text for TTS Synthesis
```bash
# Normalize text before synthesis to ensure consistent pronunciation
kalakan norm --text "Dr. Kwame bɛba ha 25 mu." | kalakan synthesize --output speech.wav
```

#### 2. Dataset Text Preprocessing
```bash
# Normalize all text files in a dataset
kalakan norm \
    --file ./dataset/texts \
    --recursive \
    --output-dir ./dataset/normalized_texts \
    --format text \
    --verbose
```

#### 3. Text Quality Analysis
```bash
# Analyze normalization changes with diff view
kalakan norm \
    --file manuscript.txt \
    --show-diff \
    --format json \
    --output analysis.json
```

#### 4. Batch Text Processing
```bash
# Interactive batch processing with file selection
kalakan norm \
    --select \
    --batch \
    --output-dir ./processed \
    --format csv \
    --show-diff
```

### Integration with Other Commands

The text normalization can be seamlessly integrated with other Kalakan TTS commands:

#### With Synthesis
```bash
# Normalize and synthesize in one pipeline
echo "Dr. Kwame bɛba ha 25 mu." | kalakan norm --text - | kalakan synthesize --output result.wav
```

#### With Metadata Generation
The `kalakan gen-metadata` command automatically uses similar normalization when the `--normalize-text` flag is enabled, ensuring consistency across the pipeline.

### Best Practices

1. **Always normalize text** before TTS synthesis for consistent results
2. **Use `--show-diff`** to review normalization changes
3. **Preserve original text** by saving both versions when processing datasets
4. **Use appropriate encoding** for legacy text files
5. **Batch process** large datasets for efficiency

## API Server

The `kalakan-api` command starts the API server for Kalakan TTS.

### Starting the REST API Server

```bash
kalakan-api \
    --host 0.0.0.0 \
    --port 8000 \
    --acoustic-model /path/to/acoustic_model.pt \
    --vocoder /path/to/vocoder.pt
```

### Starting the gRPC API Server

```bash
kalakan-api \
    --host 0.0.0.0 \
    --port 50051 \
    --acoustic-model /path/to/acoustic_model.pt \
    --vocoder /path/to/vocoder.pt \
    --api-type grpc
```

### Full Command Reference

```
Usage: kalakan-api [OPTIONS]

Options:
  --host TEXT                     Host to bind the server to
  --port INTEGER                  Port to bind the server to
  --acoustic-model FILE           Path to acoustic model checkpoint
  --vocoder FILE                  Path to vocoder checkpoint
  --api-type TEXT                 Type of API server (rest, grpc)
  --config FILE                   Path to configuration file
  --device TEXT                   Device to use (cpu, cuda, cuda:0, etc.)
  --workers INTEGER               Number of worker processes
  --help                          Show this message and exit
```

## Advanced Usage

### Using Environment Variables

You can use environment variables to set default values for CLI options:

```bash
export KALAKAN_ACOUSTIC_MODEL=/path/to/acoustic_model.pt
export KALAKAN_VOCODER=/path/to/vocoder.pt
export KALAKAN_DEVICE=cuda:0

# Now you can omit these options in the command
kalakan-synthesize --text "Akwaaba! Wo ho te sɛn?" --output output.wav
```

### Using Configuration Files

You can use configuration files to set default values for CLI options:

```yaml
# config.yaml
acoustic_model: /path/to/acoustic_model.pt
vocoder: /path/to/vocoder.pt
device: cuda:0
```

```bash
kalakan-synthesize --text "Akwaaba! Wo ho te sɛn?" --output output.wav --config config.yaml
```

### Scripting with the CLI

You can use the CLI in shell scripts for batch processing:

```bash
#!/bin/bash

# Process a list of texts
while IFS= read -r text; do
    output_file="output_$(md5sum <<< "$text" | cut -d' ' -f1).wav"
    kalakan-synthesize --text "$text" --output "$output_file"
done < texts.txt
```

## Environment Variables

The following environment variables can be used to configure the CLI:

| Variable | Description | Default |
|----------|-------------|---------|
| `KALAKAN_ACOUSTIC_MODEL` | Path to acoustic model checkpoint | None |
| `KALAKAN_VOCODER` | Path to vocoder checkpoint | None |
| `KALAKAN_DEVICE` | Device to use for inference | cpu |
| `KALAKAN_CONFIG` | Path to configuration file | None |
| `KALAKAN_DATA_DIR` | Directory containing datasets | None |
| `KALAKAN_OUTPUT_DIR` | Directory to save outputs | None |
| `KALAKAN_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |

## Troubleshooting

### Common Issues

#### Model Loading Errors

```
Error: Failed to load model from /path/to/model.pt
```

**Solution**: Ensure that the model file exists and is a valid PyTorch checkpoint. If the model was trained with a different version of PyTorch, try loading it with `torch.load(..., map_location='cpu')`.

#### CUDA Out of Memory

```
RuntimeError: CUDA out of memory
```

**Solution**: Reduce batch size, use a smaller model, or use CPU inference with `--device cpu`.

#### Audio Output Issues

```
Error: Failed to save audio to output.wav
```

**Solution**: Ensure that the output directory exists and is writable. Check that the audio data is valid (not NaN or infinite).

#### API Server Binding Issues

```
Error: Failed to bind to address 0.0.0.0:8000
```

**Solution**: Ensure that the port is not already in use. Try a different port or stop the process using the current port.

### Getting Help

If you encounter issues not covered in this guide, you can:

1. Check the logs for detailed error messages
2. Run the command with increased verbosity: `--log-level DEBUG`
3. Open an issue on the GitHub repository
4. Contact the Kalakan TTS team for support

---

This CLI usage guide provides comprehensive documentation for using the Kalakan TTS system through its command line interface. For more detailed information on specific features, refer to the API reference and other documentation in the `docs/` directory.
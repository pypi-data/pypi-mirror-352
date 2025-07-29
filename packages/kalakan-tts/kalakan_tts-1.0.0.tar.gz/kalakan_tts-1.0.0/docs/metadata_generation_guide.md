# Kalakan TTS Metadata Generation Guide

This comprehensive guide covers the `kalakan gen-metadata` command, which generates high-quality metadata for TTS datasets including phoneme sequences, text normalization, dataset splitting, and quality validation.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Input Formats](#input-formats)
4. [Text Processing](#text-processing)
5. [Phoneme Generation](#phoneme-generation)
6. [Dataset Splitting](#dataset-splitting)
7. [Quality Control](#quality-control)
8. [Output Formats](#output-formats)
9. [Advanced Usage](#advanced-usage)
10. [Command Reference](#command-reference)
11. [Examples](#examples)
12. [Troubleshooting](#troubleshooting)

## Overview

The metadata generation tool is designed to prepare TTS datasets for training by:

- **Audio Processing**: Discovering and validating audio files
- **Text Normalization**: Cleaning and standardizing text content
- **Phoneme Generation**: Converting text to phoneme sequences using G2P models
- **Dataset Splitting**: Creating train/validation/test splits
- **Quality Validation**: Filtering based on duration, text length, and duplicates
- **Multiple Output Formats**: Generating CSV and JSON metadata files
- **Statistics Generation**: Providing comprehensive dataset analytics

## Quick Start

### Basic Usage

```bash
# Generate basic metadata for a dataset
kalakan gen-metadata --input-dir /path/to/dataset --verbose
```

This assumes your dataset has the following structure:
```
dataset/
├── wavs/
│   ├── audio_001.wav
│   ├── audio_002.wav
│   └── ...
└── transcript.txt  # or metadata.csv
```

### With Phonemes and Dataset Splitting

```bash
# Generate comprehensive metadata with phonemes and splits
kalakan gen-metadata \
    --input-dir /path/to/dataset \
    --generate-phonemes \
    --split-dataset \
    --val-ratio 0.2 \
    --test-ratio 0.1 \
    --output-format both \
    --include-stats \
    --verbose
```

## Input Formats

### Directory Structure

The tool expects the following directory structure:

```
dataset/
├── wavs/                    # Audio files directory
│   ├── file_001.wav
│   ├── file_002.wav
│   └── ...
└── transcript.txt           # Transcript file (various formats supported)
```

### Transcript Formats

#### 1. Pipe-Delimited Text (Default)
```
file_001|Agoo Kalculus, mepa wo kyɛw.
file_002|Dr. Kwame bɛba ha.
file_003|Mepɛ sɛ mekɔ fie.
```

#### 2. CSV Format
```csv
id,text,speaker
file_001,"Agoo Kalculus, mepa wo kyɛw.",speaker_001
file_002,"Dr. Kwame bɛba ha.",speaker_001
file_003,"Mepɛ sɛ mekɔ fie.",speaker_001
```

Usage:
```bash
kalakan gen-metadata \
    --input-dir /path/to/dataset \
    --transcript-file dataset/transcripts.csv \
    --transcript-format csv \
    --transcript-delimiter "," \
    --text-column 1 \
    --id-column 0
```

#### 3. JSON Format
```json
[
  {
    "id": "file_001",
    "text": "Agoo Kalculus, mepa wo kyɛw.",
    "speaker": "speaker_001"
  },
  {
    "id": "file_002",
    "text": "Dr. Kwame bɛba ha.",
    "speaker": "speaker_001"
  }
]
```

Usage:
```bash
kalakan gen-metadata \
    --input-dir /path/to/dataset \
    --transcript-file dataset/transcripts.json \
    --transcript-format json \
    --text-field "text" \
    --id-field "id"
```

## Text Processing

### Normalization Options

The tool provides comprehensive text processing capabilities:

```bash
kalakan gen-metadata \
    --input-dir /path/to/dataset \
    --normalize-text \
    --clean-text \
    --expand-abbreviations \
    --convert-numbers \
    --verbose
```

#### Text Normalization Features:
- **Lowercase conversion**: "Hello" → "hello"
- **Abbreviation expansion**: "Dr." → "doctor", "Prof." → "professor"
- **Number conversion**: "25" → "twenty-five" (language-specific)
- **Punctuation handling**: Smart removal/preservation
- **Whitespace normalization**: Multiple spaces → single space

#### Example Transformations:
```
Original: "Dr. Kwame na Prof. Ama bɛba ha 25 mu."
Normalized: "dr. kwame na prof. ama bɛba ha mu."
```

### Text Validation

```bash
kalakan gen-metadata \
    --input-dir /path/to/dataset \
    --min-text-length 10 \
    --max-text-length 150 \
    --verbose
```

## Phoneme Generation

### Enabling Phoneme Generation

```bash
kalakan gen-metadata \
    --input-dir /path/to/dataset \
    --generate-phonemes \
    --verbose
```

### How It Works

The tool uses the Enhanced Twi G2P (Grapheme-to-Phoneme) model to convert text to phoneme sequences:

```
Text: "agoo kalculus, mepa wo kyɛw"
Phonemes: ["a", "g", "o", "o", "k", "a", "l", "k", "u", "l", "u", "s", "m", "e", "p", "a", "w", "o", "ky", "ɛ", "w"]
```

### Phoneme Features:
- **Language-specific**: Optimized for Twi phonology
- **Context-aware**: Considers phonetic context
- **Consistent**: Reproducible phoneme sequences
- **Comprehensive**: Handles all Twi phonemes and combinations

## Dataset Splitting

### Basic Splitting

```bash
kalakan gen-metadata \
    --input-dir /path/to/dataset \
    --split-dataset \
    --val-ratio 0.15 \
    --test-ratio 0.15 \
    --random-seed 42 \
    --verbose
```

This creates:
- **Training set**: 70% of data
- **Validation set**: 15% of data
- **Test set**: 15% of data

### Output Files:
- `train.csv` / `train.json`
- `val.csv` / `val.json`
- `test.csv` / `test.json`

### Splitting Strategy:
- **Random sampling**: Ensures balanced distribution
- **Reproducible**: Fixed random seed for consistency
- **Stratified**: Maintains speaker distribution (if applicable)

## Quality Control

### Audio Validation

```bash
kalakan gen-metadata \
    --input-dir /path/to/dataset \
    --min-duration 0.5 \
    --max-duration 10.0 \
    --verbose
```

### Duplicate Detection

```bash
kalakan gen-metadata \
    --input-dir /path/to/dataset \
    --check-duplicates \
    --remove-duplicates \
    --verbose
```

#### Duplicate Handling:
- **Detection**: Identifies identical text content
- **Reporting**: Lists all duplicate groups
- **Removal**: Keeps first occurrence, removes others
- **Logging**: Detailed information about removed duplicates

### Quality Metrics:
- **Audio duration**: Filters too short/long recordings
- **Text length**: Validates text content length
- **File integrity**: Checks audio file validity
- **Transcript matching**: Ensures audio-text alignment

## Output Formats

### CSV Format (Default)

```csv
id|audio_path|duration|text|phonemes|speaker_id|language
demo_001|wavs\demo_001.wav|2.50|agoo kalculus, mepa wo kyɛw|a g o o k a l k u l u s m e p a w o ky ɛ w|speaker_001|twi
```

### JSON Format

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

### Both Formats

```bash
kalakan gen-metadata \
    --input-dir /path/to/dataset \
    --output-format both \
    --verbose
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

## Advanced Usage

### Multi-Speaker Datasets

```bash
kalakan gen-metadata \
    --input-dir /path/to/dataset \
    --speaker-id "speaker_twi_001" \
    --language "twi" \
    --generate-phonemes \
    --verbose
```

### Custom Audio Extensions

```bash
kalakan gen-metadata \
    --input-dir /path/to/dataset \
    --audio-ext "flac" \
    --verbose
```

### Comprehensive Processing Pipeline

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
    --random-seed 42 \
    --verbose
```

## Command Reference

```
Usage: kalakan gen-metadata [OPTIONS]

Input/Output Options:
  --input-dir DIRECTORY           Directory containing the dataset [required]
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

## Examples

### Example 1: Basic Metadata Generation

```bash
# Simple metadata generation for a small dataset
kalakan gen-metadata \
    --input-dir ./my_dataset \
    --verbose
```

**Input Structure:**
```
my_dataset/
├── wavs/
│   ├── audio_001.wav
│   ├── audio_002.wav
│   └── audio_003.wav
└── transcript.txt
```

**Output:**
- `metadata.csv` with basic audio and text information

### Example 2: Complete TTS Dataset Preparation

```bash
# Comprehensive dataset preparation with all features
kalakan gen-metadata \
    --input-dir ./twi_speech_dataset \
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
    --min-duration 1.0 \
    --max-duration 8.0 \
    --speaker-id "twi_native_speaker_001" \
    --verbose
```

**Output Files:**
- `train.csv` / `train.json` (70% of data)
- `val.csv` / `val.json` (20% of data)
- `test.csv` / `test.json` (10% of data)
- `dataset_stats.json` (comprehensive statistics)

### Example 3: Working with CSV Transcripts

```bash
# Processing dataset with CSV transcript file
kalakan gen-metadata \
    --input-dir ./csv_dataset \
    --transcript-file ./csv_dataset/metadata.csv \
    --transcript-format csv \
    --transcript-delimiter "," \
    --text-column 2 \
    --id-column 0 \
    --generate-phonemes \
    --speaker-id "speaker_002" \
    --verbose
```

**CSV Input Format:**
```csv
id,speaker,text,duration
twi_001,speaker_002,"Agoo Kalculus, mepa wo kyɛw",2.5
twi_002,speaker_002,"Dr. Kwame bɛba ha",3.2
```

### Example 4: Quality Control Focus

```bash
# Emphasizing quality control and validation
kalakan gen-metadata \
    --input-dir ./quality_dataset \
    --min-duration 2.0 \
    --max-duration 6.0 \
    --min-text-length 20 \
    --max-text-length 100 \
    --check-duplicates \
    --remove-duplicates \
    --normalize-text \
    --clean-text \
    --include-stats \
    --verbose
```

### Example 5: Multi-Format Output

```bash
# Generate both CSV and JSON with comprehensive metadata
kalakan gen-metadata \
    --input-dir ./multi_format_dataset \
    --generate-phonemes \
    --split-dataset \
    --output-format both \
    --include-stats \
    --speaker-id "multi_speaker_001" \
    --language "twi" \
    --verbose
```

## Troubleshooting

### Common Issues and Solutions

#### 1. No Audio Files Found

**Error:**
```
ERROR - No audio files found in directory: /path/to/dataset/wavs
```

**Solutions:**
- Verify the directory structure includes a `wavs/` subdirectory
- Check that audio files have the correct extension (default: `.wav`)
- Use `--audio-ext` to specify different extensions: `--audio-ext "flac"`

#### 2. Transcript File Not Found

**Error:**
```
ERROR - Transcript file not found: /path/to/dataset/transcript.txt
```

**Solutions:**
- Ensure transcript file exists in the input directory
- Specify transcript file explicitly: `--transcript-file /path/to/transcripts.csv`
- Check file permissions and accessibility

#### 3. G2P Model Loading Issues

**Error:**
```
ERROR - Failed to initialize G2P model
```

**Solutions:**
- Ensure the Enhanced Twi G2P model is properly installed
- Check that all required dependencies are available
- Try running without `--generate-phonemes` first to isolate the issue

#### 4. Memory Issues with Large Datasets

**Error:**
```
MemoryError: Unable to allocate memory for audio processing
```

**Solutions:**
- Process datasets in smaller batches
- Reduce audio quality temporarily for metadata generation
- Increase system memory or use a machine with more RAM

#### 5. Duplicate Text Handling

**Warning:**
```
WARNING - Found 5 duplicate texts
```

**Solutions:**
- Use `--remove-duplicates` to automatically remove duplicates
- Review duplicates manually before removal
- Check if duplicates are intentional (e.g., different speakers)

#### 6. Invalid Audio Files

**Error:**
```
ERROR - Failed to load audio file: corrupted_audio.wav
```

**Solutions:**
- Check audio file integrity
- Re-encode problematic audio files
- Use audio validation tools to identify corrupted files

### Performance Optimization

#### For Large Datasets:
1. **Use SSD storage** for faster I/O operations
2. **Increase batch processing** where applicable
3. **Monitor memory usage** during processing
4. **Use verbose logging** to track progress

#### For Better Quality:
1. **Enable all text processing options** for cleaner data
2. **Use strict duration filtering** to remove outliers
3. **Enable duplicate detection** to ensure data quality
4. **Review statistics** to understand dataset characteristics

### Validation Checklist

Before using generated metadata for training:

- [ ] **Audio files accessible**: All referenced audio files exist
- [ ] **Duration accuracy**: Audio durations match metadata
- [ ] **Text quality**: Normalized text is appropriate
- [ ] **Phoneme validity**: Generated phonemes look correct
- [ ] **Split balance**: Train/val/test splits are reasonable
- [ ] **No duplicates**: Duplicate detection completed
- [ ] **Statistics review**: Dataset statistics are as expected

## Best Practices

### 1. Dataset Organization
- Use consistent naming conventions for audio files
- Maintain clean directory structure
- Keep original and processed versions separate

### 2. Quality Control
- Always enable duplicate detection for new datasets
- Use appropriate duration filters for your use case
- Review generated phonemes for accuracy

### 3. Text Processing
- Enable normalization for consistent training data
- Use language-appropriate text cleaning
- Validate text content before processing

### 4. Reproducibility
- Use fixed random seeds for consistent splits
- Document processing parameters used
- Keep processing logs for reference

### 5. Validation
- Always generate and review dataset statistics
- Manually check a sample of generated metadata
- Validate phoneme quality with native speakers

This comprehensive guide should help you effectively use the Kalakan TTS metadata generation tool to prepare high-quality datasets for TTS model training.
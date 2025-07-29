# Kalakan TTS Text Normalization Guide

This comprehensive guide covers the `kalakan norm` command, which provides advanced text normalization capabilities specifically designed for Twi text processing in TTS applications.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Input Methods](#input-methods)
4. [Normalization Features](#normalization-features)
5. [Output Formats](#output-formats)
6. [Advanced Usage](#advanced-usage)
7. [Command Reference](#command-reference)
8. [Examples](#examples)
9. [Integration](#integration)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

## Overview

The text normalization tool is essential for preparing Twi text for TTS synthesis. It ensures consistent text representation by:

- **Abbreviation Expansion**: Converting abbreviations to full words
- **Case Normalization**: Standardizing text case
- **Number Processing**: Converting numbers to text representation
- **Punctuation Handling**: Normalizing punctuation marks
- **Special Character Processing**: Handling Twi-specific characters
- **Multiple Input/Output Formats**: Supporting various text processing workflows

## Quick Start

### Basic Normalization

```bash
# Normalize text directly from command line
kalakan norm --text "Dr. Kwame na Prof. Ama bɛba ha 25 mu."
```

Output:
```
dr. kwame na prof. ama bɛba ha 25 mu.
```

### File Processing

```bash
# Normalize text from a file
kalakan norm --file input.txt --output normalized.txt
```

### Interactive Mode

```bash
# Open file dialog to select text file
kalakan norm --select
```

## Input Methods

### 1. Direct Text Input

```bash
# Process text directly from command line
kalakan norm --text "Agoo Kalculus! Dr. Kwame bɛba ha 25 mu."
```

### 2. File Input

```bash
# Process a single file
kalakan norm --file manuscript.txt --output normalized_manuscript.txt
```

### 3. Interactive File Selection

```bash
# Open GUI file picker
kalakan norm --select

# Batch mode with file picker
kalakan norm --select --batch --output-dir ./normalized
```

### 4. Directory Processing

```bash
# Process all .txt files in a directory
kalakan norm --file ./text_directory --recursive --output-dir ./normalized
```

## Normalization Features

### Default Normalization Pipeline

The normalization process follows this sequence:

1. **Abbreviation Expansion** (if enabled)
2. **Case Conversion** (if enabled)
3. **Punctuation Normalization** (if enabled)
4. **Number Processing** (if enabled)
5. **Special Character Normalization** (always applied)

### Abbreviation Expansion

Converts common abbreviations to their full forms:

```
Dr. → doctor
Prof. → professor
Mr. → mister
Mrs. → missus
Ms. → miss
```

Example:
```bash
kalakan norm --text "Dr. Kwame na Prof. Ama"
# Output: dr. kwame na prof. ama
```

### Case Normalization

Converts text to lowercase for consistent processing:

```
Original: "AGOO KALCULUS, Mepa Wo KYƐW"
Normalized: "agoo kalculus, mepa wo kyɛw"
```

Disable with `--preserve-case`:
```bash
kalakan norm --text "AGOO Kalculus" --preserve-case
# Output: AGOO Kalculus
```

### Number Processing

Converts numeric representations (implementation depends on language model):

```
Original: "Mepɛ sɛ mekɔ fie 25 mu"
Normalized: "mepɛ sɛ mekɔ fie 25 mu"  # Number processing applied
```

Disable with `--no-numbers`:
```bash
kalakan norm --text "Bɛba ha 25 mu" --no-numbers
```

### Punctuation Normalization

Standardizes punctuation marks and removes excessive punctuation:

```
Original: "Agoo!!!   Wo ho te sɛn???"
Normalized: "agoo! wo ho te sɛn?"
```

Disable with `--no-punctuation`:
```bash
kalakan norm --text "Agoo!!! Kalculus" --no-punctuation
```

### Special Character Normalization

Handles Twi-specific character normalization (always applied):

```
ε → ɛ  (epsilon to open e)
Ε → Ɛ  (capital epsilon to capital open e)
ο → ɔ  (omicron to open o)
Ο → Ɔ  (capital omicron to capital open o)
```

Example:
```bash
kalakan norm --text "Mεpε sε mεkɔ fiε"
# Output: mɛpɛ sɛ mɛkɔ fiɛ
```

## Output Formats

### Text Format (Default)

Simple text output:

```bash
kalakan norm --text "Dr. Kwame bɛba ha" --format text
```
Output:
```
dr. kwame bɛba ha
```

### JSON Format

Structured output with original and normalized text:

```bash
kalakan norm --text "Dr. Kwame bɛba ha" --format json
```
Output:
```json
{
  "original": "Dr. Kwame bɛba ha",
  "normalized": "dr. kwame bɛba ha"
}
```

With difference tracking:
```bash
kalakan norm --text "Dr. Kwame bɛba ha" --format json --show-diff
```
Output:
```json
{
  "original": "Dr. Kwame bɛba ha",
  "normalized": "dr. kwame bɛba ha",
  "changed": true
}
```

### CSV Format

Tabular output for batch processing:

```bash
kalakan norm --text "Dr. Kwame bɛba ha" --format csv
```
Output:
```csv
Original,Normalized
"Dr. Kwame bɛba ha","dr. kwame bɛba ha"
```

With difference tracking:
```bash
kalakan norm --text "Dr. Kwame bɛba ha" --format csv --show-diff
```
Output:
```csv
Original,Normalized,Changed
"Dr. Kwame bɛba ha","dr. kwame bɛba ha",True
```

## Advanced Usage

### Custom Normalization Options

```bash
# Selective normalization
kalakan norm \
    --text "Dr. Kwame bɛba ha 25 mu" \
    --no-numbers \
    --no-abbreviations \
    --preserve-case \
    --show-diff
```

### Batch Processing with Custom Settings

```bash
# Process multiple files with specific options
kalakan norm \
    --select \
    --batch \
    --output-dir ./processed \
    --format json \
    --no-punctuation \
    --show-diff \
    --verbose
```

### Encoding Handling

```bash
# Handle different file encodings
kalakan norm \
    --file legacy_text.txt \
    --encoding latin-1 \
    --output normalized.txt \
    --encoding utf-8
```

### Recursive Directory Processing

```bash
# Process all text files in directory tree
kalakan norm \
    --file ./manuscript_chapters \
    --recursive \
    --output-dir ./normalized_chapters \
    --format json \
    --show-diff \
    --verbose
```

## Command Reference

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

## Examples

### Example 1: Basic Text Normalization

```bash
# Simple normalization
kalakan norm --text "Dr. Kwame na Prof. Ama bɛba ha 25 mu."
```

**Output:**
```
dr. kwame na prof. ama bɛba ha 25 mu.
```

### Example 2: File Processing with Difference Tracking

```bash
# Process file and show changes
kalakan norm \
    --file manuscript.txt \
    --output normalized_manuscript.txt \
    --show-diff \
    --verbose
```

**Output:**
```
Processing: manuscript.txt
Original:   Dr. Kwame na Prof. Ama bɛba ha 25 mu.
Normalized: dr. kwame na prof. ama bɛba ha 25 mu.
Normalized 45 -> 43 characters
Saved to: normalized_manuscript.txt
```

### Example 3: Batch Processing with JSON Output

```bash
# Interactive batch processing
kalakan norm \
    --select \
    --batch \
    --output-dir ./normalized_texts \
    --format json \
    --show-diff \
    --verbose
```

**Generated Files:**
- `normalized_texts/text1_normalized.json`
- `normalized_texts/text2_normalized.json`
- etc.

### Example 4: Custom Normalization Pipeline

```bash
# Selective normalization preserving case and numbers
kalakan norm \
    --text "Dr. Kwame bɛba ha 25 mu nnε" \
    --preserve-case \
    --no-numbers \
    --format json \
    --show-diff
```

**Output:**
```json
{
  "original": "Dr. Kwame bɛba ha 25 mu nnε",
  "normalized": "doctor Kwame bɛba ha 25 mu nnɛ",
  "changed": true
}
```

### Example 5: Directory Processing

```bash
# Process all text files in a directory
kalakan norm \
    --file ./twi_texts \
    --recursive \
    --output-dir ./normalized_twi_texts \
    --format csv \
    --verbose
```

### Example 6: Pipeline Integration

```bash
# Normalize text and pipe to synthesis
echo "Dr. Kwame bɛba ha" | kalakan norm --text - | kalakan synthesize --output speech.wav
```

## Integration

### With TTS Synthesis

```bash
# Normalize before synthesis
kalakan norm --text "Dr. Kwame bɛba ha 25 mu" > normalized.txt
kalakan synthesize --file normalized.txt --output speech.wav
```

### With Metadata Generation

The `kalakan gen-metadata` command uses similar normalization when `--normalize-text` is enabled:

```bash
# Consistent normalization across pipeline
kalakan gen-metadata \
    --input-dir ./dataset \
    --normalize-text \
    --generate-phonemes
```

### With External Tools

```bash
# Export normalized text for external processing
kalakan norm \
    --file input.txt \
    --format json \
    --output normalized.json

# Process with external tool
python external_processor.py normalized.json
```

## Best Practices

### 1. Text Preparation

- **Always normalize** text before TTS synthesis
- **Review changes** using `--show-diff` for important texts
- **Preserve originals** by saving both versions

### 2. Batch Processing

- Use **consistent settings** across batches
- **Organize output** with meaningful directory structures
- **Log processing** with `--verbose` for large batches

### 3. Quality Control

- **Validate normalization** results for critical texts
- **Test with sample texts** before batch processing
- **Use appropriate encoding** for legacy files

### 4. Integration

- **Standardize normalization** across your TTS pipeline
- **Document settings** used for reproducibility
- **Version control** normalization configurations

## Troubleshooting

### Common Issues

#### 1. Encoding Problems

**Error:**
```
UnicodeDecodeError: 'utf-8' codec can't decode byte...
```

**Solution:**
```bash
# Specify correct encoding
kalakan norm --file problematic.txt --encoding latin-1
```

#### 2. File Not Found

**Error:**
```
Error reading file input.txt: [Errno 2] No such file or directory
```

**Solution:**
- Verify file path is correct
- Use absolute paths if needed
- Check file permissions

#### 3. Empty Output

**Issue:** Normalization produces empty or unexpected results

**Solutions:**
- Check input text encoding
- Verify text contains normalizable content
- Use `--show-diff` to see what changed
- Try with `--verbose` for detailed logging

#### 4. GUI Issues (File Selection)

**Issue:** File dialog doesn't open

**Solutions:**
- Ensure GUI libraries are installed
- Use `--file` instead of `--select` on headless systems
- Check display settings on remote systems

### Performance Optimization

#### For Large Files:
- Process in smaller chunks if memory issues occur
- Use appropriate output formats (text is fastest)
- Consider parallel processing for multiple files

#### For Batch Processing:
- Use `--quiet` to reduce output overhead
- Organize files efficiently
- Monitor disk space for large outputs

### Validation

#### Check Normalization Quality:
```bash
# Review changes before committing
kalakan norm --file important.txt --show-diff --format json
```

#### Verify Character Handling:
```bash
# Test special character processing
kalakan norm --text "Mεpε sε mεkɔ fiε" --show-diff
```

#### Test Integration:
```bash
# Ensure normalized text works with synthesis
kalakan norm --text "Test text" | kalakan synthesize --output test.wav
```

This comprehensive guide should help you effectively use the Kalakan TTS text normalization tool to prepare high-quality Twi text for TTS processing.
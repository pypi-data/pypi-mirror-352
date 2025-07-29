# Kalakan TTS Metadata Generation - Quick Reference

## Basic Commands

### Simple Metadata Generation
```bash
kalakan gen-metadata --input-dir /path/to/dataset --verbose
```

### Complete Dataset Preparation
```bash
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

## Common Options

| Option | Description | Example |
|--------|-------------|---------|
| `--input-dir` | Dataset directory | `--input-dir ./my_dataset` |
| `--generate-phonemes` | Enable G2P conversion | `--generate-phonemes` |
| `--split-dataset` | Create train/val/test splits | `--split-dataset` |
| `--val-ratio` | Validation set ratio | `--val-ratio 0.2` |
| `--test-ratio` | Test set ratio | `--test-ratio 0.1` |
| `--output-format` | Output format | `--output-format both` |
| `--include-stats` | Generate statistics | `--include-stats` |
| `--check-duplicates` | Check for duplicates | `--check-duplicates` |
| `--remove-duplicates` | Remove duplicates | `--remove-duplicates` |
| `--normalize-text` | Normalize text | `--normalize-text` |
| `--clean-text` | Clean text | `--clean-text` |
| `--speaker-id` | Add speaker ID | `--speaker-id "speaker_001"` |
| `--verbose` | Verbose logging | `--verbose` |

## Transcript Formats

### CSV Format
```bash
kalakan gen-metadata \
    --input-dir /path/to/dataset \
    --transcript-file dataset/transcripts.csv \
    --transcript-format csv \
    --transcript-delimiter "," \
    --text-column 1 \
    --id-column 0
```

### JSON Format
```bash
kalakan gen-metadata \
    --input-dir /path/to/dataset \
    --transcript-file dataset/transcripts.json \
    --transcript-format json \
    --text-field "text" \
    --id-field "id"
```

## Quality Control

### Duration Filtering
```bash
kalakan gen-metadata \
    --input-dir /path/to/dataset \
    --min-duration 0.5 \
    --max-duration 10.0
```

### Text Length Filtering
```bash
kalakan gen-metadata \
    --input-dir /path/to/dataset \
    --min-text-length 10 \
    --max-text-length 150
```

### Duplicate Handling
```bash
kalakan gen-metadata \
    --input-dir /path/to/dataset \
    --check-duplicates \
    --remove-duplicates
```

## Output Files

### Single Dataset
- `metadata.csv` - Main metadata file
- `metadata.json` - JSON format (if `--output-format both`)
- `dataset_stats.json` - Statistics (if `--include-stats`)

### Split Dataset
- `train.csv` / `train.json` - Training set
- `val.csv` / `val.json` - Validation set
- `test.csv` / `test.json` - Test set
- `dataset_stats.json` - Comprehensive statistics

## Expected Directory Structure

```
dataset/
├── wavs/
│   ├── audio_001.wav
│   ├── audio_002.wav
│   └── ...
└── transcript.txt  # or metadata.csv, transcripts.json
```

## Sample Output

### CSV Format
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

## Common Use Cases

### Research Dataset
```bash
kalakan gen-metadata \
    --input-dir ./research_dataset \
    --generate-phonemes \
    --split-dataset \
    --val-ratio 0.15 \
    --test-ratio 0.15 \
    --output-format both \
    --include-stats \
    --normalize-text \
    --verbose
```

### Production Dataset
```bash
kalakan gen-metadata \
    --input-dir ./production_dataset \
    --generate-phonemes \
    --split-dataset \
    --val-ratio 0.1 \
    --test-ratio 0.1 \
    --check-duplicates \
    --remove-duplicates \
    --min-duration 1.0 \
    --max-duration 8.0 \
    --normalize-text \
    --clean-text \
    --speaker-id "production_speaker" \
    --include-stats \
    --verbose
```

### Quality Control Focus
```bash
kalakan gen-metadata \
    --input-dir ./quality_dataset \
    --check-duplicates \
    --remove-duplicates \
    --min-duration 2.0 \
    --max-duration 6.0 \
    --min-text-length 20 \
    --max-text-length 100 \
    --normalize-text \
    --clean-text \
    --include-stats \
    --verbose
```

For detailed documentation, see [metadata_generation_guide.md](metadata_generation_guide.md).
# Kalakan TTS Text Normalization - Quick Reference

## Basic Commands

### Direct Text Normalization
```bash
kalakan norm --text "Dr. Kwame na Prof. Ama bɛba ha 25 mu."
```

### File Processing
```bash
kalakan norm --file input.txt --output normalized.txt
```

### Interactive File Selection
```bash
kalakan norm --select
```

### Batch Processing
```bash
kalakan norm --select --batch --output-dir ./normalized
```

## Common Options

| Option | Description | Example |
|--------|-------------|---------|
| `--text` | Direct text input | `--text "Dr. Kwame bɛba ha"` |
| `--file` | Input file path | `--file manuscript.txt` |
| `--select` | Interactive file selection | `--select` |
| `--output` | Output file path | `--output normalized.txt` |
| `--output-dir` | Output directory | `--output-dir ./processed` |
| `--format` | Output format | `--format json` |
| `--show-diff` | Show differences | `--show-diff` |
| `--verbose` | Verbose logging | `--verbose` |

## Processing Options

| Option | Description | Effect |
|--------|-------------|--------|
| `--no-numbers` | Skip number normalization | Keep "25" as "25" |
| `--no-abbreviations` | Skip abbreviation expansion | Keep "Dr." as "Dr." |
| `--no-punctuation` | Skip punctuation normalization | Keep original punctuation |
| `--preserve-case` | Keep original case | Don't convert to lowercase |

## Output Formats

### Text Format (Default)
```bash
kalakan norm --text "Dr. Kwame bɛba ha" --format text
```
Output: `dr. kwame bɛba ha`

### JSON Format
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

### CSV Format
```bash
kalakan norm --text "Dr. Kwame bɛba ha" --format csv
```
Output:
```csv
Original,Normalized
"Dr. Kwame bɛba ha","dr. kwame bɛba ha"
```

## Normalization Features

### Default Processing
1. **Abbreviation Expansion**: Dr. → doctor, Prof. → professor
2. **Case Conversion**: Convert to lowercase
3. **Punctuation Normalization**: Standardize punctuation
4. **Number Processing**: Convert numbers to text
5. **Special Characters**: ε→ɛ, Ε→Ɛ, ο→ɔ, Ο→Ɔ

### Example Transformations
```
Original:   "Dr. Kwame na Prof. Ama bɛba ha 25 mu."
Normalized: "dr. kwame na prof. ama bɛba ha 25 mu."

Original:   "Mεpε sε mεkɔ fiε"
Normalized: "mɛpɛ sɛ mɛkɔ fiɛ"
```

## Common Use Cases

### 1. Prepare Text for TTS
```bash
kalakan norm --text "Dr. Kwame bɛba ha" | kalakan synthesize --output speech.wav
```

### 2. Process Dataset Files
```bash
kalakan norm \
    --file ./dataset/texts \
    --recursive \
    --output-dir ./dataset/normalized \
    --format text \
    --verbose
```

### 3. Quality Analysis
```bash
kalakan norm \
    --file manuscript.txt \
    --show-diff \
    --format json \
    --output analysis.json
```

### 4. Custom Normalization
```bash
kalakan norm \
    --text "Dr. Kwame bɛba ha 25 mu" \
    --no-numbers \
    --preserve-case \
    --show-diff
```

### 5. Batch Processing
```bash
kalakan norm \
    --select \
    --batch \
    --output-dir ./processed \
    --format csv \
    --show-diff \
    --verbose
```

## Advanced Examples

### Selective Normalization
```bash
# Only expand abbreviations, keep case and numbers
kalakan norm \
    --text "Dr. Kwame bɛba ha 25 mu" \
    --preserve-case \
    --no-numbers \
    --format json
```

### Directory Processing
```bash
# Process all .txt files recursively
kalakan norm \
    --file ./manuscripts \
    --recursive \
    --output-dir ./normalized_manuscripts \
    --format json \
    --show-diff
```

### Encoding Handling
```bash
# Handle legacy file encoding
kalakan norm \
    --file legacy.txt \
    --encoding latin-1 \
    --output modern.txt \
    --format text
```

## Integration Examples

### With Metadata Generation
```bash
# Both commands use similar normalization
kalakan gen-metadata --input-dir ./dataset --normalize-text
kalakan norm --file ./dataset/transcript.txt --output normalized_transcript.txt
```

### Pipeline Processing
```bash
# Multi-step text processing
kalakan norm --file raw.txt --output step1.txt
# Further processing...
kalakan synthesize --file step1.txt --output final.wav
```

## Quick Troubleshooting

### File Not Found
```bash
# Use absolute paths
kalakan norm --file /full/path/to/file.txt
```

### Encoding Issues
```bash
# Specify encoding
kalakan norm --file problematic.txt --encoding latin-1
```

### Empty Output
```bash
# Check with diff view
kalakan norm --text "Your text" --show-diff --verbose
```

### GUI Issues
```bash
# Use file path instead of selection
kalakan norm --file input.txt --output output.txt
```

For detailed documentation, see [text_normalization_guide.md](text_normalization_guide.md).
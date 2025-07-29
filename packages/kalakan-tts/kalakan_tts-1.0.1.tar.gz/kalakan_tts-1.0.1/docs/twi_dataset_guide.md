# Twi Speech Dataset Collection Guide

This guide provides detailed instructions for collecting and preparing a high-quality Twi speech dataset for training the Kalakan TTS system.

## Table of Contents

1. [Dataset Requirements](#dataset-requirements)
2. [Recording Setup](#recording-setup)
3. [Text Selection](#text-selection)
4. [Recording Process](#recording-process)
5. [Post-Processing](#post-processing)
6. [Dataset Organization](#dataset-organization)
7. [Quality Assurance](#quality-assurance)

## Dataset Requirements

For a production-quality Twi TTS system, aim for:

- **Size**: 20+ hours of speech (minimum 10 hours)
- **Speaker**: Single professional speaker (native Twi speaker)
- **Consistency**: Consistent speaking style, pace, and tone
- **Quality**: Studio-quality recordings (high SNR, minimal reverb)
- **Coverage**: Comprehensive phonetic coverage of Twi sounds
- **Diversity**: Various sentence types, lengths, and contexts

## Recording Setup

### Equipment

- **Microphone**: Professional condenser microphone (e.g., Rode NT1-A, Audio-Technica AT2020)
- **Audio Interface**: Clean preamp with phantom power (e.g., Focusrite Scarlett)
- **Pop Filter**: To reduce plosive sounds
- **Acoustic Treatment**: Sound-absorbing panels or a treated room
- **Headphones**: For monitoring
- **Recording Software**: Audacity (free) or Adobe Audition

### Settings

- **Sample Rate**: 44.1 kHz or 48 kHz
- **Bit Depth**: 24-bit
- **Format**: Uncompressed WAV
- **Gain**: Set levels to peak between -12dB and -6dB

### Environment

- **Quiet Room**: Minimal background noise
- **Acoustic Treatment**: Reduce room reflections
- **Consistent Setup**: Maintain the same recording setup throughout
- **Time of Day**: Choose quiet times for recording

## Text Selection

### Sources for Twi Text

- **Books**: Contemporary Twi literature
- **News Articles**: From Ghanaian publications
- **Educational Materials**: Twi textbooks and learning resources
- **Conversational Phrases**: Common expressions and dialogues
- **Religious Texts**: Bible or other religious texts in Twi

### Text Preparation

1. **Phonetic Coverage**: Ensure all Twi phonemes are represented
2. **Special Characters**: Properly include Twi-specific characters (ɛ, ɔ)
3. **Tone Marking**: Include tone marks where appropriate
4. **Sentence Length**: Mix of short, medium, and long sentences
5. **Sentence Types**: Statements, questions, commands, exclamations
6. **Domain Variety**: Include text from multiple domains (news, conversation, narrative)

### Example Script Structure

Create a script with:
- 2000-3000 sentences
- Organized into manageable recording sessions
- Clear formatting with proper Twi orthography
- Pronunciation guides for difficult words

## Recording Process

### Preparation

1. **Voice Warm-up**: Perform vocal exercises before recording
2. **Hydration**: Drink water (room temperature) to maintain vocal quality
3. **Test Recording**: Make a short test recording to check levels and quality

### Recording Sessions

1. **Session Length**: Limit sessions to 2-3 hours to maintain voice quality
2. **Breaks**: Take 10-15 minute breaks every 30-45 minutes
3. **Consistency**: Maintain consistent speaking style, pace, and distance from microphone
4. **Monitoring**: Use headphones to monitor recording quality
5. **Multiple Takes**: Record multiple takes of difficult sentences

### Recording Protocol

1. **Sentence-by-Sentence**: Record each sentence as a separate file
2. **Slate**: Include a brief silence (0.5s) at the beginning and end of each recording
3. **Retakes**: Immediately re-record sentences with mistakes
4. **Naming Convention**: Use a consistent naming scheme (e.g., `twi_XXXX.wav`)
5. **Metadata**: Keep a log of recording sessions with notes

## Post-Processing

### Audio Editing

1. **Trimming**: Remove excess silence (leaving 0.2-0.3s at beginning and end)
2. **Noise Reduction**: Apply subtle noise reduction if necessary
3. **Normalization**: Normalize to -3dB peak
4. **Consistency**: Ensure consistent volume across all recordings

### Quality Control

1. **Listen**: Manually listen to samples from each recording session
2. **Spectrogram**: Check spectrograms for unwanted noise
3. **Clipping**: Ensure no digital clipping occurred
4. **Consistency**: Verify consistent audio quality across the dataset

## Dataset Organization

### Directory Structure

```
twi_dataset/
├── wavs/
│   ├── twi_0001.wav
│   ├── twi_0002.wav
│   └── ...
├── metadata.csv
├── texts/
│   ├── original/
│   └── normalized/
└── README.md
```

### Metadata Format

Create a CSV file with the following columns:
- File ID
- Audio filename
- Original text
- Normalized text
- Duration
- Recording date
- Session ID

Example:
```
id|audio_file|text|normalized_text|duration|date|session
twi_0001|wavs/twi_0001.wav|Agoo Kalculus, mepa wo kyɛw, wo ho te sɛn?|agoo kalculus, mepa wo kyɛw, wo ho te sɛn?|3.45|2023-05-15|session1
```

## Quality Assurance

### Verification Process

1. **Automated Checks**:
   - Check audio format, sample rate, and bit depth
   - Verify minimum and maximum durations
   - Check for clipping and low volume

2. **Manual Review**:
   - Listen to random samples (at least 5% of the dataset)
   - Verify text-audio alignment
   - Check pronunciation accuracy

3. **Phonetic Coverage Analysis**:
   - Ensure all Twi phonemes are well-represented
   - Identify and fill gaps in phonetic coverage

### Common Issues to Watch For

- **Pronunciation Errors**: Incorrect pronunciation of Twi words
- **Background Noise**: Air conditioning, computer fans, outdoor sounds
- **Mouth Sounds**: Excessive mouth clicks or breathing
- **Inconsistent Volume**: Variations in speaking volume
- **Room Reflections**: Echoes or reverberations
- **Tone Inconsistency**: Variations in speaking tone or style

## Additional Resources

- [Twi Phonology Reference](https://en.wikipedia.org/wiki/Akan_language#Phonology)
- [Twi Orthography Guide](https://www.kasahorow.org/how-to-write-twi)
- [Common Voice Project](https://commonvoice.mozilla.org/) (for methodology)
- [Audacity Manual](https://manual.audacityteam.org/)

---
kalculusGuy

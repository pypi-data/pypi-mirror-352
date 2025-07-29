# Kalakan TTS Troubleshooting Guide

This guide provides solutions for common issues encountered when using the Kalakan TTS system. It covers installation problems, runtime errors, model training issues, and performance optimization.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Text Processing Issues](#text-processing-issues)
3. [Model Loading Issues](#model-loading-issues)
4. [Synthesis Issues](#synthesis-issues)
5. [Training Issues](#training-issues)
6. [API Server Issues](#api-server-issues)
7. [Performance Issues](#performance-issues)
8. [GPU-Related Issues](#gpu-related-issues)
9. [Common Error Messages](#common-error-messages)
10. [Getting Help](#getting-help)

## Installation Issues

### Package Installation Failures

**Issue**: `pip install kalakan-tts` fails with dependency errors.

**Solution**:
1. Update pip to the latest version:
```bash
pip install --upgrade pip
```

2. Install dependencies separately:
```bash
pip install torch torchaudio
pip install kalakan-tts
```

3. If PyTorch installation is failing, install it with the specific CUDA version:
```bash
# For CUDA 11.7
pip install torch==2.0.0+cu117 torchaudio==2.0.0+cu117 -f https://download.pytorch.org/whl/torch_stable.html

# For CPU only
pip install torch==2.0.0+cpu torchaudio==2.0.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
```

### Missing Compiler Errors

**Issue**: Installation fails with "error: Microsoft Visual C++ 14.0 or greater is required" (Windows) or missing compiler errors (Linux).

**Solution**:
1. **Windows**: Install Visual C++ Build Tools from [here](https://visualstudio.microsoft.com/visual-cpp-build-tools/).

2. **Linux**: Install build essentials:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install build-essential python3-dev

# CentOS/RHEL
sudo yum groupinstall "Development Tools"
sudo yum install python3-devel
```

### Import Errors After Installation

**Issue**: `ImportError` when trying to import Kalakan modules after successful installation.

**Solution**:
1. Check if the package is installed correctly:
```bash
pip list | grep kalakan
```

2. Check if you're using the correct Python environment:
```bash
which python  # Linux/macOS
where python  # Windows
```

3. Reinstall the package:
```bash
pip uninstall kalakan-tts
pip install kalakan-tts
```

## Text Processing Issues

### Special Character Handling

**Issue**: Twi special characters (ɛ, ɔ, Ɔ) are not displayed or processed correctly.

**Solution**:
1. Ensure you're using UTF-8 encoding in your files and terminal:
```python
# In Python scripts
with open('file.txt', 'r', encoding='utf-8') as f:
    text = f.read()
```

2. Check if your font supports these characters.

3. Use Unicode escape sequences if needed:
```python
text = "Akwaaba! Wo ho te s\u025Bn?"  # ɛ = \u025B
```

### Incorrect Pronunciation

**Issue**: The system pronounces certain Twi words incorrectly.

**Solution**:
1. Create a custom pronunciation dictionary:
```python
from kalakan.text.twi_g2p import TwiG2P

# Create a dictionary file with correct pronunciations
with open('custom_dict.txt', 'w', encoding='utf-8') as f:
    f.write("word1 p h o n e m e s\n")
    f.write("word2 p h o n e m e s\n")

# Use the custom dictionary
g2p = TwiG2P(pronunciation_dict_path='custom_dict.txt')
synthesizer = Synthesizer(g2p=g2p)
```

2. Use the enhanced G2P converter:
```python
from kalakan.text.enhanced_g2p import EnhancedTwiG2P
from kalakan.synthesis.synthesizer import Synthesizer

g2p = EnhancedTwiG2P()
synthesizer = Synthesizer(g2p=g2p)
```

### Text Normalization Issues

**Issue**: Numbers, abbreviations, or special tokens are not properly expanded.

**Solution**:
1. Manually normalize the text before synthesis:
```python
from kalakan.text.normalizer import normalize_text
from kalakan.text.cleaner import clean_text

text = "Me wɔ GH₵50."
normalized_text = normalize_text(clean_text(text))
audio = synthesizer.synthesize(normalized_text, normalize=False, clean=False)
```

2. Extend the normalizer with custom rules:
```python
from kalakan.text.normalizer import normalize_text

def custom_normalize(text):
    # Apply custom normalization rules
    text = text.replace("GH₵", "Ghana Cedis ")
    # Then apply standard normalization
    return normalize_text(text)

audio = synthesizer.synthesize(custom_normalize(text), normalize=False)
```

## Model Loading Issues

### Model Not Found

**Issue**: `FileNotFoundError` when trying to load a model.

**Solution**:
1. Check if the model file exists:
```bash
ls -la /path/to/model.pt  # Linux/macOS
dir /path/to/model.pt     # Windows
```

2. Use absolute paths instead of relative paths:
```python
synthesizer = Synthesizer(
    acoustic_model="/absolute/path/to/acoustic_model.pt",
    vocoder="/absolute/path/to/vocoder.pt"
)
```

3. Download the models if you're using default models:
```bash
# Create a directory for models
mkdir -p models

# Download models
wget -O models/tacotron2.pt https://github.com/kalakan-ai/kalakan-tts/releases/download/v1.0.0/tacotron2.pt
wget -O models/hifigan.pt https://github.com/kalakan-ai/kalakan-tts/releases/download/v1.0.0/hifigan.pt
```

### Model Version Mismatch

**Issue**: `RuntimeError` when loading a model due to version mismatch.

**Solution**:
1. Check the model's PyTorch version:
```python
import torch

# Load with map_location to avoid CUDA errors
checkpoint = torch.load("/path/to/model.pt", map_location="cpu")
print(checkpoint.get("pytorch_version", "Unknown"))
```

2. Use the same PyTorch version as the one used to train the model, or convert the model:
```python
import torch

# Load the model with map_location
checkpoint = torch.load("/path/to/model.pt", map_location="cpu")

# Save it again with the current PyTorch version
torch.save(checkpoint, "/path/to/converted_model.pt")
```

### CUDA Out of Memory

**Issue**: `RuntimeError: CUDA out of memory` when loading models.

**Solution**:
1. Use CPU for inference:
```python
synthesizer = Synthesizer(
    acoustic_model="/path/to/acoustic_model.pt",
    vocoder="/path/to/vocoder.pt",
    device="cpu"
)
```

2. Use a smaller model:
```python
# Use Griffin-Lim vocoder which is lighter
synthesizer = Synthesizer(
    acoustic_model="/path/to/acoustic_model.pt",
    vocoder_type="griffin_lim",
    device="cuda:0"
)
```

3. Free up GPU memory before loading models:
```python
import torch
import gc

# Clear CUDA cache
torch.cuda.empty_cache()
gc.collect()

# Then load models
synthesizer = Synthesizer(...)
```

## Synthesis Issues

### Poor Audio Quality

**Issue**: Generated audio has poor quality, artifacts, or noise.

**Solution**:
1. Use a higher-quality vocoder:
```python
synthesizer = Synthesizer(
    acoustic_model="/path/to/acoustic_model.pt",
    vocoder="/path/to/hifigan.pt"  # Use HiFi-GAN instead of Griffin-Lim
)
```

2. Check if the input text is properly formatted:
```python
# Ensure proper formatting of Twi text
text = "Akwaaba! Wo ho te sɛn?"  # Use proper Twi characters
```

3. Adjust the vocoder parameters:
```python
from kalakan.utils.config import Config
from kalakan.synthesis.synthesizer import Synthesizer

config = Config({
    "vocoder": {
        "denoise": True,
        "denoiser_strength": 0.005
    }
})

synthesizer = Synthesizer(
    acoustic_model="/path/to/acoustic_model.pt",
    vocoder="/path/to/vocoder.pt",
    config=config
)
```

### Slow Synthesis

**Issue**: Speech synthesis is too slow.

**Solution**:
1. Use GPU acceleration:
```python
synthesizer = Synthesizer(
    acoustic_model="/path/to/acoustic_model.pt",
    vocoder="/path/to/vocoder.pt",
    device="cuda:0"
)
```

2. Use a faster model:
```python
# FastSpeech2 is faster than Tacotron2
synthesizer = Synthesizer(
    acoustic_model_type="fastspeech2",
    vocoder_type="melgan"  # MelGAN is faster than HiFi-GAN
)
```

3. Use batch processing for multiple texts:
```python
texts = ["Text 1", "Text 2", "Text 3"]
audios = synthesizer.synthesize_batch(texts, batch_size=8)
```

4. Export models to optimized formats:
```bash
kalakan-export \
    --acoustic-model /path/to/acoustic_model.pt \
    --vocoder /path/to/vocoder.pt \
    --output-dir /path/to/exported_models \
    --format onnx
```

### Incorrect Prosody

**Issue**: Generated speech has incorrect stress, intonation, or rhythm.

**Solution**:
1. Add punctuation to guide prosody:
```python
text = "Akwaaba! Wo ho te sɛn? Me ho yɛ."
```

2. Use a better acoustic model:
```python
synthesizer = Synthesizer(
    acoustic_model="/path/to/better_acoustic_model.pt",
    vocoder="/path/to/vocoder.pt"
)
```

3. Fine-tune the model on data with proper prosody:
```bash
kalakan-train \
    --model-type tacotron2 \
    --data-dir /path/to/prosody_dataset \
    --output-dir /path/to/output \
    --checkpoint /path/to/pretrained_model.pt \
    --learning-rate 0.0001 \
    --epochs 100
```

## Training Issues

### Loss Not Decreasing

**Issue**: Training loss plateaus or doesn't decrease.

**Solution**:
1. Adjust the learning rate:
```bash
kalakan-train \
    --model-type tacotron2 \
    --data-dir /path/to/dataset \
    --output-dir /path/to/output \
    --learning-rate 0.0001  # Try a smaller learning rate
```

2. Check the dataset quality:
```bash
# Validate the dataset
kalakan-prepare-dataset \
    --input-dir /path/to/raw/dataset \
    --output-dir /path/to/validated/dataset \
    --validate-only
```

3. Use a different optimizer or scheduler:
```yaml
# In your config.yaml
optimizer:
  type: "adam"
  betas: [0.9, 0.999]
  weight_decay: 0.0001
  
scheduler:
  type: "plateau"
  patience: 5
  factor: 0.5
  threshold: 0.01
```

### Gradient Explosion

**Issue**: Training fails with `RuntimeError: The gradient exploded` or NaN losses.

**Solution**:
1. Use gradient clipping:
```yaml
# In your config.yaml
training:
  grad_clip: 1.0
```

2. Use a smaller learning rate:
```bash
kalakan-train \
    --model-type tacotron2 \
    --data-dir /path/to/dataset \
    --output-dir /path/to/output \
    --learning-rate 0.0001
```

3. Check for outliers in your dataset:
```python
import librosa
import numpy as np
import pandas as pd

# Load metadata
metadata = pd.read_csv("/path/to/dataset/metadata.csv")

# Check audio durations
durations = []
for audio_path in metadata["audio_path"]:
    y, sr = librosa.load(audio_path)
    durations.append(len(y) / sr)

# Find outliers
mean_dur = np.mean(durations)
std_dur = np.std(durations)
outliers = [i for i, d in enumerate(durations) if abs(d - mean_dur) > 3 * std_dur]
print(f"Outliers: {outliers}")
```

### Out of Memory During Training

**Issue**: `RuntimeError: CUDA out of memory` during training.

**Solution**:
1. Reduce batch size:
```bash
kalakan-train \
    --model-type tacotron2 \
    --data-dir /path/to/dataset \
    --output-dir /path/to/output \
    --batch-size 8  # Try a smaller batch size
```

2. Use gradient accumulation:
```yaml
# In your config.yaml
training:
  batch_size: 8
  grad_accumulation_steps: 4  # Effective batch size = 8 * 4 = 32
```

3. Use mixed precision training:
```yaml
# In your config.yaml
training:
  mixed_precision: true
```

4. Use a smaller model:
```yaml
# In your config.yaml
model:
  type: "tacotron2"
  embedding_dim: 256  # Reduced from 512
  encoder_dim: 256    # Reduced from 512
  decoder_dim: 512    # Reduced from 1024
```

## API Server Issues

### Server Won't Start

**Issue**: API server fails to start.

**Solution**:
1. Check if the port is already in use:
```bash
# Linux/macOS
lsof -i :8000

# Windows
netstat -ano | findstr :8000
```

2. Use a different port:
```bash
kalakan-api --host 0.0.0.0 --port 8001
```

3. Check if the models can be loaded:
```python
from kalakan.synthesis.synthesizer import Synthesizer

# Try loading the models
synthesizer = Synthesizer(
    acoustic_model="/path/to/acoustic_model.pt",
    vocoder="/path/to/vocoder.pt"
)
```

### API Requests Timeout

**Issue**: API requests take too long and timeout.

**Solution**:
1. Use a faster model:
```bash
kalakan-api \
    --host 0.0.0.0 \
    --port 8000 \
    --acoustic-model-type fastspeech2 \
    --vocoder-type melgan
```

2. Increase the client timeout:
```python
import requests

response = requests.post(
    "http://localhost:8000/synthesize",
    json={"text": "Akwaaba! Wo ho te sɛn?"},
    timeout=60  # Increase timeout to 60 seconds
)
```

3. Use asynchronous API for long texts:
```python
import requests
import time

# Start synthesis job
response = requests.post(
    "http://localhost:8000/synthesize/async",
    json={"text": "Very long text..."}
)
job_id = response.json()["job_id"]

# Poll for completion
while True:
    status_response = requests.get(f"http://localhost:8000/status/{job_id}")
    status = status_response.json()["status"]
    if status == "completed":
        # Download the result
        audio_response = requests.get(f"http://localhost:8000/result/{job_id}")
        with open("output.wav", "wb") as f:
            f.write(audio_response.content)
        break
    elif status == "failed":
        print("Synthesis failed")
        break
    time.sleep(1)
```

### High Memory Usage

**Issue**: API server uses too much memory.

**Solution**:
1. Use model quantization:
```bash
# Export quantized models
kalakan-export \
    --acoustic-model /path/to/acoustic_model.pt \
    --vocoder /path/to/vocoder.pt \
    --output-dir /path/to/exported_models \
    --quantize

# Use quantized models in the API
kalakan-api \
    --host 0.0.0.0 \
    --port 8000 \
    --acoustic-model /path/to/exported_models/acoustic_model_quantized.pt \
    --vocoder /path/to/exported_models/vocoder_quantized.pt
```

2. Limit the number of worker processes:
```bash
kalakan-api \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 2
```

3. Implement request throttling:
```python
# In a custom API server
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.throttling import ThrottlingMiddleware

app = FastAPI()
app.add_middleware(
    ThrottlingMiddleware,
    rate_limit=10,  # 10 requests per minute
    time_window=60  # 60 seconds
)
```

## Performance Issues

### Slow Inference

**Issue**: Inference is too slow for production use.

**Solution**:
1. Use model optimization techniques:
```bash
# Export to ONNX format
kalakan-export \
    --acoustic-model /path/to/acoustic_model.pt \
    --vocoder /path/to/vocoder.pt \
    --output-dir /path/to/exported_models \
    --format onnx

# Use ONNX models
from kalakan.synthesis.synthesizer import Synthesizer
from kalakan.utils.config import Config

config = Config({
    "inference": {
        "use_onnx": True
    }
})

synthesizer = Synthesizer(
    acoustic_model="/path/to/exported_models/acoustic_model.onnx",
    vocoder="/path/to/exported_models/vocoder.onnx",
    config=config
)
```

2. Use batch processing:
```python
texts = ["Text 1", "Text 2", "Text 3", ...]
audios = synthesizer.synthesize_batch(texts, batch_size=16)
```

3. Use a faster but lower-quality model:
```python
synthesizer = Synthesizer(
    acoustic_model_type="fastspeech2",
    vocoder_type="melgan"
)
```

4. Profile the code to identify bottlenecks:
```python
import cProfile
import pstats

# Profile synthesis
cProfile.run('synthesizer.synthesize("Akwaaba! Wo ho te sɛn?")', 'synthesis_stats')

# Analyze results
p = pstats.Stats('synthesis_stats')
p.sort_stats('cumulative').print_stats(20)
```

### High Memory Usage

**Issue**: The system uses too much memory during inference.

**Solution**:
1. Use model quantization:
```python
from kalakan.synthesis.synthesizer import Synthesizer
from kalakan.utils.config import Config

config = Config({
    "inference": {
        "quantize": True
    }
})

synthesizer = Synthesizer(
    acoustic_model="/path/to/acoustic_model.pt",
    vocoder="/path/to/vocoder.pt",
    config=config
)
```

2. Use smaller models:
```python
synthesizer = Synthesizer(
    acoustic_model_type="fastspeech2_small",
    vocoder_type="melgan_small"
)
```

3. Process long texts in chunks:
```python
def synthesize_long_text(text, max_chars=100):
    # Split text into sentences
    sentences = text.split('.')
    
    # Group sentences into chunks
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) > max_chars:
            chunks.append(current_chunk)
            current_chunk = sentence
        else:
            current_chunk += sentence + "."
    if current_chunk:
        chunks.append(current_chunk)
    
    # Synthesize each chunk
    audio_chunks = []
    for chunk in chunks:
        audio = synthesizer.synthesize(chunk)
        audio_chunks.append(audio)
    
    # Concatenate audio chunks
    import torch
    return torch.cat(audio_chunks, dim=0)
```

## GPU-Related Issues

### CUDA Not Available

**Issue**: PyTorch reports that CUDA is not available.

**Solution**:
1. Check if CUDA is installed:
```bash
nvcc --version
```

2. Check if NVIDIA drivers are installed:
```bash
nvidia-smi
```

3. Check if PyTorch was installed with CUDA support:
```python
import torch
print(torch.__version__)
print(torch.version.cuda)
```

4. Reinstall PyTorch with CUDA support:
```bash
pip uninstall torch torchaudio
pip install torch==2.0.0+cu117 torchaudio==2.0.0+cu117 -f https://download.pytorch.org/whl/torch_stable.html
```

### Multiple GPUs

**Issue**: System doesn't use all available GPUs.

**Solution**:
1. Specify which GPU to use:
```python
synthesizer = Synthesizer(
    acoustic_model="/path/to/acoustic_model.pt",
    vocoder="/path/to/vocoder.pt",
    device="cuda:1"  # Use the second GPU
)
```

2. Use DataParallel for inference:
```python
import torch.nn as nn

# Wrap models in DataParallel
synthesizer.acoustic_model = nn.DataParallel(synthesizer.acoustic_model)
synthesizer.vocoder = nn.DataParallel(synthesizer.vocoder)
```

3. For training, use distributed training:
```bash
kalakan-train \
    --model-type tacotron2 \
    --data-dir /path/to/dataset \
    --output-dir /path/to/output \
    --distributed \
    --world-size 4
```

### GPU Memory Leaks

**Issue**: GPU memory usage increases over time.

**Solution**:
1. Clear CUDA cache between inferences:
```python
import torch
import gc

def synthesize_with_cleanup(text):
    audio = synthesizer.synthesize(text)
    # Clear CUDA cache
    torch.cuda.empty_cache()
    gc.collect()
    return audio
```

2. Move models to CPU when not in use:
```python
def synthesize_with_cpu_offload(text):
    # Move models to GPU
    synthesizer.acoustic_model.to("cuda:0")
    synthesizer.vocoder.to("cuda:0")
    
    # Synthesize
    audio = synthesizer.synthesize(text)
    
    # Move models back to CPU
    synthesizer.acoustic_model.to("cpu")
    synthesizer.vocoder.to("cpu")
    
    # Clear CUDA cache
    torch.cuda.empty_cache()
    gc.collect()
    
    return audio
```

3. Use a context manager for GPU allocation:
```python
import contextlib

@contextlib.contextmanager
def gpu_allocation():
    try:
        # Move models to GPU
        synthesizer.acoustic_model.to("cuda:0")
        synthesizer.vocoder.to("cuda:0")
        yield
    finally:
        # Move models back to CPU
        synthesizer.acoustic_model.to("cpu")
        synthesizer.vocoder.to("cpu")
        # Clear CUDA cache
        torch.cuda.empty_cache()
        gc.collect()

# Usage
with gpu_allocation():
    audio = synthesizer.synthesize(text)
```

## Common Error Messages

### "No module named 'kalakan'"

**Issue**: Python cannot find the Kalakan package.

**Solution**:
1. Check if the package is installed:
```bash
pip list | grep kalakan
```

2. Install the package:
```bash
pip install kalakan-tts
```

3. Check if you're using the correct Python environment:
```bash
which python  # Linux/macOS
where python  # Windows
```

### "RuntimeError: CUDA error: device-side assert triggered"

**Issue**: A CUDA assertion failed, often due to invalid inputs or model parameters.

**Solution**:
1. Check input data:
```python
# Ensure text is not empty
if not text:
    raise ValueError("Text cannot be empty")
```

2. Try using CPU instead:
```python
synthesizer = Synthesizer(
    acoustic_model="/path/to/acoustic_model.pt",
    vocoder="/path/to/vocoder.pt",
    device="cpu"
)
```

3. Enable CUDA assertions for more detailed error messages:
```bash
export CUDA_LAUNCH_BLOCKING=1
python your_script.py
```

### "ValueError: Expected input batch_size * time_size to match target batch_size * time_size"

**Issue**: Mismatch in dimensions between model inputs and targets.

**Solution**:
1. Check input data dimensions:
```python
print(f"Phonemes shape: {phonemes.shape}")
print(f"Mel shape: {mel.shape}")
```

2. Ensure consistent preprocessing:
```python
# Use the same preprocessing parameters for training and inference
from kalakan.audio.features import mel_spectrogram

mel = mel_spectrogram(
    audio,
    n_fft=1024,
    hop_length=256,
    win_length=1024,
    sample_rate=22050,
    n_mels=80,
    fmin=0.0,
    fmax=8000.0
)
```

3. Check model configuration:
```python
# Ensure model is configured correctly
print(synthesizer.acoustic_model.mel_channels)
print(synthesizer.vocoder.mel_channels)
```

## Getting Help

If you encounter issues not covered in this guide, you can:

1. Check the logs for detailed error messages:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. Open an issue on the GitHub repository with:
   - A detailed description of the issue
   - Steps to reproduce
   - Error messages
   - System information (OS, Python version, GPU, etc.)

3. Contact the Kalakan TTS team for support:
   - Email: support@kalakan.ai
   - Community forum: https://github.com/kalakan-ai/kalakan-tts/discussions

4. Check the API reference and other documentation in the `docs/` directory for more detailed information.

---

This troubleshooting guide provides solutions for common issues encountered when using the Kalakan TTS system. If you encounter an issue not covered in this guide, please report it so we can improve the documentation.
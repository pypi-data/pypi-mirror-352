# Publishing and Deployment Guide for Kalakan TTS

This guide covers how to package, publish, and deploy your trained Twi TTS models for production use. It provides instructions for making your models available to developers who want to integrate Twi speech synthesis into their applications without having to train their own models.

## Table of Contents

1. [Packaging Your Models](#packaging-your-models)
2. [Creating a Python Package](#creating-a-python-package)
3. [Deployment Options](#deployment-options)
4. [API Development](#api-development)
5. [Containerization](#containerization)
6. [Cloud Deployment](#cloud-deployment)
7. [Edge Deployment](#edge-deployment)
8. [Model Optimization](#model-optimization)
9. [Distribution Channels](#distribution-channels)
10. [Documentation](#documentation)
11. [Licensing](#licensing)

## Packaging Your Models

### 1. Model Export

After training, export your models in a portable format:

```python
# Export acoustic model
acoustic_model.export_model("models/twi_acoustic_model.pt")

# Export vocoder
vocoder.export_model("models/twi_vocoder.pt")

# Export configuration
export_config("models/twi_tts_config.json")
```

### 2. Create a Model Package

Package your models with metadata:

```
twi-tts-models/
├── acoustic_model.pt
├── vocoder.pt
├── config.json
├── phoneme_dict.json
├── README.md
└── LICENSE
```

Include in `config.json`:
- Model architecture details
- Training dataset information
- Performance metrics
- Version information
- Usage instructions

### 3. Version Your Models

Use semantic versioning for your models:
- Major version: Incompatible API changes
- Minor version: New features, backward compatible
- Patch version: Bug fixes, backward compatible

Example: `twi-tts-v1.2.3`

## Creating a Python Package

### 1. Package Structure

Create a distributable Python package:

```
kalakan-twi-tts/
├── kalakan_twi_tts/
│   ├── __init__.py
│   ├── synthesizer.py
│   ├── text/
│   │   ├── __init__.py
│   │   ├── cleaner.py
│   │   ├── normalizer.py
│   │   └── g2p.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── model_loader.py
│   └── utils/
│       ├── __init__.py
│       └── audio.py
├── setup.py
├── README.md
├── LICENSE
└── MANIFEST.in
```

### 2. Setup Script

Create a `setup.py` file:

```python
from setuptools import setup, find_packages

setup(
    name="kalakan-twi-tts",
    version="1.0.0",
    description="Twi Text-to-Speech system based on Kalakan TTS",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/kalakan-twi-tts",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "torch>=1.7.0",
        "numpy>=1.19.0",
        "librosa>=0.8.0",
        "soundfile>=0.10.0",
        "requests>=2.25.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
    ],
    python_requires=">=3.7",
)
```

### 3. Model Distribution Strategy

Choose a strategy for distributing your models:

1. **Include with Package**: Bundle small models directly
2. **Download on First Use**: Download models from a server when first needed
3. **Separate Download**: Require users to download models separately

Example implementation for option 2:

```python
def download_models(model_dir=None):
    """Download pre-trained models if not already present."""
    if model_dir is None:
        model_dir = os.path.join(os.path.expanduser("~"), ".kalakan-twi-tts")
    
    os.makedirs(model_dir, exist_ok=True)
    
    models = {
        "acoustic_model.pt": "https://example.com/models/twi_acoustic_model.pt",
        "vocoder.pt": "https://example.com/models/twi_vocoder.pt",
        "config.json": "https://example.com/models/twi_config.json",
    }
    
    for filename, url in models.items():
        filepath = os.path.join(model_dir, filename)
        if not os.path.exists(filepath):
            print(f"Downloading {filename}...")
            response = requests.get(url, stream=True)
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
    
    return model_dir
```

### 4. Publishing to PyPI

Make your package available on PyPI:

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

## Deployment Options

### 1. Standalone Library

For developers who want to integrate TTS directly into their applications:

```python
from kalakan_twi_tts import TwiSynthesizer

# Initialize synthesizer
synthesizer = TwiSynthesizer()

# Generate speech
audio = synthesizer.synthesize("Akwaaba! Wo ho te sɛn?")
synthesizer.save_audio(audio, "output.wav")

# Stream audio
synthesizer.speak("Akwaaba! Wo ho te sɛn?")
```

### 2. Command-Line Interface

Provide a CLI for easy use:

```bash
# Install the package
pip install kalakan-twi-tts

# Generate speech
kalakan-twi-tts --text "Akwaaba! Wo ho te sɛn?" --output output.wav

# Interactive mode
kalakan-twi-tts --interactive
```

### 3. Web Service

Deploy as a web service for applications to call:

```bash
# Start the web service
kalakan-twi-tts-server --host 0.0.0.0 --port 8000
```

## API Development

### 1. REST API

Create a REST API for your TTS service:

```python
from flask import Flask, request, send_file
from kalakan_twi_tts import TwiSynthesizer
import io

app = Flask(__name__)
synthesizer = TwiSynthesizer()

@app.route("/synthesize", methods=["POST"])
def synthesize():
    data = request.json
    text = data.get("text", "")
    
    if not text:
        return {"error": "No text provided"}, 400
    
    # Generate speech
    audio = synthesizer.synthesize(text)
    
    # Convert to bytes
    buffer = io.BytesIO()
    synthesizer.save_audio(audio, buffer)
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype="audio/wav",
        as_attachment=True,
        attachment_filename="speech.wav"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```

### 2. gRPC API

For more efficient communication, implement a gRPC API:

```protobuf
// twi_tts.proto
syntax = "proto3";

package twi_tts;

service TwiTTS {
  rpc Synthesize (SynthesizeRequest) returns (SynthesizeResponse);
  rpc SynthesizeStream (SynthesizeRequest) returns (stream AudioChunk);
}

message SynthesizeRequest {
  string text = 1;
  float speed = 2;
  float pitch = 3;
  float energy = 4;
}

message SynthesizeResponse {
  bytes audio = 1;
  string format = 2;
  int32 sample_rate = 3;
}

message AudioChunk {
  bytes audio_chunk = 1;
}
```

### 3. WebSocket API

For real-time applications, implement a WebSocket API:

```python
import asyncio
import websockets
import json
from kalakan_twi_tts import TwiSynthesizer

synthesizer = TwiSynthesizer()

async def synthesize(websocket, path):
    async for message in websocket:
        try:
            data = json.loads(message)
            text = data.get("text", "")
            
            if not text:
                await websocket.send(json.dumps({"error": "No text provided"}))
                continue
            
            # Generate speech
            audio = synthesizer.synthesize(text)
            
            # Send audio as bytes
            await websocket.send(audio.tobytes())
            
        except Exception as e:
            await websocket.send(json.dumps({"error": str(e)}))

start_server = websockets.serve(synthesize, "0.0.0.0", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
```

## Containerization

### 1. Docker Container

Create a Docker container for your TTS service:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Download models
RUN python -c "from kalakan_twi_tts import download_models; download_models('/app/models')"

# Expose port
EXPOSE 8000

# Run the server
CMD ["python", "server.py"]
```

Build and run the container:

```bash
# Build the container
docker build -t kalakan-twi-tts .

# Run the container
docker run -p 8000:8000 kalakan-twi-tts
```

### 2. Docker Compose

Create a `docker-compose.yml` file for easy deployment:

```yaml
version: '3'

services:
  tts-api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models
    restart: unless-stopped
    environment:
      - MODEL_DIR=/app/models
      - LOG_LEVEL=INFO
```

## Cloud Deployment

### 1. AWS Deployment

Deploy to AWS using Elastic Beanstalk:

1. Create an Elastic Beanstalk application
2. Configure environment variables
3. Deploy your Docker container
4. Set up auto-scaling based on demand

### 2. Google Cloud Platform

Deploy to GCP using Cloud Run:

```bash
# Build and push the container
gcloud builds submit --tag gcr.io/your-project/kalakan-twi-tts

# Deploy to Cloud Run
gcloud run deploy kalakan-twi-tts \
  --image gcr.io/your-project/kalakan-twi-tts \
  --platform managed \
  --memory 2Gi \
  --cpu 2 \
  --allow-unauthenticated
```

### 3. Azure Deployment

Deploy to Azure using App Service:

1. Create an Azure App Service
2. Configure it to use your Docker container
3. Set up scaling rules

## Edge Deployment

### 1. Model Optimization for Edge

Optimize models for edge deployment:

```python
import torch

# Load model
model = torch.load("acoustic_model.pt")

# Quantize model
quantized_model = torch.quantization.quantize_dynamic(
    model, {torch.nn.Linear}, dtype=torch.qint8
)

# Export quantized model
torch.save(quantized_model, "acoustic_model_quantized.pt")
```

### 2. ONNX Export

Export models to ONNX format for cross-platform compatibility:

```python
import torch
import onnx

# Load model
model = torch.load("acoustic_model.pt")
model.eval()

# Create dummy input
dummy_input = torch.zeros(1, 100, dtype=torch.long)

# Export to ONNX
torch.onnx.export(
    model,
    dummy_input,
    "acoustic_model.onnx",
    export_params=True,
    opset_version=11,
    do_constant_folding=True,
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={"input": {0: "batch_size", 1: "sequence_length"}}
)

# Verify ONNX model
onnx_model = onnx.load("acoustic_model.onnx")
onnx.checker.check_model(onnx_model)
```

### 3. Mobile Deployment

Create mobile-friendly versions:

1. **Android**:
   - Use TensorFlow Lite or ONNX Runtime
   - Provide Java/Kotlin bindings

2. **iOS**:
   - Use Core ML or ONNX Runtime
   - Provide Swift bindings

## Model Optimization

### 1. Quantization

Reduce model size through quantization:

```python
# Post-training quantization
def quantize_model(model_path, output_path):
    model = torch.load(model_path)
    quantized_model = torch.quantization.quantize_dynamic(
        model, {torch.nn.Linear, torch.nn.LSTM}, dtype=torch.qint8
    )
    torch.save(quantized_model, output_path)
    
    # Print size comparison
    original_size = os.path.getsize(model_path) / (1024 * 1024)
    quantized_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"Original size: {original_size:.2f} MB")
    print(f"Quantized size: {quantized_size:.2f} MB")
    print(f"Reduction: {(1 - quantized_size/original_size) * 100:.2f}%")
```

### 2. Pruning

Remove unnecessary weights:

```python
import torch.nn.utils.prune as prune

def prune_model(model, amount=0.3):
    for name, module in model.named_modules():
        if isinstance(module, torch.nn.Linear):
            prune.l1_unstructured(module, name='weight', amount=amount)
            prune.remove(module, 'weight')
    return model
```

### 3. Knowledge Distillation

Create smaller, faster models:

```python
def train_student_model(teacher_model, student_model, train_loader, epochs=10):
    teacher_model.eval()
    student_model.train()
    
    optimizer = torch.optim.Adam(student_model.parameters())
    
    for epoch in range(epochs):
        for batch in train_loader:
            # Forward pass with teacher (no grad)
            with torch.no_grad():
                teacher_outputs = teacher_model(batch["input"])
            
            # Forward pass with student
            student_outputs = student_model(batch["input"])
            
            # Compute loss (distillation + task loss)
            distillation_loss = F.mse_loss(student_outputs, teacher_outputs)
            task_loss = compute_task_loss(student_outputs, batch["target"])
            loss = 0.5 * distillation_loss + 0.5 * task_loss
            
            # Backward and optimize
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
```

## Distribution Channels

### 1. PyPI

Publish your package to PyPI:

```bash
python -m build
python -m twine upload dist/*
```

### 2. GitHub Releases

Create GitHub releases with pre-built packages:

1. Tag your release: `git tag v1.0.0`
2. Push the tag: `git push origin v1.0.0`
3. Create a release on GitHub with:
   - Release notes
   - Pre-built wheels
   - Model files

### 3. Model Hub

Create a model hub for your TTS models:

1. Set up a simple website with model downloads
2. Include:
   - Model cards with details
   - Performance metrics
   - Sample audio
   - Usage instructions

### 4. Docker Hub

Publish your Docker image:

```bash
docker tag kalakan-twi-tts yourusername/kalakan-twi-tts:v1.0.0
docker push yourusername/kalakan-twi-tts:v1.0.0
```

## Documentation

### 1. API Documentation

Create comprehensive API documentation:

```python
def synthesize(text, speed=1.0, pitch=1.0, energy=1.0):
    """
    Synthesize speech from text.
    
    Args:
        text (str): The Twi text to synthesize.
        speed (float, optional): Speech speed factor. Defaults to 1.0.
        pitch (float, optional): Pitch factor. Defaults to 1.0.
        energy (float, optional): Energy/volume factor. Defaults to 1.0.
        
    Returns:
        numpy.ndarray: Audio waveform as a numpy array.
        
    Examples:
        >>> from kalakan_twi_tts import TwiSynthesizer
        >>> synthesizer = TwiSynthesizer()
        >>> audio = synthesizer.synthesize("Akwaaba!")
        >>> synthesizer.save_audio(audio, "welcome.wav")
    """
```

### 2. User Guide

Create a user guide with:

1. Installation instructions
2. Quick start examples
3. Advanced usage
4. Troubleshooting
5. Performance optimization

### 3. Integration Examples

Provide examples for common frameworks:

- Flask/Django web applications
- React/Vue.js frontend integration
- Mobile app integration (Android/iOS)
- Desktop application integration

## Licensing

### 1. Choose a License

Select an appropriate license:

1. **Apache License 2.0**: Permissive, allows commercial use
2. **MIT License**: Very permissive, minimal restrictions
3. **GPL**: Requires derivative works to be open source
4. **Dual Licensing**: Open source for non-commercial, paid for commercial

### 2. License Your Models

Create a clear license for your models:

```
# Model License

Copyright (c) 2023 Your Name

These Twi TTS models are licensed under the Creative Commons Attribution-NonCommercial 4.0 International License.

You are free to:
- Share: Copy and redistribute the material in any medium or format
- Adapt: Remix, transform, and build upon the material

Under the following terms:
- Attribution: You must give appropriate credit, provide a link to the license, and indicate if changes were made.
- NonCommercial: You may not use the material for commercial purposes without obtaining a commercial license.

For commercial use, please contact: your.email@example.com
```

### 3. Commercial Licensing

Set up a commercial licensing program:

1. Define pricing tiers (e.g., by company size or usage volume)
2. Create a license agreement template
3. Set up a payment and license key system
4. Provide commercial support options

---

By following this guide, you'll be able to package, publish, and deploy your Twi TTS models for production use, making them accessible to developers who want to integrate Twi speech synthesis into their applications without having to train their own models.
# Kalakan TTS Installation Guide

This guide provides comprehensive instructions for installing the Kalakan TTS system in various environments and configurations.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Basic Installation](#basic-installation)
3. [Development Installation](#development-installation)
4. [Docker Installation](#docker-installation)
5. [Cloud Deployment](#cloud-deployment)
6. [Edge Device Installation](#edge-device-installation)
7. [Offline Installation](#offline-installation)
8. [Troubleshooting](#troubleshooting)
9. [Upgrading](#upgrading)
10. [Uninstallation](#uninstallation)

## System Requirements

### Minimum Requirements

- Python 3.9+
- 4GB RAM
- 2GB free disk space
- CPU with AVX2 support (for efficient inference)

### Recommended Requirements

- Python 3.9+
- CUDA-compatible GPU with 8GB+ VRAM
- 16GB+ RAM
- 100GB+ free disk space
- SSD storage

### Operating System Support

- Linux (Ubuntu 20.04+, CentOS 8+)
- macOS (10.15+)
- Windows 10/11

### Python Dependencies

- PyTorch 2.0+
- torchaudio 2.0+
- numpy 1.21+
- librosa 0.10+
- pydantic 2.0+
- pyyaml 6.0+
- tqdm 4.64+
- matplotlib 3.5+
- tensorboard 2.10+

## Basic Installation

### Installation from PyPI

The simplest way to install Kalakan TTS is from PyPI:

```bash
pip install kalakan-tts
```

This installs the core package with basic dependencies.

### Installation with Optional Dependencies

To install Kalakan TTS with additional dependencies for specific use cases:

```bash
# For API server functionality
pip install kalakan-tts[api]

# For training functionality
pip install kalakan-tts[training]

# For development
pip install kalakan-tts[dev]

# For all optional dependencies
pip install kalakan-tts[api,training,dev]
```

### Verifying the Installation

To verify that Kalakan TTS is installed correctly:

```bash
python -c "import kalakan; print(kalakan.__version__)"
```

This should print the version number of the installed package.

## Development Installation

For development purposes, it's recommended to install Kalakan TTS from source:

### Cloning the Repository

```bash
git clone https://github.com/kalakan-ai/kalakan-tts.git
cd kalakan-tts
```

### Installing in Development Mode

```bash
# Install with all dependencies for development
pip install -e ".[dev,api,training]"

# Install pre-commit hooks
pre-commit install
```

### Setting Up the Development Environment

```bash
# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev,api,training]"
```

## Docker Installation

Kalakan TTS provides Docker images for easy deployment:

### Using Pre-built Docker Images

```bash
# Pull the inference image
docker pull kalakan/kalakan-tts:inference

# Pull the API server image
docker pull kalakan/kalakan-tts:api

# Pull the training image
docker pull kalakan/kalakan-tts:training
```

### Running the Docker Container

```bash
# Run the API server
docker run -p 8000:8000 kalakan/kalakan-tts:api

# Run the inference container with a mounted volume for models and output
docker run -v /path/to/models:/models -v /path/to/output:/output kalakan/kalakan-tts:inference

# Run the training container with GPU support
docker run --gpus all -v /path/to/data:/data -v /path/to/output:/output kalakan/kalakan-tts:training
```

### Building Docker Images from Source

```bash
# Build the inference image
docker build -f docker/Dockerfile.inference -t kalakan-tts:inference .

# Build the API server image
docker build -f docker/Dockerfile.api -t kalakan-tts:api .

# Build the training image
docker build -f docker/Dockerfile.training -t kalakan-tts:training .
```

## Cloud Deployment

### AWS Deployment

#### EC2 Instance Setup

1. Launch an EC2 instance with the following specifications:
   - Amazon Linux 2 or Ubuntu 20.04
   - Instance type: g4dn.xlarge or better (for GPU support)
   - At least 100GB EBS storage

2. Install dependencies:

```bash
# For Amazon Linux 2
sudo yum update -y
sudo yum install -y python3-pip python3-devel

# For Ubuntu
sudo apt update
sudo apt install -y python3-pip python3-dev
```

3. Install CUDA and cuDNN (for GPU instances):

```bash
# For Amazon Linux 2
sudo amazon-linux-extras install -y nvidia-driver
sudo yum install -y cuda-toolkit

# For Ubuntu
sudo apt install -y nvidia-driver-510 cuda-toolkit-11-6
```

4. Install Kalakan TTS:

```bash
pip3 install kalakan-tts[api]
```

#### Using AWS Lambda (for Inference)

For serverless deployment, you can use AWS Lambda with container images:

1. Build a container image for Lambda:

```bash
docker build -f docker/Dockerfile.lambda -t kalakan-tts:lambda .
```

2. Push the image to Amazon ECR:

```bash
aws ecr create-repository --repository-name kalakan-tts
aws ecr get-login-password | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
docker tag kalakan-tts:lambda <account-id>.dkr.ecr.<region>.amazonaws.com/kalakan-tts:lambda
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/kalakan-tts:lambda
```

3. Create a Lambda function using the container image.

### Google Cloud Platform Deployment

#### GCE Instance Setup

1. Create a GCE instance with the following specifications:
   - Ubuntu 20.04
   - Machine type: n1-standard-4 or better
   - GPU: NVIDIA T4 or better
   - At least 100GB persistent disk

2. Install dependencies:

```bash
sudo apt update
sudo apt install -y python3-pip python3-dev
```

3. Install CUDA and cuDNN:

```bash
# Install CUDA
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600
sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/7fa2af80.pub
sudo add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/ /"
sudo apt update
sudo apt install -y cuda-11-6
```

4. Install Kalakan TTS:

```bash
pip3 install kalakan-tts[api]
```

#### Using Google Cloud Run (for API)

For serverless API deployment, you can use Google Cloud Run:

1. Build a container image:

```bash
docker build -f docker/Dockerfile.api -t gcr.io/<project-id>/kalakan-tts:api .
```

2. Push the image to Google Container Registry:

```bash
gcloud auth configure-docker
docker push gcr.io/<project-id>/kalakan-tts:api
```

3. Deploy to Cloud Run:

```bash
gcloud run deploy kalakan-tts-api --image gcr.io/<project-id>/kalakan-tts:api --platform managed --region us-central1 --memory 2Gi
```

## Edge Device Installation

### Raspberry Pi Installation

1. Install dependencies:

```bash
sudo apt update
sudo apt install -y python3-pip python3-dev libatlas-base-dev
```

2. Install PyTorch for Raspberry Pi:

```bash
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

3. Install Kalakan TTS:

```bash
pip3 install kalakan-tts
```

4. Optimize for edge deployment:

```bash
# Export models to ONNX format
kalakan-export \
    --acoustic-model /path/to/acoustic_model.pt \
    --vocoder /path/to/vocoder.pt \
    --output-dir /path/to/exported_models \
    --format onnx \
    --quantize
```

### NVIDIA Jetson Installation

1. Install dependencies:

```bash
sudo apt update
sudo apt install -y python3-pip python3-dev
```

2. Install PyTorch for Jetson:

```bash
# Follow the instructions at https://forums.developer.nvidia.com/t/pytorch-for-jetson/72048
```

3. Install Kalakan TTS:

```bash
pip3 install kalakan-tts
```

4. Optimize for Jetson:

```bash
# Export models to TensorRT format
kalakan-export \
    --acoustic-model /path/to/acoustic_model.pt \
    --vocoder /path/to/vocoder.pt \
    --output-dir /path/to/exported_models \
    --format tensorrt
```

## Offline Installation

For environments without internet access, you can create an offline installation package:

### Creating an Offline Package

On a machine with internet access:

```bash
# Create a directory for the package
mkdir kalakan-offline
cd kalakan-offline

# Download the wheel files
pip download kalakan-tts[api,training]

# Download the source code
git clone https://github.com/kalakan-ai/kalakan-tts.git

# Download pre-trained models
mkdir models
wget -O models/tacotron2.pt https://github.com/kalakan-ai/kalakan-tts/releases/download/v1.0.0/tacotron2.pt
wget -O models/hifigan.pt https://github.com/kalakan-ai/kalakan-tts/releases/download/v1.0.0/hifigan.pt

# Create a README file
echo "Kalakan TTS Offline Installation Package" > README.md
echo "1. Install the dependencies: pip install *.whl" >> README.md
echo "2. Install the package: pip install -e kalakan-tts" >> README.md

# Create a tarball
tar -czvf kalakan-offline.tar.gz *
```

### Installing from the Offline Package

On the target machine:

```bash
# Extract the package
tar -xzvf kalakan-offline.tar.gz
cd kalakan-offline

# Install the dependencies
pip install *.whl

# Install the package
pip install -e kalakan-tts
```

## Troubleshooting

### Common Installation Issues

#### PyTorch Installation Failures

**Issue**: PyTorch installation fails with CUDA compatibility errors.

**Solution**:
1. Check your CUDA version:
```bash
nvcc --version
```
2. Install PyTorch with the matching CUDA version:
```bash
pip install torch==2.0.0+cu117 -f https://download.pytorch.org/whl/torch_stable.html
```

#### Missing Dependencies

**Issue**: ImportError when trying to use Kalakan TTS.

**Solution**:
1. Install with all dependencies:
```bash
pip install kalakan-tts[api,training]
```
2. Check for specific missing packages and install them manually.

#### GPU Not Detected

**Issue**: PyTorch doesn't detect the GPU.

**Solution**:
1. Check if CUDA is installed correctly:
```bash
python -c "import torch; print(torch.cuda.is_available())"
```
2. Check NVIDIA driver installation:
```bash
nvidia-smi
```
3. Reinstall PyTorch with the correct CUDA version.

#### Installation Hangs

**Issue**: Installation process hangs or takes too long.

**Solution**:
1. Try installing with a different package index:
```bash
pip install kalakan-tts --index-url https://pypi.org/simple
```
2. Install dependencies one by one to identify the problematic package.

### Getting Help

If you encounter issues not covered in this guide, you can:

1. Check the logs for detailed error messages
2. Open an issue on the GitHub repository
3. Contact the Kalakan TTS team for support

## Upgrading

To upgrade Kalakan TTS to the latest version:

```bash
# Upgrade from PyPI
pip install --upgrade kalakan-tts

# Upgrade from source
cd kalakan-tts
git pull
pip install -e .
```

## Uninstallation

To uninstall Kalakan TTS:

```bash
pip uninstall kalakan-tts
```

To completely remove all dependencies (optional):

```bash
pip uninstall -y torch torchaudio numpy librosa pydantic pyyaml tqdm matplotlib tensorboard
```

---

This installation guide provides comprehensive instructions for installing the Kalakan TTS system in various environments and configurations. For more detailed information on specific features, refer to the API reference and other documentation in the `docs/` directory.
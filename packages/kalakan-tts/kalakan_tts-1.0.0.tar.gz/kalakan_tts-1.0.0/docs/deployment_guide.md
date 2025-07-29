# Kalakan TTS Deployment Guide

This guide provides comprehensive instructions for deploying the Kalakan TTS system in various production environments, from cloud services to edge devices.

## Table of Contents

1. [Deployment Overview](#deployment-overview)
2. [Preparing for Deployment](#preparing-for-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Cloud Service Deployment](#cloud-service-deployment)
6. [Edge Device Deployment](#edge-device-deployment)
7. [Serverless Deployment](#serverless-deployment)
8. [Monitoring and Logging](#monitoring-and-logging)
9. [Scaling Strategies](#scaling-strategies)
10. [Security Considerations](#security-considerations)
11. [Performance Optimization](#performance-optimization)
12. [Troubleshooting](#troubleshooting)

## Deployment Overview

### Deployment Architectures

Kalakan TTS supports several deployment architectures:

1. **Standalone Deployment**:
   - Single server deployment
   - All components run on a single machine
   - Suitable for low to medium traffic

2. **Microservices Deployment**:
   - Components deployed as separate services
   - Scalable and resilient
   - Suitable for high traffic and complex deployments

3. **Serverless Deployment**:
   - Components deployed as serverless functions
   - Pay-per-use pricing
   - Suitable for variable workloads

4. **Edge Deployment**:
   - Optimized for resource-constrained devices
   - Offline operation
   - Suitable for IoT and mobile applications

### Deployment Components

A typical Kalakan TTS deployment includes:

1. **API Server**:
   - REST API for web applications
   - gRPC API for high-performance applications
   - WebSocket API for streaming applications

2. **Inference Engine**:
   - Acoustic models
   - Vocoders
   - Text processing components

3. **Storage**:
   - Model storage
   - Audio cache (optional)
   - Configuration storage

4. **Monitoring and Logging**:
   - Performance metrics
   - Error tracking
   - Usage statistics

## Preparing for Deployment

### Model Export

Before deployment, export your models to an optimized format:

```bash
kalakan-export \
    --acoustic-model /path/to/acoustic_model.pt \
    --vocoder /path/to/vocoder.pt \
    --output-dir /path/to/exported_models \
    --format onnx \
    --quantize
```

Available export formats:
- `pytorch`: Standard PyTorch format
- `onnx`: ONNX format for cross-platform deployment
- `torchscript`: TorchScript format for optimized deployment
- `tensorrt`: TensorRT format for NVIDIA GPUs

### Configuration

Create a deployment configuration file:

```yaml
# deployment.yaml
api:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  timeout: 30
  cors_origins: ["*"]
  
models:
  acoustic_model: "/models/acoustic_model.onnx"
  vocoder: "/models/vocoder.onnx"
  use_onnx: true
  
inference:
  device: "cuda:0"
  batch_size: 8
  quantize: true
  cache_enabled: true
  cache_size: 1000
  
logging:
  level: "INFO"
  file: "/logs/kalakan.log"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  
monitoring:
  enabled: true
  prometheus_port: 9090
```

### Resource Requirements

Estimate resource requirements based on your expected workload:

| Workload | CPU | RAM | GPU | Storage |
|----------|-----|-----|-----|---------|
| Low (<10 req/min) | 2 cores | 4GB | Optional | 10GB |
| Medium (10-100 req/min) | 4 cores | 8GB | Recommended | 20GB |
| High (>100 req/min) | 8+ cores | 16GB+ | Required | 50GB+ |

## Docker Deployment

### Using Pre-built Docker Images

```bash
# Pull the API server image
docker pull kalakan/kalakan-tts:api

# Run the API server
docker run -p 8000:8000 -v /path/to/models:/models kalakan/kalakan-tts:api \
    --acoustic-model /models/acoustic_model.pt \
    --vocoder /models/vocoder.pt \
    --device cpu
```

### Building Custom Docker Images

Create a Dockerfile:

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Install Kalakan TTS
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy models
COPY models /models

# Expose port
EXPOSE 8000

# Run the API server
CMD ["kalakan-api", "--host", "0.0.0.0", "--port", "8000", "--acoustic-model", "/models/acoustic_model.pt", "--vocoder", "/models/vocoder.pt"]
```

Build and run the Docker image:

```bash
# Build the image
docker build -t kalakan-tts:custom .

# Run the container
docker run -p 8000:8000 kalakan-tts:custom
```

### Docker Compose Deployment

Create a `docker-compose.yml` file:

```yaml
version: '3'

services:
  api:
    image: kalakan/kalakan-tts:api
    ports:
      - "8000:8000"
    volumes:
      - ./models:/models
      - ./logs:/logs
    environment:
      - KALAKAN_ACOUSTIC_MODEL=/models/acoustic_model.pt
      - KALAKAN_VOCODER=/models/vocoder.pt
      - KALAKAN_DEVICE=cpu
    restart: unless-stopped
    
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    restart: unless-stopped
    
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
    depends_on:
      - prometheus
    restart: unless-stopped

volumes:
  grafana-data:
```

Run the Docker Compose deployment:

```bash
docker-compose up -d
```

## Kubernetes Deployment

### Basic Kubernetes Deployment

Create a Kubernetes deployment manifest:

```yaml
# kalakan-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kalakan-tts
  labels:
    app: kalakan-tts
spec:
  replicas: 3
  selector:
    matchLabels:
      app: kalakan-tts
  template:
    metadata:
      labels:
        app: kalakan-tts
    spec:
      containers:
      - name: kalakan-tts
        image: kalakan/kalakan-tts:api
        ports:
        - containerPort: 8000
        env:
        - name: KALAKAN_ACOUSTIC_MODEL
          value: /models/acoustic_model.pt
        - name: KALAKAN_VOCODER
          value: /models/vocoder.pt
        - name: KALAKAN_DEVICE
          value: cpu
        volumeMounts:
        - name: models-volume
          mountPath: /models
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
      volumes:
      - name: models-volume
        persistentVolumeClaim:
          claimName: models-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: kalakan-tts
spec:
  selector:
    app: kalakan-tts
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

Create a persistent volume claim:

```yaml
# models-pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: models-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

Apply the Kubernetes manifests:

```bash
kubectl apply -f models-pvc.yaml
kubectl apply -f kalakan-deployment.yaml
```

### Kubernetes with GPU Support

Create a deployment with GPU support:

```yaml
# kalakan-gpu-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kalakan-tts-gpu
  labels:
    app: kalakan-tts-gpu
spec:
  replicas: 2
  selector:
    matchLabels:
      app: kalakan-tts-gpu
  template:
    metadata:
      labels:
        app: kalakan-tts-gpu
    spec:
      containers:
      - name: kalakan-tts
        image: kalakan/kalakan-tts:api-cuda
        ports:
        - containerPort: 8000
        env:
        - name: KALAKAN_ACOUSTIC_MODEL
          value: /models/acoustic_model.pt
        - name: KALAKAN_VOCODER
          value: /models/vocoder.pt
        - name: KALAKAN_DEVICE
          value: cuda:0
        volumeMounts:
        - name: models-volume
          mountPath: /models
        resources:
          limits:
            nvidia.com/gpu: 1
      volumes:
      - name: models-volume
        persistentVolumeClaim:
          claimName: models-pvc
```

Apply the GPU deployment:

```bash
kubectl apply -f kalakan-gpu-deployment.yaml
```

### Helm Chart Deployment

Create a Helm chart for more flexible deployment:

```bash
# Create a Helm chart
helm create kalakan-tts

# Customize the chart
# Edit values.yaml, templates/, etc.

# Install the chart
helm install kalakan-tts ./kalakan-tts
```

## Cloud Service Deployment

### AWS Deployment

#### EC2 Deployment

1. Launch an EC2 instance with the following specifications:
   - Amazon Linux 2 or Ubuntu 20.04
   - Instance type: c5.2xlarge (for CPU) or g4dn.xlarge (for GPU)
   - Security group with port 8000 open

2. Install Docker:
```bash
# Amazon Linux 2
sudo yum update -y
sudo amazon-linux-extras install docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# Ubuntu
sudo apt update
sudo apt install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker ubuntu
```

3. Run the Kalakan TTS Docker container:
```bash
docker run -d -p 8000:8000 -v /path/to/models:/models kalakan/kalakan-tts:api \
    --acoustic-model /models/acoustic_model.pt \
    --vocoder /models/vocoder.pt
```

#### ECS Deployment

1. Create an ECS cluster:
```bash
aws ecs create-cluster --cluster-name kalakan-cluster
```

2. Create a task definition:
```json
{
  "family": "kalakan-tts",
  "networkMode": "awsvpc",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "kalakan-tts",
      "image": "kalakan/kalakan-tts:api",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8000,
          "hostPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "KALAKAN_ACOUSTIC_MODEL",
          "value": "/models/acoustic_model.pt"
        },
        {
          "name": "KALAKAN_VOCODER",
          "value": "/models/vocoder.pt"
        }
      ],
      "mountPoints": [
        {
          "sourceVolume": "models",
          "containerPath": "/models",
          "readOnly": true
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/kalakan-tts",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ],
  "volumes": [
    {
      "name": "models",
      "efsVolumeConfiguration": {
        "fileSystemId": "fs-12345678",
        "rootDirectory": "/"
      }
    }
  ],
  "requiresCompatibilities": [
    "FARGATE"
  ],
  "cpu": "1024",
  "memory": "2048"
}
```

3. Create a service:
```bash
aws ecs create-service \
    --cluster kalakan-cluster \
    --service-name kalakan-service \
    --task-definition kalakan-tts:1 \
    --desired-count 2 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-12345678],securityGroups=[sg-12345678],assignPublicIp=ENABLED}"
```

### Google Cloud Platform Deployment

#### GCE Deployment

1. Create a GCE instance:
```bash
gcloud compute instances create kalakan-tts \
    --machine-type=n1-standard-4 \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=50GB \
    --tags=http-server
```

2. SSH into the instance and install Docker:
```bash
sudo apt update
sudo apt install -y docker.io
sudo systemctl enable --now docker
```

3. Run the Kalakan TTS Docker container:
```bash
docker run -d -p 8000:8000 -v /path/to/models:/models kalakan/kalakan-tts:api \
    --acoustic-model /models/acoustic_model.pt \
    --vocoder /models/vocoder.pt
```

#### GKE Deployment

1. Create a GKE cluster:
```bash
gcloud container clusters create kalakan-cluster \
    --num-nodes=3 \
    --machine-type=n1-standard-4 \
    --zone=us-central1-a
```

2. Deploy to GKE:
```bash
kubectl apply -f kalakan-deployment.yaml
```

### Azure Deployment

#### Azure VM Deployment

1. Create an Azure VM:
```bash
az vm create \
    --resource-group myResourceGroup \
    --name kalakan-vm \
    --image UbuntuLTS \
    --admin-username azureuser \
    --generate-ssh-keys \
    --size Standard_D4s_v3
```

2. SSH into the VM and install Docker:
```bash
sudo apt update
sudo apt install -y docker.io
sudo systemctl enable --now docker
```

3. Run the Kalakan TTS Docker container:
```bash
docker run -d -p 8000:8000 -v /path/to/models:/models kalakan/kalakan-tts:api \
    --acoustic-model /models/acoustic_model.pt \
    --vocoder /models/vocoder.pt
```

#### AKS Deployment

1. Create an AKS cluster:
```bash
az aks create \
    --resource-group myResourceGroup \
    --name kalakan-cluster \
    --node-count 3 \
    --node-vm-size Standard_D4s_v3 \
    --generate-ssh-keys
```

2. Get credentials for the cluster:
```bash
az aks get-credentials --resource-group myResourceGroup --name kalakan-cluster
```

3. Deploy to AKS:
```bash
kubectl apply -f kalakan-deployment.yaml
```

## Edge Device Deployment

### Raspberry Pi Deployment

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

4. Export optimized models:
```bash
kalakan-export \
    --acoustic-model /path/to/acoustic_model.pt \
    --vocoder /path/to/vocoder.pt \
    --output-dir /path/to/exported_models \
    --format onnx \
    --quantize
```

5. Create a systemd service:
```bash
sudo nano /etc/systemd/system/kalakan.service
```

```
[Unit]
Description=Kalakan TTS API Server
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/kalakan
ExecStart=/usr/bin/python3 -m kalakan.api.server --host 0.0.0.0 --port 8000 --acoustic-model /home/pi/kalakan/models/acoustic_model_quantized.onnx --vocoder /home/pi/kalakan/models/vocoder_quantized.onnx --device cpu
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

6. Enable and start the service:
```bash
sudo systemctl enable kalakan
sudo systemctl start kalakan
```

### NVIDIA Jetson Deployment

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

4. Export optimized models:
```bash
kalakan-export \
    --acoustic-model /path/to/acoustic_model.pt \
    --vocoder /path/to/vocoder.pt \
    --output-dir /path/to/exported_models \
    --format tensorrt
```

5. Create a systemd service:
```bash
sudo nano /etc/systemd/system/kalakan.service
```

```
[Unit]
Description=Kalakan TTS API Server
After=network.target

[Service]
User=nvidia
WorkingDirectory=/home/nvidia/kalakan
ExecStart=/usr/bin/python3 -m kalakan.api.server --host 0.0.0.0 --port 8000 --acoustic-model /home/nvidia/kalakan/models/acoustic_model.tensorrt --vocoder /home/nvidia/kalakan/models/vocoder.tensorrt --device cuda:0
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

6. Enable and start the service:
```bash
sudo systemctl enable kalakan
sudo systemctl start kalakan
```

### Mobile Deployment

For mobile deployment, export models to formats suitable for mobile platforms:

```bash
# For Android (ONNX)
kalakan-export \
    --acoustic-model /path/to/acoustic_model.pt \
    --vocoder /path/to/vocoder.pt \
    --output-dir /path/to/exported_models \
    --format onnx \
    --quantize \
    --target android

# For iOS (CoreML)
kalakan-export \
    --acoustic-model /path/to/acoustic_model.pt \
    --vocoder /path/to/vocoder.pt \
    --output-dir /path/to/exported_models \
    --format coreml \
    --quantize \
    --target ios
```

## Serverless Deployment

### AWS Lambda Deployment

1. Create a Lambda function with container image:

```bash
# Create a Dockerfile for Lambda
cat > Dockerfile.lambda << EOF
FROM public.ecr.aws/lambda/python:3.9

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . ${LAMBDA_TASK_ROOT}

# Copy models
COPY models ${LAMBDA_TASK_ROOT}/models

# Set the CMD to your handler
CMD [ "lambda_function.handler" ]
EOF
```

2. Create a Lambda handler:

```python
# lambda_function.py
import json
import base64
import io
import os
import torch
from kalakan.synthesis.synthesizer import Synthesizer

# Initialize the synthesizer
synthesizer = Synthesizer(
    acoustic_model=os.path.join(os.environ["LAMBDA_TASK_ROOT"], "models/acoustic_model.pt"),
    vocoder=os.path.join(os.environ["LAMBDA_TASK_ROOT"], "models/vocoder.pt"),
    device="cpu"
)

def handler(event, context):
    # Get text from the event
    body = json.loads(event.get("body", "{}"))
    text = body.get("text", "")
    
    if not text:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "No text provided"})
        }
    
    try:
        # Synthesize speech
        audio = synthesizer.synthesize(text)
        
        # Convert audio to WAV
        buffer = io.BytesIO()
        synthesizer.save_audio(audio, buffer)
        buffer.seek(0)
        
        # Encode audio as base64
        audio_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "audio": audio_base64
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
```

3. Build and deploy the Lambda function:

```bash
# Build the Docker image
docker build -f Dockerfile.lambda -t kalakan-lambda .

# Create an ECR repository
aws ecr create-repository --repository-name kalakan-lambda

# Tag and push the image
aws ecr get-login-password | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
docker tag kalakan-lambda:latest <account-id>.dkr.ecr.<region>.amazonaws.com/kalakan-lambda:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/kalakan-lambda:latest

# Create the Lambda function
aws lambda create-function \
    --function-name kalakan-tts \
    --package-type Image \
    --code ImageUri=<account-id>.dkr.ecr.<region>.amazonaws.com/kalakan-lambda:latest \
    --role arn:aws:iam::<account-id>:role/lambda-execution-role \
    --timeout 30 \
    --memory-size 2048
```

4. Create an API Gateway to expose the Lambda function:

```bash
# Create an API
aws apigateway create-rest-api --name kalakan-api

# Get the API ID
API_ID=$(aws apigateway get-rest-apis --query "items[?name=='kalakan-api'].id" --output text)

# Get the root resource ID
ROOT_RESOURCE_ID=$(aws apigateway get-resources --rest-api-id $API_ID --query "items[?path=='/'].id" --output text)

# Create a resource
aws apigateway create-resource --rest-api-id $API_ID --parent-id $ROOT_RESOURCE_ID --path-part synthesize

# Get the resource ID
RESOURCE_ID=$(aws apigateway get-resources --rest-api-id $API_ID --query "items[?path=='/synthesize'].id" --output text)

# Create a POST method
aws apigateway put-method --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method POST --authorization-type NONE

# Set the Lambda integration
aws apigateway put-integration --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method POST --type AWS_PROXY --integration-http-method POST --uri arn:aws:apigateway:<region>:lambda:path/2015-03-31/functions/arn:aws:lambda:<region>:<account-id>:function:kalakan-tts/invocations

# Deploy the API
aws apigateway create-deployment --rest-api-id $API_ID --stage-name prod
```

### Google Cloud Functions Deployment

1. Create a Cloud Function:

```python
# main.py
import base64
import io
import os
import tempfile
import functions_framework
from flask import jsonify, Request
from kalakan.synthesis.synthesizer import Synthesizer

# Initialize the synthesizer
synthesizer = Synthesizer(
    acoustic_model="/tmp/models/acoustic_model.pt",
    vocoder="/tmp/models/vocoder.pt",
    device="cpu"
)

@functions_framework.http
def synthesize(request: Request):
    # Get text from the request
    request_json = request.get_json(silent=True)
    text = request_json.get("text", "")
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    try:
        # Synthesize speech
        audio = synthesizer.synthesize(text)
        
        # Convert audio to WAV
        buffer = io.BytesIO()
        synthesizer.save_audio(audio, buffer)
        buffer.seek(0)
        
        # Encode audio as base64
        audio_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        
        return jsonify({"audio": audio_base64})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

2. Create a requirements.txt file:

```
functions-framework==3.0.0
kalakan-tts==1.0.0
```

3. Deploy the Cloud Function:

```bash
gcloud functions deploy kalakan-tts \
    --runtime python39 \
    --trigger-http \
    --allow-unauthenticated \
    --entry-point synthesize \
    --memory 2048MB \
    --timeout 60s
```

## Monitoring and Logging

### Prometheus Monitoring

1. Create a Prometheus configuration file:

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'kalakan-tts'
    static_configs:
      - targets: ['kalakan-tts:9090']
```

2. Add Prometheus metrics to the API server:

```python
from prometheus_client import Counter, Histogram, start_http_server

# Initialize metrics
REQUESTS = Counter('kalakan_requests_total', 'Total number of requests', ['endpoint'])
LATENCY = Histogram('kalakan_request_latency_seconds', 'Request latency in seconds', ['endpoint'])

# Start Prometheus server
start_http_server(9090)

# Use metrics in API endpoints
@app.post("/synthesize")
async def synthesize(request: Request):
    REQUESTS.labels(endpoint="synthesize").inc()
    with LATENCY.labels(endpoint="synthesize").time():
        # Process request
        pass
```

### ELK Stack Logging

1. Create a Filebeat configuration:

```yaml
# filebeat.yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /logs/kalakan.log

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
```

2. Configure logging in the application:

```python
import logging
import logging.handlers

# Configure logging
logger = logging.getLogger("kalakan")
logger.setLevel(logging.INFO)

# File handler
file_handler = logging.handlers.RotatingFileHandler(
    "/logs/kalakan.log",
    maxBytes=10485760,  # 10MB
    backupCount=5
)
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
))
logger.addHandler(file_handler)

# Use logger in the application
logger.info("API server started")
logger.error("Error processing request", exc_info=True)
```

### Cloud Monitoring

#### AWS CloudWatch

1. Configure CloudWatch logging:

```python
import watchtower
import logging

# Configure CloudWatch logging
logger = logging.getLogger("kalakan")
logger.setLevel(logging.INFO)

# CloudWatch handler
cloudwatch_handler = watchtower.CloudWatchLogHandler(
    log_group="kalakan-tts",
    stream_name="api-server"
)
logger.addHandler(cloudwatch_handler)
```

2. Configure CloudWatch metrics:

```python
import boto3

# Create CloudWatch client
cloudwatch = boto3.client('cloudwatch')

# Publish metrics
cloudwatch.put_metric_data(
    Namespace='Kalakan',
    MetricData=[
        {
            'MetricName': 'RequestCount',
            'Dimensions': [
                {
                    'Name': 'Endpoint',
                    'Value': 'synthesize'
                },
            ],
            'Value': 1,
            'Unit': 'Count'
        },
    ]
)
```

#### Google Cloud Monitoring

1. Configure Cloud Logging:

```python
import google.cloud.logging
import logging

# Configure Cloud Logging
client = google.cloud.logging.Client()
client.setup_logging()

# Use standard logging
logging.info("API server started")
logging.error("Error processing request", exc_info=True)
```

2. Configure Cloud Monitoring:

```python
from opencensus.ext.stackdriver import stats_exporter
from opencensus.stats import stats
from opencensus.stats import measure
from opencensus.stats import view
from opencensus.stats import aggregation

# Create measures
m_request_count = measure.MeasureInt("request_count", "Number of requests", "requests")
m_latency = measure.MeasureFloat("latency", "Request latency", "ms")

# Create views
request_count_view = view.View(
    "request_count",
    "Number of requests",
    [],
    m_request_count,
    aggregation.CountAggregation()
)
latency_view = view.View(
    "latency",
    "Request latency",
    [],
    m_latency,
    aggregation.DistributionAggregation(
        [0, 10, 50, 100, 500, 1000, 5000, 10000]
    )
)

# Register views
stats.stats.view_manager.register_view(request_count_view)
stats.stats.view_manager.register_view(latency_view)

# Create exporter
exporter = stats_exporter.new_stats_exporter()
stats.stats.view_manager.register_exporter(exporter)

# Record metrics
stats.stats.record([
    m_request_count.m(1),
    m_latency.m(100)
])
```

## Scaling Strategies

### Horizontal Scaling

1. Use a load balancer to distribute traffic:

```yaml
# kubernetes-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: kalakan-tts
spec:
  selector:
    app: kalakan-tts
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

2. Configure autoscaling:

```yaml
# kubernetes-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: kalakan-tts
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: kalakan-tts
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Vertical Scaling

1. Adjust resource limits:

```yaml
# kubernetes-deployment.yaml
resources:
  requests:
    memory: "4Gi"
    cpu: "2"
  limits:
    memory: "8Gi"
    cpu: "4"
```

2. Use larger instance types:

```bash
# AWS
aws ec2 modify-instance-attribute \
    --instance-id i-1234567890abcdef0 \
    --instance-type c5.4xlarge

# GCP
gcloud compute instances set-machine-type kalakan-tts \
    --machine-type n1-standard-8

# Azure
az vm resize \
    --resource-group myResourceGroup \
    --name kalakan-vm \
    --size Standard_D8s_v3
```

### Caching Strategies

1. Implement a request cache:

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def synthesize_cached(text):
    return synthesizer.synthesize(text)
```

2. Use Redis for distributed caching:

```python
import redis
import hashlib
import pickle

# Connect to Redis
redis_client = redis.Redis(host='redis', port=6379, db=0)

def synthesize_with_cache(text):
    # Create a cache key
    cache_key = f"kalakan:synthesis:{hashlib.md5(text.encode()).hexdigest()}"
    
    # Check if result is in cache
    cached_result = redis_client.get(cache_key)
    if cached_result:
        return pickle.loads(cached_result)
    
    # Generate speech
    audio = synthesizer.synthesize(text)
    
    # Cache the result
    redis_client.set(cache_key, pickle.dumps(audio), ex=3600)  # Expire after 1 hour
    
    return audio
```

## Security Considerations

### API Authentication

1. Implement API key authentication:

```python
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader, APIKey

app = FastAPI()

API_KEY_NAME = "X-API-Key"
API_KEY = "your-api-key"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(status_code=403, detail="Invalid API Key")

@app.post("/synthesize")
async def synthesize(request: Request, api_key: APIKey = Depends(get_api_key)):
    # Process request
    pass
```

2. Implement JWT authentication:

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta

# JWT settings
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username

@app.post("/synthesize")
async def synthesize(request: Request, username: str = Depends(get_current_user)):
    # Process request
    pass
```

### HTTPS Configuration

1. Configure HTTPS with Let's Encrypt:

```bash
# Install Certbot
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Configure Nginx
sudo nano /etc/nginx/sites-available/kalakan
```

```
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

2. Configure HTTPS in Kubernetes with cert-manager:

```yaml
# cert-manager.yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: kalakan-tts
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - your-domain.com
    secretName: kalakan-tls
  rules:
  - host: your-domain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: kalakan-tts
            port:
              number: 80
```

### Rate Limiting

1. Implement rate limiting with Nginx:

```
http {
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    
    server {
        listen 80;
        
        location / {
            limit_req zone=api_limit burst=20 nodelay;
            proxy_pass http://localhost:8000;
        }
    }
}
```

2. Implement rate limiting in the application:

```python
from fastapi import FastAPI, Request, HTTPException
import time
import redis

app = FastAPI()

# Connect to Redis
redis_client = redis.Redis(host='redis', port=6379, db=0)

async def rate_limit(request: Request, limit: int = 10, window: int = 60):
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"
    
    # Get current count
    count = redis_client.get(key)
    if count is None:
        # First request, set count to 1 with expiration
        redis_client.set(key, 1, ex=window)
        return
    
    # Increment count
    count = int(count)
    if count >= limit:
        raise HTTPException(status_code=429, detail="Too many requests")
    
    # Increment count
    redis_client.incr(key)

@app.post("/synthesize")
async def synthesize(request: Request):
    await rate_limit(request)
    # Process request
    pass
```

## Performance Optimization

### Model Optimization

1. Quantize models:

```bash
kalakan-export \
    --acoustic-model /path/to/acoustic_model.pt \
    --vocoder /path/to/vocoder.pt \
    --output-dir /path/to/exported_models \
    --quantize
```

2. Use optimized formats:

```bash
kalakan-export \
    --acoustic-model /path/to/acoustic_model.pt \
    --vocoder /path/to/vocoder.pt \
    --output-dir /path/to/exported_models \
    --format onnx
```

3. Use smaller models:

```python
synthesizer = Synthesizer(
    acoustic_model_type="fastspeech2_small",
    vocoder_type="melgan_small"
)
```

### Batch Processing

1. Implement batch processing:

```python
def process_batch(texts):
    # Synthesize in batch
    audios = synthesizer.synthesize_batch(texts, batch_size=16)
    return audios
```

2. Use a task queue:

```python
from celery import Celery

app = Celery('kalakan', broker='redis://redis:6379/0')

@app.task
def synthesize_task(text):
    audio = synthesizer.synthesize(text)
    # Save audio to a file or database
    return audio_path

# In the API
@app.post("/synthesize/async")
async def synthesize_async(request: Request):
    text = request.json.get("text", "")
    task = synthesize_task.delay(text)
    return {"task_id": task.id}

@app.get("/result/{task_id}")
async def get_result(task_id: str):
    task = synthesize_task.AsyncResult(task_id)
    if task.ready():
        return {"status": "completed", "result": task.result}
    return {"status": "pending"}
```

### Resource Management

1. Limit memory usage:

```python
import torch

# Set maximum memory usage
torch.cuda.set_per_process_memory_fraction(0.8)
```

2. Use CPU offloading:

```python
def synthesize_with_offloading(text):
    # Move models to GPU
    synthesizer.acoustic_model.to("cuda:0")
    
    # Generate mel spectrogram
    with torch.no_grad():
        phonemes = torch.tensor(synthesizer.g2p.text_to_phoneme_sequence(text), dtype=torch.long).unsqueeze(0).to("cuda:0")
        mel, _ = synthesizer.acoustic_model.inference(phonemes)
    
    # Move acoustic model to CPU and vocoder to GPU
    synthesizer.acoustic_model.to("cpu")
    synthesizer.vocoder.to("cuda:0")
    
    # Generate audio
    with torch.no_grad():
        audio = synthesizer.vocoder.inference(mel)
    
    # Move vocoder to CPU
    synthesizer.vocoder.to("cpu")
    
    return audio.squeeze(0)
```

## Troubleshooting

### Common Deployment Issues

#### Container Startup Failures

**Issue**: Docker container fails to start.

**Solution**:
1. Check container logs:
```bash
docker logs <container_id>
```

2. Ensure models are mounted correctly:
```bash
docker run -v /absolute/path/to/models:/models kalakan/kalakan-tts:api
```

3. Check for permission issues:
```bash
chmod -R 755 /path/to/models
```

#### API Timeouts

**Issue**: API requests timeout.

**Solution**:
1. Increase timeout settings:
```bash
# Nginx
location / {
    proxy_pass http://localhost:8000;
    proxy_read_timeout 300s;
}

# Gunicorn
gunicorn -w 4 -t 300 -k uvicorn.workers.UvicornWorker kalakan.api.server:app
```

2. Optimize inference:
```python
synthesizer = Synthesizer(
    acoustic_model_type="fastspeech2",  # Faster model
    vocoder_type="melgan",              # Faster vocoder
    device="cuda:0"                     # Use GPU
)
```

#### Memory Issues

**Issue**: Out of memory errors.

**Solution**:
1. Use model quantization:
```bash
kalakan-export \
    --acoustic-model /path/to/acoustic_model.pt \
    --vocoder /path/to/vocoder.pt \
    --output-dir /path/to/exported_models \
    --quantize
```

2. Increase container memory limits:
```bash
docker run --memory=8g kalakan/kalakan-tts:api
```

3. Use smaller models:
```python
synthesizer = Synthesizer(
    acoustic_model_type="fastspeech2_small",
    vocoder_type="melgan_small"
)
```

### Deployment Checklist

Before deploying to production, ensure:

1. **Models are optimized** for the target environment
2. **Security measures** are in place (authentication, HTTPS, etc.)
3. **Monitoring and logging** are configured
4. **Resource limits** are set appropriately
5. **Scaling strategy** is defined
6. **Backup and recovery** procedures are in place
7. **Performance testing** has been conducted
8. **Documentation** is up-to-date

---

This deployment guide provides comprehensive instructions for deploying the Kalakan TTS system in various production environments. For more detailed information on specific features, refer to the API reference and other documentation in the `docs/` directory.
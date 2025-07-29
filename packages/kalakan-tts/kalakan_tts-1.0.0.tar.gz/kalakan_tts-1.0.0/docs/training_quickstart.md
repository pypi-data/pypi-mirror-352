# Kalakan TTS Training Quick Start Guide

This quick start guide provides the essential steps to train the Kalakan TTS system for Twi language. For more detailed instructions, refer to the comprehensive [Training Guide](training_guide.md).

## Prerequisites

- Python 3.7+
- PyTorch 1.7+
- CUDA-compatible GPU (recommended)
- Twi speech dataset

## Step 1: Install Dependencies

```bash
# Create a virtual environment (optional but recommended)
python -m venv kalakan-env
source kalakan-env/bin/activate  # On Windows: kalakan-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Prepare Your Dataset

### Option A: Use an Existing Dataset

If you have an existing Twi speech dataset:

```bash
# Prepare the dataset
python scripts/prepare_dataset.py \
    --input-dir /path/to/raw/dataset \
    --output-dir data/twi_dataset
```

### Option B: Record a New Dataset

If you need to record a new dataset:

1. Follow the [Twi Dataset Collection Guide](twi_dataset_guide.md)
2. Organize your recordings according to the guide
3. Prepare the dataset as in Option A

## Step 3: Compute Mel Spectrograms

```bash
python scripts/train_tacotron2.py \
    --data-dir data/twi_dataset \
    --output-dir models/tacotron2_twi \
    --compute-mels
```

## Step 4: Train the Acoustic Model

```bash
python scripts/train_tacotron2.py \
    --config configs/models/tacotron2_base.yaml \
    --data-dir data/twi_dataset \
    --output-dir models/tacotron2_twi \
    --batch-size 16 \
    --num-epochs 1000
```

## Step 5: Train a Neural Vocoder (Optional but Recommended)

```bash
python scripts/train_vocoder.py \
    --config configs/models/hifi_gan_base.yaml \
    --data-dir data/twi_dataset \
    --output-dir models/hifi_gan_twi \
    --batch-size 16 \
    --num-epochs 500
```

## Step 6: Test Your Trained Model

```bash
python scripts/synthesize.py \
    --text "Agoo Kalculus, mepa wo kyɛw, wo ho te sɛn?" \
    --acoustic-model models/tacotron2_twi/tacotron2_best.pt \
    --vocoder models/hifi_gan_twi/hifi_gan_best.pt \
    --output output/test.wav
```

## Training Tips

1. **Start Small**: Begin with a subset of your data to verify the pipeline
2. **Monitor Training**: Check loss curves and listen to samples regularly
3. **Adjust Learning Rate**: Decrease if training is unstable, increase if too slow
4. **Save Checkpoints**: Save models every 10-20 epochs
5. **Use Early Stopping**: Stop training when validation loss plateaus
6. **Data Quality**: Focus on data quality over quantity

## Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| Out of memory errors | Reduce batch size or sequence length |
| Slow training | Increase batch size, use mixed precision training |
| Model not converging | Check data quality, adjust learning rate |
| Robotic speech | Train longer, use a neural vocoder |
| Mispronunciations | Improve G2P converter, check phoneme coverage |

## Next Steps

After basic training:

1. **Fine-tune**: Adjust hyperparameters for better quality
2. **Evaluate**: Use objective and subjective metrics
3. **Optimize**: Export to ONNX for faster inference
4. **Expand**: Add more data or train for more dialects

For more advanced techniques and detailed explanations, refer to the comprehensive [Training Guide](training_guide.md) and [Twi Phonology Guide](twi_phonology_guide.md).

---

If you encounter issues, check the troubleshooting section in the main training guide or open an issue on the GitHub repository.
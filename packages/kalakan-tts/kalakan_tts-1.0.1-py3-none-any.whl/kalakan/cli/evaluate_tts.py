#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kalakan TTS Evaluation CLI

This module provides a command-line interface for evaluating TTS models
using the Kalakan framework.
"""

import os
import sys
import argparse
import logging
import json
import datetime
import numpy as np
import torch
import soundfile as sf
import matplotlib.pyplot as plt
from pathlib import Path
from tqdm import tqdm

from kalakan.synthesis.synthesizer import Synthesizer
from kalakan.utils.audio import AudioProcessor
from kalakan.utils.metrics import compute_mcd, compute_f0_metrics
from kalakan.utils.logging import setup_logger

logger = setup_logger("KalakanEvaluation")

def prepare_output_dir(output_dir):
    """Prepare output directory for evaluation results."""
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "samples"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "figures"), exist_ok=True)
    return output_dir

def generate_samples(synthesizer, output_dir, test_sentences):
    """Generate audio samples for subjective evaluation."""
    logger.info("Generating audio samples...")

    samples_dir = os.path.join(output_dir, "samples")
    results = []

    for i, text in enumerate(tqdm(test_sentences, desc="Generating samples")):
        sample_id = f"sample_{i+1:02d}"
        output_path = os.path.join(samples_dir, f"{sample_id}.wav")

        # Measure synthesis time
        import time
        start_time = time.time()
        audio, sr = synthesizer.synthesize(text, output_path, return_audio=True)
        synthesis_time = time.time() - start_time

        # Calculate audio duration
        duration = len(audio) / sr

        # Calculate real-time factor
        rtf = synthesis_time / duration

        results.append({
            "id": sample_id,
            "text": text,
            "audio_path": output_path,
            "duration": duration,
            "synthesis_time": synthesis_time,
            "rtf": rtf
        })

        logger.info(f"Generated sample {i+1}/{len(test_sentences)}: RTF = {rtf:.4f}")

    # Save results to JSON
    with open(os.path.join(output_dir, "synthesis_results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # Calculate average RTF
    avg_rtf = np.mean([r["rtf"] for r in results])
    logger.info(f"Average Real-Time Factor: {avg_rtf:.4f}")

    return results

def compute_objective_metrics(synthesizer, test_data, output_dir):
    """Compute objective metrics for synthesized speech."""
    logger.info("Computing objective metrics...")

    if not test_data or len(test_data) == 0:
        logger.warning("No test data provided for objective evaluation.")
        return {}

    metrics = {
        "mcd": [],
        "f0_rmse": [],
        "f0_corr": [],
        "voicing_error": []
    }

    audio_processor = AudioProcessor(
        sample_rate=22050,
        n_fft=1024,
        hop_length=256,
        win_length=1024,
        n_mels=80,
        mel_fmin=0.0,
        mel_fmax=8000.0
    )

    for item in tqdm(test_data, desc="Computing metrics"):
        # Load reference audio
        ref_audio, sr = sf.read(item["audio_path"])

        # Synthesize audio
        syn_audio, _ = synthesizer.synthesize(item["text"], return_audio=True)

        # Compute MCD
        mcd = compute_mcd(ref_audio, syn_audio, audio_processor)
        metrics["mcd"].append(mcd)

        # Compute F0 metrics
        f0_metrics = compute_f0_metrics(ref_audio, syn_audio, sr)
        metrics["f0_rmse"].append(f0_metrics["f0_rmse"])
        metrics["f0_corr"].append(f0_metrics["f0_corr"])
        metrics["voicing_error"].append(f0_metrics["voicing_error"])

    # Calculate average metrics
    avg_metrics = {
        "mcd": np.mean(metrics["mcd"]),
        "f0_rmse": np.mean(metrics["f0_rmse"]),
        "f0_corr": np.mean(metrics["f0_corr"]),
        "voicing_error": np.mean(metrics["voicing_error"])
    }

    # Save metrics to JSON
    with open(os.path.join(output_dir, "objective_metrics.json"), "w") as f:
        json.dump(avg_metrics, f, indent=2)

    # Plot metrics
    plot_metrics(metrics, output_dir)

    logger.info(f"Average MCD: {avg_metrics['mcd']:.4f} dB")
    logger.info(f"Average F0 RMSE: {avg_metrics['f0_rmse']:.4f} Hz")
    logger.info(f"Average F0 Correlation: {avg_metrics['f0_corr']:.4f}")
    logger.info(f"Average Voicing Error: {avg_metrics['voicing_error']:.4f}%")

    return avg_metrics

def plot_metrics(metrics, output_dir):
    """Plot objective metrics."""
    figures_dir = os.path.join(output_dir, "figures")

    # Plot MCD
    plt.figure(figsize=(10, 6))
    plt.plot(metrics["mcd"], marker='o')
    plt.title("Mel Cepstral Distortion (MCD)")
    plt.xlabel("Sample Index")
    plt.ylabel("MCD (dB)")
    plt.grid(True)
    plt.savefig(os.path.join(figures_dir, "mcd.png"))
    plt.close()

    # Plot F0 RMSE
    plt.figure(figsize=(10, 6))
    plt.plot(metrics["f0_rmse"], marker='o')
    plt.title("F0 Root Mean Square Error")
    plt.xlabel("Sample Index")
    plt.ylabel("RMSE (Hz)")
    plt.grid(True)
    plt.savefig(os.path.join(figures_dir, "f0_rmse.png"))
    plt.close()

    # Plot F0 Correlation
    plt.figure(figsize=(10, 6))
    plt.plot(metrics["f0_corr"], marker='o')
    plt.title("F0 Correlation")
    plt.xlabel("Sample Index")
    plt.ylabel("Correlation")
    plt.grid(True)
    plt.savefig(os.path.join(figures_dir, "f0_corr.png"))
    plt.close()

    # Plot Voicing Error
    plt.figure(figsize=(10, 6))
    plt.plot(metrics["voicing_error"], marker='o')
    plt.title("Voicing Error")
    plt.xlabel("Sample Index")
    plt.ylabel("Error (%)")
    plt.grid(True)
    plt.savefig(os.path.join(figures_dir, "voicing_error.png"))
    plt.close()

def create_html_report(synthesis_results, objective_metrics, output_dir):
    """Create an HTML report with evaluation results."""
    logger.info("Creating HTML report...")

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TTS Model Evaluation Report</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                color: #333;
            }}
            h1, h2, h3 {{
                color: #2c3e50;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            .metrics-container {{
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                margin-bottom: 30px;
            }}
            .metric-card {{
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                flex: 1;
                min-width: 200px;
            }}
            .metric-value {{
                font-size: 24px;
                font-weight: bold;
                color: #3498db;
                margin: 10px 0;
            }}
            .samples-container {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }}
            .sample-card {{
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .sample-text {{
                margin-bottom: 15px;
                font-style: italic;
            }}
            .figures-container {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }}
            .figure-card {{
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .figure-card img {{
                width: 100%;
                border-radius: 4px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                padding: 12px 15px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>TTS Model Evaluation Report</h1>
            <p>Evaluation date: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>

            <h2>Objective Metrics</h2>
            <div class="metrics-container">
                <div class="metric-card">
                    <h3>Mel Cepstral Distortion (MCD)</h3>
                    <div class="metric-value">{objective_metrics.get("mcd", "N/A"):.4f} dB</div>
                    <p>Lower is better. Measures spectral distance between reference and synthesized speech.</p>
                </div>
                <div class="metric-card">
                    <h3>F0 RMSE</h3>
                    <div class="metric-value">{objective_metrics.get("f0_rmse", "N/A"):.4f} Hz</div>
                    <p>Lower is better. Measures pitch accuracy.</p>
                </div>
                <div class="metric-card">
                    <h3>F0 Correlation</h3>
                    <div class="metric-value">{objective_metrics.get("f0_corr", "N/A"):.4f}</div>
                    <p>Higher is better. Measures pitch contour similarity.</p>
                </div>
                <div class="metric-card">
                    <h3>Voicing Error</h3>
                    <div class="metric-value">{objective_metrics.get("voicing_error", "N/A"):.4f}%</div>
                    <p>Lower is better. Measures voiced/unvoiced classification accuracy.</p>
                </div>
            </div>

            <h2>Synthesis Performance</h2>
            <div class="metric-card">
                <h3>Real-Time Factor (RTF)</h3>
                <div class="metric-value">{np.mean([r["rtf"] for r in synthesis_results]):.4f}</div>
                <p>Lower is better. RTF < 1 means faster than real-time synthesis.</p>
            </div>

            <h2>Synthesis Results</h2>
            <table>
                <tr>
                    <th>Sample ID</th>
                    <th>Text</th>
                    <th>Duration (s)</th>
                    <th>Synthesis Time (s)</th>
                    <th>RTF</th>
                </tr>
                {"".join([
                f'<tr><td>{r["id"]}</td><td>{r["text"]}</td><td>{r["duration"]:.2f}</td><td>{r["synthesis_time"]:.2f}</td><td>{r["rtf"]:.4f}</td></tr>'
                for r in synthesis_results])}
            </table>

            <h2>Audio Samples</h2>
            <div class="samples-container">
                {"".join([
                f'<div class="sample-card">'
                f'<h3>Sample {i+1}</h3>'
                f'<div class="sample-text">"{r["text"]}"</div>'
                f'<audio controls style="width: 100%;">'
                f'<source src="samples/{r["id"]}.wav" type="audio/wav">'
                f'Your browser does not support the audio element.'
                f'</audio>'
                f'<p>Duration: {r["duration"]:.2f}s | RTF: {r["rtf"]:.4f}</p>'
                f'</div>'
                for i, r in enumerate(synthesis_results)])}
            </div>

            <h2>Metric Visualizations</h2>
            <div class="figures-container">
                <div class="figure-card">
                    <h3>Mel Cepstral Distortion (MCD)</h3>
                    <img src="figures/mcd.png" alt="MCD Plot">
                </div>
                <div class="figure-card">
                    <h3>F0 Root Mean Square Error</h3>
                    <img src="figures/f0_rmse.png" alt="F0 RMSE Plot">
                </div>
                <div class="figure-card">
                    <h3>F0 Correlation</h3>
                    <img src="figures/f0_corr.png" alt="F0 Correlation Plot">
                </div>
                <div class="figure-card">
                    <h3>Voicing Error</h3>
                    <img src="figures/voicing_error.png" alt="Voicing Error Plot">
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    with open(os.path.join(output_dir, "evaluation_report.html"), "w", encoding="utf-8") as f:
        f.write(html_content)

    logger.info(f"HTML report created at {os.path.join(output_dir, 'evaluation_report.html')}")

def main():
    parser = argparse.ArgumentParser(description="Evaluate a trained TTS model")
    parser.add_argument("--acoustic-model", required=True, help="Path to acoustic model checkpoint")
    parser.add_argument("--vocoder", required=True, help="Path to vocoder checkpoint")
    parser.add_argument("--test-data", help="Path to test data JSON file (for objective metrics)")
    parser.add_argument("--test-sentences", help="Path to file containing test sentences")
    parser.add_argument("--output-dir", default="evaluation_results", help="Directory to save evaluation results")
    args = parser.parse_args()

    # Prepare output directory
    output_dir = prepare_output_dir(args.output_dir)

    # Initialize synthesizer
    logger.info("Initializing synthesizer...")
    synthesizer = Synthesizer(
        acoustic_model=args.acoustic_model,
        vocoder=args.vocoder
    )

    # Load test sentences
    test_sentences = []
    if args.test_sentences:
        with open(args.test_sentences, 'r', encoding='utf-8') as f:
            test_sentences = [line.strip() for line in f if line.strip()]

    # Use default test sentences if none provided
    if not test_sentences:
        test_sentences = [
            "Hello, this is a test sentence for the Kalakan TTS system.",
            "The quick brown fox jumps over the lazy dog.",
            "Kalakan is a powerful text-to-speech framework.",
            "This is a sample of synthesized speech.",
            "Evaluating the quality of text-to-speech systems."
        ]

    # Generate samples
    synthesis_results = generate_samples(synthesizer, output_dir, test_sentences)

    # Compute objective metrics if test data is provided
    objective_metrics = {}
    if args.test_data:
        try:
            with open(args.test_data, "r", encoding="utf-8") as f:
                test_data = json.load(f)
            objective_metrics = compute_objective_metrics(synthesizer, test_data, output_dir)
        except Exception as e:
            logger.error(f"Error computing objective metrics: {str(e)}")

    # Create HTML report
    create_html_report(synthesis_results, objective_metrics, output_dir)

    logger.info(f"Evaluation complete. Results saved to {output_dir}")

if __name__ == "__main__":
    main()
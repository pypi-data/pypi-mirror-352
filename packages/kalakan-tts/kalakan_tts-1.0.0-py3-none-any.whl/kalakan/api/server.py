"""
REST API server for Kalakan TTS.

This module provides a REST API server for Kalakan TTS using FastAPI.
"""

import argparse
import base64
import io
import os
import sys
from typing import Dict, List, Optional, Union

import numpy as np
import torch
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field

from kalakan.synthesis.synthesizer import Synthesizer
from kalakan.utils.device import get_device
from kalakan.utils.logging import setup_logger


# Define API models
class SynthesisRequest(BaseModel):
    """Request model for speech synthesis."""
    
    text: str = Field(..., description="Text to synthesize")
    normalize: bool = Field(False, description="Whether to normalize the text")
    clean: bool = Field(False, description="Whether to clean the text")
    return_format: str = Field("wav", description="Format to return audio in (wav or base64)")


class SynthesisResponse(BaseModel):
    """Response model for speech synthesis."""
    
    audio: Optional[str] = Field(None, description="Base64-encoded audio data (if return_format is base64)")
    message: str = Field("Success", description="Status message")


# Create FastAPI app
app = FastAPI(
    title="Kalakan TTS API",
    description="API for Kalakan Text-to-Speech system",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
synthesizer = None
logger = None
temp_dir = None


@app.on_event("startup")
async def startup_event():
    """Initialize the API server."""
    global synthesizer, logger, temp_dir
    
    # Set up logger
    logger = setup_logger("api")
    
    # Create temporary directory
    temp_dir = os.path.join(os.getcwd(), "temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    # Create synthesizer
    logger.info("Creating synthesizer...")
    
    # Get environment variables
    acoustic_model = os.environ.get("KALAKAN_ACOUSTIC_MODEL")
    vocoder = os.environ.get("KALAKAN_VOCODER")
    device = os.environ.get("KALAKAN_DEVICE")
    
    # Create synthesizer
    synthesizer = Synthesizer(
        acoustic_model=acoustic_model,
        vocoder=vocoder,
        device=get_device(device),
    )
    
    logger.info("API server initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources."""
    global temp_dir
    
    # Clean up temporary directory
    if temp_dir and os.path.exists(temp_dir):
        for file in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, file))


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to Kalakan TTS API"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/synthesize", response_model=SynthesisResponse)
async def synthesize(request: SynthesisRequest):
    """
    Synthesize speech from text.
    
    Args:
        request: Synthesis request.
        
    Returns:
        Synthesis response.
    """
    global synthesizer, logger, temp_dir
    
    if synthesizer is None:
        raise HTTPException(status_code=500, detail="Synthesizer not initialized")
    
    try:
        # Synthesize speech
        logger.info(f"Synthesizing: {request.text}")
        audio = synthesizer.synthesize(
            text=request.text,
            normalize=request.normalize,
            clean=request.clean,
        )
        
        # Return audio based on requested format
        if request.return_format == "base64":
            # Convert to WAV and encode as base64
            buffer = io.BytesIO()
            synthesizer.save_audio(audio, buffer)
            buffer.seek(0)
            audio_base64 = base64.b64encode(buffer.read()).decode("utf-8")
            return SynthesisResponse(audio=audio_base64)
        else:
            # Save to temporary file and return as file response
            output_file = os.path.join(temp_dir, f"synthesized_{id(request)}.wav")
            synthesizer.save_audio(audio, output_file)
            return FileResponse(
                output_file,
                media_type="audio/wav",
                filename="synthesized.wav",
            )
    
    except Exception as e:
        logger.error(f"Error synthesizing speech: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/synthesize_get")
async def synthesize_get(
    text: str = Query(..., description="Text to synthesize"),
    normalize: bool = Query(False, description="Whether to normalize the text"),
    clean: bool = Query(False, description="Whether to clean the text"),
):
    """
    Synthesize speech from text (GET endpoint).
    
    Args:
        text: Text to synthesize.
        normalize: Whether to normalize the text.
        clean: Whether to clean the text.
        
    Returns:
        Audio file response.
    """
    global synthesizer, logger, temp_dir
    
    if synthesizer is None:
        raise HTTPException(status_code=500, detail="Synthesizer not initialized")
    
    try:
        # Synthesize speech
        logger.info(f"Synthesizing: {text}")
        audio = synthesizer.synthesize(
            text=text,
            normalize=normalize,
            clean=clean,
        )
        
        # Save to temporary file and return as file response
        output_file = os.path.join(temp_dir, f"synthesized_{hash(text)}.wav")
        synthesizer.save_audio(audio, output_file)
        return FileResponse(
            output_file,
            media_type="audio/wav",
            filename="synthesized.wav",
        )
    
    except Exception as e:
        logger.error(f"Error synthesizing speech: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def create_app(
    acoustic_model: Optional[str] = None,
    vocoder: Optional[str] = None,
    device: Optional[str] = None,
) -> FastAPI:
    """
    Create a FastAPI app for Kalakan TTS.
    
    Args:
        acoustic_model: Path to acoustic model checkpoint.
        vocoder: Path to vocoder checkpoint.
        device: Device to use for inference.
        
    Returns:
        FastAPI app.
    """
    # Set environment variables
    if acoustic_model is not None:
        os.environ["KALAKAN_ACOUSTIC_MODEL"] = acoustic_model
    if vocoder is not None:
        os.environ["KALAKAN_VOCODER"] = vocoder
    if device is not None:
        os.environ["KALAKAN_DEVICE"] = device
    
    return app


def parse_args():
    #Parse command-line arguments.
    parser = argparse.ArgumentParser(description="Start Kalakan TTS API server")
    
    # Server arguments
    parser.add_argument("--host", type=str, default="0.0.0.0",
                        help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8000,
                        help="Port to bind the server to")
    
    # Model arguments
    parser.add_argument("--acoustic_model", "-a", type=str, default=None,
                        help="Path to acoustic model checkpoint")
    parser.add_argument("--vocoder", "-v", type=str, default=None,
                        help="Path to vocoder checkpoint")
    
    # Device arguments
    parser.add_argument("--device", type=str, default=None,
                        help="Device to use for inference (e.g., 'cuda:0', 'cpu')")
    
    return parser.parse_args()


def main():
    """Main function."""
    # Parse arguments
    args = parse_args()
    
    # Create app
    app = create_app(
        acoustic_model=args.acoustic_model,
        vocoder=args.vocoder,
        device=args.device,
    )
    
    # Start server
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
    )


if __name__ == "__main__":
    main()
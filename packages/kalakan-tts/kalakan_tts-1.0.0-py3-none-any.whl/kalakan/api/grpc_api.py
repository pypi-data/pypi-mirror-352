"""
gRPC API server for Kalakan TTS.

This module provides a gRPC API server for Kalakan TTS.
"""

import argparse
import base64
import io
import os
import sys
import time
from concurrent import futures
from typing import Dict, List, Optional, Union

import grpc
import numpy as np
import torch

from kalakan.synthesis.synthesizer import Synthesizer
from kalakan.utils.device import get_device
from kalakan.utils.logging import setup_logger

# Import generated gRPC code
try:
    from kalakan.api.proto import tts_pb2, tts_pb2_grpc
except ImportError:
    # If the proto files haven't been compiled yet, we'll define a placeholder
    # This allows the module to be imported without errors
    class tts_pb2:
        class SynthesisRequest:
            pass
        
        class SynthesisResponse:
            pass
    
    class tts_pb2_grpc:
        class TTSServicer:
            pass
        
        def add_TTSServicer_to_server(servicer, server):
            pass


class TTSServicer(tts_pb2_grpc.TTSServicer):
    """
    gRPC servicer for Kalakan TTS.
    
    This class implements the gRPC service for Kalakan TTS.
    """
    
    def __init__(
        self,
        acoustic_model: Optional[str] = None,
        vocoder: Optional[str] = None,
        device: Optional[str] = None,
    ):
        """
        Initialize the TTS servicer.
        
        Args:
            acoustic_model: Path to acoustic model checkpoint.
            vocoder: Path to vocoder checkpoint.
            device: Device to use for inference.
        """
        # Set up logger
        self.logger = setup_logger("grpc_api")
        
        # Create synthesizer
        self.logger.info("Creating synthesizer...")
        
        # Get environment variables if not provided
        if acoustic_model is None:
            acoustic_model = os.environ.get("KALAKAN_ACOUSTIC_MODEL")
        if vocoder is None:
            vocoder = os.environ.get("KALAKAN_VOCODER")
        if device is None:
            device = os.environ.get("KALAKAN_DEVICE")
        
        # Create synthesizer
        self.synthesizer = Synthesizer(
            acoustic_model=acoustic_model,
            vocoder=vocoder,
            device=get_device(device),
        )
        
        self.logger.info("TTS servicer initialized")
    
    def Synthesize(self, request, context):
        """
        Synthesize speech from text.
        
        Args:
            request: Synthesis request.
            context: gRPC context.
            
        Returns:
            Synthesis response.
        """
        try:
            # Synthesize speech
            self.logger.info(f"Synthesizing: {request.text}")
            audio = self.synthesizer.synthesize(
                text=request.text,
                normalize=request.normalize,
                clean=request.clean,
            )
            
            # Convert to WAV
            buffer = io.BytesIO()
            self.synthesizer.save_audio(audio, buffer)
            buffer.seek(0)
            audio_data = buffer.read()
            
            # Create response
            response = tts_pb2.SynthesisResponse(
                audio=audio_data,
                sample_rate=self.synthesizer.vocoder.sample_rate,
                message="Success",
            )
            
            return response
        
        except Exception as e:
            self.logger.error(f"Error synthesizing speech: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return tts_pb2.SynthesisResponse(
                audio=b"",
                sample_rate=0,
                message=f"Error: {str(e)}",
            )
    
    def SynthesizeStream(self, request, context):
        """
        Synthesize speech from text and stream the audio.
        
        Args:
            request: Synthesis request.
            context: gRPC context.
            
        Yields:
            Chunks of the synthesis response.
        """
        try:
            # Synthesize speech
            self.logger.info(f"Synthesizing (stream): {request.text}")
            audio = self.synthesizer.synthesize(
                text=request.text,
                normalize=request.normalize,
                clean=request.clean,
            )
            
            # Convert to WAV
            buffer = io.BytesIO()
            self.synthesizer.save_audio(audio, buffer)
            buffer.seek(0)
            audio_data = buffer.read()
            
            # Stream in chunks
            chunk_size = 1024 * 16  # 16 KB chunks
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i:i+chunk_size]
                
                # Create response chunk
                response = tts_pb2.SynthesisResponse(
                    audio=chunk,
                    sample_rate=self.synthesizer.vocoder.sample_rate,
                    message="Success",
                )
                
                yield response
        
        except Exception as e:
            self.logger.error(f"Error synthesizing speech (stream): {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            yield tts_pb2.SynthesisResponse(
                audio=b"",
                sample_rate=0,
                message=f"Error: {str(e)}",
            )


def serve(
    host: str = "0.0.0.0",
    port: int = 50051,
    acoustic_model: Optional[str] = None,
    vocoder: Optional[str] = None,
    device: Optional[str] = None,
    max_workers: int = 10,
):
    """
    Start the gRPC server.
    
    Args:
        host: Host to bind the server to.
        port: Port to bind the server to.
        acoustic_model: Path to acoustic model checkpoint.
        vocoder: Path to vocoder checkpoint.
        device: Device to use for inference.
        max_workers: Maximum number of worker threads.
    """
    # Create server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    
    # Add servicer
    servicer = TTSServicer(
        acoustic_model=acoustic_model,
        vocoder=vocoder,
        device=device,
    )
    tts_pb2_grpc.add_TTSServicer_to_server(servicer, server)
    
    # Start server
    server.add_insecure_port(f"{host}:{port}")
    server.start()
    
    print(f"Server started on {host}:{port}")
    
    try:
        while True:
            time.sleep(86400)  # Sleep for a day
    except KeyboardInterrupt:
        server.stop(0)


def parse_args():
    #Parse command-line arguments.
    parser = argparse.ArgumentParser(description="Start Kalakan TTS gRPC server")
    
    # Server arguments
    parser.add_argument("--host", type=str, default="0.0.0.0",
                        help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=50051,
                        help="Port to bind the server to")
    
    # Model arguments
    parser.add_argument("--acoustic_model", "-a", type=str, default=None,
                        help="Path to acoustic model checkpoint")
    parser.add_argument("--vocoder", "-v", type=str, default=None,
                        help="Path to vocoder checkpoint")
    
    # Device arguments
    parser.add_argument("--device", type=str, default=None,
                        help="Device to use for inference (e.g., 'cuda:0', 'cpu')")
    
    # Server arguments
    parser.add_argument("--max_workers", type=int, default=10,
                        help="Maximum number of worker threads")
    
    return parser.parse_args()


def main():
    """Main function."""
    # Parse arguments
    args = parse_args()
    
    # Start server
    serve(
        host=args.host,
        port=args.port,
        acoustic_model=args.acoustic_model,
        vocoder=args.vocoder,
        device=args.device,
        max_workers=args.max_workers,
    )


if __name__ == "__main__":
    main()
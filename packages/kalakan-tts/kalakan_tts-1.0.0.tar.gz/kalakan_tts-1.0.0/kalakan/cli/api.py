"""
API CLI for Kalakan TTS.
This module provides a command-line interface for starting the Kalakan TTS API.
"""

import argparse
import os
import sys
from typing import Optional

from kalakan.utils.logging import setup_logger


def add_api_args(parser):
    """Add API arguments to the parser."""
    # Server arguments
    parser.add_argument("--host", type=str, default="0.0.0.0",
                        help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8000,
                        help="Port to bind the server to")

    # API type arguments
    parser.add_argument("--api_type", type=str, default="rest",
                        choices=["rest", "grpc"],
                        help="Type of API to start")

    # Model arguments
    parser.add_argument("--acoustic_model", "-a", type=str, default=None,
                        help="Path to acoustic model checkpoint or model name")
    parser.add_argument("--vocoder", "-v", type=str, default=None,
                        help="Path to vocoder checkpoint or model name")

    # Device arguments
    parser.add_argument("--device", type=str, default=None,
                        help="Device to use for inference (e.g., 'cuda:0', 'cpu')")

    # Server arguments
    parser.add_argument("--max_workers", type=int, default=10,
                        help="Maximum number of worker threads (for gRPC)")


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Kalakan TTS API")
    add_api_args(parser)
    return parser.parse_args()


def main(args=None):
    """Main function."""
    # Parse arguments if not provided
    if args is None:
        args = parse_args()

    # Set up logger
    logger = setup_logger("api")

    # Set environment variables
    if args.acoustic_model is not None:
        os.environ["KALAKAN_ACOUSTIC_MODEL"] = args.acoustic_model
    if args.vocoder is not None:
        os.environ["KALAKAN_VOCODER"] = args.vocoder
    if args.device is not None:
        os.environ["KALAKAN_DEVICE"] = args.device

    # Start API server
    if args.api_type == "rest":
        # Import REST API server
        from kalakan.api.server import create_app
        import uvicorn

        # Create app
        app = create_app(
            acoustic_model=args.acoustic_model,
            vocoder=args.vocoder,
            device=args.device,
        )

        # Start server
        logger.info(f"Starting REST API server on {args.host}:{args.port}")
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
        )
    else:
        # Import gRPC API server
        from kalakan.api.grpc_api import serve

        # Start server
        logger.info(f"Starting gRPC API server on {args.host}:{args.port}")
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
import argparse
from PIL import Image
import cv2
import numpy as np
from pathlib import Path
import logging
import torch
from transparent_background import Remover

# Set up logging to show only INFO and above
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Check available devices
CUDA_AVAILABLE = torch.cuda.is_available()
MPS_AVAILABLE = hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()
DEVICE = 'cuda' if CUDA_AVAILABLE else ('mps' if MPS_AVAILABLE else 'cpu')

# Initialize models
logger.info(f"Initializing models on device: {DEVICE}")
inspyrenet_model = Remover()
inspyrenet_model.model.cpu()

def process_image(input_path, output_path):
    """Process a single image file"""
    try:
        logger.info(f"Processing image: {input_path}")
        # Load and process image
        input_img = Image.open(input_path).convert('RGB')

        if DEVICE != 'cpu':
            inspyrenet_model.model.to(DEVICE)
            try:
                result = inspyrenet_model.process(input_img, type='rgba')
            finally:
                inspyrenet_model.model.to('cpu')
        else:
            result = inspyrenet_model.process(input_img, type='rgba')

        if CUDA_AVAILABLE:
            torch.cuda.empty_cache()

        # Save result
        result.save(output_path)
        logger.info(f"Successfully saved processed image to: {output_path}")
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise

def process_video(input_path, output_path, mask_only=False):
    """Process a video file frame by frame"""
    try:
        logger.info(f"Processing video: {input_path}")
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            raise ValueError("Could not open video file")

        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        logger.info(f"Video properties: {width}x{height} @ {fps}fps, {total_frames} frames")

        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Convert frame to PIL Image
            frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
            # Process frame
            if DEVICE != 'cpu':
                inspyrenet_model.model.to(DEVICE)
                try:
                    processed = inspyrenet_model.process(frame_pil, type='rgba')
                finally:
                    inspyrenet_model.model.to('cpu')
            else:
                processed = inspyrenet_model.process(frame_pil, type='rgba')
            
            if mask_only:
                # Extract alpha channel as mask
                mask = np.array(processed.split()[-1])
                processed_frame = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
            else:
                # Convert back to OpenCV format
                processed_frame = cv2.cvtColor(np.array(processed), cv2.COLOR_RGBA2BGR)

            out.write(processed_frame)
            
            frame_count += 1
            if frame_count % 30 == 0:  # Update progress less frequently
                progress = (frame_count / total_frames) * 100
                logger.info(f"Progress: {progress:.1f}% ({frame_count}/{total_frames} frames)")

            if CUDA_AVAILABLE:
                torch.cuda.empty_cache()

        cap.release()
        out.release()
        logger.info(f"Successfully saved processed video to: {output_path}")

    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description="RemoveBG CLI tool using InSPyReNet model")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Image processing command
    img_parser = subparsers.add_parser("image", help="Process a single image")
    img_parser.add_argument("-i", "--input", required=True, help="Input image path")
    img_parser.add_argument("-o", "--output", required=True, help="Output image path")

    # Video processing command
    video_parser = subparsers.add_parser("video", help="Process a video file")
    video_parser.add_argument("-i", "--input", required=True, help="Input video path")
    video_parser.add_argument("-o", "--output", required=True, help="Output video path")
    video_parser.add_argument("-mk", "--mask", action="store_true", help="Output mask only")

    args = parser.parse_args()

    try:
        if args.command == "image":
            process_image(args.input, args.output)
        elif args.command == "video":
            process_video(args.input, args.output, args.mask)
        else:
            parser.print_help()
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 
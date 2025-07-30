"""
Video utilities for reading and writing video files, extracting frames, and assembling videos.
This module isolates video I/O logic from the rest of the pipeline.
"""

import cv2
import numpy as np
from typing import Generator, List, Tuple, Optional
from pathlib import Path


def extract_frames(video_path: str) -> Generator[np.ndarray, None, None]:
    """
    Extract frames from a video file.
    
    Args:
        video_path: Path to the input video file
        
    Yields:
        numpy arrays representing each frame (BGR format)
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            yield frame
    finally:
        cap.release()


def get_video_info(video_path: str) -> Tuple[int, float, Tuple[int, int]]:
    """
    Get video metadata.
    
    Args:
        video_path: Path to the video file
        
    Returns:
        Tuple of (frame_count, fps, (width, height))
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")
    
    try:
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return frame_count, fps, (width, height)
    finally:
        cap.release()


def assemble_video(frames: List[np.ndarray], output_path: str, fps: float) -> str:
    """
    Assemble frames into a video file.
    
    Args:
        frames: List of frame arrays (BGR format)
        output_path: Path for the output video file
        fps: Frames per second for the output video
        
    Returns:
        Path to the created video file
    """
    if not frames:
        raise ValueError("No frames provided for video assembly")
    
    # Get frame dimensions from first frame
    height, width = frames[0].shape[:2]
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    if not out.isOpened():
        raise ValueError(f"Could not create video writer for: {output_path}")
    
    try:
        for frame in frames:
            out.write(frame)
        return output_path
    finally:
        out.release()


def resize_frame(frame: np.ndarray, size: Optional[Tuple[int, int]] = None, 
                 max_dimension: Optional[int] = None) -> np.ndarray:
    """
    Resize a frame to specified dimensions.
    
    Args:
        frame: Input frame array
        size: Target (width, height) if provided
        max_dimension: Max dimension to constrain to while maintaining aspect ratio
        
    Returns:
        Resized frame
    """
    if size is not None:
        return cv2.resize(frame, size)
    
    if max_dimension is not None:
        h, w = frame.shape[:2]
        if max(h, w) > max_dimension:
            scale = max_dimension / max(h, w)
            new_w = int(w * scale)
            new_h = int(h * scale)
            return cv2.resize(frame, (new_w, new_h))
    
    return frame


def frames_to_video_buffer(frames: List[np.ndarray], fps: float) -> bytes:
    """
    Convert frames to video buffer in memory (useful for Gradio).
    
    Args:
        frames: List of frame arrays
        fps: Frames per second
        
    Returns:
        Video data as bytes
    """
    import tempfile
    import os
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # Write video to temp file
        assemble_video(frames, tmp_path, fps)
        
        # Read back as bytes
        with open(tmp_path, 'rb') as f:
            video_data = f.read()
        
        return video_data
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path) 
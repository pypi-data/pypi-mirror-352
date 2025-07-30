"""
Professional WebRTC handler for real-time video streaming and movement analysis
Using FastRTC (the current WebRTC standard, replaces deprecated gradio-webrtc)
Based on: https://fastrtc.org and https://www.gradio.app/guides/object-detection-from-webcam-with-webrtc
"""

import cv2
import numpy as np
from typing import Optional, Dict, Any, Tuple
from collections import deque
import time
import logging
import os

from .pose_estimation import get_pose_estimator
from .notation_engine import MovementAnalyzer
from .visualizer import PoseVisualizer

logger = logging.getLogger(__name__)

# Official Gradio WebRTC approach (compatible with NumPy 1.x)
try:
    from gradio_webrtc import WebRTC
    HAS_WEBRTC_COMPONENT = True
except ImportError:
    HAS_WEBRTC_COMPONENT = False


class RealtimeMovementAnalyzer:
    """Real-time movement analyzer for WebRTC streams following Gradio 5 best practices"""
    
    # Gradio component compatibility
    events = {}
    
    def __init__(self, model: str = "mediapipe-lite", buffer_size: int = 30):
        """
        Initialize real-time movement analyzer.
        
        Args:
            model: Pose estimation model optimized for real-time processing
            buffer_size: Number of frames to buffer for analysis
        """
        self.model = model
        self.pose_estimator = get_pose_estimator(model)
        self.movement_analyzer = MovementAnalyzer(fps=30.0)
        self.visualizer = PoseVisualizer(
            trail_length=10,
            show_skeleton=True,
            show_trails=True,
            show_direction_arrows=True,
            show_metrics=True
        )
        
        # Real-time buffers
        self.pose_buffer = deque(maxlen=buffer_size)
        self.metrics_buffer = deque(maxlen=buffer_size)
        
        # Performance tracking
        self.frame_count = 0
        self.last_fps_update = time.time()
        self.current_fps = 0.0
        
        # Current metrics for display
        self.current_metrics = {
            "direction": "stationary",
            "intensity": "low",
            "fluidity": 0.0,
            "expansion": 0.5,
            "fps": 0.0
        }
    
    def process_frame(self, image: np.ndarray, conf_threshold: float = 0.5) -> np.ndarray:
        """
        Process a single frame from WebRTC stream for real-time movement analysis.
        
        Args:
            image: Input frame from webcam as numpy array (RGB format from WebRTC)
            conf_threshold: Confidence threshold for pose detection
            
        Returns:
            Processed frame with pose overlay and movement metrics
        """
        if image is None:
            return None
        
        # Convert RGB to BGR for OpenCV processing
        frame_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # Update frame count and FPS
        self.frame_count += 1
        current_time = time.time()
        if current_time - self.last_fps_update >= 1.0:
            self.current_fps = self.frame_count / (current_time - self.last_fps_update)
            self.frame_count = 0
            self.last_fps_update = current_time
            self.current_metrics["fps"] = self.current_fps
        
        # Pose detection
        pose_results = self.pose_estimator.detect(frame_bgr)
        
        # Store pose data
        self.pose_buffer.append(pose_results)
        
        # Calculate movement metrics if we have enough frames
        if len(self.pose_buffer) >= 2:
            recent_poses = list(self.pose_buffer)[-10:]  # Last 10 frames for analysis
            
            try:
                # Analyze movement from recent poses
                movement_metrics = self.movement_analyzer.analyze_movement(recent_poses)
                
                if movement_metrics:
                    latest_metrics = movement_metrics[-1]
                    self.current_metrics.update({
                        "direction": latest_metrics.direction.value if latest_metrics.direction else "stationary",
                        "intensity": latest_metrics.intensity.value if latest_metrics.intensity else "low", 
                        "fluidity": latest_metrics.fluidity if latest_metrics.fluidity is not None else 0.0,
                        "expansion": latest_metrics.expansion if latest_metrics.expansion is not None else 0.5
                    })
                    
                    self.metrics_buffer.append(self.current_metrics.copy())
                    
            except Exception as e:
                logger.warning(f"Movement analysis error: {e}")
        
        # Apply visualization overlays
        output_frame = self._apply_visualization(frame_bgr, pose_results, self.current_metrics)
        
        # Convert back to RGB for WebRTC output
        output_rgb = cv2.cvtColor(output_frame, cv2.COLOR_BGR2RGB)
        
        return output_rgb
    
    def _apply_visualization(self, frame: np.ndarray, pose_results: list, metrics: dict) -> np.ndarray:
        """Apply pose and movement visualization overlays"""
        output_frame = frame.copy()
        
        # Draw pose skeleton if detected
        if pose_results:
            for pose_result in pose_results:
                # Draw skeleton
                if hasattr(self.visualizer, 'draw_skeleton'):
                    output_frame = self.visualizer.draw_skeleton(output_frame, pose_result.keypoints)
                
                # Draw keypoints
                for keypoint in pose_result.keypoints:
                    if keypoint.confidence > 0.5:
                        x = int(keypoint.x * frame.shape[1])
                        y = int(keypoint.y * frame.shape[0])
                        cv2.circle(output_frame, (x, y), 5, (0, 255, 0), -1)
        
        # Draw real-time metrics overlay
        self._draw_metrics_overlay(output_frame, metrics)
        
        return output_frame
    
    def _draw_metrics_overlay(self, frame: np.ndarray, metrics: dict):
        """Draw real-time metrics overlay following professional UI standards"""
        h, w = frame.shape[:2]
        
        # Semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (320, 160), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
        
        # Header
        cv2.putText(frame, "Real-time Movement Analysis", (20, 35), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Metrics
        y_offset = 60
        spacing = 22
        
        cv2.putText(frame, f"Direction: {metrics['direction']}", 
                   (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        y_offset += spacing
        
        cv2.putText(frame, f"Intensity: {metrics['intensity']}", 
                   (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        y_offset += spacing
        
        cv2.putText(frame, f"Fluidity: {metrics['fluidity']:.2f}", 
                   (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        y_offset += spacing
        
        cv2.putText(frame, f"FPS: {metrics['fps']:.1f}", 
                   (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
    
    def get_current_metrics(self) -> dict:
        """Get current movement metrics for external display"""
        return self.current_metrics.copy()


def get_rtc_configuration():
    """
    Get RTC configuration for WebRTC.
    Uses Twilio TURN servers if credentials are available, otherwise uses default.
    """
    # For local development, no TURN servers needed
    # For cloud deployment, set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN
    
    twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    
    if twilio_account_sid and twilio_auth_token:
        # Use Twilio TURN servers for cloud deployment
        return {
            "iceServers": [
                {"urls": ["stun:global.stun.twilio.com:3478"]},
                {
                    "urls": ["turn:global.turn.twilio.com:3478?transport=udp"],
                    "username": twilio_account_sid,
                    "credential": twilio_auth_token,
                },
                {
                    "urls": ["turn:global.turn.twilio.com:3478?transport=tcp"],
                    "username": twilio_account_sid, 
                    "credential": twilio_auth_token,
                },
            ]
        }
    else:
        # Default configuration for local development
        return {
            "iceServers": [
                {"urls": ["stun:stun.l.google.com:19302"]}
            ]
        }


# Global analyzer instance for demo
_analyzer = None

def get_analyzer(model: str = "mediapipe-lite") -> RealtimeMovementAnalyzer:
    """Get or create analyzer instance"""
    global _analyzer
    if _analyzer is None or _analyzer.model != model:
        _analyzer = RealtimeMovementAnalyzer(model)
    return _analyzer


def webrtc_detection(image: np.ndarray, model: str, conf_threshold: float = 0.5) -> np.ndarray:
    """
    Main detection function for WebRTC streaming.
    Compatible with Gradio 5 WebRTC streaming API.
    
    Args:
        image: Input frame from webcam (RGB format)
        model: Pose estimation model name
        conf_threshold: Confidence threshold for pose detection
        
    Returns:
        Processed frame with pose overlay and metrics
    """
    analyzer = get_analyzer(model)
    return analyzer.process_frame(image, conf_threshold)


def get_webrtc_interface():
    """
    Create streaming interface using built-in Gradio components.
    Avoids NumPy 2.x dependency conflicts with FastRTC.
    
    Returns:
        Tuple of (streaming_config, rtc_configuration)
    """
    rtc_config = get_rtc_configuration()
    
    # Use built-in Gradio streaming capabilities
    streaming_config = {
        "sources": ["webcam"],
        "streaming": True,
        "mirror_webcam": False
    }
    
    return streaming_config, rtc_config


# Compatibility exports with Gradio component attributes
class WebRTCMovementAnalyzer(RealtimeMovementAnalyzer):
    """Real-time movement analyzer for WebRTC streams following Gradio 5 best practices"""
    events = {}  # Gradio component compatibility


class WebRTCGradioInterface:
    """Create streaming interface using built-in Gradio components.
    Avoids NumPy 2.x dependency conflicts with FastRTC."""
    
    events = {}  # Gradio component compatibility
    
    @staticmethod
    def get_config():
        return get_webrtc_interface() 
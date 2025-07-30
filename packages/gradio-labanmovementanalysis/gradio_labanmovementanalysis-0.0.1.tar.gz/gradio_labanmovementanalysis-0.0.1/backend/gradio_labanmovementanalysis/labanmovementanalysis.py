"""
Custom Gradio v5 component for video-based pose analysis with LMA-inspired metrics.
"""

import gradio as gr
from gradio.components.base import Component
from typing import Dict, Any, Optional, Tuple, List, Union
import tempfile
import os
import numpy as np

from .video_utils import extract_frames, get_video_info
from .pose_estimation import get_pose_estimator
from .notation_engine import analyze_pose_sequence
from .json_generator import generate_json, format_for_display
from .visualizer import PoseVisualizer
from .video_downloader import SmartVideoInput

# Advanced features reserved for Version 2
# SkateFormer AI integration will be available in future release

try:
    from .webrtc_handler import WebRTCMovementAnalyzer, WebRTCGradioInterface
    HAS_WEBRTC = True
except ImportError:
    HAS_WEBRTC = False


# SkateFormerCompatibility class removed for Version 1 stability
# Will be reimplemented in Version 2 with enhanced AI features


class LabanMovementAnalysis(Component):
    """
    Gradio component for video-based pose analysis with Laban Movement Analysis metrics.
    """
    
    # Component metadata
    COMPONENT_TYPE = "composite"
    DEFAULT_MODEL = "mediapipe"
    
    def __init__(self,
                 default_model: str = DEFAULT_MODEL,
                 enable_visualization: bool = True,
                 include_keypoints: bool = False,
                 enable_webrtc: bool = False,
                 label: Optional[str] = None,
                 every: Optional[float] = None,
                 show_label: Optional[bool] = None,
                 container: bool = True,
                 scale: Optional[int] = None,
                 min_width: int = 160,
                 interactive: Optional[bool] = None,
                 visible: bool = True,
                 elem_id: Optional[str] = None,
                 elem_classes: Optional[List[str]] = None,
                 render: bool = True,
                 **kwargs):
        """
        Initialize the Laban Movement Analysis component.
        
        Args:
            default_model: Default pose estimation model ("mediapipe", "movenet", "yolo")
            enable_visualization: Whether to generate visualization video by default
            include_keypoints: Whether to include raw keypoints in JSON output
            enable_webrtc: Whether to enable WebRTC real-time analysis
            label: Component label
            ... (other standard Gradio component args)
        """
        super().__init__(
            label=label,
            every=every,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            **kwargs
        )
        
        self.default_model = default_model
        self.enable_visualization = enable_visualization
        self.include_keypoints = include_keypoints
        self.enable_webrtc = enable_webrtc and HAS_WEBRTC
        
        # Cache for pose estimators
        self._estimators = {}
        
        # Video input handler for URLs
        self.video_input = SmartVideoInput()
        
        # SkateFormer features reserved for Version 2
        
        self.webrtc_analyzer = None
        if self.enable_webrtc:
            try:
                self.webrtc_analyzer = WebRTCMovementAnalyzer(model=default_model)
            except Exception as e:
                print(f"Warning: Failed to initialize WebRTC: {e}")
                self.enable_webrtc = False
    
    def preprocess(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess input from the frontend.
        
        Args:
            payload: Input data containing video file and options
            
        Returns:
            Processed data for analysis
        """
        if not payload:
            return None
            
        # Extract video file path
        video_data = payload.get("video")
        if not video_data:
            return None
            
        # Handle different input formats
        if isinstance(video_data, str):
            video_path = video_data
        elif isinstance(video_data, dict):
            video_path = video_data.get("path") or video_data.get("name")
        else:
            # Assume it's a file object
            video_path = video_data.name if hasattr(video_data, "name") else str(video_data)
        
        # Extract options
        options = {
            "video_path": video_path,
            "model": payload.get("model", self.default_model),
            "enable_visualization": payload.get("enable_visualization", self.enable_visualization),
            "include_keypoints": payload.get("include_keypoints", self.include_keypoints)
        }
        
        return options
    
    def postprocess(self, value: Any) -> Dict[str, Any]:
        """
        Postprocess analysis results for the frontend.
        
        Args:
            value: Analysis results
            
        Returns:
            Formatted output for display
        """
        if value is None:
            return {"json_output": {}, "video_output": None}
        
        # Ensure we have the expected format
        if isinstance(value, tuple) and len(value) == 2:
            json_data, video_path = value
        else:
            json_data = value
            video_path = None
        
        return {
            "json_output": json_data,
            "video_output": video_path
        }
    
    def process_video(self, video_input: Union[str, os.PathLike], model: str = DEFAULT_MODEL,
                     enable_visualization: bool = True,
                     include_keypoints: bool = False) -> Tuple[Dict[str, Any], Optional[str]]:
        """
        Main processing function that performs pose analysis on a video.
        
        Args:
            video_input: Path to input video, video URL (YouTube/Vimeo), or file object
            model: Pose estimation model to use (supports enhanced syntax like "yolo-v11-s")
            enable_visualization: Whether to generate visualization video
            include_keypoints: Whether to include keypoints in JSON
            
        Returns:
            Tuple of (analysis_json, visualization_video_path)
        """
        # Handle video input (local file, URL, etc.)
        try:
            video_path, video_metadata = self.video_input.process_input(str(video_input))
            print(f"Processing video: {video_metadata.get('title', 'Unknown')}")
            if video_metadata.get('platform') in ['youtube', 'vimeo']:
                print(f"Downloaded from {video_metadata['platform']}")
        except Exception as e:
            raise ValueError(f"Failed to process video input: {str(e)}")
        # Get video metadata
        frame_count, fps, (width, height) = get_video_info(video_path)
        
        # Create or get pose estimator
        if model not in self._estimators:
            self._estimators[model] = get_pose_estimator(model)
        estimator = self._estimators[model]
        
        # Process video frame by frame
        print(f"Processing {frame_count} frames with {model} model...")
        
        all_frames = []
        all_pose_results = []
        
        for i, frame in enumerate(extract_frames(video_path)):
            # Store frame if visualization is needed
            if enable_visualization:
                all_frames.append(frame)
            
            # Detect poses
            pose_results = estimator.detect(frame)
            
            # Update frame indices
            for result in pose_results:
                result.frame_index = i
            
            all_pose_results.append(pose_results)
            
            # Progress indicator
            if i % 30 == 0:
                print(f"Processed {i}/{frame_count} frames...")
        
        print("Analyzing movement patterns...")
        
        # Analyze movement
        movement_metrics = analyze_pose_sequence(all_pose_results, fps=fps)
        
        # Enhanced AI analysis reserved for Version 2
        print("LMA analysis complete - advanced AI features coming in Version 2!")
        
        # Generate JSON output
        video_metadata = {
            "fps": fps,
            "width": width,
            "height": height,
            "frame_count": frame_count,
            "model_info": {
                "name": model,
                "type": "pose_estimation"
            },
            "input_metadata": video_metadata  # Include video source metadata
        }
        
        json_output = generate_json(
            movement_metrics,
            all_pose_results if include_keypoints else None,
            video_metadata,
            include_keypoints=include_keypoints
        )
        
        # Enhanced AI analysis will be added in Version 2
        
        # Generate visualization if requested
        visualization_path = None
        if enable_visualization:
            print("Generating visualization video...")
            
            # Create temporary output file
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
                visualization_path = tmp.name
            
            # Create visualizer
            visualizer = PoseVisualizer(
                show_trails=True,
                show_skeleton=True,
                show_direction_arrows=True,
                show_metrics=True
            )
            
            # Generate overlay video
            visualization_path = visualizer.generate_overlay_video(
                all_frames,
                all_pose_results,
                movement_metrics,
                visualization_path,
                fps
            )
            
            print(f"Visualization saved to: {visualization_path}")
        
        return json_output, visualization_path
    
    def __call__(self, video_path: str, **kwargs) -> Tuple[Dict[str, Any], Optional[str]]:
        """
        Make the component callable for easy use.
        
        Args:
            video_path: Path to video file
            **kwargs: Additional options
            
        Returns:
            Analysis results
        """
        return self.process_video(video_path, **kwargs)
    
    def start_webrtc_stream(self, model: str = None) -> bool:
        """
        Start WebRTC real-time analysis stream.
        
        Args:
            model: Pose model to use for real-time analysis
            
        Returns:
            True if stream started successfully
        """
        if not self.enable_webrtc or not self.webrtc_analyzer:
            print("WebRTC not enabled or available")
            return False
            
        try:
            if model:
                self.webrtc_analyzer.model = model
                self.webrtc_analyzer.pose_estimator = get_pose_estimator(model)
            
            self.webrtc_analyzer.start_stream()
            print(f"WebRTC stream started with {self.webrtc_analyzer.model} model")
            return True
        except Exception as e:
            print(f"Failed to start WebRTC stream: {e}")
            return False
    
    def stop_webrtc_stream(self) -> bool:
        """
        Stop WebRTC real-time analysis stream.
        
        Returns:
            True if stream stopped successfully
        """
        if not self.webrtc_analyzer:
            return False
            
        try:
            self.webrtc_analyzer.stop_stream()
            print("WebRTC stream stopped")
            return True
        except Exception as e:
            print(f"Failed to stop WebRTC stream: {e}")
            return False
    
    def get_webrtc_interface(self):
        """
        Get WebRTC Gradio interface for real-time streaming.
        
        Returns:
            WebRTCGradioInterface instance or None
        """
        if not self.enable_webrtc or not self.webrtc_analyzer:
            return None
            
        return WebRTCGradioInterface(self.webrtc_analyzer)
    
    # SkateFormer methods moved to Version 2 development
    # get_skateformer_compatibility() and get_skateformer_status_report() 
    # will be available in the next major release
    
    def cleanup(self):
        """Clean up temporary files and resources."""
        # Clean up video input handler
        if hasattr(self, 'video_input'):
            self.video_input.cleanup()
        
        # Stop WebRTC if running
        if self.webrtc_analyzer and self.webrtc_analyzer.is_running:
            self.stop_webrtc_stream()
    
    def example_payload(self) -> Dict[str, Any]:
        """Example input payload for documentation."""
        return {
            "video": {"path": "/path/to/video.mp4"},
            "model": "mediapipe",
            "enable_visualization": True,
            "include_keypoints": False
        }
    
    def example_value(self) -> Dict[str, Any]:
        """Example output value for documentation."""
        return {
            "json_output": {
                "analysis_metadata": {
                    "timestamp": "2024-01-01T00:00:00",
                    "version": "1.0.0",
                    "model_info": {"name": "mediapipe", "type": "pose_estimation"}
                },
                "video_info": {
                    "fps": 30.0,
                    "duration_seconds": 5.0,
                    "width": 1920,
                    "height": 1080,
                    "frame_count": 150
                },
                "movement_analysis": {
                    "frame_count": 150,
                    "frames": [
                        {
                            "frame_index": 0,
                            "timestamp": 0.0,
                            "metrics": {
                                "direction": "stationary",
                                "intensity": "low",
                                "speed": "slow",
                                "velocity": 0.0,
                                "acceleration": 0.0,
                                "fluidity": 1.0,
                                "expansion": 0.5
                            }
                        }
                    ],
                    "summary": {
                        "direction": {
                            "distribution": {"stationary": 50, "up": 30, "down": 20},
                            "dominant": "stationary"
                        },
                        "intensity": {
                            "distribution": {"low": 80, "medium": 15, "high": 5},
                            "dominant": "low"
                        }
                    }
                }
            },
            "video_output": "/tmp/visualization.mp4"
        }
    
    def api_info(self) -> Dict[str, Any]:
        """API information for the component."""
        return {
            "type": "composite",
            "description": "Video-based pose analysis with Laban Movement Analysis metrics",
            "parameters": {
                "video": {"type": "file", "description": "Input video file or URL (YouTube/Vimeo)"},
                "model": {"type": "string", "description": "Pose model: mediapipe, movenet, or yolo variants"},
                "enable_visualization": {"type": "boolean", "description": "Generate visualization video"},
                "include_keypoints": {"type": "boolean", "description": "Include keypoints in JSON"}
            },
            "returns": {
                "json_output": {"type": "object", "description": "LMA analysis results"},
                "video_output": {"type": "file", "description": "Visualization video (optional)"}
            },
            "version_2_preview": {
                "planned_features": ["SkateFormer AI integration", "Enhanced movement recognition", "Real-time analysis"],
                "note": "Advanced AI features coming in Version 2!"
            }
        }

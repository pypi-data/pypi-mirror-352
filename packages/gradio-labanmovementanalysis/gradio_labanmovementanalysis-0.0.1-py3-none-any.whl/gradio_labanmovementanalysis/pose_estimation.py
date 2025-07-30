"""
Model-agnostic pose estimation interface with adapters for various pose detection models.
Each adapter provides a uniform interface for pose estimation, abstracting model-specific details.
"""

from abc import ABC, abstractmethod
import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass


@dataclass
class Keypoint:
    """Represents a single pose keypoint."""
    x: float  # Normalized x coordinate (0-1)
    y: float  # Normalized y coordinate (0-1)
    confidence: float  # Confidence score (0-1)
    name: Optional[str] = None  # Joint name (e.g., "left_shoulder")


@dataclass
class PoseResult:
    """Result of pose estimation for a single frame."""
    keypoints: List[Keypoint]
    frame_index: int
    timestamp: Optional[float] = None
    person_id: Optional[int] = None  # For multi-person tracking


class PoseEstimator(ABC):
    """Abstract base class for pose estimation models."""
    
    @abstractmethod
    def detect(self, frame: np.ndarray) -> List[PoseResult]:
        """
        Detect poses in a single frame.
        
        Args:
            frame: Input frame as numpy array (BGR format)
            
        Returns:
            List of PoseResult objects (one per detected person)
        """
        pass
    
    @abstractmethod
    def get_keypoint_names(self) -> List[str]:
        """Get the list of keypoint names this model provides."""
        pass
    
    def detect_batch(self, frames: List[np.ndarray]) -> List[List[PoseResult]]:
        """
        Process multiple frames (default implementation processes sequentially).
        
        Args:
            frames: List of frames
            
        Returns:
            List of results per frame
        """
        results = []
        for i, frame in enumerate(frames):
            frame_results = self.detect(frame)
            # Update frame indices
            for result in frame_results:
                result.frame_index = i
            results.append(frame_results)
        return results


class MoveNetPoseEstimator(PoseEstimator):
    """MoveNet pose estimation adapter (TensorFlow-based)."""
    
    # COCO keypoint names used by MoveNet
    KEYPOINT_NAMES = [
        "nose", "left_eye", "right_eye", "left_ear", "right_ear",
        "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
        "left_wrist", "right_wrist", "left_hip", "right_hip",
        "left_knee", "right_knee", "left_ankle", "right_ankle"
    ]
    
    def __init__(self, model_variant: str = "lightning"):
        """
        Initialize MoveNet model.
        
        Args:
            model_variant: "lightning" (faster) or "thunder" (more accurate)
        """
        self.model_variant = model_variant
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load MoveNet model using TensorFlow."""
        try:
            import tensorflow as tf
            import tensorflow_hub as hub
            
            # Model URLs for different variants
            model_urls = {
                "lightning": "https://tfhub.dev/google/movenet/singlepose/lightning/4",
                "thunder": "https://tfhub.dev/google/movenet/singlepose/thunder/4"
            }
            
            self.model = hub.load(model_urls[self.model_variant])
            self.movenet = self.model.signatures['serving_default']
            
        except ImportError:
            raise ImportError("TensorFlow and tensorflow_hub required for MoveNet. "
                            "Install with: pip install tensorflow tensorflow_hub")
    
    def detect(self, frame: np.ndarray) -> List[PoseResult]:
        """Detect pose using MoveNet."""
        if self.model is None:
            self._load_model()
        
        import tensorflow as tf
        
        # Prepare input
        height, width = frame.shape[:2]
        
        # MoveNet expects RGB
        rgb_frame = frame[:, :, ::-1]  # BGR to RGB
        
        # Resize and normalize
        input_size = 192 if self.model_variant == "lightning" else 256
        input_image = tf.image.resize_with_pad(
            tf.expand_dims(rgb_frame, axis=0), input_size, input_size
        )
        input_image = tf.cast(input_image, dtype=tf.int32)
        
        # Run inference
        outputs = self.movenet(input_image)
        keypoints_with_scores = outputs['output_0'].numpy()[0, 0, :, :]
        
        # Convert to our format
        keypoints = []
        for i, (y, x, score) in enumerate(keypoints_with_scores):
            keypoints.append(Keypoint(
                x=float(x),
                y=float(y),
                confidence=float(score),
                name=self.KEYPOINT_NAMES[i]
            ))
        
        return [PoseResult(keypoints=keypoints, frame_index=0)]
    
    def get_keypoint_names(self) -> List[str]:
        return self.KEYPOINT_NAMES.copy()


class MediaPipePoseEstimator(PoseEstimator):
    """MediaPipe Pose (BlazePose) estimation adapter."""
    
    # MediaPipe landmark names
    LANDMARK_NAMES = [
        "nose", "left_eye_inner", "left_eye", "left_eye_outer",
        "right_eye_inner", "right_eye", "right_eye_outer",
        "left_ear", "right_ear", "mouth_left", "mouth_right",
        "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
        "left_wrist", "right_wrist", "left_pinky", "right_pinky",
        "left_index", "right_index", "left_thumb", "right_thumb",
        "left_hip", "right_hip", "left_knee", "right_knee",
        "left_ankle", "right_ankle", "left_heel", "right_heel",
        "left_foot_index", "right_foot_index"
    ]
    
    def __init__(self, model_complexity: int = 1, min_detection_confidence: float = 0.5):
        """
        Initialize MediaPipe Pose.
        
        Args:
            model_complexity: 0 (lite), 1 (full), or 2 (heavy)
            min_detection_confidence: Minimum confidence for detection
        """
        self.model_complexity = model_complexity
        self.min_detection_confidence = min_detection_confidence
        self.pose = None
        self._initialize()
    
    def _initialize(self):
        """Initialize MediaPipe Pose."""
        try:
            import mediapipe as mp
            self.mp_pose = mp.solutions.pose
            self.pose = self.mp_pose.Pose(
                static_image_mode=False,
                model_complexity=self.model_complexity,
                min_detection_confidence=self.min_detection_confidence,
                min_tracking_confidence=0.5
            )
        except ImportError:
            raise ImportError("MediaPipe required. Install with: pip install mediapipe")
    
    def detect(self, frame: np.ndarray) -> List[PoseResult]:
        """Detect pose using MediaPipe."""
        if self.pose is None:
            self._initialize()
        
        # MediaPipe expects RGB
        rgb_frame = frame[:, :, ::-1]  # BGR to RGB
        height, width = frame.shape[:2]
        
        # Process frame
        results = self.pose.process(rgb_frame)
        
        if not results.pose_landmarks:
            return []
        
        # Convert landmarks to keypoints
        keypoints = []
        for i, landmark in enumerate(results.pose_landmarks.landmark):
            keypoints.append(Keypoint(
                x=landmark.x,
                y=landmark.y,
                confidence=landmark.visibility if hasattr(landmark, 'visibility') else 1.0,
                name=self.LANDMARK_NAMES[i] if i < len(self.LANDMARK_NAMES) else f"landmark_{i}"
            ))
        
        return [PoseResult(keypoints=keypoints, frame_index=0)]
    
    def get_keypoint_names(self) -> List[str]:
        return self.LANDMARK_NAMES.copy()
    
    def __del__(self):
        """Clean up MediaPipe resources."""
        if self.pose:
            self.pose.close()


class YOLOPoseEstimator(PoseEstimator):
    """YOLO-based pose estimation adapter (supports YOLOv8 and YOLOv11)."""
    
    # COCO keypoint format used by YOLO
    KEYPOINT_NAMES = [
        "nose", "left_eye", "right_eye", "left_ear", "right_ear",
        "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
        "left_wrist", "right_wrist", "left_hip", "right_hip",
        "left_knee", "right_knee", "left_ankle", "right_ankle"
    ]
    
    def __init__(self, model_version: str = "v11", model_size: str = "n", confidence_threshold: float = 0.25):
        """
        Initialize YOLO pose model.
        
        Args:
            model_version: "v8" or "v11"
            model_size: Model size - "n" (nano), "s" (small), "m" (medium), "l" (large), "x" (xlarge)
            confidence_threshold: Minimum confidence for detections
        """
        self.model_version = model_version
        self.model_size = model_size
        self.confidence_threshold = confidence_threshold
        self.model = None
        
        # Determine model path
        if model_version == "v8":
            self.model_path = f"yolov8{model_size}-pose.pt"
        else:  # v11
            self.model_path = f"yolo11{model_size}-pose.pt"
            
        self._load_model()
    
    def _load_model(self):
        """Load YOLO model."""
        try:
            from ultralytics import YOLO
            self.model = YOLO(self.model_path)
        except ImportError:
            raise ImportError("Ultralytics required for YOLO. "
                            "Install with: pip install ultralytics")
    
    def detect(self, frame: np.ndarray) -> List[PoseResult]:
        """Detect poses using YOLO."""
        if self.model is None:
            self._load_model()
        
        # Run inference
        results = self.model(frame, conf=self.confidence_threshold)
        
        pose_results = []
        
        # Process each detection
        for r in results:
            if r.keypoints is not None:
                for person_idx, keypoints_data in enumerate(r.keypoints.data):
                    keypoints = []
                    
                    # YOLO returns keypoints as [x, y, conf]
                    height, width = frame.shape[:2]
                    for i, (x, y, conf) in enumerate(keypoints_data):
                        keypoints.append(Keypoint(
                            x=float(x) / width,  # Normalize to 0-1
                            y=float(y) / height,  # Normalize to 0-1
                            confidence=float(conf),
                            name=self.KEYPOINT_NAMES[i] if i < len(self.KEYPOINT_NAMES) else f"joint_{i}"
                        ))
                    
                    pose_results.append(PoseResult(
                        keypoints=keypoints,
                        frame_index=0,
                        person_id=person_idx
                    ))
        
        return pose_results
    
    def get_keypoint_names(self) -> List[str]:
        return self.KEYPOINT_NAMES.copy()


# Note: Sapiens models removed due to complex setup requirements
# They require the official repository and cannot be integrated cleanly
# with the agent/MCP pipeline without significant complexity


def create_pose_estimator(model_type: str, **kwargs) -> PoseEstimator:
    """
    Factory function to create pose estimator instances.
    
    Args:
        model_type: One of "movenet", "mediapipe", "yolo"
        **kwargs: Model-specific parameters
        
    Returns:
        PoseEstimator instance
    """
    estimators = {
        "movenet": MoveNetPoseEstimator,
        "mediapipe": MediaPipePoseEstimator,
        "yolo": YOLOPoseEstimator,
    }
    
    if model_type not in estimators:
        raise ValueError(f"Unknown model type: {model_type}. "
                        f"Available: {list(estimators.keys())}")
    
    return estimators[model_type](**kwargs)


def get_pose_estimator(model_spec: str) -> PoseEstimator:
    """
    Get pose estimator from model specification string.
    
    Args:
        model_spec: Model specification string, e.g.:
            - "mediapipe" or "mediapipe-lite" or "mediapipe-full" or "mediapipe-heavy"
            - "movenet-lightning" or "movenet-thunder"
            - "yolo-v8-n" or "yolo-v11-s" etc.
            
    Returns:
        PoseEstimator instance
    """
    model_spec = model_spec.lower()
    
    # MediaPipe variants
    if model_spec.startswith("mediapipe"):
        complexity_map = {
            "mediapipe-lite": 0,
            "mediapipe-full": 1,
            "mediapipe-heavy": 2,
            "mediapipe": 1  # default
        }
        complexity = complexity_map.get(model_spec, 1)
        return create_pose_estimator("mediapipe", model_complexity=complexity)
    
    # MoveNet variants
    elif model_spec.startswith("movenet"):
        variant = "lightning" if "lightning" in model_spec else "thunder"
        return create_pose_estimator("movenet", model_variant=variant)
    
    # YOLO variants
    elif model_spec.startswith("yolo"):
        parts = model_spec.split("-")
        version = "v8" if "v8" in model_spec else "v11"
        size = parts[-1] if len(parts) > 2 else "n"
        return create_pose_estimator("yolo", model_version=version, model_size=size)
    
    # Legacy format support
    else:
        return create_pose_estimator(model_spec) 
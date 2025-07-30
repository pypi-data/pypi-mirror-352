"""
Laban Movement Analysis (LMA) inspired notation engine.
Computes movement metrics like direction, intensity, and speed from pose keypoints.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from .pose_estimation import PoseResult, Keypoint


class Direction(Enum):
    """Movement direction categories."""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    FORWARD = "forward"
    BACKWARD = "backward"
    STATIONARY = "stationary"


class Intensity(Enum):
    """Movement intensity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Speed(Enum):
    """Movement speed categories."""
    SLOW = "slow"
    MODERATE = "moderate"
    FAST = "fast"


@dataclass
class MovementMetrics:
    """LMA-inspired movement metrics for a frame or segment."""
    frame_index: int
    timestamp: Optional[float] = None
    
    # Primary metrics
    direction: Direction = Direction.STATIONARY
    intensity: Intensity = Intensity.LOW
    speed: Speed = Speed.SLOW
    
    # Numeric values
    velocity: float = 0.0  # pixels/second or normalized units
    acceleration: float = 0.0
    
    # Additional qualities
    fluidity: float = 0.0  # 0-1, smoothness of movement
    expansion: float = 0.0  # 0-1, how spread out the pose is
    
    # Raw displacement data
    center_displacement: Optional[Tuple[float, float]] = None
    total_displacement: float = 0.0


class MovementAnalyzer:
    """Analyzes pose sequences to extract LMA-style movement metrics."""
    
    def __init__(self, fps: float = 30.0, 
                 velocity_threshold_slow: float = 0.01,
                 velocity_threshold_fast: float = 0.1,
                 intensity_accel_threshold: float = 0.05):
        """
        Initialize movement analyzer.
        
        Args:
            fps: Frames per second of the video
            velocity_threshold_slow: Threshold for slow movement (normalized)
            velocity_threshold_fast: Threshold for fast movement (normalized)
            intensity_accel_threshold: Acceleration threshold for intensity
        """
        self.fps = fps
        self.frame_duration = 1.0 / fps
        self.velocity_threshold_slow = velocity_threshold_slow
        self.velocity_threshold_fast = velocity_threshold_fast
        self.intensity_accel_threshold = intensity_accel_threshold
    
    def analyze_movement(self, pose_sequence: List[List[PoseResult]]) -> List[MovementMetrics]:
        """
        Analyze a sequence of poses to compute movement metrics.
        
        Args:
            pose_sequence: List of pose results per frame
            
        Returns:
            List of movement metrics per frame
        """
        if not pose_sequence:
            return []
        
        metrics = []
        prev_centers = None
        prev_velocity = None
        
        for frame_idx, frame_poses in enumerate(pose_sequence):
            if not frame_poses:
                # No pose detected in this frame
                metrics.append(MovementMetrics(
                    frame_index=frame_idx,
                    timestamp=frame_idx * self.frame_duration
                ))
                continue
            
            # For now, analyze first person only
            # TODO: Extend to multi-person analysis
            pose = frame_poses[0]
            
            # Compute body center and limb positions
            center = self._compute_body_center(pose.keypoints)
            limb_positions = self._get_limb_positions(pose.keypoints)
            
            # Initialize metrics for this frame
            frame_metrics = MovementMetrics(
                frame_index=frame_idx,
                timestamp=frame_idx * self.frame_duration
            )
            
            if prev_centers is not None and frame_idx > 0:
                # Compute displacement and velocity
                displacement = (
                    center[0] - prev_centers[0],
                    center[1] - prev_centers[1]
                )
                frame_metrics.center_displacement = displacement
                frame_metrics.total_displacement = np.sqrt(
                    displacement[0]**2 + displacement[1]**2
                )
                
                # Velocity (normalized units per second)
                frame_metrics.velocity = frame_metrics.total_displacement * self.fps
                
                # Direction
                frame_metrics.direction = self._compute_direction(displacement)
                
                # Speed category
                frame_metrics.speed = self._categorize_speed(frame_metrics.velocity)
                
                # Acceleration and intensity
                if prev_velocity is not None:
                    frame_metrics.acceleration = abs(
                        frame_metrics.velocity - prev_velocity
                    ) * self.fps
                    frame_metrics.intensity = self._compute_intensity(
                        frame_metrics.acceleration,
                        frame_metrics.velocity
                    )
                
                # Fluidity (based on acceleration smoothness)
                frame_metrics.fluidity = self._compute_fluidity(
                    frame_metrics.acceleration
                )
            
            # Expansion (how spread out the pose is)
            frame_metrics.expansion = self._compute_expansion(pose.keypoints)
            
            metrics.append(frame_metrics)
            
            # Update previous values
            prev_centers = center
            prev_velocity = frame_metrics.velocity
        
        # Post-process to smooth metrics if needed
        metrics = self._smooth_metrics(metrics)
        
        return metrics
    
    def _compute_body_center(self, keypoints: List[Keypoint]) -> Tuple[float, float]:
        """Compute the center of mass of the body."""
        # Use major body joints for center calculation
        major_joints = ["left_hip", "right_hip", "left_shoulder", "right_shoulder"]
        
        x_coords = []
        y_coords = []
        
        for kp in keypoints:
            if kp.name in major_joints and kp.confidence > 0.5:
                x_coords.append(kp.x)
                y_coords.append(kp.y)
        
        if not x_coords:
            # Fallback to all keypoints
            x_coords = [kp.x for kp in keypoints if kp.confidence > 0.3]
            y_coords = [kp.y for kp in keypoints if kp.confidence > 0.3]
        
        if x_coords:
            return (np.mean(x_coords), np.mean(y_coords))
        return (0.5, 0.5)  # Default center
    
    def _get_limb_positions(self, keypoints: List[Keypoint]) -> Dict[str, Tuple[float, float]]:
        """Get positions of major limbs."""
        positions = {}
        for kp in keypoints:
            if kp.confidence > 0.3:
                positions[kp.name] = (kp.x, kp.y)
        return positions
    
    def _compute_direction(self, displacement: Tuple[float, float]) -> Direction:
        """Compute movement direction from displacement vector."""
        dx, dy = displacement
        
        # Threshold for considering movement
        threshold = 0.005
        
        if abs(dx) < threshold and abs(dy) < threshold:
            return Direction.STATIONARY
        
        # Determine primary direction
        if abs(dx) > abs(dy):
            return Direction.RIGHT if dx > 0 else Direction.LEFT
        else:
            return Direction.DOWN if dy > 0 else Direction.UP
    
    def _categorize_speed(self, velocity: float) -> Speed:
        """Categorize velocity into speed levels."""
        if velocity < self.velocity_threshold_slow:
            return Speed.SLOW
        elif velocity < self.velocity_threshold_fast:
            return Speed.FAST
        else:
            return Speed.FAST
    
    def _compute_intensity(self, acceleration: float, velocity: float) -> Intensity:
        """Compute movement intensity based on acceleration and velocity."""
        # High acceleration or high velocity indicates high intensity
        if acceleration > self.intensity_accel_threshold * 2 or velocity > self.velocity_threshold_fast:
            return Intensity.HIGH
        elif acceleration > self.intensity_accel_threshold or velocity > self.velocity_threshold_slow:
            return Intensity.MEDIUM
        else:
            return Intensity.LOW
    
    def _compute_fluidity(self, acceleration: float) -> float:
        """
        Compute fluidity score (0-1) based on acceleration.
        Lower acceleration = higher fluidity (smoother movement).
        """
        # Normalize acceleration to 0-1 range
        max_accel = 0.2  # Expected maximum acceleration
        norm_accel = min(acceleration / max_accel, 1.0)
        
        # Invert so low acceleration = high fluidity
        return 1.0 - norm_accel
    
    def _compute_expansion(self, keypoints: List[Keypoint]) -> float:
        """
        Compute how expanded/contracted the pose is.
        Returns 0-1 where 1 is fully expanded.
        """
        # Calculate distances between opposite limbs
        limb_pairs = [
            ("left_wrist", "right_wrist"),
            ("left_ankle", "right_ankle"),
            ("left_wrist", "left_ankle"),
            ("right_wrist", "right_ankle")
        ]
        
        kp_dict = {kp.name: kp for kp in keypoints if kp.confidence > 0.3}
        
        distances = []
        for limb1, limb2 in limb_pairs:
            if limb1 in kp_dict and limb2 in kp_dict:
                kp1 = kp_dict[limb1]
                kp2 = kp_dict[limb2]
                dist = np.sqrt((kp1.x - kp2.x)**2 + (kp1.y - kp2.y)**2)
                distances.append(dist)
        
        if distances:
            # Normalize by expected maximum distance
            avg_dist = np.mean(distances)
            max_expected = 1.4  # Diagonal of normalized space
            return min(avg_dist / max_expected, 1.0)
        
        return 0.5  # Default neutral expansion
    
    def _smooth_metrics(self, metrics: List[MovementMetrics]) -> List[MovementMetrics]:
        """Apply smoothing to reduce noise in metrics."""
        # Simple moving average for numeric values
        window_size = 3
        
        if len(metrics) <= window_size:
            return metrics
        
        # Smooth velocity and acceleration
        for i in range(window_size, len(metrics)):
            velocities = [m.velocity for m in metrics[i-window_size:i+1]]
            metrics[i].velocity = np.mean(velocities)
            
            accels = [m.acceleration for m in metrics[i-window_size:i+1]]
            metrics[i].acceleration = np.mean(accels)
            
            fluidities = [m.fluidity for m in metrics[i-window_size:i+1]]
            metrics[i].fluidity = np.mean(fluidities)
        
        return metrics


def analyze_pose_sequence(pose_sequence: List[List[PoseResult]], 
                         fps: float = 30.0) -> List[MovementMetrics]:
    """
    Convenience function to analyze a pose sequence.
    
    Args:
        pose_sequence: List of pose results per frame
        fps: Video frame rate
        
    Returns:
        List of movement metrics
    """
    analyzer = MovementAnalyzer(fps=fps)
    return analyzer.analyze_movement(pose_sequence) 
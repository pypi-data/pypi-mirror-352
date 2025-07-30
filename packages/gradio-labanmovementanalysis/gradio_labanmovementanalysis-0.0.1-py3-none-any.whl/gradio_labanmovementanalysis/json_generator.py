"""
JSON generator for converting movement annotations and keypoint data to structured JSON format.
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from .pose_estimation import PoseResult, Keypoint
from .notation_engine import MovementMetrics, Direction, Intensity, Speed


def generate_json(
    movement_metrics: List[MovementMetrics],
    pose_results: Optional[List[List[PoseResult]]] = None,
    video_metadata: Optional[Dict[str, Any]] = None,
    include_keypoints: bool = False
) -> Dict[str, Any]:
    """
    Generate structured JSON output from movement analysis results.
    
    Args:
        movement_metrics: List of movement metrics per frame
        pose_results: Optional pose keypoints per frame
        video_metadata: Optional video metadata (fps, dimensions, etc.)
        include_keypoints: Whether to include raw keypoint data
        
    Returns:
        Dictionary containing formatted analysis results
    """
    output = {
        "analysis_metadata": {
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "model_info": video_metadata.get("model_info", {}) if video_metadata else {}
        },
        "video_info": {},
        "movement_analysis": {
            "frame_count": len(movement_metrics),
            "frames": []
        }
    }
    
    # Add video metadata if provided
    if video_metadata:
        output["video_info"] = {
            "fps": video_metadata.get("fps", 30.0),
            "duration_seconds": len(movement_metrics) / video_metadata.get("fps", 30.0),
            "width": video_metadata.get("width"),
            "height": video_metadata.get("height"),
            "frame_count": video_metadata.get("frame_count", len(movement_metrics))
        }
    
    # Process each frame's metrics
    for i, metrics in enumerate(movement_metrics):
        frame_data = {
            "frame_index": metrics.frame_index,
            "timestamp": metrics.timestamp,
            "metrics": {
                "direction": metrics.direction.value,
                "intensity": metrics.intensity.value,
                "speed": metrics.speed.value,
                "velocity": round(metrics.velocity, 4),
                "acceleration": round(metrics.acceleration, 4),
                "fluidity": round(metrics.fluidity, 3),
                "expansion": round(metrics.expansion, 3),
                "total_displacement": round(metrics.total_displacement, 4)
            }
        }
        
        # Add displacement if available
        if metrics.center_displacement:
            frame_data["metrics"]["center_displacement"] = {
                "x": round(metrics.center_displacement[0], 4),
                "y": round(metrics.center_displacement[1], 4)
            }
        
        # Add keypoints if requested and available
        if include_keypoints and pose_results and i < len(pose_results):
            frame_poses = pose_results[i]
            if frame_poses:
                frame_data["keypoints"] = []
                for pose in frame_poses:
                    keypoint_data = {
                        "person_id": pose.person_id,
                        "points": []
                    }
                    for kp in pose.keypoints:
                        keypoint_data["points"].append({
                            "name": kp.name,
                            "x": round(kp.x, 4),
                            "y": round(kp.y, 4),
                            "confidence": round(kp.confidence, 3)
                        })
                    frame_data["keypoints"].append(keypoint_data)
        
        output["movement_analysis"]["frames"].append(frame_data)
    
    # Add summary statistics
    output["movement_analysis"]["summary"] = _generate_summary(movement_metrics)
    
    return output


def _generate_summary(metrics: List[MovementMetrics]) -> Dict[str, Any]:
    """Generate summary statistics from movement metrics."""
    if not metrics:
        return {}
    
    # Count occurrences of each category
    direction_counts = {}
    intensity_counts = {}
    speed_counts = {}
    
    velocities = []
    accelerations = []
    fluidities = []
    expansions = []
    
    for m in metrics:
        # Count categories
        direction_counts[m.direction.value] = direction_counts.get(m.direction.value, 0) + 1
        intensity_counts[m.intensity.value] = intensity_counts.get(m.intensity.value, 0) + 1
        speed_counts[m.speed.value] = speed_counts.get(m.speed.value, 0) + 1
        
        # Collect numeric values
        velocities.append(m.velocity)
        accelerations.append(m.acceleration)
        fluidities.append(m.fluidity)
        expansions.append(m.expansion)
    
    # Calculate statistics
    import numpy as np
    
    summary = {
        "direction": {
            "distribution": direction_counts,
            "dominant": max(direction_counts, key=direction_counts.get)
        },
        "intensity": {
            "distribution": intensity_counts,
            "dominant": max(intensity_counts, key=intensity_counts.get)
        },
        "speed": {
            "distribution": speed_counts,
            "dominant": max(speed_counts, key=speed_counts.get)
        },
        "velocity": {
            "mean": round(float(np.mean(velocities)), 4),
            "std": round(float(np.std(velocities)), 4),
            "min": round(float(np.min(velocities)), 4),
            "max": round(float(np.max(velocities)), 4)
        },
        "acceleration": {
            "mean": round(float(np.mean(accelerations)), 4),
            "std": round(float(np.std(accelerations)), 4),
            "min": round(float(np.min(accelerations)), 4),
            "max": round(float(np.max(accelerations)), 4)
        },
        "fluidity": {
            "mean": round(float(np.mean(fluidities)), 3),
            "std": round(float(np.std(fluidities)), 3)
        },
        "expansion": {
            "mean": round(float(np.mean(expansions)), 3),
            "std": round(float(np.std(expansions)), 3)
        }
    }
    
    # Identify significant movement segments
    summary["movement_segments"] = _identify_movement_segments(metrics)
    
    return summary


def _identify_movement_segments(metrics: List[MovementMetrics]) -> List[Dict[str, Any]]:
    """Identify significant movement segments (e.g., bursts of activity)."""
    segments = []
    
    # Simple segmentation based on intensity changes
    current_segment = None
    intensity_threshold = Intensity.MEDIUM
    
    for i, m in enumerate(metrics):
        if m.intensity.value >= intensity_threshold.value:
            if current_segment is None:
                # Start new segment
                current_segment = {
                    "start_frame": i,
                    "start_time": m.timestamp,
                    "peak_velocity": m.velocity,
                    "dominant_direction": m.direction.value
                }
            else:
                # Update segment
                if m.velocity > current_segment["peak_velocity"]:
                    current_segment["peak_velocity"] = m.velocity
                    current_segment["dominant_direction"] = m.direction.value
        else:
            if current_segment is not None:
                # End segment
                current_segment["end_frame"] = i - 1
                current_segment["end_time"] = metrics[i-1].timestamp if i > 0 else 0
                current_segment["duration"] = (
                    current_segment["end_time"] - current_segment["start_time"]
                )
                current_segment["peak_velocity"] = round(current_segment["peak_velocity"], 4)
                segments.append(current_segment)
                current_segment = None
    
    # Handle segment that extends to end
    if current_segment is not None:
        current_segment["end_frame"] = len(metrics) - 1
        current_segment["end_time"] = metrics[-1].timestamp
        current_segment["duration"] = (
            current_segment["end_time"] - current_segment["start_time"]
        )
        current_segment["peak_velocity"] = round(current_segment["peak_velocity"], 4)
        segments.append(current_segment)
    
    return segments


def save_json(data: Dict[str, Any], output_path: str, pretty: bool = True) -> None:
    """
    Save JSON data to file.
    
    Args:
        data: Dictionary to save
        output_path: Path to output file
        pretty: Whether to format JSON with indentation
    """
    with open(output_path, 'w') as f:
        if pretty:
            json.dump(data, f, indent=2, sort_keys=False)
        else:
            json.dump(data, f)


def format_for_display(data: Dict[str, Any]) -> str:
    """
    Format JSON data for display in Gradio.
    
    Args:
        data: Dictionary to format
        
    Returns:
        Formatted JSON string
    """
    return json.dumps(data, indent=2, sort_keys=False) 
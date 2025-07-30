"""
Agent-friendly API for Laban Movement Analysis
Provides simplified interfaces for AI agents and automation
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the main component
from .labanmovementanalysis import LabanMovementAnalysis


class PoseModel(str, Enum):
    """Available pose estimation models"""
    MEDIAPIPE = "mediapipe"
    MOVENET = "movenet" 
    YOLO = "yolo"


class MovementIntensity(str, Enum):
    """Movement intensity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class MovementDirection(str, Enum):
    """Movement direction categories"""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    STATIONARY = "stationary"


@dataclass
class AnalysisResult:
    """Structured analysis result for agents"""
    success: bool
    video_path: str
    duration_seconds: float
    fps: float
    dominant_direction: MovementDirection
    dominant_intensity: MovementIntensity
    dominant_speed: str
    movement_segments: List[Dict[str, Any]]
    fluidity_score: float
    expansion_score: float
    error: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None
    visualization_path: Optional[str] = None


class LabanAgentAPI:
    """
    Simplified API for AI agents to analyze movement in videos.
    Provides high-level methods with structured outputs.
    """
    
    # Gradio component compatibility
    events = {}
    
    def __init__(self, default_model: PoseModel = PoseModel.MEDIAPIPE):
        """
        Initialize the agent API.
        
        Args:
            default_model: Default pose estimation model to use
        """
        self.analyzer = LabanMovementAnalysis(default_model=default_model.value)
        self.default_model = default_model
        self._analysis_cache = {}
        
    def analyze(
        self,
        video_path: Union[str, Path],
        model: Optional[PoseModel] = None,
        generate_visualization: bool = False,
        cache_results: bool = True
    ) -> AnalysisResult:
        """
        Analyze a video and return structured results.
        
        Args:
            video_path: Path to video file
            model: Pose estimation model to use (defaults to instance default)
            generate_visualization: Whether to create annotated video
            cache_results: Whether to cache results for later retrieval
            
        Returns:
            AnalysisResult with structured movement data
        """
        try:
            # Convert path to string
            video_path = str(video_path)
            
            # Use default model if not specified
            if model is None:
                model = self.default_model
                
            # Process video
            json_output, viz_video = self.analyzer.process_video(
                video_path,
                model=model.value,
                enable_visualization=generate_visualization,
                include_keypoints=False
            )
            
            # Parse results
            result = self._parse_analysis_output(
                json_output, 
                video_path,
                viz_video
            )
            
            # Cache if requested
            if cache_results:
                cache_key = f"{Path(video_path).stem}_{model.value}"
                self._analysis_cache[cache_key] = result
                
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            return AnalysisResult(
                success=False,
                video_path=str(video_path),
                duration_seconds=0.0,
                fps=0.0,
                dominant_direction=MovementDirection.STATIONARY,
                dominant_intensity=MovementIntensity.LOW,
                dominant_speed="unknown",
                movement_segments=[],
                fluidity_score=0.0,
                expansion_score=0.0,
                error=str(e)
            )
    
    async def analyze_async(
        self,
        video_path: Union[str, Path],
        model: Optional[PoseModel] = None,
        generate_visualization: bool = False
    ) -> AnalysisResult:
        """
        Asynchronously analyze a video.
        
        Args:
            video_path: Path to video file
            model: Pose estimation model to use
            generate_visualization: Whether to create annotated video
            
        Returns:
            AnalysisResult with structured movement data
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.analyze,
            video_path,
            model,
            generate_visualization
        )
    
    def batch_analyze(
        self,
        video_paths: List[Union[str, Path]],
        model: Optional[PoseModel] = None,
        parallel: bool = True,
        max_workers: int = 4
    ) -> List[AnalysisResult]:
        """
        Analyze multiple videos in batch.
        
        Args:
            video_paths: List of video file paths
            model: Pose estimation model to use
            parallel: Whether to process in parallel
            max_workers: Maximum parallel workers
            
        Returns:
            List of AnalysisResult objects
        """
        if parallel:
            from concurrent.futures import ThreadPoolExecutor
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [
                    executor.submit(self.analyze, path, model, False)
                    for path in video_paths
                ]
                results = [future.result() for future in futures]
        else:
            results = [
                self.analyze(path, model, False)
                for path in video_paths
            ]
            
        return results
    
    def get_movement_summary(self, analysis_result: AnalysisResult) -> str:
        """
        Generate a natural language summary of movement analysis.
        
        Args:
            analysis_result: Analysis result to summarize
            
        Returns:
            Human-readable summary string
        """
        if not analysis_result.success:
            return f"Analysis failed: {analysis_result.error}"
            
        summary_parts = [
            f"Movement Analysis Summary for {Path(analysis_result.video_path).name}:",
            f"- Duration: {analysis_result.duration_seconds:.1f} seconds",
            f"- Primary movement direction: {analysis_result.dominant_direction.value}",
            f"- Movement intensity: {analysis_result.dominant_intensity.value}",
            f"- Movement speed: {analysis_result.dominant_speed}",
            f"- Fluidity score: {analysis_result.fluidity_score:.2f}/1.00",
            f"- Expansion score: {analysis_result.expansion_score:.2f}/1.00"
        ]
        
        if analysis_result.movement_segments:
            summary_parts.append(f"- Detected {len(analysis_result.movement_segments)} movement segments")
            
        return "\n".join(summary_parts)
    
    def compare_videos(
        self,
        video_path1: Union[str, Path],
        video_path2: Union[str, Path],
        model: Optional[PoseModel] = None
    ) -> Dict[str, Any]:
        """
        Compare movement patterns between two videos.
        
        Args:
            video_path1: First video path
            video_path2: Second video path
            model: Pose estimation model to use
            
        Returns:
            Comparison results dictionary
        """
        # Analyze both videos
        result1 = self.analyze(video_path1, model, False)
        result2 = self.analyze(video_path2, model, False)
        
        if not result1.success or not result2.success:
            return {
                "success": False,
                "error": "One or both analyses failed"
            }
            
        # Compare metrics
        comparison = {
            "success": True,
            "video1": Path(video_path1).name,
            "video2": Path(video_path2).name,
            "metrics": {
                "direction_match": result1.dominant_direction == result2.dominant_direction,
                "intensity_match": result1.dominant_intensity == result2.dominant_intensity,
                "speed_match": result1.dominant_speed == result2.dominant_speed,
                "fluidity_difference": abs(result1.fluidity_score - result2.fluidity_score),
                "expansion_difference": abs(result1.expansion_score - result2.expansion_score)
            },
            "details": {
                "video1": {
                    "direction": result1.dominant_direction.value,
                    "intensity": result1.dominant_intensity.value,
                    "speed": result1.dominant_speed,
                    "fluidity": result1.fluidity_score,
                    "expansion": result1.expansion_score
                },
                "video2": {
                    "direction": result2.dominant_direction.value,
                    "intensity": result2.dominant_intensity.value,
                    "speed": result2.dominant_speed,
                    "fluidity": result2.fluidity_score,
                    "expansion": result2.expansion_score
                }
            }
        }
        
        return comparison
    
    def filter_by_movement(
        self,
        video_paths: List[Union[str, Path]],
        direction: Optional[MovementDirection] = None,
        intensity: Optional[MovementIntensity] = None,
        min_fluidity: Optional[float] = None,
        min_expansion: Optional[float] = None
    ) -> List[AnalysisResult]:
        """
        Filter videos based on movement characteristics.
        
        Args:
            video_paths: List of video paths to analyze
            direction: Filter by movement direction
            intensity: Filter by movement intensity
            min_fluidity: Minimum fluidity score
            min_expansion: Minimum expansion score
            
        Returns:
            List of AnalysisResults that match criteria
        """
        # Analyze all videos
        results = self.batch_analyze(video_paths)
        
        # Apply filters
        filtered = []
        for result in results:
            if not result.success:
                continue
                
            if direction and result.dominant_direction != direction:
                continue
                
            if intensity and result.dominant_intensity != intensity:
                continue
                
            if min_fluidity and result.fluidity_score < min_fluidity:
                continue
                
            if min_expansion and result.expansion_score < min_expansion:
                continue
                
            filtered.append(result)
            
        return filtered
    
    def _parse_analysis_output(
        self,
        json_output: Dict[str, Any],
        video_path: str,
        viz_path: Optional[str]
    ) -> AnalysisResult:
        """Parse JSON output into structured result"""
        try:
            # Extract video info
            video_info = json_output.get("video_info", {})
            duration = video_info.get("duration_seconds", 0.0)
            fps = video_info.get("fps", 0.0)
            
            # Extract movement summary
            movement_analysis = json_output.get("movement_analysis", {})
            summary = movement_analysis.get("summary", {})
            
            # Parse dominant metrics
            direction_data = summary.get("direction", {})
            dominant_direction = direction_data.get("dominant", "stationary")
            dominant_direction = MovementDirection(dominant_direction.lower())
            
            intensity_data = summary.get("intensity", {})
            dominant_intensity = intensity_data.get("dominant", "low")
            dominant_intensity = MovementIntensity(dominant_intensity.lower())
            
            speed_data = summary.get("speed", {})
            dominant_speed = speed_data.get("dominant", "unknown")
            
            # Get segments
            segments = summary.get("movement_segments", [])
            
            # Calculate aggregate scores
            frames = movement_analysis.get("frames", [])
            fluidity_scores = [f.get("metrics", {}).get("fluidity", 0) for f in frames]
            expansion_scores = [f.get("metrics", {}).get("expansion", 0) for f in frames]
            
            avg_fluidity = sum(fluidity_scores) / len(fluidity_scores) if fluidity_scores else 0.0
            avg_expansion = sum(expansion_scores) / len(expansion_scores) if expansion_scores else 0.0
            
            return AnalysisResult(
                success=True,
                video_path=video_path,
                duration_seconds=duration,
                fps=fps,
                dominant_direction=dominant_direction,
                dominant_intensity=dominant_intensity,
                dominant_speed=dominant_speed,
                movement_segments=segments,
                fluidity_score=avg_fluidity,
                expansion_score=avg_expansion,
                raw_data=json_output,
                visualization_path=viz_path
            )
            
        except Exception as e:
            logger.error(f"Failed to parse analysis output: {str(e)}")
            return AnalysisResult(
                success=False,
                video_path=video_path,
                duration_seconds=0.0,
                fps=0.0,
                dominant_direction=MovementDirection.STATIONARY,
                dominant_intensity=MovementIntensity.LOW,
                dominant_speed="unknown",
                movement_segments=[],
                fluidity_score=0.0,
                expansion_score=0.0,
                error=f"Parse error: {str(e)}",
                raw_data=json_output
            )


# Convenience functions for quick analysis
def quick_analyze(video_path: Union[str, Path]) -> Dict[str, Any]:
    """Quick analysis with default settings, returns dict"""
    api = LabanAgentAPI()
    result = api.analyze(video_path)
    return asdict(result)

# Gradio component compatibility
quick_analyze.events = {}


def analyze_and_summarize(video_path: Union[str, Path]) -> str:
    """Analyze video and return natural language summary"""
    api = LabanAgentAPI()
    result = api.analyze(video_path)
    return api.get_movement_summary(result)

# Gradio component compatibility
analyze_and_summarize.events = {} 
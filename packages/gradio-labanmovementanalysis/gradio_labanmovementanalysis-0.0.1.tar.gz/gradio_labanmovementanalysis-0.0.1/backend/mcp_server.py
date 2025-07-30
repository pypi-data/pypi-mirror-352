"""
MCP (Model Context Protocol) Server for Laban Movement Analysis
Provides tools for video movement analysis accessible to AI agents
"""

import asyncio
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse
import aiofiles
import httpx

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    ToolParameterType,
    ToolResponse,
    ToolResult,
    ToolError
)

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent))

from gradio_labanmovementanalysis import LabanMovementAnalysis


class LabanMCPServer:
    """MCP Server for Laban Movement Analysis"""
    
    def __init__(self):
        self.server = Server("laban-movement-analysis")
        self.analyzer = LabanMovementAnalysis()
        self.analysis_cache = {}
        self.temp_dir = tempfile.mkdtemp(prefix="laban_mcp_")
        
        # Register tools
        self._register_tools()
        
    def _register_tools(self):
        """Register all available tools"""
        
        @self.server.tool()
        async def analyze_video(
            video_path: str,
            model: str = "mediapipe",
            enable_visualization: bool = False,
            include_keypoints: bool = False
        ) -> ToolResult:
            """
            Analyze movement in a video file using Laban Movement Analysis.
            
            Args:
                video_path: Path or URL to video file
                model: Pose estimation model ('mediapipe', 'movenet', 'yolo')
                enable_visualization: Generate annotated video output
                include_keypoints: Include raw keypoint data in JSON
                
            Returns:
                Movement analysis results and optional visualization
            """
            try:
                # Handle URL vs local path
                if video_path.startswith(('http://', 'https://')):
                    video_path = await self._download_video(video_path)
                
                # Process video
                json_output, viz_video = await asyncio.to_thread(
                    self.analyzer.process_video,
                    video_path,
                    model=model,
                    enable_visualization=enable_visualization,
                    include_keypoints=include_keypoints
                )
                
                # Store in cache
                analysis_id = f"{Path(video_path).stem}_{datetime.now().isoformat()}"
                self.analysis_cache[analysis_id] = {
                    "json_output": json_output,
                    "viz_video": viz_video,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Format response
                response_data = {
                    "analysis_id": analysis_id,
                    "analysis": json_output,
                    "visualization_path": viz_video if viz_video else None
                }
                
                return ToolResult(
                    success=True,
                    content=[TextContent(text=json.dumps(response_data, indent=2))]
                )
                
            except Exception as e:
                return ToolResult(
                    success=False,
                    error=ToolError(message=f"Analysis failed: {str(e)}")
                )
        
        @self.server.tool()
        async def get_analysis_summary(
            analysis_id: str
        ) -> ToolResult:
            """
            Get a human-readable summary of a previous analysis.
            
            Args:
                analysis_id: ID of the analysis to summarize
                
            Returns:
                Summary of movement analysis
            """
            try:
                if analysis_id not in self.analysis_cache:
                    return ToolResult(
                        success=False,
                        error=ToolError(message=f"Analysis ID '{analysis_id}' not found")
                    )
                
                analysis_data = self.analysis_cache[analysis_id]["json_output"]
                
                # Extract key information
                summary = self._generate_summary(analysis_data)
                
                return ToolResult(
                    success=True,
                    content=[TextContent(text=summary)]
                )
                
            except Exception as e:
                return ToolResult(
                    success=False,
                    error=ToolError(message=f"Summary generation failed: {str(e)}")
                )
        
        @self.server.tool()
        async def list_available_models() -> ToolResult:
            """
            List available pose estimation models with their characteristics.
            
            Returns:
                Information about available models
            """
            models_info = {
                "mediapipe": {
                    "name": "MediaPipe Pose",
                    "keypoints": 33,
                    "dimensions": "3D",
                    "optimization": "CPU",
                    "best_for": "Single person, detailed analysis",
                    "speed": "Fast"
                },
                "movenet": {
                    "name": "MoveNet",
                    "keypoints": 17,
                    "dimensions": "2D",
                    "optimization": "Mobile/Edge",
                    "best_for": "Real-time applications, mobile devices",
                    "speed": "Very Fast"
                },
                "yolo": {
                    "name": "YOLO Pose",
                    "keypoints": 17,
                    "dimensions": "2D", 
                    "optimization": "GPU",
                    "best_for": "Multi-person detection",
                    "speed": "Fast (with GPU)"
                }
            }
            
            return ToolResult(
                success=True,
                content=[TextContent(text=json.dumps(models_info, indent=2))]
            )
        
        @self.server.tool()
        async def batch_analyze(
            video_paths: List[str],
            model: str = "mediapipe",
            parallel: bool = True
        ) -> ToolResult:
            """
            Analyze multiple videos in batch.
            
            Args:
                video_paths: List of video paths or URLs
                model: Pose estimation model to use
                parallel: Process videos in parallel
                
            Returns:
                Batch analysis results
            """
            try:
                results = {}
                
                if parallel:
                    # Process in parallel
                    tasks = []
                    for path in video_paths:
                        task = self._analyze_single_video(path, model)
                        tasks.append(task)
                    
                    analyses = await asyncio.gather(*tasks)
                    
                    for path, analysis in zip(video_paths, analyses):
                        results[path] = analysis
                else:
                    # Process sequentially
                    for path in video_paths:
                        results[path] = await self._analyze_single_video(path, model)
                
                return ToolResult(
                    success=True,
                    content=[TextContent(text=json.dumps(results, indent=2))]
                )
                
            except Exception as e:
                return ToolResult(
                    success=False,
                    error=ToolError(message=f"Batch analysis failed: {str(e)}")
                )
        
        @self.server.tool()
        async def compare_movements(
            analysis_id1: str,
            analysis_id2: str
        ) -> ToolResult:
            """
            Compare movement patterns between two analyzed videos.
            
            Args:
                analysis_id1: First analysis ID
                analysis_id2: Second analysis ID
                
            Returns:
                Comparison of movement metrics
            """
            try:
                if analysis_id1 not in self.analysis_cache:
                    return ToolResult(
                        success=False,
                        error=ToolError(message=f"Analysis ID '{analysis_id1}' not found")
                    )
                    
                if analysis_id2 not in self.analysis_cache:
                    return ToolResult(
                        success=False,
                        error=ToolError(message=f"Analysis ID '{analysis_id2}' not found")
                    )
                
                # Get analyses
                analysis1 = self.analysis_cache[analysis_id1]["json_output"]
                analysis2 = self.analysis_cache[analysis_id2]["json_output"]
                
                # Compare metrics
                comparison = self._compare_analyses(analysis1, analysis2)
                
                return ToolResult(
                    success=True,
                    content=[TextContent(text=json.dumps(comparison, indent=2))]
                )
                
            except Exception as e:
                return ToolResult(
                    success=False,
                    error=ToolError(message=f"Comparison failed: {str(e)}")
                )
    
    async def _download_video(self, url: str) -> str:
        """Download video from URL to temporary file"""
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            
            # Save to temp file
            filename = Path(urlparse(url).path).name or "video.mp4"
            temp_path = os.path.join(self.temp_dir, filename)
            
            async with aiofiles.open(temp_path, 'wb') as f:
                await f.write(response.content)
            
            return temp_path
    
    async def _analyze_single_video(self, path: str, model: str) -> Dict[str, Any]:
        """Analyze a single video"""
        try:
            if path.startswith(('http://', 'https://')):
                path = await self._download_video(path)
                
            json_output, _ = await asyncio.to_thread(
                self.analyzer.process_video,
                path,
                model=model,
                enable_visualization=False
            )
            
            return {
                "status": "success",
                "analysis": json_output
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _generate_summary(self, analysis_data: Dict[str, Any]) -> str:
        """Generate human-readable summary from analysis data"""
        summary_parts = []
        
        # Video info
        video_info = analysis_data.get("video_info", {})
        summary_parts.append(f"Video Analysis Summary")
        summary_parts.append(f"Duration: {video_info.get('duration_seconds', 0):.1f} seconds")
        summary_parts.append(f"Resolution: {video_info.get('width', 0)}x{video_info.get('height', 0)}")
        summary_parts.append("")
        
        # Movement summary
        movement_summary = analysis_data.get("movement_analysis", {}).get("summary", {})
        
        # Direction analysis
        direction_data = movement_summary.get("direction", {})
        dominant_direction = direction_data.get("dominant", "unknown")
        summary_parts.append(f"Dominant Movement Direction: {dominant_direction}")
        
        # Intensity analysis
        intensity_data = movement_summary.get("intensity", {})
        dominant_intensity = intensity_data.get("dominant", "unknown")
        summary_parts.append(f"Movement Intensity: {dominant_intensity}")
        
        # Speed analysis
        speed_data = movement_summary.get("speed", {})
        dominant_speed = speed_data.get("dominant", "unknown")
        summary_parts.append(f"Movement Speed: {dominant_speed}")
        
        # Segments
        segments = movement_summary.get("movement_segments", [])
        if segments:
            summary_parts.append(f"\nMovement Segments: {len(segments)}")
            for i, segment in enumerate(segments[:3]):  # Show first 3
                start_time = segment.get("start_time", 0)
                end_time = segment.get("end_time", 0)
                movement_type = segment.get("movement_type", "unknown")
                summary_parts.append(f"  Segment {i+1}: {movement_type} ({start_time:.1f}s - {end_time:.1f}s)")
        
        return "\n".join(summary_parts)
    
    def _compare_analyses(self, analysis1: Dict, analysis2: Dict) -> Dict[str, Any]:
        """Compare two movement analyses"""
        comparison = {
            "video1_info": analysis1.get("video_info", {}),
            "video2_info": analysis2.get("video_info", {}),
            "metric_comparison": {}
        }
        
        # Compare summaries
        summary1 = analysis1.get("movement_analysis", {}).get("summary", {})
        summary2 = analysis2.get("movement_analysis", {}).get("summary", {})
        
        # Compare directions
        dir1 = summary1.get("direction", {})
        dir2 = summary2.get("direction", {})
        comparison["metric_comparison"]["direction"] = {
            "video1_dominant": dir1.get("dominant", "unknown"),
            "video2_dominant": dir2.get("dominant", "unknown"),
            "match": dir1.get("dominant") == dir2.get("dominant")
        }
        
        # Compare intensity
        int1 = summary1.get("intensity", {})
        int2 = summary2.get("intensity", {})
        comparison["metric_comparison"]["intensity"] = {
            "video1_dominant": int1.get("dominant", "unknown"),
            "video2_dominant": int2.get("dominant", "unknown"),
            "match": int1.get("dominant") == int2.get("dominant")
        }
        
        # Compare speed
        speed1 = summary1.get("speed", {})
        speed2 = summary2.get("speed", {})
        comparison["metric_comparison"]["speed"] = {
            "video1_dominant": speed1.get("dominant", "unknown"),
            "video2_dominant": speed2.get("dominant", "unknown"),
            "match": speed1.get("dominant") == speed2.get("dominant")
        }
        
        return comparison
    
    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream)


async def main():
    """Main entry point"""
    server = LabanMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main()) 
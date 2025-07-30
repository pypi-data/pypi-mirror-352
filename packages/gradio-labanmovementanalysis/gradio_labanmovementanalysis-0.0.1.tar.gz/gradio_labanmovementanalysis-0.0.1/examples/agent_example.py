"""
Example script demonstrating agent-friendly API usage
for Laban Movement Analysis
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from gradio_labanmovementanalysis import (
    LabanAgentAPI, 
    PoseModel,
    MovementDirection,
    MovementIntensity,
    quick_analyze,
    analyze_and_summarize
)


def main():
    """Demonstrate various agent API features"""
    
    print("🎭 Laban Movement Analysis - Agent API Examples\n")
    
    # Example video paths (replace with your own)
    video_path = "examples/dance.mp4"
    
    # 1. Quick analysis with summary
    print("1. Quick Analysis with Summary")
    print("-" * 40)
    summary = analyze_and_summarize(video_path)
    print(summary)
    print()
    
    # 2. Detailed analysis with structured output
    print("2. Detailed Analysis")
    print("-" * 40)
    api = LabanAgentAPI()
    result = api.analyze(video_path, generate_visualization=True)
    
    if result.success:
        print(f"✓ Analysis successful!")
        print(f"  Direction: {result.dominant_direction.value}")
        print(f"  Intensity: {result.dominant_intensity.value}")
        print(f"  Speed: {result.dominant_speed}")
        print(f"  Fluidity: {result.fluidity_score:.2f}")
        print(f"  Expansion: {result.expansion_score:.2f}")
        print(f"  Segments: {len(result.movement_segments)}")
        if result.visualization_path:
            print(f"  Visualization saved to: {result.visualization_path}")
    else:
        print(f"✗ Analysis failed: {result.error}")
    print()
    
    # 3. Batch processing example
    print("3. Batch Processing")
    print("-" * 40)
    video_paths = [
        "examples/dance.mp4",
        "examples/exercise.mp4",
        "examples/walking.mp4"
    ]
    
    # Filter out non-existent files
    existing_paths = [p for p in video_paths if Path(p).exists()]
    
    if existing_paths:
        results = api.batch_analyze(existing_paths, parallel=True)
        for i, result in enumerate(results):
            print(f"Video {i+1}: {Path(result.video_path).name}")
            if result.success:
                print(f"  ✓ {result.dominant_direction.value} movement, "
                      f"{result.dominant_intensity.value} intensity")
            else:
                print(f"  ✗ Failed: {result.error}")
    else:
        print("  No example videos found")
    print()
    
    # 4. Movement filtering example
    print("4. Movement Filtering")
    print("-" * 40)
    if existing_paths and len(existing_paths) > 1:
        # Find high-intensity movements
        high_intensity = api.filter_by_movement(
            existing_paths,
            intensity=MovementIntensity.HIGH,
            min_fluidity=0.5
        )
        
        print(f"Found {len(high_intensity)} high-intensity videos:")
        for result in high_intensity:
            print(f"  - {Path(result.video_path).name}: "
                  f"fluidity={result.fluidity_score:.2f}")
    print()
    
    # 5. Video comparison example
    print("5. Video Comparison")
    print("-" * 40)
    if len(existing_paths) >= 2:
        comparison = api.compare_videos(existing_paths[0], existing_paths[1])
        print(f"Comparing: {comparison['video1']} vs {comparison['video2']}")
        print(f"  Direction match: {comparison['metrics']['direction_match']}")
        print(f"  Intensity match: {comparison['metrics']['intensity_match']}")
        print(f"  Fluidity difference: {comparison['metrics']['fluidity_difference']:.2f}")
    print()
    
    # 6. Model comparison
    print("6. Model Comparison")
    print("-" * 40)
    if existing_paths:
        test_video = existing_paths[0]
        models = [PoseModel.MEDIAPIPE, PoseModel.MOVENET]
        
        for model in models:
            result = api.analyze(test_video, model=model)
            if result.success:
                print(f"{model.value}: {result.dominant_direction.value} "
                      f"({result.dominant_intensity.value})")


def async_example():
    """Example of async usage"""
    import asyncio
    
    async def analyze_async():
        api = LabanAgentAPI()
        result = await api.analyze_async("examples/dance.mp4")
        return api.get_movement_summary(result)
    
    # Run async example
    summary = asyncio.run(analyze_async())
    print("Async Analysis:", summary)


if __name__ == "__main__":
    main()
    
    # Uncomment to run async example
    # async_example() 
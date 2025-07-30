# MCP & Agent Integration for Laban Movement Analysis

This project provides comprehensive MCP (Model Context Protocol) integration and agent-ready APIs for professional movement analysis with pose estimation, AI action recognition, and automation capabilities.

## 🚀 Quick Start

### 1. Install All Dependencies

```bash
# Clone the repository
git clone https://github.com/[your-repo]/labanmovementanalysis
cd labanmovementanalysis

# Install core dependencies
pip install -r backend/requirements.txt

# Install MCP and enhanced features
pip install -r backend/requirements-mcp.txt
```

### 2. Start the MCP Server

```bash
# Start MCP server for AI assistants
python -m backend.mcp_server
```

### 3. Configure Your AI Assistant

Add to your Claude Desktop or other MCP-compatible assistant configuration:

```json
{
  "mcpServers": {
    "laban-movement-analysis": {
      "command": "python",
      "args": ["-m", "backend.mcp_server"],
      "env": {
        "PYTHONPATH": "/path/to/labanmovementanalysis"
      }
    }
  }
}
```

## 🛠️ Enhanced MCP Tools

### 1. `analyze_video`
Comprehensive video analysis with enhanced features including SkateFormer AI and multiple pose models.

**Parameters:**
- `video_path` (string): Path or URL to video (supports YouTube, Vimeo, local files)
- `model` (string, optional): Advanced pose model selection:
  - **MediaPipe**: `mediapipe-lite`, `mediapipe-full`, `mediapipe-heavy`
  - **MoveNet**: `movenet-lightning`, `movenet-thunder`
  - **YOLO**: `yolo-v8-n/s/m/l`, `yolo-v11-n/s/m/l`

- `enable_visualization` (boolean, optional): Generate annotated video
- `include_keypoints` (boolean, optional): Include raw keypoint data
- `use_skateformer` (boolean, optional): Enable AI action recognition

**Examples:**
```
Analyze the dance video at https://youtube.com/watch?v=dQw4w9WgXcQ using SkateFormer AI
Analyze movement in video.mp4 using yolo-v11-s model with visualization
Process the exercise video with mediapipe-full and include keypoints
```

### 2. `get_analysis_summary`
Get human-readable summaries with enhanced AI insights.

**Parameters:**
- `analysis_id` (string): ID from previous analysis

**Enhanced Output Includes:**
- SkateFormer action recognition results
- Movement quality metrics (rhythm, complexity, symmetry)
- Temporal action segmentation
- Video source metadata (YouTube/Vimeo titles, etc.)

**Example:**
```
Get a detailed summary of analysis dance_2024-01-01T12:00:00 including AI insights
```

### 3. `list_available_models`
Comprehensive list of all 20+ pose estimation models with detailed specifications.

**Enhanced Model Information:**
- Performance characteristics (speed, accuracy, memory usage)
- Recommended use cases (real-time, research, production)
- Hardware requirements (CPU, GPU, memory)
- Keypoint specifications (17 COCO, 33 MediaPipe)

**Example:**
```
What pose estimation models are available for real-time processing?
List all YOLO v11 model variants with their specifications
```

### 4. `batch_analyze`
Enhanced batch processing with parallel execution and progress tracking.

**Parameters:**
- `video_paths` (array): List of video paths/URLs (supports mixed sources)
- `model` (string, optional): Pose estimation model for all videos
- `parallel` (boolean, optional): Enable parallel processing
- `use_skateformer` (boolean, optional): Enable AI analysis for all videos
- `output_format` (string, optional): Output format ("summary", "structured", "full")

**Enhanced Features:**
- Mixed source support (local files + YouTube URLs)
- Progress tracking and partial results
- Resource management and optimization
- Failure recovery and retry logic

**Examples:**
```
Analyze all dance videos in the playlist with SkateFormer AI
Batch process exercise videos using yolo-v11-s with parallel execution
```

### 5. `compare_movements`
Advanced movement comparison with AI-powered insights.

**Parameters:**
- `analysis_id1` (string): First analysis ID  
- `analysis_id2` (string): Second analysis ID
- `comparison_type` (string, optional): Type of comparison ("basic", "detailed", "ai_enhanced")

**Enhanced Comparison Features:**
- SkateFormer action similarity analysis
- Movement quality comparisons (rhythm, complexity, symmetry)
- Temporal pattern matching
- Statistical significance testing

**Example:**
```
Compare the movement patterns between the two dance analyses with AI insights
Detailed comparison of exercise form between beginner and expert videos
```

### 6. `real_time_analysis` (New)
Start/stop real-time WebRTC analysis.

**Parameters:**
- `action` (string): "start" or "stop"
- `model` (string, optional): Real-time optimized model
- `stream_config` (object, optional): WebRTC configuration

**Example:**
```
Start real-time movement analysis using mediapipe-lite
```

### 7. `filter_videos_advanced` (New)
Advanced video filtering with AI-powered criteria.

**Parameters:**
- `video_paths` (array): List of video paths/URLs
- `criteria` (object): Enhanced filtering criteria including:
  - Traditional LMA metrics (direction, intensity, fluidity)
  - SkateFormer actions (dancing, jumping, etc.)
  - Movement qualities (rhythm, complexity, symmetry)
  - Temporal characteristics (duration, segment count)

**Example:**
```
Filter videos for high-energy dance movements with good rhythm
Find exercise videos with proper form (high fluidity and symmetry)
```

## 🤖 Enhanced Agent API

### Comprehensive Python Agent API

```python
from gradio_labanmovementanalysis import LabanMovementAnalysis
from gradio_labanmovementanalysis.agent_api import (
    LabanAgentAPI,
    PoseModel,
    MovementDirection,
    MovementIntensity,
    analyze_and_summarize
)

# Initialize with all features enabled
analyzer = LabanMovementAnalysis(
    enable_skateformer=True,
    enable_webrtc=True,
    enable_visualization=True
)

agent_api = LabanAgentAPI(analyzer=analyzer)
```

### Advanced Analysis Workflows

```python
# YouTube video analysis with AI
result = agent_api.analyze(
    "https://youtube.com/watch?v=...",
    model=PoseModel.YOLO_V11_S,
    use_skateformer=True,
    generate_visualization=True
)

# Enhanced batch processing
results = agent_api.batch_analyze(
    ["video1.mp4", "https://youtube.com/watch?v=...", "https://vimeo.com/..."],
    model=PoseModel.YOLO_V11_S,
    parallel=True,
    use_skateformer=True
)

# AI-powered movement filtering
filtered = agent_api.filter_by_movement_advanced(
    video_paths,
    skateformer_actions=["dancing", "jumping"],
    movement_qualities={"rhythm": 0.8, "complexity": 0.6},
    traditional_criteria={
        "direction": MovementDirection.UP,
        "intensity": MovementIntensity.HIGH,
        "min_fluidity": 0.7
    }
)

# Real-time analysis control
agent_api.start_realtime_analysis(model=PoseModel.MEDIAPIPE_LITE)
live_metrics = agent_api.get_realtime_metrics()
agent_api.stop_realtime_analysis()
```

### Enhanced Quick Functions

```python
from gradio_labanmovementanalysis import (
    quick_analyze_enhanced,
    analyze_and_summarize_with_ai,
    compare_videos_detailed
)

# Enhanced analysis with AI
data = quick_analyze_enhanced(
    "https://youtube.com/watch?v=...",
    model="yolo-v11-s",
    use_skateformer=True
)

# AI-powered summary
summary = analyze_and_summarize_with_ai(
    "dance_video.mp4",
    include_skateformer=True,
    detail_level="comprehensive"
)

# Detailed video comparison
comparison = compare_videos_detailed(
    "video1.mp4", 
    "video2.mp4",
    include_ai_analysis=True
)
```

## 🌐 Enhanced Gradio 5 Agent Features

### Comprehensive API Endpoints

The unified Gradio 5 app exposes these endpoints optimized for agents:

1. **`/analyze_standard`** - Basic LMA analysis
2. **`/analyze_enhanced`** - Advanced analysis with all features
3. **`/analyze_agent`** - Agent-optimized structured output
4. **`/batch_analyze`** - Efficient multiple video processing
5. **`/filter_videos`** - Movement-based filtering
6. **`/compare_models`** - Model performance comparison
7. **`/real_time_start`** - Start WebRTC real-time analysis
8. **`/real_time_stop`** - Stop WebRTC real-time analysis

### Enhanced Gradio Client Usage

```python
from gradio_client import Client

# Connect to unified demo
client = Client("http://localhost:7860")

# Enhanced single analysis
result = client.predict(
    video_input="https://youtube.com/watch?v=...",
    model="yolo-v11-s",
    enable_viz=True,
    use_skateformer=True,
    include_keypoints=False,
    api_name="/analyze_enhanced"
)

# Agent-optimized batch processing
batch_results = client.predict(
    files=["video1.mp4", "video2.mp4"],
    model="yolo-v11-s",
    api_name="/batch_analyze"
)

# Advanced movement filtering
filtered_results = client.predict(
    files=video_list,
    direction_filter="up",
    intensity_filter="high", 
    fluidity_threshold=0.7,
    expansion_threshold=0.5,
    api_name="/filter_videos"
)

# Model comparison analysis
comparison = client.predict(
    video="test_video.mp4",
    model1="mediapipe-full",
    model2="yolo-v11-s",
    api_name="/compare_models"
)
```

## 📊 Enhanced Output Formats

### AI-Enhanced Summary Format
```
🎭 Movement Analysis Summary for "Dance Performance"
Source: YouTube (10.5 seconds, 30fps)
Model: YOLO-v11-S with SkateFormer AI

📊 Traditional LMA Metrics:
• Primary direction: up (65% of frames)
• Movement intensity: high (80% of frames)  
• Average speed: fast (2.3 units/frame)
• Fluidity score: 0.85/1.00 (very smooth)
• Expansion score: 0.72/1.00 (moderately extended)

🤖 SkateFormer AI Analysis:
• Detected actions: dancing (95% confidence), jumping (78% confidence)
• Movement qualities:
  - Rhythm: 0.89/1.00 (highly rhythmic)
  - Complexity: 0.76/1.00 (moderately complex)
  - Symmetry: 0.68/1.00 (slightly asymmetric)
  - Smoothness: 0.85/1.00 (very smooth)
  - Energy: 0.88/1.00 (high energy)

⏱️ Temporal Analysis:
• 7 movement segments identified
• Average segment duration: 1.5 seconds
• Transition quality: smooth (0.82/1.00)

🎯 Overall Assessment: Excellent dance performance with high energy, 
good rhythm, and smooth transitions. Slightly asymmetric but shows 
advanced movement complexity.
```

### Enhanced Structured Format
```json
{
    "success": true,
    "video_metadata": {
        "source": "youtube",
        "title": "Dance Performance",
        "duration": 10.5,
        "platform_id": "dQw4w9WgXcQ"
    },
    "model_info": {
        "pose_model": "yolo-v11-s",
        "ai_enhanced": true,
        "skateformer_enabled": true
    },
    "lma_metrics": {
        "direction": "up",
        "intensity": "high",
        "speed": "fast",
        "fluidity": 0.85,
        "expansion": 0.72
    },
    "skateformer_analysis": {
        "actions": [
            {"type": "dancing", "confidence": 0.95, "duration": 8.2},
            {"type": "jumping", "confidence": 0.78, "duration": 2.3}
        ],
        "movement_qualities": {
            "rhythm": 0.89,
            "complexity": 0.76,
            "symmetry": 0.68,
            "smoothness": 0.85,
            "energy": 0.88
        },
        "temporal_segments": 7,
        "transition_quality": 0.82
    },
    "performance_metrics": {
        "processing_time": 12.3,
        "frames_analyzed": 315,
        "keypoints_detected": 24
    }
}
```

### Comprehensive JSON Format
Complete analysis including frame-by-frame data, SkateFormer attention maps, movement trajectories, and statistical summaries.

## 🏗️ Enhanced Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Assistant Integration                  │
│          (Claude, GPT, Local Models via MCP)               │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   MCP Server                                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│  │   Video     │ │   Enhanced  │ │      Real-time          ││
│  │  Analysis   │ │    Batch    │ │      WebRTC             ││
│  │   Tools     │ │ Processing  │ │     Analysis            ││
│  └─────────────┘ └─────────────┘ └─────────────────────────┘│
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Enhanced Agent API Layer                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│  │  Movement   │ │ AI-Enhanced │ │     Advanced            ││
│  │  Filtering  │ │ Comparisons │ │    Workflows            ││
│  └─────────────┘ └─────────────┘ └─────────────────────────┘│
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│             Core Analysis Engine                            │
│                                                             │
│  📹 Video Input    🤖 Pose Models   🎭 SkateFormer AI      │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────────┐│
│  │Local Files  │   │MediaPipe(3) │   │  Action Recognition ││
│  │YouTube URLs │   │MoveNet(2)   │   │Movement Qualities   ││
│  │Vimeo URLs   │   │YOLO(8)      │   │Temporal Segments    ││
│  │Direct URLs  │   │            │   │Attention Analysis   ││
│  └─────────────┘   └─────────────┘   └─────────────────────┘│
│                                                             │
│  📊 LMA Engine     📹 WebRTC       🎨 Visualization        │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────────┐│
│  │Direction    │   │Live Camera  │   │  Pose Overlays      ││
│  │Intensity    │   │Real-time    │   │  Motion Trails      ││
│  │Speed/Flow   │   │Sub-100ms    │   │  Metric Displays    ││
│  │Expansion    │   │Adaptive FPS │   │  AI Visualizations  ││
│  └─────────────┘   └─────────────┘   └─────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## 📝 Advanced Agent Workflows

### 1. Comprehensive Dance Analysis Pipeline
```python
# Multi-source dance video analysis
videos = [
    "local_dance.mp4",
    "https://youtube.com/watch?v=dance1",
    "https://vimeo.com/dance2"
]

# Batch analyze with AI
results = agent_api.batch_analyze(
    videos,
    model=PoseModel.YOLO_V11_S,
    use_skateformer=True,
    parallel=True
)

# Filter for high-quality performances
excellent_dances = agent_api.filter_by_movement_advanced(
    videos,
    skateformer_actions=["dancing"],
    movement_qualities={
        "rhythm": 0.8,
        "complexity": 0.7,
        "energy": 0.8
    },
    traditional_criteria={
        "intensity": MovementIntensity.HIGH,
        "min_fluidity": 0.75
    }
)

# Generate comprehensive report
report = agent_api.generate_analysis_report(
    results,
    include_comparisons=True,
    include_recommendations=True
)
```

### 2. Real-time Exercise Form Checker
```python
# Start real-time analysis
agent_api.start_realtime_analysis(
    model=PoseModel.MEDIAPIPE_FULL,
    enable_skateformer=True
)

# Monitor form in real-time
while exercise_in_progress:
    metrics = agent_api.get_realtime_metrics()
    
    # Check form quality
    if metrics["fluidity"] < 0.6:
        send_feedback("Improve movement smoothness")
    
    if metrics["symmetry"] < 0.7:
        send_feedback("Balance left and right movements")
    
    time.sleep(0.1)  # 10Hz monitoring

# Stop and get session summary
agent_api.stop_realtime_analysis()
session_summary = agent_api.get_session_summary()
```

### 3. Movement Pattern Research Workflow
```python
# Large-scale analysis for research
research_videos = get_research_dataset()

# Batch process with comprehensive analysis
results = agent_api.batch_analyze(
    research_videos,
    model=PoseModel.YOLO_V11_L,  # High accuracy for research
    use_skateformer=True,
    include_keypoints=True,  # Full data for research
    parallel=True
)

# Statistical analysis
patterns = agent_api.extract_movement_patterns(
    results,
    pattern_types=["temporal", "spatial", "quality"],
    clustering_method="hierarchical"
)

# Generate research insights
insights = agent_api.generate_research_insights(
    patterns,
    include_visualizations=True,
    statistical_tests=True
)
```

## 🔧 Advanced Configuration & Customization

### Environment Variables

```bash
# Core configuration
export LABAN_DEFAULT_MODEL="mediapipe-full"
export LABAN_CACHE_DIR="/path/to/cache"
export LABAN_MAX_WORKERS=4

# Enhanced features
export LABAN_ENABLE_SKATEFORMER=true
export LABAN_ENABLE_WEBRTC=true
export LABAN_SKATEFORMER_MODEL_PATH="/path/to/skateformer"

# Performance tuning
export LABAN_GPU_ENABLED=true
export LABAN_BATCH_SIZE=8
export LABAN_REALTIME_FPS=30

# Video download configuration
export LABAN_YOUTUBE_QUALITY="720p"
export LABAN_MAX_DOWNLOAD_SIZE="500MB"
export LABAN_TEMP_DIR="/tmp/laban_downloads"
```

### Custom MCP Tools

```python
# Add custom MCP tool
from backend.mcp_server import server

@server.tool("custom_movement_analysis")
async def custom_analysis(
    video_path: str,
    custom_params: dict
) -> dict:
    """Custom movement analysis with specific parameters."""
    # Your custom implementation
    return results

# Register enhanced filters
@server.tool("filter_by_sport_type")
async def filter_by_sport(
    videos: list,
    sport_type: str
) -> dict:
    """Filter videos by detected sport type using SkateFormer."""
    # Implementation using SkateFormer sport classification
    return filtered_videos
```

### WebRTC Configuration

```python
# Custom WebRTC configuration
webrtc_config = {
    "video_constraints": {
        "width": 1280,
        "height": 720,
        "frameRate": 30
    },
    "processing_config": {
        "max_latency_ms": 100,
        "quality_adaptation": True,
        "model_switching": True
    }
}

agent_api.configure_webrtc(webrtc_config)
```

## 🤝 Contributing to Agent Features

### Adding New MCP Tools

1. Define tool in `backend/mcp_server.py`
2. Implement core logic in agent API
3. Add comprehensive documentation
4. Include usage examples
5. Write integration tests

### Extending Agent API

1. Add methods to `LabanAgentAPI` class
2. Ensure compatibility with existing workflows
3. Add structured output formats
4. Include error handling and validation
5. Update documentation

### Enhancing SkateFormer Integration

1. Extend action recognition types
2. Add custom movement quality metrics  
3. Implement temporal analysis features
4. Add visualization components
5. Validate with research datasets

## 📚 Resources & References

- [MCP Specification](https://github.com/anthropics/mcp)
- [SkateFormer Research Paper](https://kaist-viclab.github.io/SkateFormer_site/)
- [Gradio 5 Documentation](https://www.gradio.app/docs)
- [Unified Demo Application](demo/app.py)
- [Core Component Code](backend/gradio_labanmovementanalysis/)

## 🎯 Production Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

COPY . /app
WORKDIR /app

RUN pip install -r backend/requirements.txt
RUN pip install -r backend/requirements-mcp.txt

EXPOSE 7860 8080

CMD ["python", "-m", "backend.mcp_server"]
```

### Kubernetes Configuration

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: laban-mcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: laban-mcp
  template:
    metadata:
      labels:
        app: laban-mcp
    spec:
      containers:
      - name: mcp-server
        image: laban-movement-analysis:latest
        ports:
        - containerPort: 8080
        env:
        - name: LABAN_MAX_WORKERS
          value: "2"
        - name: LABAN_ENABLE_SKATEFORMER
          value: "true"
```

---

**🤖 Transform your AI assistant into a movement analysis expert with comprehensive MCP integration and agent-ready automation.** 
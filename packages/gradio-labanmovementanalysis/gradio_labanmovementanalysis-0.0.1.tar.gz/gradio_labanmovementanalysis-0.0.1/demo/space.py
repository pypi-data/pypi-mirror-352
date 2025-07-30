
import gradio as gr
from app import demo as app
import os

_docs = {'LabanMovementAnalysis': {'description': 'Gradio component for video-based pose analysis with Laban Movement Analysis metrics.', 'members': {'__init__': {'default_model': {'type': 'str', 'default': '"mediapipe"', 'description': 'Default pose estimation model ("mediapipe", "movenet", "yolo")'}, 'enable_visualization': {'type': 'bool', 'default': 'True', 'description': 'Whether to generate visualization video by default'}, 'include_keypoints': {'type': 'bool', 'default': 'False', 'description': 'Whether to include raw keypoints in JSON output'}, 'enable_webrtc': {'type': 'bool', 'default': 'False', 'description': 'Whether to enable WebRTC real-time analysis'}, 'label': {'type': 'typing.Optional[str][str, None]', 'default': 'None', 'description': 'Component label'}, 'every': {'type': 'typing.Optional[float][float, None]', 'default': 'None', 'description': None}, 'show_label': {'type': 'typing.Optional[bool][bool, None]', 'default': 'None', 'description': None}, 'container': {'type': 'bool', 'default': 'True', 'description': None}, 'scale': {'type': 'typing.Optional[int][int, None]', 'default': 'None', 'description': None}, 'min_width': {'type': 'int', 'default': '160', 'description': None}, 'interactive': {'type': 'typing.Optional[bool][bool, None]', 'default': 'None', 'description': None}, 'visible': {'type': 'bool', 'default': 'True', 'description': None}, 'elem_id': {'type': 'typing.Optional[str][str, None]', 'default': 'None', 'description': None}, 'elem_classes': {'type': 'typing.Optional[typing.List[str]][\n    typing.List[str][str], None\n]', 'default': 'None', 'description': None}, 'render': {'type': 'bool', 'default': 'True', 'description': None}}, 'postprocess': {'value': {'type': 'typing.Any', 'description': 'Analysis results'}}, 'preprocess': {'return': {'type': 'typing.Dict[str, typing.Any][str, typing.Any]', 'description': 'Processed data for analysis'}, 'value': None}}, 'events': {}}, '__meta__': {'additional_interfaces': {}, 'user_fn_refs': {'LabanMovementAnalysis': []}}}

abs_path = os.path.join(os.path.dirname(__file__), "css.css")

with gr.Blocks(
    css=abs_path,
    theme=gr.themes.Default(
        font_mono=[
            gr.themes.GoogleFont("Inconsolata"),
            "monospace",
        ],
    ),
) as demo:
    gr.Markdown(
"""
# `gradio_labanmovementanalysis`

<div style="display: flex; gap: 7px;">
<img alt="Static Badge" src="https://img.shields.io/badge/version%20-%200.0.1%20-%20orange">  
</div>

A Gradio 5 component for video movement analysis using Laban Movement Analysis (LMA) with MCP support for AI agents
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
## Installation

```bash
pip install gradio_labanmovementanalysis
```

## Usage

```python
\"\"\"
Unified Laban Movement Analysis Demo
Comprehensive interface combining all features: 
- Standard LMA analysis
- Enhanced features (WebRTC, YouTube/Vimeo)
- Agent API (batch processing, filtering)
- Real-time analysis
- Model comparison

Created by: Csaba Bolyós (BladeSzaSza)
Contact: bladeszasza@gmail.com
GitHub: https://github.com/bladeszasza
LinkedIn: https://www.linkedin.com/in/csaba-bolyós-00a11767/
Hugging Face: https://huggingface.co/BladeSzaSza

Heavy Beta Version - Under Active Development
\"\"\"

import gradio as gr
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from gradio_labanmovementanalysis import LabanMovementAnalysis

# Import agent API if available
try:
    from gradio_labanmovementanalysis.agent_api import (
        LabanAgentAPI,
        PoseModel,
        MovementDirection,
        MovementIntensity
    )
    HAS_AGENT_API = True
except ImportError:
    HAS_AGENT_API = False

# Import WebRTC components if available
try:
    from gradio_webrtc import WebRTC
    from gradio_labanmovementanalysis.webrtc_handler import (
        webrtc_detection,
        get_rtc_configuration
    )
    HAS_WEBRTC = True
except ImportError as e:
    print(f"WebRTC import failed: {e}")
    HAS_WEBRTC = False

# Initialize components
try:
    # Initialize with WebRTC support
    analyzer = LabanMovementAnalysis(
        enable_webrtc=True,
        enable_visualization=True
    )
    print("✅ Core features initialized successfully")
except Exception as e:
    print(f"Warning: Some features may not be available: {e}")
    analyzer = LabanMovementAnalysis(enable_webrtc=False)

# Initialize agent API if available
agent_api = None
if HAS_AGENT_API:
    try:
        agent_api = LabanAgentAPI()
    except Exception as e:
        print(f"Warning: Agent API not available: {e}")
        agent_api = None


def process_video_standard(video, model, enable_viz, include_keypoints):
    \"\"\"Standard video processing function.\"\"\"
    if video is None:
        return None, None
    
    try:
        json_output, video_output = analyzer.process_video(
            video,
            model=model,
            enable_visualization=enable_viz,
            include_keypoints=include_keypoints
        )
        return json_output, video_output
    except Exception as e:
        return {"error": str(e)}, None


def process_video_enhanced(video_input, model, enable_viz, include_keypoints):
    \"\"\"Enhanced video processing with all new features.\"\"\"
    if not video_input:
        return {"error": "No video provided"}, None
    
    try:
        # Handle both file upload and URL input
        video_path = video_input.name if hasattr(video_input, 'name') else video_input
        
        json_result, viz_result = analyzer.process_video(
            video_path,
            model=model,
            enable_visualization=enable_viz,
            include_keypoints=include_keypoints
        )
        return json_result, viz_result
    except Exception as e:
        error_result = {"error": str(e)}
        return error_result, None


def process_video_for_agent(video, model, output_format="summary"):
    \"\"\"Process video with agent-friendly output format.\"\"\"
    if not HAS_AGENT_API or agent_api is None:
        return {"error": "Agent API not available"}
    
    if not video:
        return {"error": "No video provided"}
    
    try:
        model_enum = PoseModel(model)
        result = agent_api.analyze(video, model=model_enum, generate_visualization=False)
        
        if output_format == "summary":
            return {"summary": agent_api.get_movement_summary(result)}
        elif output_format == "structured":
            return {
                "success": result.success,
                "direction": result.dominant_direction.value,
                "intensity": result.dominant_intensity.value,
                "speed": result.dominant_speed,
                "fluidity": result.fluidity_score,
                "expansion": result.expansion_score,
                "segments": len(result.movement_segments)
            }
        else:  # json
            return result.raw_data
    except Exception as e:
        return {"error": str(e)}


def batch_process_videos(files, model):
    \"\"\"Process multiple videos in batch.\"\"\"
    if not HAS_AGENT_API or agent_api is None:
        return {"error": "Agent API not available"}
    
    if not files:
        return {"error": "No videos provided"}
    
    try:
        video_paths = [f.name for f in files]
        results = agent_api.batch_analyze(video_paths, model=PoseModel(model), parallel=True)
        
        output = {
            "total_videos": len(results),
            "successful": sum(1 for r in results if r.success),
            "failed": sum(1 for r in results if not r.success),
            "results": []
        }
        
        for result in results:
            output["results"].append({
                "video": Path(result.video_path).name,
                "success": result.success,
                "summary": agent_api.get_movement_summary(result) if result.success else result.error
            })
        
        return output
    except Exception as e:
        return {"error": str(e)}


def filter_videos_by_movement(files, direction, intensity, min_fluidity, min_expansion):
    \"\"\"Filter videos based on movement characteristics.\"\"\"
    if not HAS_AGENT_API or agent_api is None:
        return {"error": "Agent API not available"}
    
    if not files:
        return {"error": "No videos provided"}
    
    try:
        video_paths = [f.name for f in files]
        
        dir_filter = MovementDirection(direction) if direction != "any" else None
        int_filter = MovementIntensity(intensity) if intensity != "any" else None
        
        filtered = agent_api.filter_by_movement(
            video_paths,
            direction=dir_filter,
            intensity=int_filter,
            min_fluidity=min_fluidity if min_fluidity > 0 else None,
            min_expansion=min_expansion if min_expansion > 0 else None
        )
        
        return {
            "total_analyzed": len(video_paths),
            "matching_videos": len(filtered),
            "matches": [
                {
                    "video": Path(r.video_path).name,
                    "direction": r.dominant_direction.value,
                    "intensity": r.dominant_intensity.value,
                    "fluidity": r.fluidity_score,
                    "expansion": r.expansion_score
                }
                for r in filtered
            ]
        }
    except Exception as e:
        return {"error": str(e)}


def compare_models(video, model1, model2):
    \"\"\"Compare two different pose models on the same video.\"\"\"
    if not video:
        return "No video provided"
    
    try:
        # Analyze with both models
        result1, _ = analyzer.process_video(video, model=model1, enable_visualization=False)
        result2, _ = analyzer.process_video(video, model=model2, enable_visualization=False)
        
        # Extract key metrics for comparison
        def extract_metrics(result):
            summary = result.get("movement_analysis", {}).get("summary", {})
            return {
                "direction": summary.get("direction", {}).get("dominant", "unknown"),
                "intensity": summary.get("intensity", {}).get("dominant", "unknown"), 
                "speed": summary.get("speed", {}).get("dominant", "unknown"),
                "frame_count": result.get("video_info", {}).get("frame_count", 0)
            }
        
        metrics1 = extract_metrics(result1)
        metrics2 = extract_metrics(result2)
        
        # Create comparison table data
        comparison_data = [
            ["Direction", metrics1["direction"], metrics2["direction"], 
             "✓" if metrics1["direction"] == metrics2["direction"] else "✗"],
            ["Intensity", metrics1["intensity"], metrics2["intensity"],
             "✓" if metrics1["intensity"] == metrics2["intensity"] else "✗"],
            ["Speed", metrics1["speed"], metrics2["speed"],
             "✓" if metrics1["speed"] == metrics2["speed"] else "✗"],
            ["Frames Processed", str(metrics1["frame_count"]), str(metrics2["frame_count"]),
             "✓" if metrics1["frame_count"] == metrics2["frame_count"] else "✗"]
        ]
        
        return comparison_data
        
    except Exception as e:
        return [["Error", str(e), "", ""]]


def start_webrtc_stream(model):
    \"\"\"Start WebRTC real-time analysis.\"\"\"
    try:
        success = analyzer.start_webrtc_stream(model)
        if success:
            return "🟢 Stream Active", {"status": "streaming", "model": model}
        else:
            return "🔴 Failed to start", {"status": "error"}
    except Exception as e:
        return f"🔴 Error: {str(e)}", {"status": "error"}


def stop_webrtc_stream():
    \"\"\"Stop WebRTC real-time analysis.\"\"\"
    try:
        success = analyzer.stop_webrtc_stream()
        if success:
            return "🟡 Stream Stopped", {"status": "stopped"}
        else:
            return "🔴 Failed to stop", {"status": "error"}
    except Exception as e:
        return f"🔴 Error: {str(e)}", {"status": "error"}


def create_unified_demo():
    \"\"\"Create the unified comprehensive demo.\"\"\"
    
    with gr.Blocks(
        title="Laban Movement Analysis - Complete Suite by Csaba Bolyós",
        theme=gr.themes.Soft(),
        css=\"\"\"
        .main-header {
            background: linear-gradient(135deg, #40826D 0%, #2E5E4A 50%, #1B3A2F 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .feature-card {
            border: 1px solid #e1e5e9;
            border-radius: 8px;
            padding: 16px;
            margin: 8px 0;
            background: #f8f9fa;
        }
        .json-output {
            max-height: 600px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 12px;
        }
        .author-info {
            background: linear-gradient(135deg, #40826D 0%, #2E5E4A 100%);
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            text-align: center;
        }
        \"\"\"
    ) as demo:
        
        # Main Header
        gr.HTML(\"\"\"
        <div class="main-header">
            <h1>🎭 Laban Movement Analysis - Complete Suite</h1>
            <p style="font-size: 18px; margin: 10px 0;">
                Professional movement analysis with pose estimation, AI action recognition, 
                real-time processing, and agent automation
            </p>
            <p style="font-size: 14px; opacity: 0.9;">
                Supports YouTube/Vimeo URLs • WebRTC Streaming • 20+ Pose Models • MCP Integration
            </p>
            <p style="font-size: 12px; margin-top: 15px; opacity: 0.8;">
                <strong>Version 0.01-beta</strong> - Heavy Beta Under Active Development
            </p>
        </div>
        \"\"\")
     
        with gr.Tabs():
            # Tab 1: Standard Analysis
            with gr.Tab("🎬 Standard Analysis"):
                gr.Markdown(\"\"\"
                ### Classic Laban Movement Analysis
                Upload a video file to analyze movement using traditional LMA metrics with pose estimation.
                \"\"\")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        video_input_std = gr.Video(
                            label="Upload Video",
                            sources=["upload"],
                            format="mp4"
                        )
                        
                        model_dropdown_std = gr.Dropdown(
                            choices=["mediapipe", "movenet", "yolo"],
                            value="mediapipe",
                            label="Pose Estimation Model"
                        )
                        
                        with gr.Row():
                            enable_viz_std = gr.Checkbox(
                                value=True,
                                label="Generate Visualization"
                            )
                            
                            include_keypoints_std = gr.Checkbox(
                                value=False,
                                label="Include Keypoints"
                            )
                        
                        process_btn_std = gr.Button("Analyze Movement", variant="primary")
                        
                        gr.Examples(
                            examples=[
                                ["examples/balette.mov"],
                                ["examples/balette.mp4"],
                            ],
                            inputs=video_input_std,
                            label="Example Videos"
                        )
                    
                    with gr.Column(scale=2):
                        with gr.Tab("Analysis Results"):
                            json_output_std = gr.JSON(
                                label="Movement Analysis (JSON)",
                                elem_classes=["json-output"]
                            )
                        
                        with gr.Tab("Visualization"):
                            video_output_std = gr.Video(
                                label="Annotated Video",
                                format="mp4"
                            )
                            
                            gr.Markdown(\"\"\"
                            **Visualization Guide:**
                            - 🦴 **Skeleton**: Pose keypoints and connections
                            - 🌊 **Trails**: Motion history (fading lines)
                            - ➡️ **Arrows**: Movement direction indicators
                            - 🎨 **Colors**: Green (low) → Orange (medium) → Red (high) intensity
                            \"\"\")
                
                process_btn_std.click(
                    fn=process_video_standard,
                    inputs=[video_input_std, model_dropdown_std, enable_viz_std, include_keypoints_std],
                    outputs=[json_output_std, video_output_std],
                    api_name="analyze_standard"
                )
            
            # Tab 2: Enhanced Analysis
            with gr.Tab("🚀 Enhanced Analysis"):
                gr.Markdown(\"\"\"
                ### Advanced Analysis with AI and URL Support
                Analyze videos from URLs (YouTube/Vimeo), use advanced pose models, and get AI-powered insights.
                \"\"\")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.HTML('<div class="feature-card">')
                        gr.Markdown("**Video Input**")
                        
                        # Changed from textbox to file upload as requested
                        video_input_enh = gr.File(
                            label="Upload Video or Drop File",
                            file_types=["video"],
                            type="filepath"
                        )
                        
                        # URL input option
                        url_input_enh = gr.Textbox(
                            label="Or Enter Video URL",
                            placeholder="YouTube URL, Vimeo URL, or direct video URL",
                            info="Leave file upload empty to use URL"
                        )
                        
                        gr.Examples(
                            examples=[
                                ["examples/balette.mov"],
                                ["https://www.youtube.com/shorts/RX9kH2l3L8U"],
                                ["https://vimeo.com/815392738"]
                            ],
                            inputs=url_input_enh,
                            label="Example URLs"
                        )
                        
                        gr.Markdown("**Model Selection**")
                        
                        model_select_enh = gr.Dropdown(
                            choices=[
                                # MediaPipe variants
                                "mediapipe-lite", "mediapipe-full", "mediapipe-heavy",
                                # MoveNet variants  
                                "movenet-lightning", "movenet-thunder",
                                # YOLO variants (added X models)
                                "yolo-v8-n", "yolo-v8-s", "yolo-v8-m", "yolo-v8-l", "yolo-v8-x",
                                # YOLO v11 variants
                                "yolo-v11-n", "yolo-v11-s", "yolo-v11-m", "yolo-v11-l", "yolo-v11-x"
                            ],
                            value="mediapipe-full",
                            label="Advanced Pose Models",
                            info="17+ model variants available"
                        )
                        
                        gr.Markdown("**Analysis Options**")
                        
                        with gr.Row():
                            enable_viz_enh = gr.Checkbox(value=True, label="Visualization")
                        
                        with gr.Row():
                            include_keypoints_enh = gr.Checkbox(value=False, label="Raw Keypoints")
                        
                        analyze_btn_enh = gr.Button("🚀 Enhanced Analysis", variant="primary", size="lg")
                        gr.HTML('</div>')
                    
                    with gr.Column(scale=2):
                        with gr.Tab("📊 Analysis"):
                            analysis_output_enh = gr.JSON(label="Enhanced Analysis Results")
                        
                        with gr.Tab("🎥 Visualization"):
                            viz_output_enh = gr.Video(label="Annotated Video")
                
                def process_enhanced_input(file_input, url_input, model, enable_viz, include_keypoints):
                    \"\"\"Process either file upload or URL input.\"\"\"
                    video_source = file_input if file_input else url_input
                    return process_video_enhanced(video_source, model, enable_viz, include_keypoints)
                
                analyze_btn_enh.click(
                    fn=process_enhanced_input,
                    inputs=[video_input_enh, url_input_enh, model_select_enh, enable_viz_enh, include_keypoints_enh],
                    outputs=[analysis_output_enh, viz_output_enh],
                    api_name="analyze_enhanced"
                )
            
            # Tab 3: Agent API
            with gr.Tab("🤖 Agent API"):
                gr.Markdown(\"\"\"
                ### AI Agent & Automation Features
                Batch processing, filtering, and structured outputs designed for AI agents and automation.
                \"\"\")
                
                with gr.Tabs():
                    with gr.Tab("Single Analysis"):
                        with gr.Row():
                            with gr.Column():
                                video_input_agent = gr.Video(label="Upload Video", sources=["upload"])
                                model_select_agent = gr.Dropdown(
                                    choices=["mediapipe", "movenet", "yolo"],
                                    value="mediapipe",
                                    label="Model"
                                )
                                output_format_agent = gr.Radio(
                                    choices=["summary", "structured", "json"],
                                    value="summary",
                                    label="Output Format"
                                )
                                analyze_btn_agent = gr.Button("Analyze", variant="primary")
                            
                            with gr.Column():
                                output_display_agent = gr.JSON(label="Agent Output")
                        
                        analyze_btn_agent.click(
                            fn=process_video_for_agent,
                            inputs=[video_input_agent, model_select_agent, output_format_agent],
                            outputs=output_display_agent,
                            api_name="analyze_agent"
                        )
                    
                    with gr.Tab("Batch Processing"):
                        with gr.Row():
                            with gr.Column():
                                batch_files = gr.File(
                                    label="Upload Multiple Videos",
                                    file_count="multiple",
                                    file_types=["video"]
                                )
                                batch_model = gr.Dropdown(
                                    choices=["mediapipe", "movenet", "yolo"],
                                    value="mediapipe",
                                    label="Model"
                                )
                                batch_btn = gr.Button("Process Batch", variant="primary")
                            
                            with gr.Column():
                                batch_output = gr.JSON(label="Batch Results")
                        
                        batch_btn.click(
                            fn=batch_process_videos,
                            inputs=[batch_files, batch_model],
                            outputs=batch_output,
                            api_name="batch_analyze"
                        )
                    
                    with gr.Tab("Movement Filter"):
                        with gr.Row():
                            with gr.Column():
                                filter_files = gr.File(
                                    label="Videos to Filter",
                                    file_count="multiple",
                                    file_types=["video"]
                                )
                                
                                with gr.Group():
                                    direction_filter = gr.Dropdown(
                                        choices=["any", "up", "down", "left", "right", "stationary"],
                                        value="any",
                                        label="Direction Filter"
                                    )
                                    intensity_filter = gr.Dropdown(
                                        choices=["any", "low", "medium", "high"],
                                        value="any",
                                        label="Intensity Filter"
                                    )
                                    fluidity_threshold = gr.Slider(0.0, 1.0, 0.0, label="Min Fluidity")
                                    expansion_threshold = gr.Slider(0.0, 1.0, 0.0, label="Min Expansion")
                                
                                filter_btn = gr.Button("Apply Filters", variant="primary")
                            
                            with gr.Column():
                                filter_output = gr.JSON(label="Filtered Results")
                        
                        filter_btn.click(
                            fn=filter_videos_by_movement,
                            inputs=[filter_files, direction_filter, intensity_filter,
                                   fluidity_threshold, expansion_threshold],
                            outputs=filter_output,
                            api_name="filter_videos"
                        )
            
            # Tab 4: Real-time WebRTC
            with gr.Tab("📹 Real-time Analysis"):
                gr.Markdown(\"\"\"
                ### Live Camera Movement Analysis
                Real-time pose detection and movement analysis from your webcam using WebRTC.
                **Grant camera permissions when prompted for best experience.**
                \"\"\")
                
                # Official Gradio WebRTC approach (compatible with NumPy 1.x)
                if HAS_WEBRTC:
                    
                    # Get RTC configuration
                    rtc_config = get_rtc_configuration()
                    
                    # Custom CSS following official guide
                    css_webrtc = \"\"\"
                    .my-group {max-width: 480px !important; max-height: 480px !important;}
                    .my-column {display: flex !important; justify-content: center !important; align-items: center !important;}
                    \"\"\"
                    
                    with gr.Column(elem_classes=["my-column"]):
                        with gr.Group(elem_classes=["my-group"]):
                            # Official WebRTC Component
                            webrtc_stream = WebRTC(
                                label="🎥 Live Camera Stream", 
                                rtc_configuration=rtc_config
                            )
                        
                            webrtc_model = gr.Dropdown(
                                choices=["mediapipe-lite", "movenet-lightning", "yolo-v11-n"],
                                value="mediapipe-lite",
                                label="Pose Model",
                                info="Optimized for real-time processing"
                            )
                            
                            confidence_slider = gr.Slider(
                                label="Detection Confidence",
                                minimum=0.0,
                                maximum=1.0,
                                step=0.05,
                                value=0.5,
                                info="Higher = fewer false positives"
                            )
                    
                    # Official WebRTC streaming setup following Gradio guide
                    webrtc_stream.stream(
                        fn=webrtc_detection,
                        inputs=[webrtc_stream, webrtc_model, confidence_slider],
                        outputs=[webrtc_stream],
                        time_limit=10  # Following official guide: 10 seconds per user
                    )
                    
                    # Info display
                    gr.HTML(\"\"\"
                    <div style="background: #e8f4fd; padding: 15px; border-radius: 8px; margin-top: 10px;">
                        <h4>📹 WebRTC Pose Analysis</h4>
                        <p style="margin: 5px 0;">Real-time movement analysis using your webcam</p>
                        
                        <h4>🔒 Privacy</h4>
                        <p style="margin: 5px 0;">Processing happens locally - no video data stored</p>
                        
                        <h4>💡 Usage</h4>
                        <ul style="margin: 5px 0; padding-left: 20px;">
                            <li>Grant camera permission when prompted</li>
                            <li>Move in front of camera to see pose detection</li>
                            <li>Adjust confidence threshold as needed</li>
                        </ul>
                    </div>
                                         \"\"\")
                    
                else:
                    # Fallback if WebRTC component not available  
                    gr.HTML(\"\"\"
                    <div style="text-align: center; padding: 50px; border: 2px dashed #ff6b6b; border-radius: 8px; background: #ffe0e0;">
                        <h3>📦 WebRTC Component Required</h3>
                        <p><strong>To enable real-time camera analysis, install:</strong></p>
                        <code style="background: #f0f0f0; padding: 10px; border-radius: 4px; display: block; margin: 10px 0;">
                            pip install gradio-webrtc twilio
                        </code>
                        <p style="margin-top: 15px;"><em>Use Enhanced Analysis tab for video files meanwhile</em></p>
                    </div>
                    \"\"\")
            
            # Tab 5: Model Comparison
            with gr.Tab("⚖️ Model Comparison"):
                gr.Markdown(\"\"\"
                ### Compare Pose Estimation Models
                Analyze the same video with different models to compare accuracy and results.
                \"\"\")
                
                with gr.Column():
                    comparison_video = gr.Video(
                        label="Video for Comparison",
                        sources=["upload"]
                    )
                    
                    with gr.Row():
                        model1_comp = gr.Dropdown(
                            choices=["mediapipe-full", "movenet-thunder", "yolo-v11-s"],
                            value="mediapipe-full",
                            label="Model 1"
                        )
                        
                        model2_comp = gr.Dropdown(
                            choices=["mediapipe-full", "movenet-thunder", "yolo-v11-s"],
                            value="yolo-v11-s",
                            label="Model 2"
                        )
                    
                    compare_btn = gr.Button("🔄 Compare Models", variant="primary")
                    
                    comparison_results = gr.DataFrame(
                        headers=["Metric", "Model 1", "Model 2", "Match"],
                        label="Comparison Results"
                    )
                
                compare_btn.click(
                    fn=compare_models,
                    inputs=[comparison_video, model1_comp, model2_comp],
                    outputs=comparison_results,
                    api_name="compare_models"
                )
            
            # Tab 6: Documentation
            with gr.Tab("📚 Documentation"):
                gr.Markdown(\"\"\"
                # Complete Feature Documentation
                
                ## 🎥 Video Input Support
                - **Local Files**: MP4, AVI, MOV, WebM formats
                - **YouTube**: Automatic download from YouTube URLs
                - **Vimeo**: Automatic download from Vimeo URLs
                - **Direct URLs**: Any direct video file URL
                
                ## 🤖 Pose Estimation Models
                
                ### MediaPipe (Google) - 33 3D Landmarks
                - **Lite**: Fastest CPU performance
                - **Full**: Balanced accuracy/speed (recommended)
                - **Heavy**: Highest accuracy
                
                ### MoveNet (Google) - 17 COCO Keypoints  
                - **Lightning**: Mobile-optimized, very fast
                - **Thunder**: Higher accuracy variant
                
                ### YOLO (Ultralytics) - 17 COCO Keypoints
                - **v8 variants**: n/s/m/l/x sizes (nano to extra-large)
                - **v11 variants**: Latest with improved accuracy (n/s/m/l/x)
                - **Multi-person**: Supports multiple people in frame
                
                ## 📹 Real-time WebRTC
                
                - **Live Camera**: Direct webcam access via WebRTC
                - **Low Latency**: Sub-100ms processing
                - **Adaptive Quality**: Automatic performance optimization
                - **Live Overlay**: Real-time pose and metrics display
                
                ## 🤖 Agent & MCP Integration
                
                ### API Endpoints
                - `/analyze_standard` - Basic LMA analysis
                - `/analyze_enhanced` - Advanced analysis with all features
                - `/analyze_agent` - Agent-optimized output
                - `/batch_analyze` - Multiple video processing
                - `/filter_videos` - Movement-based filtering
                - `/compare_models` - Model comparison
                
                ### MCP Server
                ```bash
                # Start MCP server for AI assistants
                python -m backend.mcp_server
                ```
                
                ### Python API
                ```python
                from gradio_labanmovementanalysis import LabanMovementAnalysis
                
                # Initialize with all features
                analyzer = LabanMovementAnalysis(
                    enable_webrtc=True
                )
                
                # Analyze YouTube video
                result, viz = analyzer.process_video(
                    "https://youtube.com/watch?v=...",
                    model="yolo-v11-s"
                )
                ```
                
                ## 📊 Output Formats
                
                ### Summary Format
                Human-readable movement analysis summary.
                
                ### Structured Format  
                ```json
                {
                    "success": true,
                    "direction": "up", 
                    "intensity": "medium",
                    "fluidity": 0.85,
                    "expansion": 0.72
                }
                ```
                
                ### Full JSON Format
                Complete frame-by-frame analysis with all metrics.
                
                ## 🎯 Applications
                
                - **Sports**: Technique analysis and performance tracking
                - **Dance**: Choreography analysis and movement quality
                - **Healthcare**: Physical therapy and rehabilitation
                - **Research**: Large-scale movement pattern studies
                - **Entertainment**: Interactive applications and games
                - **Education**: Movement teaching and body awareness
                
                ## 🔗 Integration Examples
                
                ### Gradio Client
                ```python
                from gradio_client import Client
                
                client = Client("http://localhost:7860")
                result = client.predict(
                    video="path/to/video.mp4",
                    model="mediapipe-full",
                    api_name="/analyze_enhanced"
                )
                ```
                
                ### Batch Processing
                ```python
                results = client.predict(
                    files=["video1.mp4", "video2.mp4"],
                    model="yolo-v11-s", 
                    api_name="/batch_analyze"
                )
                ```
                \"\"\")
                gr.HTML(\"\"\"
                        <div class="author-info">
                            <p><strong>Created by:</strong> Csaba Bolyós (BladeSzaSza)</p>
                            <p style="margin: 5px 0;">
                                <a href="https://github.com/bladeszasza" style="color: #a8e6cf; text-decoration: none;">🔗 GitHub</a> • 
                                <a href="https://huggingface.co/BladeSzaSza" style="color: #a8e6cf; text-decoration: none;">🤗 Hugging Face</a> • 
                                <a href="https://www.linkedin.com/in/csaba-bolyós-00a11767/" style="color: #a8e6cf; text-decoration: none;">💼 LinkedIn</a>
                            </p>
                            <p style="font-size: 12px; opacity: 0.9;">Contact: bladeszasza@gmail.com</p>
                        </div>
                        \"\"\")
                        
                        # Footer with proper attribution
        gr.HTML(\"\"\"
        <div style="text-align: center; padding: 20px; margin-top: 30px; border-top: 1px solid #eee;">
            <p style="color: #666; margin-bottom: 10px;">
                🎭 Laban Movement Analysis - Complete Suite | Heavy Beta Version
            </p>
            <p style="color: #666; font-size: 12px;">
                Created by <strong>Csaba Bolyós</strong> | Powered by MediaPipe, MoveNet & YOLO
            </p>
            <p style="color: #666; font-size: 10px; margin-top: 10px;">
                <a href="https://github.com/bladeszasza" style="color: #40826D;">GitHub</a> • 
                <a href="https://huggingface.co/BladeSzaSza" style="color: #40826D;">Hugging Face</a> • 
                <a href="https://www.linkedin.com/in/csaba-bolyós-00a11767/" style="color: #40826D;">LinkedIn</a>
            </p>
        </div>
        \"\"\")
    
    return demo


if __name__ == "__main__":
    demo = create_unified_demo()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        favicon_path=None
    )

```
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `LabanMovementAnalysis`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["LabanMovementAnalysis"]["members"]["__init__"], linkify=[])




    gr.Markdown("""

### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As input:** Is passed, processed data for analysis.
- **As output:** Should return, analysis results.

 ```python
def predict(
    value: typing.Dict[str, typing.Any][str, typing.Any]
) -> typing.Any:
    return value
```
""", elem_classes=["md-custom", "LabanMovementAnalysis-user-fn"], header_links=True)




    demo.load(None, js=r"""function() {
    const refs = {};
    const user_fn_refs = {
          LabanMovementAnalysis: [], };
    requestAnimationFrame(() => {

        Object.entries(user_fn_refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}-user-fn`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })

        Object.entries(refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })
    })
}

""")

demo.launch()

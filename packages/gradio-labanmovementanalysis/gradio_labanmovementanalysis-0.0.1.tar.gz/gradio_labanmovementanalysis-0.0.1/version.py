"""
Laban Movement Analysis - Complete Suite
Version Information

Created by: Csaba Bolyós (BladeSzaSza)
Contact: bladeszasza@gmail.com
GitHub: https://github.com/bladeszasza
LinkedIn: https://www.linkedin.com/in/csaba-bolyós-00a11767/
Hugging Face: https://huggingface.co/BladeSzaSza
"""

__version__ = "0.01-beta"
__author__ = "Csaba Bolyós (BladeSzaSza)"
__email__ = "bladeszasza@gmail.com"
__description__ = "Professional movement analysis with pose estimation, AI action recognition, real-time processing, and agent automation"
__url__ = "https://huggingface.co/spaces/BladeSzaSza/laban-movement-analysis"

# Release Information
RELEASE_NOTES = """
🎭 Laban Movement Analysis - Complete Suite v0.01-beta

✨ INITIAL BETA RELEASE ✨

🌟 Core Features:
- 17+ Pose Estimation Models (MediaPipe, MoveNet, YOLO v8/v11 with x variants)
- YouTube & Vimeo URL Support
- Real-time WebRTC Camera Analysis
- Agent API with MCP Integration
- Batch Processing & Movement Filtering
- Professional VIRIDIAN UI Theme

🚀 Technical Stack:
- Gradio 5.0+ Frontend
- OpenCV + MediaPipe + Ultralytics YOLO
- WebRTC Streaming Technology
- FastAPI Backend Integration

⚠️  Beta Status:
This is a heavy beta release. Features are actively being developed and refined.
Report issues at: https://github.com/bladeszasza/labanmovementanalysis

Created with ❤️ by Csaba Bolyós
"""

def get_version_info():
    """Get detailed version information."""
    return {
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "description": __description__,
        "url": __url__,
        "release_notes": RELEASE_NOTES
    } 
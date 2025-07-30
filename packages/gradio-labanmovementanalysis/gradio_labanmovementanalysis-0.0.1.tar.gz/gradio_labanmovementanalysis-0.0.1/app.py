#!/usr/bin/env python3
"""
Laban Movement Analysis - Complete Suite
Hugging Face Spaces Deployment

Created by: Csaba Bolyós (BladeSzaSza)
Contact: bladeszasza@gmail.com
GitHub: https://github.com/bladeszasza
LinkedIn: https://www.linkedin.com/in/csaba-bolyós-00a11767/
Hugging Face: https://huggingface.co/BladeSzaSza

Heavy Beta Version - Under Active Development
"""

import sys
from pathlib import Path

# Import version info
try:
    from version import __version__, __author__, get_version_info
    print(f"🎭 Laban Movement Analysis v{__version__} by {__author__}")
except ImportError:
    __version__ = "0.01-beta"
    print("🎭 Laban Movement Analysis - Version info not found")

# Add demo directory to path
sys.path.insert(0, str(Path(__file__).parent / "demo"))

try:
    from app import create_unified_demo
    
    if __name__ == "__main__":
        demo = create_unified_demo()
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            show_error=True,
            favicon_path=None,
            show_api=True
        )
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all dependencies are installed.")
    
except Exception as e:
    print(f"Error launching demo: {e}") 
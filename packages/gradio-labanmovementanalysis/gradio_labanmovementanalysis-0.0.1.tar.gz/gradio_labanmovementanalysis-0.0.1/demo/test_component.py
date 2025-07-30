"""
Test script to verify the Laban Movement Analysis component structure.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

# Test imports
try:
    from gradio_labanmovementanalysis import LabanMovementAnalysis
    print("✓ LabanMovementAnalysis component imported successfully")
    
    from gradio_labanmovementanalysis import video_utils
    print("✓ video_utils module imported successfully")
    
    from gradio_labanmovementanalysis import pose_estimation
    print("✓ pose_estimation module imported successfully")
    
    from gradio_labanmovementanalysis import notation_engine
    print("✓ notation_engine module imported successfully")
    
    from gradio_labanmovementanalysis import json_generator
    print("✓ json_generator module imported successfully")
    
    from gradio_labanmovementanalysis import visualizer
    print("✓ visualizer module imported successfully")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

# Test component instantiation
try:
    component = LabanMovementAnalysis()
    print("\n✓ Component instantiated successfully")
    
    # Test component methods
    example_payload = component.example_payload()
    print(f"✓ Example payload: {example_payload}")
    
    example_value = component.example_value()
    print(f"✓ Example value keys: {list(example_value.keys())}")
    
    api_info = component.api_info()
    print(f"✓ API info type: {api_info['type']}")
    
except Exception as e:
    print(f"✗ Component error: {e}")
    sys.exit(1)

# Test data structures
try:
    from gradio_labanmovementanalysis.pose_estimation import Keypoint, PoseResult
    kp = Keypoint(x=0.5, y=0.5, confidence=0.9, name="nose")
    print(f"\n✓ Keypoint created: {kp}")
    
    from gradio_labanmovementanalysis.notation_engine import Direction, Speed, Intensity
    print(f"✓ Direction values: {[d.value for d in Direction]}")
    print(f"✓ Speed values: {[s.value for s in Speed]}")
    print(f"✓ Intensity values: {[i.value for i in Intensity]}")
    
except Exception as e:
    print(f"✗ Data structure error: {e}")
    sys.exit(1)

print("\n✅ All tests passed! The component is properly structured.") 
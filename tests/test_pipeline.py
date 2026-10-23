import pytest
import os
import sys
import numpy as np

# Add parent to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.onnx_pipeline import VoicePipeline

@pytest.fixture(scope="module")
def pipeline():
    return VoicePipeline()

def test_pipeline_no_crash(pipeline):
    # Send dummy float32 buffer of 2 seconds
    dummy_audio = np.random.randn(32000).astype(np.float32).tobytes()
    score = pipeline.process_chunk(dummy_audio)
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0

def test_genuine_vs_cloned(pipeline):
    genuine_path = os.path.join(os.path.dirname(__file__), 'data', 'genuine.wav')
    cloned_path = os.path.join(os.path.dirname(__file__), 'data', 'cloned.wav')
    
    # Skip test if files don't exist yet so it doesn't hard-fail CI before we record them
    if not os.path.exists(genuine_path) or not os.path.exists(cloned_path):
        pytest.skip("Test data not found. Add genuine.wav and cloned.wav to tests/data/")
        
    genuine_score = pipeline.process_file(genuine_path)
    cloned_score = pipeline.process_file(cloned_path)
    
    # cloned score should be noticeably higher than genuine score
    # AASIST threshold is typically around 0.5 (or whatever softmax calibrates to)
    assert genuine_score < 0.5, f"Genuine score too high: {genuine_score}"
    assert cloned_score > 0.5, f"Cloned score too low: {cloned_score}"

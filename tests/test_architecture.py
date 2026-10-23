import pytest
import os
import sys
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.app import app

client = TestClient(app)

def test_health_endpoint():
    """
    Verify healthcheck endpoint returns healthy status.
    """
    with TestClient(app) as c:
        response = c.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

def test_root_endpoint():
    """
    Verify root telemetry metadata endpoint returns online status.
    """
    with TestClient(app) as c:
        response = c.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "redis_connected" in data

def test_websocket_returns_score_and_heatmap():
    """
    Test that the websocket accepts bytes and returns score, agg_score, and spectrogram heatmap.
    """
    with TestClient(app) as c:
        with c.websocket_connect("/ws/audio") as websocket:
            # Send 1 second of dummy float32 audio bytes
            dummy_audio = (b'\x00' * 4) * 16000
            websocket.send_bytes(dummy_audio)
            
            data = websocket.receive_json()
            
            assert "score" in data
            assert "agg_score" in data
            assert "heatmap" in data
            assert data["heatmap"].startswith("data:image/png;base64,")
            assert 0.0 <= data["score"] <= 1.0

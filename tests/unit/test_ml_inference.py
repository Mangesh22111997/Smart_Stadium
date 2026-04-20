# Author: Mangesh Wagh
# Email: mangeshwagh2722@gmail.com



import pytest
from app.ml.inference_server import InferenceServer, get_inference_server

def test_inference_server_predicts_reasonable_values():
    """ML model should return valid predictions for standard inputs."""
    server = InferenceServer()
    
    # Test with standard inputs
    result = server.predict_gate_load(
        gate_id="A",
        timestamp_minute=15,
        attendees_passed=1000,
        weather="clear",
        event_type="football",
        day_of_week=2
    )
    
    assert "predicted_queue_t10" in result
    assert "predicted_queue_t30" in result
    assert isinstance(result["predicted_queue_t10"], (int, float))
    assert result["predicted_queue_t10"] >= 0

def test_inference_server_singleton_behavior():
    """Ensure InferenceServer is a singleton to save memory."""
    s1 = get_inference_server()
    s2 = get_inference_server()
    assert s1 is s2

def test_predict_gate_queue_wrapper():
    """Test the FastAPI-compatible wrapper function."""
    from app.ml.inference_server import predict_gate_queue
    
    context = {
        "timestamp_minute": 10,
        "attendees_passed": 500,
        "weather": "rain"
    }
    result = predict_gate_queue("B", context)
    
    assert result["gate_id"] == "B"
    assert "predicted_queue_t10" in result

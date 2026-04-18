#!/usr/bin/env python3
"""
Smart Stadium ML - Phase ML-7: Unified Inference Server

Wraps all trained models and provides fast, consistent prediction API.
This server is called by backend services to make real-time predictions.

Models loaded:
- gate_load_t10.pkl (XGBoost) - 10-minute queue prediction
- gate_load_t30.pkl (XGBoost) - 30-minute queue prediction  
"""

import pickle
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class InferenceServer:
    """Unified ML inference engine for Smart Stadium"""
    
    def __init__(self, model_dir: str = "app/ml/models"):
        """Load all trained models and encoders"""
        self.model_dir = Path(model_dir)
        
        # Load models
        with open(self.model_dir / "gate_load_t10.pkl", 'rb') as f:
            self.model_t10 = pickle.load(f)
        with open(self.model_dir / "gate_load_t30.pkl", 'rb') as f:
            self.model_t30 = pickle.load(f)
        
        # Load encoders
        with open(self.model_dir / "gate_encoders.pkl", 'rb') as f:
            encoders_dict = pickle.load(f)
            self.le_weather = encoders_dict['weather']
            self.le_event_type = encoders_dict['event_type']
            self.le_gate = encoders_dict['gate']
        
        # Load feature names
        with open(self.model_dir / "gate_features.pkl", 'rb') as f:
            self.feature_cols = pickle.load(f)
        
        print("✅ InferenceServer initialized")
        print(f"   Models loaded from: {self.model_dir}")
    
    def predict_gate_load(
        self,
        gate_id: str,
        timestamp_minute: int,
        attendees_passed: int,
        weather: str = "clear",
        event_type: str = "football",
        day_of_week: int = 2,
        queue_depth: int = 0
    ) -> Dict[str, float]:
        """
        Predict queue depth at a gate for T+10 and T+30 horizons.
        
        Args:
            gate_id: Gate identifier ("A", "B", "C", "D")
            timestamp_minute: Minutes since event end
            attendees_passed: Cumulative attendees who have exited
            weather: Weather condition ("clear", "rain", "extreme")
            event_type: Type of event ("cricket", "football", "concert")
            day_of_week: Day of week (0=Monday, 6=Sunday)
            queue_depth: Current queue depth (sampled from live sensor)
        
        Returns:
            Dict with predictions and recommendations
        """
        
        # Feature engineering
        is_peak_time = 1 if 10 <= timestamp_minute <= 30 else 0
        pre_match = 1 if timestamp_minute < -10 else 0
        rainy = 1 if weather == "rain" else 0
        extreme_weather = 1 if weather == "extreme" else 0
        is_weekend = 1 if day_of_week >= 5 else 0
        
        # Encoding
        weather_encoded = int(self.le_weather.transform([weather])[0])
        event_type_encoded = int(self.le_event_type.transform([event_type])[0])
        gate_encoded = int(self.le_gate.transform([gate_id])[0])
        
        # Prepare feature vector exactly as training
        features = np.array([[
            timestamp_minute,
            attendees_passed,
            is_peak_time,
            pre_match,
            rainy,
            extreme_weather,
            is_weekend,
            day_of_week,
            gate_encoded,
            event_type_encoded
        ]])
        
        # Predict
        pred_t10 = float(self.model_t10.predict(features)[0])
        pred_t30 = float(self.model_t30.predict(features)[0])
        
        # Clamp to reasonable range
        pred_t10 = max(0, min(500, pred_t10))
        pred_t30 = max(0, min(500, pred_t30))
        
        # Generate recommendations
        reroute_t10 = pred_t10 > 200
        reroute_t30 = pred_t30 > 200
        staff_needed_t10 = max(2, int(pred_t10 / 50))
        staff_needed_t30 = max(2, int(pred_t30 / 50))
        
        return {
            "gate_id": gate_id,
            "timestamp_minute": timestamp_minute,
            "predicted_queue_t10": round(pred_t10, 1),
            "predicted_queue_t30": round(pred_t30, 1),
            "should_proactive_reroute": reroute_t10 or reroute_t30,
            "reroute_urgency": "HIGH" if reroute_t10 else ("MEDIUM" if reroute_t30 else "LOW"),
            "recommended_staff_t10": staff_needed_t10,
            "recommended_staff_t30": staff_needed_t30,
            "overflow_eta_minutes": next(
                (i for i in range(timestamp_minute, timestamp_minute + 30) if i in [timestamp_minute + 10, timestamp_minute + 30] and 
                 (pred_t10 > 200 if i == timestamp_minute + 10 else pred_t30 > 200)),
                None
            )
        }
    
    def predict_batch_gates(
        self,
        gate_records: List[Dict]
    ) -> List[Dict]:
        """
        Predict for multiple gates at once (batch processing).
        
        Args:
            gate_records: List of gate state dicts
        
        Returns:
            List of prediction dicts
        """
        predictions = []
        for record in gate_records:
            pred = self.predict_gate_load(
                gate_id=record['gate_id'],
                timestamp_minute=record.get('timestamp_minute', 0),
                attendees_passed=record.get('attendees_passed', 0),
                weather=record.get('weather', 'clear'),
                event_type=record.get('event_type', 'football'),
                day_of_week=record.get('day_of_week', 2),
                queue_depth=record.get('queue_depth', 0)
            )
            predictions.append(pred)
        return predictions


# ============================================================================
# FAST API INTEGRATION - Example usage
# ============================================================================

# Initialize globally (once at startup)
_inference_server = None

def get_inference_server() -> InferenceServer:
    """Singleton inference server (lazy initialization)"""
    global _inference_server
    if _inference_server is None:
        _inference_server = InferenceServer()
    return _inference_server


def predict_gate_queue(gate_id: str, context: Dict) -> Dict:
    """
    FastAPI-compatible prediction endpoint wrapper.
    
    Example:
        response = predict_gate_queue("A", {
            "timestamp_minute": 15,
            "attendees_passed": 1200,
            "weather": "rain",
            "event_type": "cricket",
            "day_of_week": 5
        })
    """
    server = get_inference_server()
    return server.predict_gate_load(
        gate_id=gate_id,
        timestamp_minute=context.get('timestamp_minute', 0),
        attendees_passed=context.get('attendees_passed', 0),
        weather=context.get('weather', 'clear'),
        event_type=context.get('event_type', 'football'),
        day_of_week=context.get('day_of_week', 2),
        queue_depth=context.get('queue_depth', 0)
    )


if __name__ == "__main__":
    # Test inference
    print("\n" + "="*70)
    print("  INFERENCE SERVER - TEST RUN")
    print("="*70)
    
    server = InferenceServer()
    
    # Test case 1: Normal exit scenario
    print("\n[Test 1] Normal post-match exit")
    pred1 = server.predict_gate_load(
        gate_id="A",
        timestamp_minute=15,  # 15 mins after match end
        attendees_passed=1200,
        weather="clear",
        event_type="cricket",
        day_of_week=2,
        queue_depth=150
    )
    print(f"  Gate A at T+15:")
    print(f"    Predicted queue T+10: {pred1['predicted_queue_t10']} people")
    print(f"    Predicted queue T+30: {pred1['predicted_queue_t30']} people")
    print(f"    Reroute needed:       {pred1['should_proactive_reroute']}")
    print(f"    Urgency:              {pred1['reroute_urgency']}")
    
    # Test case 2: Rainy condition
    print("\n[Test 2] Rainy weather scenario")
    pred2 = server.predict_gate_load(
        gate_id="B",
        timestamp_minute=20,
        attendees_passed=800,
        weather="rain",
        event_type="football"
    )
    print(f"  Gate B at T+20 (rainy):")
    print(f"    Predicted queue T+10: {pred2['predicted_queue_t10']} people")
    print(f"    Predicted queue T+30: {pred2['predicted_queue_t30']} people")
    print(f"    Recommended staff:    {pred2['recommended_staff_t10']} (T+10), {pred2['recommended_staff_t30']} (T+30)")
    
    # Test case 3: Weekend vs weekday
    print("\n[Test 3] Weekend vs weekday comparison")
    pred3a = server.predict_gate_load(gate_id="C", timestamp_minute=5, attendees_passed=500, day_of_week=3)  # Wednesday
    pred3b = server.predict_gate_load(gate_id="C", timestamp_minute=5, attendees_passed=500, day_of_week=5)  # Friday
    print(f"  Wednesday (weekday):  T+10={pred3a['predicted_queue_t10']}, T+30={pred3a['predicted_queue_t30']}")
    print(f"  Friday (weekend):     T+10={pred3b['predicted_queue_t10']}, T+30={pred3b['predicted_queue_t30']}")
    
    print("\n" + "="*70)
    print("  ✅ INFERENCE SERVER READY FOR INTEGRATION")
    print("="*70)

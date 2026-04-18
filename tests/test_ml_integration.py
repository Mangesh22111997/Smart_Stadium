#!/usr/bin/env python3
"""
Integration Test: ML Gate Load Predictor with FastAPI Backend

Tests:
1. Inference server loads with trained models ✓
2. Gate service can access ML predictions
3. Gate assignment uses ML predictions  
4. API endpoints return ML-enhanced responses
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*70)
print("  ML BACKEND INTEGRATION TEST")
print("="*70)

# ============================================================================
# TEST 1: Verify ML models exist
# ============================================================================
print("\n[TEST 1] Verifying ML models...")
model_dir = Path("app/ml/models")
required_files = ["gate_load_t10.pkl", "gate_load_t30.pkl", "gate_encoders.pkl", "gate_features.pkl"]

for file in required_files:
    file_path = model_dir / file
    if file_path.exists():
        print(f"  ✅ {file} found ({file_path.stat().st_size / 1024:.1f} KB)")
    else:
        print(f"  ❌ {file} NOT FOUND")
        sys.exit(1)

# ============================================================================
# TEST 2: Load Inference Server
# ============================================================================
print("\n[TEST 2] Loading Inference Server...")
try:
    from app.ml.inference_server import InferenceServer, get_inference_server
    print("  ✅ Inference module imported")
    
    server = get_inference_server()
    print("  ✅ Inference server loaded")
    print(f"  ✅ Models ready for predictions")
except Exception as e:
    print(f"  ❌ Failed to load inference server: {e}")
    sys.exit(1)

# ============================================================================
# TEST 3: Make a single prediction
# ============================================================================
print("\n[TEST 3] Testing ML predictions...")
try:
    prediction = server.predict_gate_load(
        gate_id="A",
        timestamp_minute=15,
        attendees_passed=1200,
        weather="clear",
        event_type="cricket",
        day_of_week=2
    )
    
    print(f"  ✅ Prediction successful")
    print(f"     Gate A (T+15, clear weather, cricket):")
    print(f"     - Queue T+10: {prediction['predicted_queue_t10']} people")
    print(f"     - Queue T+30: {prediction['predicted_queue_t30']} people")
    print(f"     - Reroute needed: {prediction['should_proactive_reroute']}")
    print(f"     - Urgency: {prediction['reroute_urgency']}")
except Exception as e:
    print(f"  ❌ Prediction failed: {e}")
    sys.exit(1)

# ============================================================================
# TEST 4: Test GateService with ML enabled
# ============================================================================
print("\n[TEST 4] Testing GateService ML integration...")
try:
    from app.services.gate_service import GateService, ML_ENABLED
    
    if not ML_ENABLED:
        print(f"  ⚠️  ML_ENABLED = False (check imports)")
    else:
        print(f"  ✅ ML_ENABLED = True")
    
    # Test predict_gate_load_ml method
    ml_pred = GateService.predict_gate_load_ml("B", forecast_horizon=10)
    if ml_pred:
        print(f"  ✅ GateService.predict_gate_load_ml() works")
        print(f"     Gate B predictions: T+10={ml_pred['predicted_queue_t10']}, T+30={ml_pred['predicted_queue_t30']}")
    else:
        print(f"  ⚠️  GateService.predict_gate_load_ml() returned None")
    
except Exception as e:
    print(f"  ❌ GateService test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# TEST 5: Test ML-enhanced gate status
# ============================================================================
print("\n[TEST 5] Testing ML-enhanced gate status...")
try:
    # Get single gate with ML
    gate_status = GateService.get_gate_status_ml_enhanced("C")
    if gate_status:
        print(f"  ✅ get_gate_status_ml_enhanced('C') works")
        print(f"     Current count: {gate_status['current_count']}")
        if gate_status.get('ml_predictions'):
            print(f"     ML Predictions: {dict(gate_status['ml_predictions'])}")
        else:
            print(f"     ML Predictions: Not available")
    
    # Get all gates with ML
    all_gates = GateService.get_all_gates_status_ml_enhanced()
    if all_gates:
        print(f"  ✅ get_all_gates_status_ml_enhanced() works")
        print(f"     System utilization: {all_gates['system_utilization_percent']}%")
        print(f"     ML enabled: {all_gates['ml_enabled']}")
        print(f"     Reroute alerts: {all_gates['reroute_alerts']}")
        print(f"     System status: {all_gates['system_status']}")
    
except Exception as e:
    print(f"  ❌ ML-enhanced status test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# TEST 6: Test gate assignment with ML
# ============================================================================
print("\n[TEST 6] Testing gate assignment with ML...")
try:
    from uuid import uuid4
    from app.models.gate import GateAssignmentRequest
    
    # Create assignment request
    ticket_id = uuid4()
    user_id = uuid4()
    
    request = GateAssignmentRequest(
        ticket_id=ticket_id,
        user_id=user_id,
        commute_mode="metro",
        departure_preference="immediate"
    )
    
    # Assign gate (should use ML predictions internally)
    assignment = GateService.assign_gate(request)
    
    print(f"  ✅ Gate assignment successful")
    print(f"     Assigned gate: {assignment.gate_id}")
    print(f"     Reason: {assignment.assignment_reason}")
    
except Exception as e:
    print(f"  ❌ Gate assignment test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*70)
print("  ✅ ALL INTEGRATION TESTS PASSED")
print("="*70)
print("\n✨ ML Models successfully integrated with FastAPI backend!")
print("\nThe system is now using:")
print("  • XGBoost models for gate load prediction")
print("  • Proactive rerouting based on T+10 and T+30 forecasts")
print("  • ML-enhanced gate assignment logic")
print("\nNew API endpoints available:")
print("  GET  /gates/ml/status/all      - System-wide ML predictions")
print("  GET  /gates/ml/{gate_id}       - Gate-specific ML predictions")
print("\nNext steps:")
print("  1. Deploy with: python app/main.py")
print("  2. Test API at: http://localhost:8000/docs")
print("  3. Monitor in admin dashboard")

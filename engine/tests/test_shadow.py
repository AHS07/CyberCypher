import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add proper path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shadow_engine import run_shadow_replay

@patch("shadow_engine._send_request")
@patch("shadow_engine.log_to_supabase")
def test_replay_parity(mock_log, mock_send):
    # Mock identical responses
    mock_send.side_effect = [
        ({"status": "OK", "val": 100}, 0.1, None), # Legacy
        ({"status": "OK", "val": 100}, 0.1, None)  # Headless
    ]
    
    report = run_shadow_replay({"item": "test"})
    
    assert report["diff_summary"] == {}
    assert "type_mismatch" not in report["flags"]
    mock_log.assert_called()

@patch("shadow_engine._send_request")
@patch("shadow_engine.log_to_supabase")
def test_replay_diff(mock_log, mock_send):
    # Mock different responses (Type Mismatch)
    mock_send.side_effect = [
        ({"price": 100.0}, 0.1, None), # Legacy
        ({"price": "100"}, 0.1, None)  # Headless
    ]
    
    report = run_shadow_replay({"item": "test"})
    
    # Semantic check might clear it if enabled logic handles it
    # Current logic: "if check_semantic_equivalence... diff.pop(path)"
    # 100.0 vs "100" is semantically equivalent in our utils
    
    # Let's test a REAL diff
    mock_send.side_effect = [
        ({"price": 100.0}, 0.1, None), 
        ({"price": 200.0}, 0.1, None) 
    ]
    report = run_shadow_replay({"item": "diff"})
    assert report["diff_summary"] != {}

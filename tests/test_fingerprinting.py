import unittest
import os
import sys
import json

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.fingerprinting import create_journey_fingerprint, predict_outcome

class TestFingerprinting(unittest.TestCase):
    
    def setUp(self):
        # Sample journey data for testing
        self.upgrade_journey_path = os.path.join('cancels and upgrades', 'upgrades', 'upgrade-a.json')
        self.cancel_journey_path = os.path.join('cancels and upgrades', 'cancellations', 'cancel-a.json')
        
        # Load sample journey data
        with open(self.upgrade_journey_path, 'r') as f:
            upgrade_data = json.load(f)
        
        with open(self.cancel_journey_path, 'r') as f:
            cancel_data = json.load(f)
        
        # Extract steps for testing
        self.upgrade_steps = []
        for chunk_key, chunk_data in upgrade_data.items():
            if 'steps' in chunk_data:
                for step in chunk_data['steps']:
                    step['chunk_id'] = chunk_key
                    self.upgrade_steps.append(step)
        
        self.cancel_steps = []
        for chunk_key, chunk_data in cancel_data.items():
            if 'steps' in chunk_data:
                for step in chunk_data['steps']:
                    step['chunk_id'] = chunk_key
                    self.cancel_steps.append(step)
        
        # Create journey data dictionaries
        self.upgrade_journey = {
            'steps': self.upgrade_steps,
            'journey_type': 'upgrade'
        }
        
        self.cancel_journey = {
            'steps': self.cancel_steps,
            'journey_type': 'cancel'
        }
    
    def test_create_journey_fingerprint(self):
        # Test fingerprinting for upgrade journey
        upgrade_fingerprint = create_journey_fingerprint(self.upgrade_journey)
        
        # Check if fingerprint has expected fields
        self.assertIn('step_count', upgrade_fingerprint)
        self.assertIn('status_distribution', upgrade_fingerprint)
        self.assertIn('total_time_ms', upgrade_fingerprint)
        self.assertIn('upgrade_indicator_count', upgrade_fingerprint)
        self.assertIn('cancel_indicator_count', upgrade_fingerprint)
        
        # Test fingerprinting for cancel journey
        cancel_fingerprint = create_journey_fingerprint(self.cancel_journey)
        
        # Check if fingerprint has expected fields
        self.assertIn('step_count', cancel_fingerprint)
        self.assertIn('status_distribution', cancel_fingerprint)
        self.assertIn('total_time_ms', cancel_fingerprint)
        self.assertIn('upgrade_indicator_count', cancel_fingerprint)
        self.assertIn('cancel_indicator_count', cancel_fingerprint)
    
    def test_predict_outcome(self):
        # Test prediction for upgrade journey
        upgrade_fingerprint = create_journey_fingerprint(self.upgrade_journey)
        upgrade_prediction, upgrade_confidence = predict_outcome(upgrade_fingerprint)
        
        # Check if prediction and confidence are valid
        self.assertIn(upgrade_prediction, ['upgrade', 'cancel', 'uncertain'])
        self.assertGreaterEqual(upgrade_confidence, 0.0)
        self.assertLessEqual(upgrade_confidence, 1.0)
        
        # Test prediction for cancel journey
        cancel_fingerprint = create_journey_fingerprint(self.cancel_journey)
        cancel_prediction, cancel_confidence = predict_outcome(cancel_fingerprint)
        
        # Check if prediction and confidence are valid
        self.assertIn(cancel_prediction, ['upgrade', 'cancel', 'uncertain'])
        self.assertGreaterEqual(cancel_confidence, 0.0)
        self.assertLessEqual(cancel_confidence, 1.0)
    
    def test_upgrade_indicators(self):
        # Test if upgrade journey has more upgrade indicators than cancel indicators
        upgrade_fingerprint = create_journey_fingerprint(self.upgrade_journey)
        
        self.assertGreaterEqual(
            upgrade_fingerprint['upgrade_indicator_count'],
            upgrade_fingerprint['cancel_indicator_count']
        )
    
    def test_cancel_indicators(self):
        # Test if cancel journey has more cancel indicators than a random threshold
        cancel_fingerprint = create_journey_fingerprint(self.cancel_journey)
        
        # Cancellation journeys should have at least some cancel indicators
        self.assertGreater(cancel_fingerprint['cancel_indicator_count'], 0)

if __name__ == '__main__':
    unittest.main() 
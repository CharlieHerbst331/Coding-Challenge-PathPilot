import unittest
import os
import sys
import json
from unittest.mock import patch

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.data_processor import process_journey_data, analyze_journey_with_ai

class TestDataProcessor(unittest.TestCase):
    
    def setUp(self):
        # Sample journey data for testing
        self.upgrade_journey_path = os.path.join('cancels and upgrades', 'upgrades', 'upgrade-a.json')
        self.cancel_journey_path = os.path.join('cancels and upgrades', 'cancellations', 'cancel-a.json')
        
        # Process sample journeys
        self.upgrade_journey = process_journey_data(self.upgrade_journey_path)
        self.cancel_journey = process_journey_data(self.cancel_journey_path)
    
    def test_process_journey_data(self):
        # Test if journey data was processed correctly
        self.assertIn('steps', self.upgrade_journey)
        self.assertIn('status_groups', self.upgrade_journey)
        self.assertIn('journey_type', self.upgrade_journey)
        
        self.assertIn('steps', self.cancel_journey)
        self.assertIn('status_groups', self.cancel_journey)
        self.assertIn('journey_type', self.cancel_journey)
        
        # Check if we have steps in the journeys
        self.assertGreater(len(self.upgrade_journey['steps']), 0)
        self.assertGreater(len(self.cancel_journey['steps']), 0)
        
        # Check if steps have the expected structure
        upgrade_step = self.upgrade_journey['steps'][0]
        self.assertIn('label', upgrade_step)
        self.assertIn('date', upgrade_step)
        self.assertIn('status', upgrade_step)
        self.assertIn('recordingReel', upgrade_step)
        self.assertIn('chunk_id', upgrade_step)
        
        # Check if journey type is extracted correctly
        self.assertEqual(self.upgrade_journey['journey_type'], 'upgrade')
        self.assertEqual(self.cancel_journey['journey_type'], 'cancel')
    
    @patch('app.utils.data_processor.openai.chat.completions.create')
    def test_analyze_journey_with_ai(self, mock_openai):
        # Mock the OpenAI API response
        mock_response = type('obj', (object,), {
            'choices': [
                type('obj', (object,), {
                    'message': type('obj', (object,), {
                        'content': json.dumps({
                            "summary": "Test summary",
                            "key_insights": ["Insight 1", "Insight 2"],
                            "critical_points": ["Point 1", "Point 2"],
                            "suggestions": ["Suggestion 1", "Suggestion 2"],
                            "prediction": "Test prediction"
                        })
                    })
                })
            ]
        })
        
        mock_openai.return_value = mock_response
        
        # Test AI analysis
        analysis = analyze_journey_with_ai(self.upgrade_journey)
        
        # Check if analysis has expected structure
        self.assertIn('summary', analysis)
        self.assertIn('key_insights', analysis)
        self.assertIn('critical_points', analysis)
        self.assertIn('suggestions', analysis)
        self.assertIn('prediction', analysis)
        
        # Check if mock data is returned correctly
        self.assertEqual(analysis['summary'], "Test summary")
        self.assertEqual(len(analysis['key_insights']), 2)
        self.assertEqual(len(analysis['critical_points']), 2)
        self.assertEqual(len(analysis['suggestions']), 2)
        self.assertEqual(analysis['prediction'], "Test prediction")

if __name__ == '__main__':
    unittest.main() 
import os
import json
import time
from app.utils.data_processor import process_journey_data, analyze_journey_with_ai
from app.utils.fingerprinting import create_journey_fingerprint, predict_outcome

class JourneyCache:
    def __init__(self, cache_dir='.cache'):
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, 'journey_cache.json')
        self.cache = {}
        self._ensure_cache_dir()
        self._load_cache()

    def _ensure_cache_dir(self):
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
            except:
                self.cache = {}

    def _save_cache(self):
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f)

    def get_journey_data(self, journey_type, journey_id):
        cache_key = f"{journey_type}/{journey_id}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        return None

    def precompute_all_journeys(self):
        """Precompute all journey data and store in cache"""
        journey_files = {
            'upgrades': [],
            'cancellations': []
        }
        
        # Get upgrade journeys
        upgrade_dir = os.path.join('cancels and upgrades', 'upgrades')
        for file in os.listdir(upgrade_dir):
            if file.endswith('.json'):
                journey_files['upgrades'].append(os.path.join(upgrade_dir, file))
        
        # Get cancellation journeys
        cancel_dir = os.path.join('cancels and upgrades', 'cancellations')
        for file in os.listdir(cancel_dir):
            if file.endswith('.json'):
                journey_files['cancellations'].append(os.path.join(cancel_dir, file))

        # Process all journeys
        for journey_type, files in journey_files.items():
            for file_path in files:
                journey_id = os.path.basename(file_path).replace('.json', '')
                cache_key = f"{journey_type}/{journey_id}"
                
                if cache_key not in self.cache:
                    print(f"Processing {journey_type} journey: {journey_id}")
                    
                    # Process journey data
                    journey_data = process_journey_data(file_path)
                    
                    # Generate AI analysis
                    ai_analysis = analyze_journey_with_ai(journey_data)
                    
                    # Create fingerprint
                    fingerprint = create_journey_fingerprint(journey_data)
                    
                    # Predict outcome
                    prediction, confidence = predict_outcome(fingerprint)
                    
                    # Store in cache
                    self.cache[cache_key] = {
                        'journey_data': journey_data,
                        'ai_analysis': ai_analysis,
                        'fingerprint': fingerprint,
                        'prediction': prediction,
                        'confidence': confidence,
                        'timestamp': time.time()
                    }
        
        # Save cache to disk
        self._save_cache()

# Create a global cache instance
journey_cache = JourneyCache() 
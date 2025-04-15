import os
import json
import numpy as np
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import re

# Common patterns that might indicate upgrades or cancellations
UPGRADE_PATTERNS = [
    r'upgrad(e|ing)',
    r'pricing',
    r'subscri(be|ption)',
    r'payment',
    r'pro',
    r'premium',
    r'feature',
    r'limit',
    r'plan',
    r'annual',
    r'billing'
]

CANCEL_PATTERNS = [
    r'cancel',
    r'churn',
    r'downgrad',
    r'refund',
    r'expensive',
    r'dissatisf',
    r'issue',
    r'problem',
    r'frustra',
    r'error',
    r'bug'
]

def create_journey_fingerprint(journey_data):
    """
    Create a fingerprint for a user journey that captures key patterns
    """
    steps = journey_data['steps']
    
    # Extract various metrics
    step_count = len(steps)
    status_counts = Counter([step['status'] for step in steps])
    
    # Calculate time spent in journey
    if step_count > 1:
        first_step = steps[0]['recordingReel']
        last_step = steps[-1]['recordingReel']
        
        # Try to get start and end times
        try:
            start_time = first_step.get('start_ms_since', 0)
            end_time = last_step.get('end_ms_since', 0)
            
            # If we don't have ms_since values, use the MM:SS.S format
            if start_time == 0 and 'start' in first_step:
                start_parts = first_step['start'].split(':')
                start_time = (int(start_parts[0]) * 60 + float(start_parts[1])) * 1000
                
            if end_time == 0 and 'end' in last_step:
                end_parts = last_step['end'].split(':')
                end_time = (int(end_parts[0]) * 60 + float(end_parts[1])) * 1000
                
            total_time = max(end_time - start_time, 0)
        except:
            total_time = 0
    else:
        total_time = 0
    
    # Extract all text for analysis
    all_text = " ".join([
        f"{step['label']} {step['recordingReel']['details']}"
        for step in steps
    ]).lower()
    
    # Count pattern matches
    upgrade_indicators = 0
    for pattern in UPGRADE_PATTERNS:
        upgrade_indicators += len(re.findall(pattern, all_text))
    
    cancel_indicators = 0
    for pattern in CANCEL_PATTERNS:
        cancel_indicators += len(re.findall(pattern, all_text))
    
    # Calculate the ratio of time between attempted_conversion and the final status
    conversion_attempts = [i for i, step in enumerate(steps) if step['status'] == 'attempted_conversion']
    if conversion_attempts and step_count > 0:
        first_conversion_attempt = conversion_attempts[0]
        conversion_attempt_ratio = first_conversion_attempt / step_count
    else:
        conversion_attempt_ratio = 0
    
    # Create the fingerprint
    fingerprint = {
        'step_count': step_count,
        'status_distribution': {k: v/step_count for k, v in status_counts.items()},
        'total_time_ms': total_time,
        'upgrade_indicator_count': upgrade_indicators,
        'cancel_indicator_count': cancel_indicators,
        'conversion_attempt_ratio': conversion_attempt_ratio,
        'text_length': len(all_text),
        'final_status': steps[-1]['status'] if steps else 'unknown'
    }
    
    return fingerprint

def predict_outcome(fingerprint):
    """
    Predict whether a user is likely to upgrade or cancel based on their journey fingerprint
    """
    # Extract key features
    status_dist = fingerprint['status_distribution']
    
    # Conversion status indicators
    converted_ratio = status_dist.get('converted', 0)
    attempted_ratio = status_dist.get('attempted_conversion', 0)
    at_risk_ratio = status_dist.get('conversion_at_risk', 0)
    churned_ratio = status_dist.get('churned', 0)
    
    # Indicator counts
    upgrade_indicators = fingerprint['upgrade_indicator_count']
    cancel_indicators = fingerprint['cancel_indicator_count']
    
    # Calculate upgrade probability
    # This is a simplified model; in a real-world scenario, we would train a 
    # machine learning model on historical data
    upgrade_score = (
        (converted_ratio * 0.8) + 
        (attempted_ratio * 0.4) - 
        (at_risk_ratio * 0.5) - 
        (churned_ratio * 0.9) +
        (upgrade_indicators * 0.1) - 
        (cancel_indicators * 0.1)
    )
    
    # Normalize to 0-1 range
    upgrade_probability = max(0, min(1, upgrade_score + 0.5))
    
    # Determine prediction and confidence
    if upgrade_probability > 0.7:
        prediction = "upgrade"
        confidence = upgrade_probability
    elif upgrade_probability < 0.3:
        prediction = "cancel"
        confidence = 1 - upgrade_probability
    else:
        prediction = "uncertain"
        confidence = 0.5
        
    # Check final status for override
    if fingerprint['final_status'] == 'churned':
        prediction = "cancel"
        confidence = 0.95
    elif fingerprint['final_status'] == 'converted':
        prediction = "upgrade"
        confidence = 0.95
    
    return prediction, confidence 
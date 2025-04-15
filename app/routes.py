import os
import json
import openai
import time
from dotenv import load_dotenv
from flask import render_template, request, jsonify
from app import app
from app.utils.data_processor import process_journey_data, analyze_journey_with_ai
from app.utils.fingerprinting import create_journey_fingerprint, predict_outcome
from app.utils.cache import journey_cache
from collections import Counter

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Get all journey data paths
def get_journey_files():
    journey_files = {
        'upgrades': [],
        'cancellations': []
    }
    
    try:
        # Get upgrade journeys
        upgrade_dir = os.path.join('cancels and upgrades', 'upgrades')
        if os.path.exists(upgrade_dir):
            for file in os.listdir(upgrade_dir):
                if file.endswith('.json'):
                    journey_files['upgrades'].append(os.path.join(upgrade_dir, file))
        else:
            print(f"Warning: Upgrade directory not found: {upgrade_dir}")
        
        # Get cancellation journeys
        cancel_dir = os.path.join('cancels and upgrades', 'cancellations')
        if os.path.exists(cancel_dir):
            for file in os.listdir(cancel_dir):
                if file.endswith('.json'):
                    journey_files['cancellations'].append(os.path.join(cancel_dir, file))
        else:
            print(f"Warning: Cancellation directory not found: {cancel_dir}")
        
        return journey_files
    except Exception as e:
        print(f"Error getting journey files: {str(e)}")
        return journey_files

@app.route('/')
def index():
    journey_files = get_journey_files()
    journeys = {
        'upgrades': [],
        'cancellations': []
    }
    
    # Process upgrade journeys
    for file_path in journey_files['upgrades']:
        journey_id = os.path.basename(file_path).replace('.json', '')
        journeys['upgrades'].append({
            'id': journey_id,
            'name': journey_id.capitalize(),
            'path': file_path
        })
    
    # Process cancellation journeys
    for file_path in journey_files['cancellations']:
        journey_id = os.path.basename(file_path).replace('.json', '')
        journeys['cancellations'].append({
            'id': journey_id,
            'name': journey_id.capitalize(),
            'path': file_path
        })
    
    return render_template('index.html', journeys=journeys)

@app.route('/journey/<journey_type>/<journey_id>')
def view_journey(journey_type, journey_id):
    if journey_type not in ['upgrades', 'cancellations']:
        return "Invalid journey type", 400
    
    # Try to get data from cache
    cached_data = journey_cache.get_journey_data(journey_type, journey_id)
    
    if cached_data:
        return render_template(
            'journey.html',
            journey_id=journey_id,
            journey_type=journey_type,
            journey_data=cached_data['journey_data'],
            ai_analysis=cached_data['ai_analysis'],
            fingerprint=cached_data['fingerprint'],
            prediction=cached_data['prediction'],
            confidence=cached_data['confidence']
        )
    
    # If not in cache, process the data
    file_path = os.path.join('cancels and upgrades', journey_type, f"{journey_id}.json")
    
    if not os.path.exists(file_path):
        return "Journey not found", 404
    
    # Process journey data
    journey_data = process_journey_data(file_path)
    
    # Generate AI analysis for the journey
    ai_analysis = analyze_journey_with_ai(journey_data)
    
    # Create journey fingerprint
    fingerprint = create_journey_fingerprint(journey_data)
    
    # Predict outcome based on fingerprint
    prediction, confidence = predict_outcome(fingerprint)
    
    return render_template(
        'journey.html',
        journey_id=journey_id,
        journey_type=journey_type,
        journey_data=journey_data,
        ai_analysis=ai_analysis,
        fingerprint=fingerprint,
        prediction=prediction,
        confidence=confidence
    )

@app.route('/api/journey/<journey_type>/<journey_id>')
def api_journey_data(journey_type, journey_id):
    if journey_type not in ['upgrades', 'cancellations']:
        return jsonify({"error": "Invalid journey type"}), 400
    
    # Try to get data from cache
    cached_data = journey_cache.get_journey_data(journey_type, journey_id)
    
    if cached_data:
        return jsonify(cached_data['journey_data'])
    
    # If not in cache, process the data
    file_path = os.path.join('cancels and upgrades', journey_type, f"{journey_id}.json")
    
    if not os.path.exists(file_path):
        return jsonify({"error": "Journey not found"}), 404
    
    # Process journey data
    journey_data = process_journey_data(file_path)
    
    return jsonify(journey_data)

@app.route('/api/analyze', methods=['POST'])
def api_analyze_journey():
    data = request.json
    
    if not data or 'steps' not in data:
        return jsonify({"error": "Invalid data format"}), 400
    
    # Generate AI analysis for the journey
    ai_analysis = analyze_journey_with_ai(data)
    
    # Create journey fingerprint
    fingerprint = create_journey_fingerprint(data)
    
    # Predict outcome based on fingerprint
    prediction, confidence = predict_outcome(fingerprint)
    
    return jsonify({
        "analysis": ai_analysis,
        "fingerprint": fingerprint,
        "prediction": prediction,
        "confidence": confidence
    })

def categorize_journey_with_gpt(journey_summary, journey_type):
    """
    Use GPT-3.5 to categorize a journey into one of the predefined categories based on its AI summary
    """
    try:
        # Define the categories based on journey type
        if journey_type == 'upgrades':  # Changed from 'upgrade' to match cache
            categories = [
                "Storage Limitations",
                "Pricing Incentives",
                "Free Tier Limitations",
                "Feature Access",
                "Free Trial"
            ]
        else:  # cancellations
            categories = [
                "No Longer Need",
                "Missing Features",
                "Cost Concerns",
                "Technical Problems",
                "Usability Issues"
            ]
        
        # Create the prompt for GPT
        prompt = f"""Analyze this user journey summary and categorize it into exactly one of these categories: {', '.join(categories)}.
        Return ONLY the category name, nothing else.
        
        Journey summary: {journey_summary}
        
        Category: """
        
        # Call GPT-3.5 using the new API format
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that categorizes user journeys. Return ONLY the category name, nothing else."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=50
        )
        
        # Extract and validate the response
        category = response.choices[0].message.content.strip()
        if category in categories:
            return category
        
        # If response is not valid, return default category
        return "Storage Limitations" if journey_type == 'upgrades' else "No Longer Need"
        
    except Exception as e:
        print(f"Error in GPT categorization: {str(e)}")
        return "Storage Limitations" if journey_type == 'upgrades' else "No Longer Need"

@app.route('/analytics')
def analytics():
    journey_files = get_journey_files()
    
    # Initialize dictionaries for counting categories
    upgrade_categories = {
        "Storage Limitations": 0,
        "Pricing Incentives": 0,
        "Free Tier Limitations": 0,
        "Feature Access": 0,
        "Free Trial": 0
    }
    
    cancellation_categories = {
        "No Longer Need": 0,
        "Missing Features": 0,
        "Cost Concerns": 0,
        "Technical Problems": 0,
        "Usability Issues": 0
    }
    
    # Process upgrade journeys
    for file_path in journey_files['upgrades']:
        journey_id = os.path.basename(file_path).replace('.json', '')
        
        try:
            # Try to get data from cache
            cached_data = journey_cache.get_journey_data('upgrades', journey_id)
            
            if cached_data and 'ai_analysis' in cached_data and 'summary' in cached_data['ai_analysis']:
                journey_data = cached_data['journey_data']
                ai_analysis = cached_data['ai_analysis']
            else:
                # If not in cache or missing required data, process the data
                journey_data = process_journey_data(file_path)
                ai_analysis = analyze_journey_with_ai(journey_data)
            
            # Categorize the journey using GPT
            category = categorize_journey_with_gpt(ai_analysis['summary'], 'upgrades')
            
            # Increment the count for this category
            upgrade_categories[category] += 1
        except Exception as e:
            print(f"Error processing upgrade journey {journey_id}: {str(e)}")
            continue
    
    # Process cancellation journeys
    for file_path in journey_files['cancellations']:
        journey_id = os.path.basename(file_path).replace('.json', '')
        
        try:
            # Try to get data from cache
            cached_data = journey_cache.get_journey_data('cancellations', journey_id)
            
            if cached_data and 'ai_analysis' in cached_data and 'summary' in cached_data['ai_analysis']:
                journey_data = cached_data['journey_data']
                ai_analysis = cached_data['ai_analysis']
            else:
                # If not in cache or missing required data, process the data
                journey_data = process_journey_data(file_path)
                ai_analysis = analyze_journey_with_ai(journey_data)
            
            # Categorize the journey using GPT
            category = categorize_journey_with_gpt(ai_analysis['summary'], 'cancellations')
            
            # Increment the count for this category
            cancellation_categories[category] += 1
        except Exception as e:
            print(f"Error processing cancellation journey {journey_id}: {str(e)}")
            continue
    
    # Prepare chart data
    chart_data = {
        'upgrade': {
            'labels': list(upgrade_categories.keys()),
            'values': list(upgrade_categories.values())
        },
        'cancel': {
            'labels': list(cancellation_categories.keys()),
            'values': list(cancellation_categories.values())
        }
    }
    
    # Write chart data to static file
    try:
        js_dir = os.path.join('app', 'static', 'js')
        os.makedirs(js_dir, exist_ok=True)  # Create directory if it doesn't exist
        
        chart_data_path = os.path.join(js_dir, 'chart-data.json')
        with open(chart_data_path, 'w') as f:
            json.dump(chart_data, f)
    except Exception as e:
        print(f"Error writing chart data: {str(e)}")
        # Continue execution even if writing fails
    
    return render_template(
        'analytics.html',
        upgrade_reason_counts=upgrade_categories,
        cancel_reason_counts=cancellation_categories,
        upgrade_labels=list(upgrade_categories.keys()),
        upgrade_values=list(upgrade_categories.values()),
        cancel_labels=list(cancellation_categories.keys()),
        cancel_values=list(cancellation_categories.values())
    )

@app.route('/api/analytics/chart-data')
def api_analytics_chart_data():
    """API endpoint to serve chart data directly from the server"""
    try:
        with open(os.path.join('app', 'static', 'js', 'chart-data.json'), 'r') as f:
            chart_data = json.load(f)
        return jsonify(chart_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500 
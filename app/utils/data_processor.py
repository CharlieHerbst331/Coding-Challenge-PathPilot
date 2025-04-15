import os
import json
import openai
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def process_journey_data(file_path):
    """
    Process journey data from a JSON file
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Extract all steps from each recording chunk
    all_steps = []
    for chunk_key, chunk_data in data.items():
        if 'steps' in chunk_data:
            for step in chunk_data['steps']:
                # Add chunk_id to each step
                step['chunk_id'] = chunk_key
                
                # Add more specific status labels
                if step['status'] == 'non-converted':
                    step['status_detail'] = 'Exploring'
                elif step['status'] == 'attempted_conversion':
                    step['status_detail'] = 'Considering Purchase'
                elif step['status'] == 'converted':
                    step['status_detail'] = 'Completed Purchase'
                elif step['status'] == 'conversion_at_risk':
                    step['status_detail'] = 'Considering Cancellation'
                elif step['status'] == 'churned':
                    step['status_detail'] = 'Cancelled Subscription'
                else:
                    step['status_detail'] = step['status'].replace('_', ' ').capitalize()
                
                # Calculate duration in a more robust way
                try:
                    start_ms = step['recordingReel'].get('start_ms_since', 0)
                    end_ms = step['recordingReel'].get('end_ms_since', 0)
                    
                    # If we have start and end values in MM:SS.S format, convert to ms
                    if start_ms == 0 and 'start' in step['recordingReel']:
                        parts = step['recordingReel']['start'].split(':')
                        if len(parts) == 2:
                            start_ms = (int(parts[0]) * 60 + float(parts[1])) * 1000
                    
                    if end_ms == 0 and 'end' in step['recordingReel']:
                        parts = step['recordingReel']['end'].split(':')
                        if len(parts) == 2:
                            end_ms = (int(parts[0]) * 60 + float(parts[1])) * 1000
                    
                    # Calculate duration
                    if start_ms > 0 and end_ms > 0:
                        step['duration_ms'] = end_ms - start_ms
                    else:
                        step['duration_ms'] = 0
                except Exception as e:
                    # If there's an error, set duration to 0
                    step['duration_ms'] = 0
                
                all_steps.append(step)
    
    # Sort steps by date and time
    all_steps.sort(key=lambda x: (
        x['date'], 
        x['recordingReel']['start_ms_since'] if 'start_ms_since' in x['recordingReel'] else 0
    ))
    
    # Calculate time differences between steps
    previous_start_time = 0
    for step in all_steps:
        current_start = step['recordingReel'].get('start_ms_since', 0)
        time_diff = current_start - previous_start_time
        step['recordingReel']['time_since_previous'] = time_diff if time_diff > 0 else current_start
        previous_start_time = current_start
    
    # Group steps by status
    status_groups = {}
    for step in all_steps:
        status = step['status']
        if status not in status_groups:
            status_groups[status] = []
        status_groups[status].append(step)
    
    journey_type = os.path.basename(file_path).split('-')[0]
    
    return {
        'steps': all_steps,
        'status_groups': status_groups,
        'journey_type': journey_type
    }

def analyze_journey_data(journey_data):
    """Analyze journey data using GPT-3.5 Turbo for better performance"""
    try:
        # Prepare the prompt
        prompt = f"""
        Analyze this user journey data and provide insights:
        {json.dumps(journey_data, indent=2)}
        
        Please provide:
        1. A brief summary of the journey
        2. Key insights about user behavior
        3. Critical decision points
        4. Specific recommendations for improvement
        """
        
        # Use GPT-3.5 Turbo for faster response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in user journey analysis and conversion optimization."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Parse the response
        analysis = response.choices[0].message.content
        
        return {
            "summary": analysis,
            "key_insights": [],
            "critical_points": [],
            "suggestions": []
        }
        
    except Exception as e:
        print(f"Error in journey analysis: {str(e)}")
        return {"error": str(e)}

def analyze_journey_with_ai(journey_data):
    """
    Analyze journey data using OpenAI API
    """
    # Extract all step labels and details for analysis
    step_descriptions = []
    for step in journey_data['steps']:
        step_descriptions.append(f"Action: {step['label']}")
        step_descriptions.append(f"Status: {step['status']}")
        step_descriptions.append(f"Details: {step['recordingReel']['details']}")
        step_descriptions.append("---")
    
    # Join all descriptions
    journey_text = "\n".join(step_descriptions)
    
    # Prepare the prompt for GPT
    prompt = f"""
    As a user journey analyst, analyze the following user journey steps:
    
    {journey_text}
    
    Please provide:
    1. A concise summary of this user's journey
    2. Key insights about this user's behavior
    3. Critical points where the user made important decisions
    4. Suggestions for improving user experience based on this journey
    5. Prediction of whether this user is likely to upgrade, stay, or churn in the future
    
    Format your response STRICTLY as JSON with the following structure:
    {{
        "summary": "...",
        "key_insights": ["...", "...", "..."],
        "critical_points": ["...", "...", "..."],
        "suggestions": ["...", "...", "..."],
        "prediction": "..."
    }}
    """
    
    # Use GPT-4 for better accuracy
    for attempt in range(3):  # Try up to 3 times
        try:
            response = openai.chat.completions.create(
                model="gpt-4",  # Using GPT-4 for better accuracy
                messages=[
                    {"role": "system", "content": "You are an expert in analyzing user journeys to identify patterns that lead to upgrades or cancellations. You MUST return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent responses
                max_tokens=1500,
                top_p=0.9,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            analysis_text = response.choices[0].message.content
            
            # Clean the text (remove leading/trailing backticks if present)
            analysis_text = analysis_text.strip()
            if analysis_text.startswith('```json'):
                analysis_text = analysis_text[7:]
            if analysis_text.startswith('```'):
                analysis_text = analysis_text[3:]
            if analysis_text.endswith('```'):
                analysis_text = analysis_text[:-3]
            analysis_text = analysis_text.strip()
            
            # Parse the JSON response
            try:
                analysis = json.loads(analysis_text)
                return analysis
            except json.JSONDecodeError:
                # If not valid JSON, continue to next attempt
                if attempt < 2:  
                    time.sleep(1)  # Wait a second before trying again
                    continue
                else:
                    # Fall back to generated analysis
                    return generate_fallback_analysis(journey_data)
                    
        except Exception as e:
            print(f"Error in AI analysis attempt {attempt + 1}: {str(e)}")
            if attempt < 2:
                time.sleep(1)
                continue
            else:
                return generate_fallback_analysis(journey_data)

def generate_fallback_analysis(journey_data):
    """
    Generate a fallback analysis when the OpenAI API is not available
    """
    steps = journey_data['steps']
    journey_type = journey_data.get('journey_type', 'unknown')
    
    # Count different status types
    status_counts = {}
    for step in steps:
        status = step['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Find key decision points
    key_points = []
    critical_status = ['attempted_conversion', 'converted', 'conversion_at_risk', 'churned']
    for step in steps:
        if step['status'] in critical_status:
            key_points.append(f"{step['label']} ({step['status_detail']})")
    
    # Generate basic insights
    insights = []
    if 'non-converted' in status_counts:
        insights.append("User spent time exploring the product before making a decision.")
    if 'attempted_conversion' in status_counts:
        insights.append("User showed interest in upgrading by taking steps toward conversion.")
    if 'converted' in status_counts:
        insights.append("User successfully completed the conversion/upgrade process.")
    if 'conversion_at_risk' in status_counts:
        insights.append("User showed signs of dissatisfaction or hesitation after conversion.")
    if 'churned' in status_counts:
        insights.append("User ultimately decided to cancel their subscription.")
    
    # Add journey-specific insights
    if journey_type == 'upgrade':
        insights.append("The journey shows a successful upgrade path that can be used as a positive example.")
    elif journey_type == 'cancel':
        insights.append("The journey shows issues that led to cancellation which should be addressed.")
    
    # Generate suggestions
    suggestions = [
        "Simplify the upgrade process to reduce friction points",
        "Improve onboarding to better showcase premium features",
        "Add targeted messaging at key decision points",
        "Implement proactive support for users showing risk signals"
    ]
    
    # Determine prediction
    if journey_type == 'upgrade' or 'converted' in status_counts:
        prediction = "This user is likely to maintain their upgraded subscription if properly supported."
    elif journey_type == 'cancel' or 'churned' in status_counts:
        prediction = "This user has already churned. Future similar users might be retained with improved engagement strategies."
    else:
        prediction = "Based on behavior patterns, this user needs additional touchpoints to encourage conversion."
    
    # Create the analysis object
    return {
        "summary": f"This journey contains {len(steps)} steps across various stages from exploration to {'conversion' if journey_type == 'upgrade' else 'cancellation'}.",
        "key_insights": insights[:3],  # Limit to 3 insights
        "critical_points": key_points[:3],  # Limit to 3 points
        "suggestions": suggestions[:3],  # Limit to 3 suggestions
        "prediction": prediction
    } 
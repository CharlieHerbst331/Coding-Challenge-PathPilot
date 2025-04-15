# PathPilot - User Journey Analysis

PathPilot is a web application that analyzes user journey data to identify patterns leading to subscription upgrades or cancellations. It provides visual timeline representations and creates "fingerprints" to predict user behavior.

## Quick Start

1. Clone the repository
2. Run the start script:
   ```
   ./start.sh
   ```
3. Open your browser and navigate to the associated localhost

## Features

- **Journey Timeline Visualization**: Interactive timeline showing the progression of each user journey with detailed step information
- **AI-Powered Analysis**: Uses OpenAI's GPT-4 to analyze journey patterns and provide insights
- **User Journey Fingerprinting**: Creates fingerprints to identify key patterns that precede upgrades or cancellations
- **Outcome Prediction**: Predicts whether a user is likely to upgrade or cancel their subscription
- **Modern UI/UX**: Clean, intuitive interface with responsive design

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd path-pilot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with your OpenAI API key:
```
OPENAI_API_KEY=your_openai_api_key
```

## Running the Application

1. Start the Flask development server:
```bash
python app.py
```

2. Open a web browser and navigate to:
```
http://localhost:5000
```

## Approach and Methodology

### Data Processing

The application processes JSON files containing user journey recordings by:
1. Extracting and normalizing steps from multiple recording chunks
2. Sorting steps chronologically by date and time
3. Grouping steps by status (non-converted, attempted_conversion, converted, etc.)

### Journey Visualization

The timeline visualization:
- Displays each step in chronological order
- Color-codes steps based on their status
- Provides expandable details for each step
- Highlights critical decision points

### Journey Fingerprinting

The fingerprinting process:
1. Extracts key metrics from user journeys (step count, status distribution, time spent)
2. Identifies language patterns associated with upgrades and cancellations
3. Analyzes the sequence and timing of status changes
4. Creates a compact representation of journey characteristics

### Outcome Prediction

The prediction model:
- Uses a weighted scoring system based on status distribution and indicators
- Analyzes the ratio of upgrade vs. cancellation language patterns
- Evaluates timing and sequence of conversion attempts
- Provides a confidence score for predictions

## Running Tests

To run the unit tests:
```bash
python -m unittest discover tests
```

## Future Improvements

- Implement machine learning models trained on larger datasets
- Add more advanced visualization options (heatmaps, comparison views)
- Include real-time analysis of ongoing user journeys
- Expand the API for integration with other systems
- Add user segmentation and cohort analysis 

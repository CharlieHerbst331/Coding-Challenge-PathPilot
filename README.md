## Quick Start

1. Clone the repository
2. Run the start script:
   ```
   ./start.sh
   ```
3. Open your browser and navigate to: http://localhost:5002

## Features

- **Journey Timeline Visualization**: Interactive timeline showing the progression of each user journey with detailed step information
- **AI-Powered Analysis**: Uses OpenAI's GPT-4 to analyze journey patterns and provide insights
- **User Journey Fingerprinting**: Creates fingerprints to identify key patterns that precede upgrades or cancellations
- **Outcome Prediction**: Predicts whether a user is likely to upgrade or cancel their subscription
- **Journey Analytics**: Aggregates and categorizes journeys to identify common patterns and trends
- **Modern UI/UX**: Clean, intuitive interface with responsive design

## Codebase Structure

### Core Files
- `app.py` - Entry point that runs the Flask application
- `run.py` - Alternative entry point that runs Flask on port 5002
- `start.sh` - Setup script that creates a virtual environment, installs dependencies, precomputes journey data, and starts the application
- `requirements.txt` - Lists all Python dependencies for the project

### Flask Application (`app/`)
- `__init__.py` - Initializes the Flask application
- `routes.py` - Defines all routes and API endpoints
- `templates/` (not shown) - Contains HTML templates for the frontend
- `static/` (not shown) - Contains JavaScript, CSS, and other static assets

### Utility Modules (`app/utils/`)
- `__init__.py` - Empty file marking utils as a Python package
- `cache.py` - Implements caching mechanism for journey data
- `data_processor.py` - Handles loading and preprocessing of journey data
- `fingerprinting.py` - Creates journey fingerprints and predicts outcomes

## Utility Modules in Detail

### Cache Module (`cache.py`)

The cache module implements a simple file-based caching system to avoid redundant processing of journey data.

#### Key Components:
- `JourneyCache` class: Handles storage and retrieval of processed journey data
  - `get_journey_data()`: Retrieves cached journey data by type and ID
  - `precompute_all_journeys()`: Processes all available journeys and stores them in cache
  - `_load_cache()` and `_save_cache()`: Handles reading from and writing to the cache file

The caching mechanism significantly improves performance by:
1. Avoiding repeated expensive API calls to OpenAI
2. Reducing data processing overhead
3. Enabling immediate access to previously analyzed journeys

### Data Processor Module (`data_processor.py`)

This module handles the loading, processing, and AI-based analysis of journey data.

#### Key Components:
- `process_journey_data()`: Loads and normalizes journey data from JSON files
  - Extracts steps from recording chunks
  - Adds detailed status labels
  - Calculates step durations
  - Sorts steps chronologically
  - Groups steps by status

- `analyze_journey_with_ai()`: Uses OpenAI's GPT-4 to generate insights about user journeys
  - Creates a structured prompt from journey data
  - Makes API calls to OpenAI
  - Parses and structures the AI response
  - Includes retry logic and fallback mechanisms

- `generate_fallback_analysis()`: Creates basic journey insights when AI analysis fails
  - Generates a simple but useful analysis based on status counts and patterns
  - Ensures the application remains functional even without API access

### Fingerprinting Module (`fingerprinting.py`)

This module implements the journey "fingerprinting" concept - a way to characterize and classify user journeys.

#### Key Components:
- `create_journey_fingerprint()`: Extracts key metrics from a journey to create a unique fingerprint
  - Calculates step counts and status distributions
  - Measures total journey time
  - Identifies upgrade and cancellation indicators through pattern matching
  - Determines conversion attempt timing and ratios

- `predict_outcome()`: Predicts whether a user is likely to upgrade or cancel based on fingerprint
  - Uses a weighted scoring system based on status distribution
  - Analyzes the ratio of upgrade vs. cancellation indicators
  - Provides confidence scores for predictions

The fingerprinting approach enables:
1. Standardized comparison between different user journeys
2. Quantitative prediction of user outcomes
3. Identification of common patterns across journeys

## Prediction Model Details

The prediction model in `fingerprinting.py` uses a weighted linear scoring system to estimate the probability of user upgrades or cancellations. Here's how it works:

### Core Algorithm

The model calculates an `upgrade_score` using the following formula:

```python
upgrade_score = (
    (converted_ratio * 0.8) +      # Strong positive indicator for upgrade
    (attempted_ratio * 0.4) -      # Moderate positive indicator
    (at_risk_ratio * 0.5) -        # Moderate negative indicator
    (churned_ratio * 0.9) +        # Strong negative indicator
    (upgrade_indicators * 0.1) -   # Slight boost for upgrade language
    (cancel_indicators * 0.1)      # Slight reduction for cancellation language
)
```

This score is then normalized to a probability between 0 and 1.

### Key Components

1. **Status Distribution Weighting**:
   - `converted_ratio`: Percentage of steps with "converted" status (weight: 0.8)
   - `attempted_ratio`: Percentage of steps with "attempted_conversion" status (weight: 0.4)
   - `at_risk_ratio`: Percentage of steps with "conversion_at_risk" status (weight: -0.5)
   - `churned_ratio`: Percentage of steps with "churned" status (weight: -0.9)

2. **Language Pattern Analysis**:
   - `upgrade_indicators`: Count of upgrade-related terms in journey text (weight: 0.1)
   - `cancel_indicators`: Count of cancellation-related terms in journey text (weight: -0.1)

3. **Decision Boundaries**:
   - Probability > 0.7: Predicted outcome is "upgrade"
   - Probability < 0.3: Predicted outcome is "cancel"
   - 0.3 ≤ Probability ≤ 0.7: Outcome is "uncertain"

4. **Final Status Override**:
   - If final status is "churned": Override to "cancel" with 95% confidence
   - If final status is "converted": Override to "upgrade" with 95% confidence

### Pattern Detection

The model uses regex pattern matching to identify key language indicators:

- **Upgrade Patterns**: Terms like "upgrade", "pricing", "subscribe", "payment", "pro", "premium", etc.
- **Cancel Patterns**: Terms like "cancel", "churn", "downgrade", "refund", "expensive", "dissatisfied", etc.

This heuristic approach provides a simple but effective prediction mechanism without requiring extensive training data or complex machine learning models.

## Application Flow

### Initialization Flow

1. `start.sh` sets up the environment and starts the application
2. `run.py` or `app.py` initializes the Flask application
3. `app/__init__.py` configures Flask settings
4. `app/routes.py` registers all routes and API endpoints
5. `JourneyCache.precompute_all_journeys()` pre-processes all available journey data

### Request Handling Flow

When a user accesses a journey page:

1. The browser sends a request to the `/journey/<journey_type>/<journey_id>` route
2. `view_journey()` in `routes.py` handles the request
3. The function checks `journey_cache` for previously processed data
4. If cached data exists, it's returned directly
5. If not, the journey is processed:
   - `process_journey_data()` extracts and normalizes steps
   - `analyze_journey_with_ai()` generates AI insights
   - `create_journey_fingerprint()` creates a journey fingerprint
   - `predict_outcome()` predicts user behavior
   - Results are cached for future requests
6. The rendered template is returned to the browser

### Analytics Flow

When a user accesses the analytics page:

1. The browser sends a request to the `/analytics` route
2. `analytics()` in `routes.py` handles the request
3. All journey files are retrieved and processed
4. For each journey:
   - Cached data is retrieved or generated
   - `categorize_journey_with_gpt()` classifies the journey
   - Category counts are updated
5. Chart data is generated and saved to a static file
6. The rendered template with chart data is returned to the browser

## Component Interaction Diagram

```
┌─────────────────┐     ┌───────────────┐     ┌────────────────┐
│                 │     │               │     │                │
│  Client Browser │◄────┤ Flask Routes  │◄────┤ HTML Templates │
│                 │     │               │     │                │
└─────────────────┘     └───────────────┘     └────────────────┘
         ▲                      ▲                      ▲
         │                      │                      │
         │                      │                      │
         │                      ▼                      │
         │              ┌───────────────┐              │
         │              │               │              │
         └───────────── │ Journey Cache │ ◄────────────┘
                        │               │
                        └───────────────┘
                                ▲
                                │
                                │
                                ▼
┌──────────────────┐    ┌───────────────┐    ┌─────────────────┐
│                  │    │               │    │                 │
│ Data Processor   │◄───┤ Journey Data  │───►│ Fingerprinting  │
│                  │    │  (JSON files) │    │                 │
└──────────────────┘    └───────────────┘    └─────────────────┘
         ▲                                             ▲
         │                                             │
         ▼                                             ▼
┌──────────────────┐                        ┌─────────────────┐
│                  │                        │                 │
│   OpenAI API     │                        │ Prediction Model│
│                  │                        │                 │
└──────────────────┘                        └─────────────────┘
```

## Key Technologies and Dependencies

- **Flask**: Web framework for handling HTTP requests and rendering templates
- **OpenAI API**: Powers the AI analysis of user journeys
- **SciKit-Learn**: Used for pattern detection and fingerprint analysis
- **JavaScript/Chart.js** (implied): For frontend visualizations and interactive elements
- **Python-dotenv**: Manages environment variables for API keys
- **NumPy/Pandas**: Data processing and analysis tools

## Approach and Methodology

### Data Processing

The application processes JSON files containing user journey recordings by:
1. Extracting and normalizing steps from multiple recording chunks
2. Sorting steps chronologically by date and time
3. Grouping steps by status (non-converted, attempted_conversion, converted, etc.)
4. Adding detailed contextual information to each step

### Journey Analysis

The AI-powered analysis:
1. Creates a structured prompt describing the journey steps
2. Sends the prompt to OpenAI's GPT-4 model
3. Processes the response to extract insights, critical points, and recommendations
4. Includes retry logic and fallback mechanisms for robustness

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

## Future Improvements

- Implement machine learning models trained on larger datasets
- Add more advanced visualization options (heatmaps, comparison views)
- Include real-time analysis of ongoing user journeys
- Expand the API for integration with other systems
- Add user segmentation and cohort analysis
- Implement A/B testing capabilities to validate optimization strategies

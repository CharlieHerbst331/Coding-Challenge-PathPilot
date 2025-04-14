# User Journey Analysis Coding Challenge

## Background

Our product team captures detailed user session data to understand customer behavior patterns that lead to subscription upgrades or cancellations. We have a collection of JSON files containing anonymized user journey recordings, with each file representing a different user session. These recordings contain timestamped actions, user status flags, and detailed descriptions of user interactions.

We need to build tools that can help us analyze these patterns to proactively identify users at risk of churning and recognize opportunities to encourage upgrades.

---

## Challenge Overview

Your task is to develop a solution that:

- Ingests and processes multiple user journey JSON files
- Generates visual timeline representations of each user journey that can be compared
- Creates a "fingerprint" or profile for each journey type to predict whether a user is likely to upgrade or cancel

---

## Requirements

### 1. Data Processing

- Parse the provided JSON files containing user journey recordings
- Clean and normalize the data for analysis
- Extract meaningful patterns and metrics from the user journeys

### 2. Timeline Visualization

- Create a visual representation showing the progression of each user journey
- Design the visualization to allow easy comparison between different journey types
- Include timestamps, user actions, and status changes in the visualization
- The timeline should clearly distinguish between different journey stages:
  - `converted`
  - `conversion_at_risk`
  - `churned`

### 3. User Journey Fingerprinting

- Develop a method to profile different types of user journeys
- Identify key indicators or patterns that precede subscription upgrades or cancellations
- Create a model or algorithm that can classify a user journey as likely to result in upgrade or cancellation
- Provide metrics on the accuracy of your classification method

---

## Technical Requirements

- Python is preferred, but other languages are acceptable
- Include clear documentation and instructions for running your code
- Write modular, maintainable code with appropriate comments
- Include appropriate error handling and edge case management
- Optimize for performance when processing multiple files

---

## Deliverables

- **Source code** for your solution
- A `README.md` file that includes:
  - A clear explanation of your approach to solving the problem
  - Your methodology for journey fingerprinting and classification
  - Instructions for running the code
  - Example outputs from your visualization
  - Discussion of any challenges faced and how you overcame them
  - Thoughts on how this solution could be improved or expanded
  - Any visualization outputs or sample results
- **Unit tests** demonstrating the correctness of your solution

---


##Build out specifications (Very Important!)

this implementation should be a web app with dropdown bars for each individual user journey, in each dropdown bar should outline the steps the user has went htrough and include the analysis by ChatGPT in each section. This should incorporate modern UI/UX and styling and should have clean and intuitive flow. Also incorporate the fingerprinting into this web app.


## Data Format

You will receive a zip file containing multiple JSON files. Each file represents user session recordings with the following structure:

```json
{
  "export-[identifier].ph-recording-chunk-summaries": {
    "steps": [
      {
        "label": "Action Description",
        "date": "YYYY-MM-DD",
        "status": "converted|non-converted|conversion_at_risk|churned",
        "recordingReel": {
          "start": "MM:SS.S",
          "end": "MM:SS.S",
          "details": "Detailed description of user action",
          "filename": "export-[identifier].ph-recording-chunk-summaries.json",
          "start_ms_since": 12345,
          "end_ms_since": 67890,
          "recording_id": "export-[identifier].ph-recording-chunk-summaries"
        }
      }
      // Additional steps...
    ],
    "usage_metadata": {
      "input_tokens": 12345,
      "output_tokens": 6789,
      "total_tokens": 19234
    },
    "_order": 0
  }
  // Additional recording chunks...
}




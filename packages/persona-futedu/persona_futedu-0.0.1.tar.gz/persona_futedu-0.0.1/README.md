# Student Persona Generator

A Python package for generating detailed student personas from educational chat conversations using Google's Gemini API.

## Overview

The Student Persona Generator analyzes chat conversations between students and educational AI systems to create comprehensive student profiles. These profiles include information about the student's knowledge level, engagement, learning style, interests, and question complexity, providing valuable insights for educators.

## Features

- Analyze educational chat conversations stored in JSON format
- Generate detailed student personas with multiple metrics
- Save personas as JSON files for further analysis or integration
- Easy-to-use command-line interface

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/persona_module.git
cd persona_module

# Install the package
pip install -e .
```

## Requirements

- Python 3.6+
- Google Gemini API key
- Required Python packages:
  - google-generativeai
  - python-dotenv

## Usage

### Command Line Interface

```bash
# Basic usage
persona path/to/chat.json

# Specify output file
persona path/to/chat.json -o output.json

# Provide API key directly
persona path/to/chat.json -k YOUR_API_KEY
```

If you don't provide arguments, the CLI will prompt you for the required information.

### Environment Variables

You can set your Gemini API key as an environment variable:

```bash
export GEMINI_API_KEY=your_api_key
```

Or create a `.env` file in your project directory:

```
GEMINI_API_KEY=your_api_key
```

### Python API

```python
from persona import PersonaGenerator

# Initialize the generator
generator = PersonaGenerator("path/to/chat.json", "your_gemini_api_key")

# Generate a persona
persona = generator.generate_persona()

# Save the persona to a file
output_file = generator.save_persona(persona, "output.json")
```

## Input Format

The input JSON file should have the following structure:

```json
{
  "subject": "Mathematics",
  "title": "Algebra Fundamentals",
  "date": "2023-06-15",
  "duration": 45,
  "student_id": "S12345",
  "messages": [
    {
      "sender": "user",
      "content": "I'm having trouble understanding quadratic equations.",
      "timestamp": "14:30:15"
    },
    {
      "sender": "bot",
      "content": "I'd be happy to help! Let's start with the basics...",
      "timestamp": "14:30:45"
    },
    ...
  ]
}
```

## Output Format

The generated persona is a JSON object with the following structure:

```json
{
  "student_profile": {
    "knowledge_level": "beginner",
    "engagement_level": "highly engaged",
    "dominant_learning_style": "analytical",
    "primary_interests": ["algebra", "problem-solving"],
    "question_complexity": 6,
    "engagement_score": 8.5
  },
  "detailed_analysis": {
    "complexity": {
      "complexity_score": 6.2,
      "avg_message_length": 42,
      "follow_up_questions": 5,
      "analytical_questions": 3,
      "total_questions": 8
    },
    "engagement": {
      "engagement_score": 8.5,
      "message_frequency": "high",
      "session_duration": 45,
      "avg_time_between_messages": 30
    },
    "interests": {
      "top_interests": ["algebra", "problem-solving", "real-world applications"],
      "interest_distribution": {
        "algebra": 0.6,
        "problem-solving": 0.3,
        "real-world applications": 0.1
      }
    },
    "learning_style": {
      "dominant_style": "analytical",
      "style_breakdown": {
        "analytical": 0.7,
        "practical": 0.2,
        "big-picture": 0.1
      }
    }
  },
  "summary": "This student is a beginner in algebra who shows high engagement...",
  "session_info": {
    "subject": "Mathematics",
    "title": "Algebra Fundamentals",
    "date": "2023-06-15",
    "duration": 45,
    "student_id": "S12345"
  }
}
```

## License

[MIT License](LICENSE)

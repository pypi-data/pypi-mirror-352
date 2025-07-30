#!/usr/bin/env python3
"""
Command-line interface for the Student Persona Generator.
"""

import os
import sys
import argparse
from dotenv import load_dotenv
from .persona_generator import PersonaGenerator

def main():
    """
    Main entry point for the persona generator CLI.
    """
    # Load environment variables from .env file if present
    load_dotenv()
    
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Generate student personas from educational chat conversations using Google's Gemini API."
    )
    parser.add_argument(
        "json_file",
        help="Path to the JSON file containing the chat conversation.",
        nargs="?",
        default=None
    )
    parser.add_argument(
        "-o", "--output",
        help="Path to save the generated persona JSON file.",
        default=None
    )
    parser.add_argument(
        "-k", "--api-key",
        help="Google Gemini API key. If not provided, will look for GEMINI_API_KEY environment variable.",
        default=None
    )
    
    args = parser.parse_args()
    
    # Check if JSON file is provided or prompt for it
    json_file = args.json_file
    if not json_file:
        json_file = input("Enter path to the JSON chat file: ")
    
    if not os.path.exists(json_file):
        print(f"Error: Could not find {json_file}")
        return 1
    
    # Get API key from arguments, environment variable, or prompt
    api_key = args.api_key or os.environ.get('GEMINI_API_KEY')
    if not api_key:
        api_key = input("Please enter your Gemini API key: ")
        if not api_key:
            print("Error: Gemini API key is required")
            return 1
    
    print(f"Analyzing chat conversation from {json_file}...")
    
    # Generate student persona
    generator = PersonaGenerator(json_file, api_key)
    persona = generator.generate_persona()
    
    if persona:
        # Save persona to file
        output_file = generator.save_persona(persona, args.output)
        
        if output_file:
            print(f"\nStudent Persona Generated Successfully!")
            print(f"Saved to: {output_file}")
            print("\nSummary:")
            print("-" * 80)
            print(persona.get('summary', 'No summary available'))
            print("-" * 80)
            print("\nStudent Profile:")
            for key, value in persona.get('student_profile', {}).items():
                print(f"- {key.replace('_', ' ').title()}: {value}")
            return 0
    else:
        print("Failed to generate student persona.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
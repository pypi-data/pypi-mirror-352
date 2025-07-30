#!/usr/bin/env python3
"""
Student Persona Generator

This module contains the PersonaGenerator class for analyzing educational chat conversations
and generating student personas using Google's Gemini API.
"""

import json
import os
import datetime
from google import genai
from google.genai import types

class PersonaGenerator:
    """
    A class for generating student personas from educational chat conversations using Google's Gemini API.
    
    Attributes:
        json_file (str): Path to the JSON file containing the chat conversation.
        api_key (str): Google Gemini API key.
        data (dict): Parsed JSON data from the chat file.
        client (genai.Client): Google Generative AI client.
    """
    
    def __init__(self, json_file, api_key):
        """
        Initialize the PersonaGenerator with a JSON file and API key.
        
        Args:
            json_file (str): Path to the JSON file containing the chat conversation.
            api_key (str): Google Gemini API key.
        """
        self.json_file = json_file
        self.api_key = api_key
        self.data = self._load_json()
        self.client = genai.Client(api_key=self.api_key)
        
    def _load_json(self):
        """
        Load the JSON file containing the chat conversation.
        
        Returns:
            dict: The parsed JSON data.
        """
        with open(self.json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _format_conversation(self):
        """
        Format the conversation for the Gemini API.
        
        Returns:
            str: Formatted conversation string.
        """
        messages = self.data.get('messages', [])
        formatted_conversation = []
        
        for msg in messages:
            sender = msg.get('sender')
            content = msg.get('content')
            timestamp = msg.get('timestamp')
            
            formatted_message = f"{sender.upper()} ({timestamp}): {content}"
            formatted_conversation.append(formatted_message)
            
        return "\n\n".join(formatted_conversation)
    
    def _create_prompt(self):
        """
        Create a prompt for the Gemini API to generate a student persona.
        
        Returns:
            str: The prompt for the Gemini API.
        """
        conversation = self._format_conversation()
        session_info = {
            'subject': self.data.get('subject'),
            'title': self.data.get('title'),
            'date': self.data.get('date'),
            'duration': self.data.get('duration')
        }
        
        prompt = f"""
You are an expert educational analyst. Analyze the following chat conversation between a student (USER) and an educational AI (BOT).

Session Information:
- Subject: {session_info['subject']}
- Title: {session_info['title']}
- Date: {session_info['date']}
- Duration: {session_info['duration']} minutes

Chat Conversation:
{conversation}

Based on this conversation, create a detailed student persona that includes:

1. Knowledge Level: Assess if the student is a beginner, intermediate, or advanced learner based on their questions and engagement.
2. Engagement Level: Evaluate how engaged the student is with the material (passive, moderately engaged, highly engaged).
3. Learning Style: Identify the student's dominant learning style (analytical, detail-oriented, big-picture, practical, or balanced).
4. Interests: Determine the student's primary interests within the subject area.
5. Question Complexity: Rate the complexity of the student's questions on a scale of 1-10.
6. Detailed Analysis: Provide metrics on message frequency, follow-up questions, session duration, etc.
7. Educational Recommendations: Suggest teaching approaches that would be most effective for this student.

Format your response as a valid JSON object with the following structure:
{{
  "student_profile": {{
    "knowledge_level": string,
    "engagement_level": string,
    "dominant_learning_style": string,
    "primary_interests": [string],
    "question_complexity": number,
    "engagement_score": number
  }},
  "detailed_analysis": {{
    "complexity": {{
      "complexity_score": number,
      "avg_message_length": number,
      "follow_up_questions": number,
      "analytical_questions": number,
      "total_questions": number
    }},
    "engagement": {{
      "engagement_score": number,
      "message_frequency": string,
      "session_duration": number,
      "avg_time_between_messages": number
    }},
    "interests": {{
      "top_interests": [string],
      "interest_distribution": {{}}
    }},
    "learning_style": {{
      "dominant_style": string,
      "style_breakdown": {{}}
    }}
  }},
  "summary": string
}}

IMPORTANT: Return ONLY a valid JSON object with no additional text, markdown formatting, or code blocks.
"""
        return prompt
    
    def generate_persona(self):
        """
        Generate a student persona using the Gemini API.
        
        Returns:
            dict: The generated student persona, or None if generation failed.
        """
        prompt = self._create_prompt()
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-preview-04-17",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1
                )
            )
            
            # Extract the JSON from the response
            response_text = response.text
            
            # Clean up the response text to handle potential markdown code blocks
            if "```json" in response_text:
                # Extract content between ```json and ``` markers
                start_idx = response_text.find("```json") + 7
                end_idx = response_text.rfind("```")
                if start_idx > 7 and end_idx > start_idx:
                    response_text = response_text[start_idx:end_idx].strip()
            elif "```" in response_text:
                # Extract content between ``` markers
                start_idx = response_text.find("```") + 3
                end_idx = response_text.rfind("```")
                if start_idx > 3 and end_idx > start_idx:
                    response_text = response_text[start_idx:end_idx].strip()
            
            # Parse the JSON response
            try:
                persona = json.loads(response_text)
                
                # Add session info to the persona
                persona['session_info'] = {
                    'subject': self.data.get('subject'),
                    'title': self.data.get('title'),
                    'date': self.data.get('date'),
                    'duration': self.data.get('duration'),
                    'student_id': self.data.get('student_id')
                }
                
                return persona
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response: {e}")
                print("Raw response:")
                print(response_text)
                
                # Try to fix common JSON formatting issues
                try:
                    # Sometimes the model might include extra characters or formatting
                    # Try to extract just the JSON part
                    if "{" in response_text and "}" in response_text:
                        start_idx = response_text.find("{")
                        end_idx = response_text.rfind("}") + 1
                        clean_json = response_text[start_idx:end_idx]
                        persona = json.loads(clean_json)
                        
                        # Add session info to the persona
                        persona['session_info'] = {
                            'subject': self.data.get('subject'),
                            'title': self.data.get('title'),
                            'date': self.data.get('date'),
                            'duration': self.data.get('duration'),
                            'student_id': self.data.get('student_id')
                        }
                        
                        return persona
                except Exception:
                    return None
                
                return None
                
        except Exception as e:
            print(f"Error generating content with Gemini API: {e}")
            return None
    
    def save_persona(self, persona, output_file=None):
        """
        Save the generated persona to a JSON file.
        
        Args:
            persona (dict): The persona to save.
            output_file (str, optional): Path to save the persona. If None, a name will be generated.
            
        Returns:
            str: Path to the saved file, or None if saving failed.
        """
        if not persona:
            print("No persona to save.")
            return None
        
        # Use the title from the data to name the output file
        if output_file is None:
            title = self.data.get('title', 'student_persona').replace(' ', '_').lower()
            output_file = f"{title}_persona.json"
            
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(persona, f, indent=2)
            
        return output_file 
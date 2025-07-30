"""
Student Persona Generator

A package for generating student personas from educational chat conversations using Google's Gemini API.
"""

__version__ = "0.0.1"

from .persona_generator import PersonaGenerator
from .cli import main

__all__ = ["PersonaGenerator", "main"] 
#!/usr/bin/env python3
"""
Test script to verify the application works correctly
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Test imports
    print("Testing imports...")
    
    import flask
    print("✓ Flask imported successfully")
    
    import google.generativeai as genai
    print("✓ Google Generative AI imported successfully")
    
    from flask_cors import CORS
    print("✓ Flask-CORS imported successfully")
    
    import yfinance as yf
    print("✓ yfinance imported successfully")
    
    import pandas as pd
    print("✓ pandas imported successfully")
    
    from dotenv import load_dotenv
    print("✓ python-dotenv imported successfully")
    
    # Test loading environment variables
    load_dotenv()
    gemini_key = os.getenv('GEMINI_API_KEY')
    if gemini_key:
        print(f"✓ Gemini API key loaded: {gemini_key[:10]}...")
    else:
        print("⚠ Gemini API key not found in environment")
    
    # Test basic Gemini configuration
    genai.configure(api_key=gemini_key)
    print("✓ Gemini AI configured successfully")
    
    print("\n✅ All dependencies are working correctly!")
    print("🚀 The application should be ready to run!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

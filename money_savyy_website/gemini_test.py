#!/usr/bin/env python3
"""
Quick test script to check Gemini models and fix the issue
"""

import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure Gemini AI
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
print(f"API Key loaded: {GEMINI_API_KEY[:10]}..." if GEMINI_API_KEY else "No API key found")

genai.configure(api_key=GEMINI_API_KEY)

def list_available_models():
    """List all available Gemini models"""
    try:
        print("🔍 Fetching available Gemini models...")
        models = genai.list_models()
        
        available_models = []
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                available_models.append(model.name)
                print(f"✅ {model.name} - Supports generateContent")
            else:
                print(f"❌ {model.name} - Does not support generateContent")
        
        return available_models
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        return []

def test_model(model_name):
    """Test a specific model"""
    try:
        print(f"\n🧪 Testing model: {model_name}")
        model = genai.GenerativeModel(model_name)
        
        # Simple test prompt
        response = model.generate_content("What is 2+2? Answer briefly.")
        print(f"✅ {model_name} works! Response: {response.text}")
        return True
    except Exception as e:
        print(f"❌ {model_name} failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Gemini Model Diagnostics\n")
    
    # Test the specific model first
    print("🎯 Testing gemini-2.0-flash specifically...")
    if test_model("gemini-2.0-flash"):
        print("✅ gemini-2.0-flash is working perfectly!")
    
    # List available models
    available_models = list_available_models()
    
    if not available_models:
        print("❌ No models available for generateContent")
    else:
        print(f"\n📋 Found {len(available_models)} compatible models:")
        for model in available_models:
            print(f"  - {model}")
        
        # Test a few key models
        print(f"\n🧪 Testing key models...")
        key_models = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
        for model_name in key_models:
            if model_name in [m.split('/')[-1] for m in available_models]:
                test_model(model_name)

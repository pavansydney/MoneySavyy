#!/usr/bin/env python3
"""
Quick test for gemini-2.0-flash model specifically
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

def test_gemini_2_flash():
    """Test gemini-2.0-flash specifically"""
    try:
        print("🧪 Testing gemini-2.0-flash model...")
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Test with a simple prompt
        response = model.generate_content("Analyze TCS stock briefly in 2 sentences.")
        print(f"✅ SUCCESS! Model response: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_stock_analysis():
    """Test stock analysis with gemini-2.0-flash"""
    try:
        print("\n📈 Testing stock analysis prompt...")
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = """
        Analyze the Indian stock TCS with the following data:
        - Current Price: ₹3850.75
        - Price Change: +1.5%
        - Volume: 2,500,000
        
        Provide analysis in JSON format with:
        - "recommendation": "BUY", "HOLD", or "SELL"
        - "risk_level": "LOW", "MEDIUM", or "HIGH"
        - "summary": Brief analysis
        """
        
        response = model.generate_content(prompt)
        print(f"✅ Stock Analysis Response: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ Stock Analysis Failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Gemini 2.0 Flash Model\n")
    
    # Basic test
    if test_gemini_2_flash():
        print("\n🎉 Basic test passed! Now testing stock analysis...")
        test_stock_analysis()
    else:
        print("\n❌ Basic test failed. Check your API key and model access.")

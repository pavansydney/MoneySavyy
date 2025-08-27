#!/usr/bin/env python3
"""
Quick test to check the API response structure
"""

import requests
import json

def test_api_response():
    try:
        print("🧪 Testing API response structure...")
        response = requests.get("http://localhost:5000/api/analyze/TCS", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ API Response received!")
            print(f"Symbol: {data.get('symbol', 'N/A')}")
            print(f"Company: {data.get('company_name', 'N/A')}")
            
            # Check recommendation structure
            if 'recommendation' in data:
                rec = data['recommendation']
                print(f"\n📊 Recommendation structure:")
                print(f"Type: {type(rec)}")
                print(f"Content: {rec}")
                
                if isinstance(rec, dict):
                    print("  - recommendation:", rec.get('recommendation', 'N/A'))
                    print("  - color:", rec.get('color', 'N/A'))
                    print("  - confidence:", rec.get('confidence', 'N/A'))
                    print("  - score:", rec.get('score', 'N/A'))
            
            # Check other structures
            print(f"\n🔍 Available keys: {list(data.keys())}")
            
            if 'news_sentiment' in data:
                print(f"📰 News Sentiment Available: {bool(data['news_sentiment'])}")
            
            if 'fundamentals_analysis' in data:
                print(f"📈 Fundamentals Analysis Available: {bool(data['fundamentals_analysis'])}")
                
            if 'gemini_analysis' in data:
                print(f"🤖 Gemini Analysis Available: {bool(data['gemini_analysis'])}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Is the Flask app running on localhost:5000?")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_api_response()

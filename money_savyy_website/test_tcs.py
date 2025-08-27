#!/usr/bin/env python3
"""
Test the fixed TCS stock analysis
"""

import requests
import json

def test_tcs_analysis():
    """Test TCS stock analysis with the fixes"""
    try:
        print("🧪 Testing TCS stock analysis...")
        
        # Test the API endpoint
        response = requests.get("http://localhost:5000/api/analyze/TCS", timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS! TCS analysis worked")
            
            # Print key information
            if 'success' in data and data['success']:
                print(f"📊 Stock: {data.get('symbol', 'N/A')}")
                print(f"💰 Current Price: ₹{data.get('current_price', 'N/A')}")
                print(f"📈 Change: {data.get('change_percent', 'N/A')}%")
                print(f"🎯 Recommendation: {data.get('recommendation', 'N/A')}")
                
                # Check if Gemini analysis is present
                if 'gemini_analysis' in data:
                    gemini = data['gemini_analysis']
                    print(f"🤖 Gemini Analysis Available: {bool(gemini)}")
                    if gemini:
                        print(f"   - Technical: {gemini.get('technical_summary', 'N/A')[:100]}...")
                        print(f"   - Recommendation: {gemini.get('recommendation', 'N/A')}")
                        print(f"   - Risk Level: {gemini.get('risk_level', 'N/A')}")
                else:
                    print("⚠️ No Gemini analysis in response")
            else:
                print("❌ Response indicates failure")
                print(f"Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Is the Flask app running on localhost:5000?")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_tcs_analysis()

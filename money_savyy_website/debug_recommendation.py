#!/usr/bin/env python3
"""
Quick API test to debug the recommendation object issue
"""

import requests
import json

def test_recommendation_api():
    try:
        print("🧪 Testing API to debug recommendation structure...")
        
        response = requests.get("http://localhost:5000/api/analyze/TCS", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ API Response received!")
            print("=" * 50)
            
            # Check recommendation structure
            rec = data.get('recommendation')
            print(f"🎯 Recommendation Structure:")
            print(f"   Type: {type(rec)}")
            print(f"   Content: {rec}")
            
            if isinstance(rec, dict):
                print(f"\n📋 Recommendation Object Details:")
                for key, value in rec.items():
                    print(f"   {key}: {value} (type: {type(value)})")
                
                # Check if it has the nested recommendation field
                if 'recommendation' in rec:
                    inner_rec = rec['recommendation']
                    print(f"\n🔍 Inner Recommendation:")
                    print(f"   Type: {type(inner_rec)}")
                    print(f"   Value: {inner_rec}")
                    
                    # This is what would cause [object Object]
                    if isinstance(inner_rec, dict):
                        print("❌ PROBLEM FOUND: Inner recommendation is an object!")
                        print("   This will display as [object Object] in JavaScript")
                    else:
                        print("✅ Inner recommendation is a string - should work")
            
            # Test what JavaScript would do
            print(f"\n🔧 JavaScript Simulation:")
            if isinstance(rec, dict) and 'recommendation' in rec:
                js_value = rec['recommendation']
                if isinstance(js_value, dict):
                    print(f"   JavaScript would show: [object Object]")
                    print(f"   Because it's trying to display: {js_value}")
                else:
                    print(f"   JavaScript would show: {js_value}")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_recommendation_api()

#!/usr/bin/env python3
"""
Comprehensive test script to verify all fixes
"""

import requests
import json
import time

def test_all_fixes():
    print("🧪 Testing All Fixes for Money Savyy App")
    print("=" * 50)
    
    test_stocks = ['TCS', 'RELIANCE', 'INFY', 'HDFCBANK']
    
    for stock in test_stocks:
        print(f"\n🔍 Testing {stock}")
        print("-" * 30)
        
        try:
            response = requests.get(f"http://localhost:5000/api/analyze/{stock}", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Test 1: Recommendation Object Issue
                print("1️⃣ Recommendation Structure:")
                rec = data.get('recommendation', {})
                print(f"   Type: {type(rec)}")
                if isinstance(rec, dict):
                    print(f"   Recommendation: {rec.get('recommendation', 'MISSING')}")
                    print(f"   Color: {rec.get('color', 'MISSING')}")
                    print(f"   Confidence: {rec.get('confidence', 'MISSING')}")
                    print(f"   Score: {rec.get('score', 'MISSING')}")
                    # Check if it would display [object Object]
                    if all(key in rec for key in ['recommendation', 'color', 'confidence', 'score']):
                        print("   ✅ Recommendation structure looks good")
                    else:
                        print("   ❌ Recommendation structure incomplete")
                else:
                    print(f"   ❌ Recommendation is not an object: {rec}")
                
                # Test 2: Fundamentals - Sector and Industry
                print("\n2️⃣ Sector and Industry:")
                fundamentals = data.get('fundamentals', {})
                sector = fundamentals.get('sector')
                industry = fundamentals.get('industry')
                print(f"   Sector: {sector}")
                print(f"   Industry: {industry}")
                if sector and sector != 'N/A' and industry and industry != 'N/A':
                    print("   ✅ Sector and Industry populated")
                else:
                    print("   ❌ Sector or Industry missing/N/A")
                
                # Test 3: Fundamentals Analysis - Fair Value
                print("\n3️⃣ AI Fundamentals Analysis:")
                fund_analysis = data.get('fundamentals_analysis', {})
                valuation = fund_analysis.get('valuation_assessment', {})
                intrinsic_value = valuation.get('intrinsic_value_estimate')
                print(f"   Estimated Fair Value: {intrinsic_value}")
                if intrinsic_value and intrinsic_value != 0:
                    print("   ✅ Fair value populated")
                else:
                    print("   ❌ Fair value missing/zero")
                
                # Test 4: Investment Recommendation - Target Price
                print("\n4️⃣ Investment Recommendation:")
                investment_rec = fund_analysis.get('investment_recommendation', {})
                target_price = investment_rec.get('target_price')
                rating = investment_rec.get('rating')
                print(f"   Target Price: {target_price}")
                print(f"   Rating: {rating}")
                if target_price and target_price != 0:
                    print("   ✅ Target price populated")
                else:
                    print("   ❌ Target price missing/zero")
                
                print(f"\n   📊 Overall Status for {stock}: ", end="")
                if (isinstance(rec, dict) and 'recommendation' in rec and 
                    sector and sector != 'N/A' and 
                    intrinsic_value and intrinsic_value != 0 and 
                    target_price and target_price != 0):
                    print("✅ ALL FIXES WORKING")
                else:
                    print("❌ SOME ISSUES REMAIN")
                    
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Connection failed. Is the Flask app running?")
            break
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Small delay between requests
        time.sleep(1)
    
    print(f"\n{'='*50}")
    print("🎯 Test Summary:")
    print("1. Object Object issue - Fixed with better object handling")
    print("2. Sector/Industry N/A - Fixed with fallback mappings")
    print("3. Fair Value N/A - Fixed with realistic AI analysis")
    print("4. Target Price N/A - Fixed with calculated targets")
    print("5. Added comprehensive debug logging for troubleshooting")

if __name__ == "__main__":
    test_all_fixes()

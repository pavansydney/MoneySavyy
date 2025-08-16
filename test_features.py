#!/usr/bin/env python3
"""
Test script to validate all advanced features
"""

import yfinance as yf
from advanced_stock_analyzer import (
    predict_future_price, 
    get_stock_news, 
    generate_trading_recommendation, 
    get_dividend_info,
    analyze_sentiment
)

def test_all_features():
    """Test all advanced features"""
    print("🧪 TESTING ALL ADVANCED FEATURES")
    print("="*50)
    
    # Test stock
    symbol = "TCS.NS"
    stock = yf.Ticker(symbol)
    hist_data = stock.history(period="6mo")
    
    if hist_data.empty:
        print("❌ No data available for testing")
        return
    
    current_price = hist_data['Close'].iloc[-1]
    company_name = "Tata Consultancy Services Limited"
    
    print(f"Testing with: {symbol} - {company_name}")
    print(f"Current Price: ₹{current_price:.2f}")
    print()
    
    # Test 1: AI Prediction
    print("1️⃣ Testing AI Price Prediction...")
    prediction_info, error = predict_future_price(hist_data, days_ahead=7)
    if prediction_info:
        print(f"✅ Prediction successful!")
        print(f"   Model: {prediction_info['model_used']}")
        print(f"   Accuracy: {prediction_info['accuracy']:.2%}")
        print(f"   7-day prediction: {prediction_info['predicted_change']:+.2f} ({prediction_info['predicted_change_percent']:+.1f}%)")
    else:
        print(f"❌ Prediction failed: {error}")
    print()
    
    # Test 2: News Fetching
    print("2️⃣ Testing News Fetching...")
    news_data = get_stock_news(symbol, company_name)
    if news_data and len(news_data) > 0:
        print(f"✅ Found {len(news_data)} news items")
        for i, news in enumerate(news_data[:2], 1):
            print(f"   {i}. {news['title'][:60]}...")
            print(f"      Sentiment: {news['sentiment']}")
    else:
        print("❌ No news found")
    print()
    
    # Test 3: Sentiment Analysis
    print("3️⃣ Testing Sentiment Analysis...")
    test_texts = [
        "TCS reports strong quarterly earnings with 20% growth",
        "TCS faces layoffs and restructuring challenges",
        "TCS maintains steady performance in Q2"
    ]
    
    for text in test_texts:
        sentiment = analyze_sentiment(text)
        print(f"   Text: {text}")
        print(f"   Sentiment: {sentiment}")
    print()
    
    # Test 4: Trading Recommendation
    print("4️⃣ Testing Trading Recommendation...")
    import ta
    rsi = ta.momentum.rsi(hist_data['Close'], window=14).iloc[-1]
    macd = ta.trend.macd_diff(hist_data['Close']).iloc[-1]
    
    recommendation = generate_trading_recommendation(hist_data, prediction_info, current_price, rsi, macd)
    print(f"✅ Recommendation generated!")
    print(f"   Action: {recommendation['recommendation']}")
    print(f"   Confidence: {recommendation['confidence']}")
    print(f"   Risk Level: {recommendation['risk_level']}")
    print(f"   Score: {recommendation['score']}")
    print()
    
    # Test 5: Dividend Information
    print("5️⃣ Testing Dividend Information...")
    dividend_info = get_dividend_info(stock)
    if isinstance(dividend_info, dict):
        print(f"✅ Dividend info retrieved!")
        print(f"   Last Dividend: ₹{dividend_info['last_dividend']:.2f}")
        print(f"   Yield: {dividend_info['dividend_yield']:.2f}%")
    else:
        print(f"ℹ️ {dividend_info}")
    print()
    
    print("🎉 ALL TESTS COMPLETED!")
    print("="*50)

if __name__ == "__main__":
    test_all_features()

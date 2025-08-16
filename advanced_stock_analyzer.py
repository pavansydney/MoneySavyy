#!/usr/bin/env python3
"""
Advanced Stock Analyzer with AI Predictions, News, and Trading Recommendations
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
from difflib import get_close_matches
import ta
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score
import requests
from bs4 import BeautifulSoup
import feedparser
from textblob import TextBlob
import re

warnings.filterwarnings('ignore')
plt.style.use('default')

# Popular Indian stocks dictionary
INDIAN_STOCKS = {
    'tcs': 'TCS.NS', 'tata consultancy services': 'TCS.NS',
    'infosys': 'INFY.NS', 'wipro': 'WIPRO.NS',
    'reliance': 'RELIANCE.NS', 'reliance industries': 'RELIANCE.NS',
    'hdfc bank': 'HDFCBANK.NS', 'hdfc': 'HDFCBANK.NS',
    'icici bank': 'ICICIBANK.NS', 'icici': 'ICICIBANK.NS',
    'sbi': 'SBIN.NS', 'state bank of india': 'SBIN.NS',
    'bharti airtel': 'BHARTIARTL.NS', 'airtel': 'BHARTIARTL.NS',
    'itc': 'ITC.NS', 'hindustan unilever': 'HINDUNILVR.NS', 'hul': 'HINDUNILVR.NS',
    'bajaj finance': 'BAJFINANCE.NS', 'bajaj': 'BAJFINANCE.NS',
    'maruti suzuki': 'MARUTI.NS', 'maruti': 'MARUTI.NS',
    'asian paints': 'ASIANPAINT.NS', 'larsen': 'LT.NS', 'l&t': 'LT.NS',
    'axis bank': 'AXISBANK.NS', 'axis': 'AXISBANK.NS',
    'kotak bank': 'KOTAKBANK.NS', 'kotak': 'KOTAKBANK.NS',
    'sun pharma': 'SUNPHARMA.NS', 'titan': 'TITAN.NS',
    'nestle': 'NESTLEIND.NS', 'ongc': 'ONGC.NS', 'ntpc': 'NTPC.NS'
}

def search_stock_symbol(user_input):
    """Search for stock symbol based on user input"""
    user_input = user_input.lower().strip()
    
    if user_input in INDIAN_STOCKS:
        return INDIAN_STOCKS[user_input], user_input
    
    for stock_name, symbol in INDIAN_STOCKS.items():
        if user_input in stock_name or stock_name in user_input:
            return symbol, stock_name
    
    close_matches = get_close_matches(user_input, INDIAN_STOCKS.keys(), n=1, cutoff=0.6)
    if close_matches:
        return INDIAN_STOCKS[close_matches[0]], close_matches[0]
    
    return user_input.upper() + '.NS', user_input

def predict_future_price(stock_data, days_ahead=30):
    """
    Predict future stock prices using machine learning
    """
    try:
        if len(stock_data) < 50:
            return None, "Insufficient data for prediction"
        
        # Prepare data for prediction
        data = stock_data.copy()
        data['Days'] = range(len(data))
        data['Price'] = data['Close']
        
        # Use multiple features for prediction
        data['SMA_10'] = data['Close'].rolling(window=10).mean()
        data['SMA_30'] = data['Close'].rolling(window=30).mean()
        data['Volume_MA'] = data['Volume'].rolling(window=10).mean()
        data['Price_Change'] = data['Close'].pct_change()
        data['Volatility'] = data['Close'].rolling(window=20).std()
        
        # Remove NaN values
        data = data.dropna()
        
        if len(data) < 30:
            return None, "Insufficient clean data for prediction"
        
        # Prepare features
        X = data[['Days', 'SMA_10', 'SMA_30', 'Volume_MA', 'Volatility']].values
        y = data['Price'].values
        
        # Train multiple models
        models = {}
        
        # Linear Regression
        lr_model = LinearRegression()
        lr_model.fit(X, y)
        models['Linear'] = lr_model
        
        # Polynomial Regression (degree 2)
        poly_features = PolynomialFeatures(degree=2, include_bias=False)
        X_poly = poly_features.fit_transform(X)
        poly_model = LinearRegression()
        poly_model.fit(X_poly, y)
        models['Polynomial'] = (poly_model, poly_features)
        
        # Calculate model accuracy
        lr_score = r2_score(y, lr_model.predict(X))
        poly_score = r2_score(y, poly_model.predict(X_poly))
        
        # Choose best model
        if poly_score > lr_score:
            best_model = 'Polynomial'
            accuracy = poly_score
        else:
            best_model = 'Linear'
            accuracy = lr_score
        
        # Make future predictions
        last_day = data['Days'].iloc[-1]
        future_days = []
        predictions = []
        
        for i in range(1, days_ahead + 1):
            future_day = last_day + i
            
            # Use last known values for other features
            last_sma10 = data['SMA_10'].iloc[-1]
            last_sma30 = data['SMA_30'].iloc[-1]
            last_volume_ma = data['Volume_MA'].iloc[-1]
            last_volatility = data['Volatility'].iloc[-1]
            
            future_X = np.array([[future_day, last_sma10, last_sma30, last_volume_ma, last_volatility]])
            
            if best_model == 'Linear':
                pred_price = models['Linear'].predict(future_X)[0]
            else:
                future_X_poly = models['Polynomial'][1].transform(future_X)
                pred_price = models['Polynomial'][0].predict(future_X_poly)[0]
            
            future_days.append(future_day)
            predictions.append(pred_price)
        
        # Create prediction dataframe
        future_dates = [data.index[-1] + timedelta(days=i) for i in range(1, days_ahead + 1)]
        prediction_df = pd.DataFrame({
            'Date': future_dates,
            'Predicted_Price': predictions
        })
        
        # Calculate prediction trend
        current_price = data['Price'].iloc[-1]
        avg_future_price = np.mean(predictions)
        price_change = avg_future_price - current_price
        price_change_percent = (price_change / current_price) * 100
        
        prediction_info = {
            'model_used': best_model,
            'accuracy': accuracy,
            'current_price': current_price,
            'predicted_30d_avg': avg_future_price,
            'predicted_change': price_change,
            'predicted_change_percent': price_change_percent,
            'predictions': prediction_df
        }
        
        return prediction_info, None
        
    except Exception as e:
        return None, f"Prediction error: {str(e)}"

def get_stock_news(symbol, company_name):
    """
    Fetch latest news about the stock
    """
    try:
        news_data = []
        
        # Method 1: Try to get news from Google News RSS
        company_search = company_name.replace(' Limited', '').replace(' Ltd', '')
        search_terms = [company_search, symbol.replace('.NS', '')]
        
        for term in search_terms:
            try:
                # Google News RSS feed
                rss_url = f"https://news.google.com/rss/search?q={term.replace(' ', '+')}&hl=en-IN&gl=IN&ceid=IN:en"
                feed = feedparser.parse(rss_url)
                
                for entry in feed.entries[:3]:  # Get top 3 news items
                    # Parse published date
                    pub_date = 'N/A'
                    if hasattr(entry, 'published'):
                        try:
                            pub_date = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %Z').strftime('%Y-%m-%d %H:%M')
                        except:
                            pub_date = entry.published
                    
                    # Analyze sentiment
                    sentiment = analyze_sentiment(entry.title + " " + entry.get('summary', ''))
                    
                    news_item = {
                        'title': entry.title,
                        'summary': entry.get('summary', 'N/A')[:200] + '...',
                        'link': entry.link,
                        'published': pub_date,
                        'source': entry.get('source', {}).get('title', 'Google News'),
                        'sentiment': sentiment
                    }
                    news_data.append(news_item)
                
                if news_data:
                    break  # If we found news, no need to try other search terms
                    
            except Exception as e:
                continue
        
        # Method 2: Try Yahoo Finance news (backup)
        if not news_data:
            try:
                stock = yf.Ticker(symbol)
                yahoo_news = stock.news
                
                for item in yahoo_news[:3]:
                    pub_date = 'N/A'
                    if item.get('providerPublishTime'):
                        pub_date = datetime.fromtimestamp(item['providerPublishTime']).strftime('%Y-%m-%d %H:%M')
                    
                    sentiment = analyze_sentiment(item.get('title', '') + " " + item.get('summary', ''))
                    
                    news_item = {
                        'title': item.get('title', 'N/A'),
                        'summary': item.get('summary', 'N/A')[:200] + '...',
                        'link': item.get('link', 'N/A'),
                        'published': pub_date,
                        'source': item.get('publisher', 'Yahoo Finance'),
                        'sentiment': sentiment
                    }
                    news_data.append(news_item)
            except:
                pass
        
        return news_data if news_data else [{'title': 'No recent news found', 'summary': 'Please check financial news websites manually', 'link': 'N/A', 'published': 'N/A', 'source': 'N/A', 'sentiment': 'Neutral'}]
    
    except Exception as e:
        return [{'title': f'Error fetching news: {str(e)}', 'summary': 'N/A', 'link': 'N/A', 'published': 'N/A', 'source': 'N/A', 'sentiment': 'Neutral'}]

def analyze_sentiment(text):
    """
    Analyze sentiment of news text
    """
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.1:
            return 'Positive'
        elif polarity < -0.1:
            return 'Negative'
        else:
            return 'Neutral'
    except:
        return 'Neutral'

def get_dividend_info(stock):
    """
    Get dividend information
    """
    try:
        dividends = stock.dividends
        if dividends.empty:
            return "No dividend history available"
        
        # Get last dividend
        last_dividend = dividends.iloc[-1]
        last_dividend_date = dividends.index[-1].strftime('%Y-%m-%d')
        
        # Calculate annual dividend yield
        info = stock.info
        current_price = info.get('currentPrice', 0)
        annual_dividend = dividends.groupby(dividends.index.year).sum().iloc[-1] if len(dividends) > 0 else 0
        
        if current_price > 0:
            dividend_yield = (annual_dividend / current_price) * 100
        else:
            dividend_yield = 0
        
        return {
            'last_dividend': last_dividend,
            'last_dividend_date': last_dividend_date,
            'annual_dividend': annual_dividend,
            'dividend_yield': dividend_yield
        }
    except Exception as e:
        return f"Error getting dividend info: {str(e)}"

def generate_trading_recommendation(stock_data, prediction_info, current_price, rsi, macd):
    """
    Generate BUY/SELL/HOLD recommendation based on technical analysis
    """
    try:
        signals = []
        score = 0  # Positive = Buy, Negative = Sell, 0 = Hold
        
        # RSI Analysis
        if rsi < 30:
            signals.append("RSI indicates oversold condition (Bullish)")
            score += 2
        elif rsi > 70:
            signals.append("RSI indicates overbought condition (Bearish)")
            score -= 2
        else:
            signals.append("RSI in neutral zone")
        
        # MACD Analysis
        if macd > 0:
            signals.append("MACD above zero (Bullish)")
            score += 1
        else:
            signals.append("MACD below zero (Bearish)")
            score -= 1
        
        # Moving Average Analysis
        sma_20 = stock_data['Close'].rolling(window=20).mean().iloc[-1]
        sma_50 = stock_data['Close'].rolling(window=50).mean().iloc[-1]
        
        if current_price > sma_20:
            signals.append("Price above 20-day SMA (Bullish)")
            score += 1
        else:
            signals.append("Price below 20-day SMA (Bearish)")
            score -= 1
        
        if sma_20 > sma_50:
            signals.append("20-day SMA above 50-day SMA (Bullish)")
            score += 1
        else:
            signals.append("20-day SMA below 50-day SMA (Bearish)")
            score -= 1
        
        # Volume Analysis
        avg_volume = stock_data['Volume'].rolling(window=20).mean().iloc[-1]
        current_volume = stock_data['Volume'].iloc[-1]
        
        if current_volume > avg_volume * 1.5:
            signals.append("High volume activity (Significant move)")
            score += 0.5 if score > 0 else -0.5  # Amplify existing trend
        
        # Prediction Analysis
        if prediction_info and prediction_info['predicted_change_percent'] > 5:
            signals.append("AI prediction shows strong upward trend")
            score += 2
        elif prediction_info and prediction_info['predicted_change_percent'] < -5:
            signals.append("AI prediction shows strong downward trend")
            score -= 2
        elif prediction_info:
            signals.append(f"AI prediction: {prediction_info['predicted_change_percent']:.1f}% change expected")
        
        # Volatility Analysis
        volatility = stock_data['Close'].rolling(window=20).std().iloc[-1]
        avg_volatility = stock_data['Close'].rolling(window=20).std().mean()
        
        if volatility > avg_volatility * 1.5:
            signals.append("High volatility - exercise caution")
            score *= 0.8  # Reduce confidence in volatile conditions
        
        # Generate recommendation
        if score >= 3:
            recommendation = "STRONG BUY"
            confidence = "High"
        elif score >= 1:
            recommendation = "BUY"
            confidence = "Medium"
        elif score <= -3:
            recommendation = "STRONG SELL"
            confidence = "High"
        elif score <= -1:
            recommendation = "SELL"
            confidence = "Medium"
        else:
            recommendation = "HOLD"
            confidence = "Medium"
        
        return {
            'recommendation': recommendation,
            'confidence': confidence,
            'score': score,
            'signals': signals,
            'risk_level': 'High' if volatility > avg_volatility * 1.5 else 'Medium' if volatility > avg_volatility else 'Low'
        }
        
    except Exception as e:
        return {
            'recommendation': 'HOLD',
            'confidence': 'Low',
            'score': 0,
            'signals': [f'Error in analysis: {str(e)}'],
            'risk_level': 'Unknown'
        }

def create_prediction_chart(stock_data, prediction_info, symbol):
    """
    Create chart showing historical data and future predictions
    """
    try:
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'{symbol} - Advanced Analysis with AI Predictions', fontsize=16, fontweight='bold')
        
        # Historical price with prediction
        ax1.plot(stock_data.index, stock_data['Close'], label='Historical Price', linewidth=2, color='blue')
        
        if prediction_info:
            pred_df = prediction_info['predictions']
            ax1.plot(pred_df['Date'], pred_df['Predicted_Price'], 
                    label=f'AI Prediction ({prediction_info["model_used"]})', 
                    linewidth=2, color='red', linestyle='--')
            
            # Add prediction accuracy
            ax1.text(0.02, 0.98, f'Model Accuracy: {prediction_info["accuracy"]:.2%}', 
                    transform=ax1.transAxes, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        ax1.set_title('Price History & AI Predictions')
        ax1.set_ylabel('Price (₹)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Technical indicators
        stock_data['RSI'] = ta.momentum.rsi(stock_data['Close'], window=14)
        stock_data['MACD'] = ta.trend.macd_diff(stock_data['Close'])
        
        ax2.plot(stock_data.index, stock_data['RSI'], color='purple', linewidth=2)
        ax2.axhline(y=70, color='r', linestyle='--', alpha=0.7, label='Overbought')
        ax2.axhline(y=30, color='g', linestyle='--', alpha=0.7, label='Oversold')
        ax2.fill_between(stock_data.index, 30, 70, alpha=0.1, color='yellow')
        ax2.set_title('RSI - Momentum Indicator')
        ax2.set_ylabel('RSI')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Volume analysis
        ax3.bar(stock_data.index, stock_data['Volume'], alpha=0.7, color='green', width=1)
        avg_volume = stock_data['Volume'].rolling(window=20).mean()
        ax3.plot(stock_data.index, avg_volume, color='red', linewidth=2, label='20-day Avg Volume')
        ax3.set_title('Volume Analysis')
        ax3.set_ylabel('Volume')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # MACD
        ax4.plot(stock_data.index, stock_data['MACD'], color='blue', linewidth=2, label='MACD')
        ax4.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        ax4.set_title('MACD - Trend Indicator')
        ax4.set_ylabel('MACD')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"Error creating prediction chart: {e}")

def comprehensive_stock_analysis(symbol):
    """
    Perform comprehensive stock analysis with all features
    """
    try:
        stock = yf.Ticker(symbol)
        
        # Get stock data
        hist_data = stock.history(period="1y")  # Get 1 year for better prediction
        info = stock.info
        
        if hist_data.empty:
            return False
        
        # Current price info
        current_price = hist_data['Close'].iloc[-1]
        company_name = info.get('longName', symbol)
        
        print("\n" + "="*80)
        print(f"🚀 ADVANCED STOCK ANALYSIS - {symbol}")
        print("="*80)
        
        # Basic info
        print(f"\n💰 CURRENT INFORMATION")
        print("-"*50)
        print(f"Company: {company_name}")
        print(f"Current Price: ₹{current_price:.2f}")
        
        # Technical indicators
        rsi = ta.momentum.rsi(hist_data['Close'], window=14).iloc[-1]
        macd = ta.trend.macd_diff(hist_data['Close']).iloc[-1]
        
        print(f"\n📈 TECHNICAL INDICATORS")
        print("-"*50)
        print(f"RSI: {rsi:.2f} ({'Overbought' if rsi > 70 else 'Oversold' if rsi < 30 else 'Neutral'})")
        print(f"MACD: {macd:.2f} ({'Bullish' if macd > 0 else 'Bearish'})")
        
        # AI Prediction
        print(f"\n🤖 AI PRICE PREDICTION (30 days)")
        print("-"*50)
        prediction_info, pred_error = predict_future_price(hist_data, days_ahead=30)
        
        if prediction_info:
            print(f"Model Used: {prediction_info['model_used']}")
            print(f"Model Accuracy: {prediction_info['accuracy']:.2%}")
            print(f"Current Price: ₹{prediction_info['current_price']:.2f}")
            print(f"Predicted 30-day Average: ₹{prediction_info['predicted_30d_avg']:.2f}")
            print(f"Expected Change: {prediction_info['predicted_change']:+.2f} ({prediction_info['predicted_change_percent']:+.1f}%)")
            
            if prediction_info['predicted_change_percent'] > 0:
                print(f"🟢 AI suggests UPWARD trend")
            else:
                print(f"🔴 AI suggests DOWNWARD trend")
        else:
            print(f"❌ Prediction failed: {pred_error}")
        
        # Trading Recommendation
        print(f"\n📊 TRADING RECOMMENDATION")
        print("-"*50)
        recommendation = generate_trading_recommendation(hist_data, prediction_info, current_price, rsi, macd)
        
        print(f"Recommendation: {recommendation['recommendation']}")
        print(f"Confidence: {recommendation['confidence']}")
        print(f"Risk Level: {recommendation['risk_level']}")
        print(f"Analysis Score: {recommendation['score']:.1f}")
        print("\nKey Signals:")
        for signal in recommendation['signals']:
            print(f"  • {signal}")
        
        # Dividend Information
        print(f"\n💵 DIVIDEND INFORMATION")
        print("-"*50)
        dividend_info = get_dividend_info(stock)
        if isinstance(dividend_info, dict):
            print(f"Last Dividend: ₹{dividend_info['last_dividend']:.2f}")
            print(f"Last Dividend Date: {dividend_info['last_dividend_date']}")
            print(f"Annual Dividend Yield: {dividend_info['dividend_yield']:.2f}%")
        else:
            print(dividend_info)
        
        # Latest News
        print(f"\n📰 LATEST NEWS & SENTIMENT")
        print("-"*50)
        news_data = get_stock_news(symbol, company_name)
        
        for i, news in enumerate(news_data[:3], 1):
            sentiment_emoji = "🟢" if news['sentiment'] == 'Positive' else "🔴" if news['sentiment'] == 'Negative' else "🟡"
            print(f"{i}. {news['title']}")
            print(f"   Source: {news['source']} | Date: {news['published']}")
            print(f"   Sentiment: {sentiment_emoji} {news['sentiment']}")
            print(f"   Summary: {news['summary']}")
            print()
        
        # Create comprehensive chart
        print("📊 Generating comprehensive analysis chart...")
        create_prediction_chart(hist_data, prediction_info, symbol)
        
        print("\n" + "="*80)
        print("✅ ANALYSIS COMPLETED!")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"❌ Error in comprehensive analysis: {e}")
        return False

def main():
    """
    Main function for advanced stock analyzer
    """
    print("🚀 ADVANCED AI-POWERED STOCK ANALYZER")
    print("="*60)
    print("Features:")
    print("✅ AI Price Predictions")
    print("✅ Latest News & Sentiment Analysis")
    print("✅ BUY/SELL/HOLD Recommendations")
    print("✅ Dividend Information")
    print("✅ Advanced Technical Analysis")
    print()
    
    while True:
        user_input = input("Enter stock name (or 'quit' to exit): ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Thanks for using the Advanced Stock Analyzer!")
            break
        
        if not user_input:
            print("Please enter a stock name.")
            continue
        
        print(f"\n🔍 Performing advanced analysis for '{user_input}'...")
        
        symbol, matched_name = search_stock_symbol(user_input)
        
        success = comprehensive_stock_analysis(symbol)
        if not success:
            print(f"❌ Unable to analyze '{user_input}'. Please try a different stock.")

if __name__ == "__main__":
    main()

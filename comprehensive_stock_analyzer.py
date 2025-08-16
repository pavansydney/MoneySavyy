#!/usr/bin/env python3
"""
Comprehensive Stock Analysis Tool with Charts, Fundamentals, Technical Analysis and News
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

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Set style for better looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# Dictionary of popular Indian stocks with their symbols
INDIAN_STOCKS = {
    'tcs': 'TCS.NS',
    'tata consultancy services': 'TCS.NS',
    'infosys': 'INFY.NS',
    'wipro': 'WIPRO.NS',
    'reliance': 'RELIANCE.NS',
    'reliance industries': 'RELIANCE.NS',
    'hdfc bank': 'HDFCBANK.NS',
    'hdfc': 'HDFCBANK.NS',
    'icici bank': 'ICICIBANK.NS',
    'icici': 'ICICIBANK.NS',
    'sbi': 'SBIN.NS',
    'state bank of india': 'SBIN.NS',
    'bharti airtel': 'BHARTIARTL.NS',
    'airtel': 'BHARTIARTL.NS',
    'itc': 'ITC.NS',
    'hindustan unilever': 'HINDUNILVR.NS',
    'hul': 'HINDUNILVR.NS',
    'bajaj finance': 'BAJFINANCE.NS',
    'bajaj': 'BAJFINANCE.NS',
    'maruti suzuki': 'MARUTI.NS',
    'maruti': 'MARUTI.NS',
    'asian paints': 'ASIANPAINT.NS',
    'larsen': 'LT.NS',
    'l&t': 'LT.NS',
    'larsen and toubro': 'LT.NS',
    'axis bank': 'AXISBANK.NS',
    'axis': 'AXISBANK.NS',
    'kotak bank': 'KOTAKBANK.NS',
    'kotak': 'KOTAKBANK.NS',
    'sun pharma': 'SUNPHARMA.NS',
    'titan': 'TITAN.NS',
    'nestle': 'NESTLEIND.NS',
    'ongc': 'ONGC.NS',
    'ntpc': 'NTPC.NS',
    'powergrid': 'POWERGRID.NS',
    'coal india': 'COALINDIA.NS',
    'dr reddy': 'DRREDDY.NS',
    'tech mahindra': 'TECHM.NS',
    'mahindra tech': 'TECHM.NS',
    'hcl tech': 'HCLTECH.NS',
    'hcl': 'HCLTECH.NS',
    'adani': 'ADANIENT.NS',
    'tata steel': 'TATASTEEL.NS',
    'jsw steel': 'JSWSTEEL.NS',
    'ultratech cement': 'ULTRACEMCO.NS',
    'ultratech': 'ULTRACEMCO.NS',
    'britannia': 'BRITANNIA.NS'
}

def search_stock_symbol(user_input):
    """Search for stock symbol based on user input"""
    user_input = user_input.lower().strip()
    
    if user_input in INDIAN_STOCKS:
        return INDIAN_STOCKS[user_input], user_input
    
    for stock_name, symbol in INDIAN_STOCKS.items():
        if user_input in stock_name or stock_name in user_input:
            return symbol, stock_name
    
    close_matches = get_close_matches(user_input, INDIAN_STOCKS.keys(), n=3, cutoff=0.6)
    if close_matches:
        best_match = close_matches[0]
        return INDIAN_STOCKS[best_match], best_match
    
    if not user_input.endswith('.ns') and not user_input.endswith('.bo'):
        test_symbol = user_input.upper() + '.NS'
    else:
        test_symbol = user_input.upper()
    
    return test_symbol, user_input

def get_current_price_info(stock):
    """Get current price and basic info"""
    try:
        info = stock.info
        hist = stock.history(period="1d")
        
        if hist.empty:
            return None
        
        current_price = hist['Close'].iloc[-1]
        open_price = hist['Open'].iloc[-1]
        high_price = hist['High'].iloc[-1]
        low_price = hist['Low'].iloc[-1]
        volume = hist['Volume'].iloc[-1]
        
        change = current_price - open_price
        change_percent = (change / open_price) * 100
        
        return {
            'current_price': current_price,
            'open_price': open_price,
            'high_price': high_price,
            'low_price': low_price,
            'volume': volume,
            'change': change,
            'change_percent': change_percent,
            'company_name': info.get('longName', info.get('shortName', 'N/A'))
        }
    except Exception as e:
        print(f"Error getting current price: {e}")
        return None

def plot_historical_charts(stock, symbol, period='6mo'):
    """Create historical price charts with technical indicators"""
    try:
        # Get historical data
        hist_data = stock.history(period=period)
        
        if hist_data.empty:
            print("No historical data available")
            return
        
        # Calculate technical indicators
        hist_data['SMA_20'] = ta.trend.sma_indicator(hist_data['Close'], window=20)
        hist_data['SMA_50'] = ta.trend.sma_indicator(hist_data['Close'], window=50)
        hist_data['RSI'] = ta.momentum.rsi(hist_data['Close'], window=14)
        hist_data['MACD'] = ta.trend.macd_diff(hist_data['Close'])
        hist_data['BB_upper'] = ta.volatility.bollinger_hband(hist_data['Close'])
        hist_data['BB_lower'] = ta.volatility.bollinger_lband(hist_data['Close'])
        
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'{symbol} - Comprehensive Technical Analysis', fontsize=16, fontweight='bold')
        
        # 1. Price chart with moving averages and Bollinger Bands
        ax1.plot(hist_data.index, hist_data['Close'], label='Close Price', linewidth=2, color='blue')
        ax1.plot(hist_data.index, hist_data['SMA_20'], label='SMA 20', alpha=0.7, color='orange')
        ax1.plot(hist_data.index, hist_data['SMA_50'], label='SMA 50', alpha=0.7, color='red')
        ax1.fill_between(hist_data.index, hist_data['BB_upper'], hist_data['BB_lower'], 
                        alpha=0.2, color='gray', label='Bollinger Bands')
        ax1.set_title('Price Chart with Technical Indicators')
        ax1.set_ylabel('Price (₹)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Volume chart
        ax2.bar(hist_data.index, hist_data['Volume'], alpha=0.7, color='green')
        ax2.set_title('Trading Volume')
        ax2.set_ylabel('Volume')
        ax2.grid(True, alpha=0.3)
        
        # 3. RSI
        ax3.plot(hist_data.index, hist_data['RSI'], color='purple', linewidth=2)
        ax3.axhline(y=70, color='r', linestyle='--', alpha=0.7, label='Overbought (70)')
        ax3.axhline(y=30, color='g', linestyle='--', alpha=0.7, label='Oversold (30)')
        ax3.fill_between(hist_data.index, 30, 70, alpha=0.1, color='yellow')
        ax3.set_title('RSI (Relative Strength Index)')
        ax3.set_ylabel('RSI')
        ax3.set_ylim(0, 100)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. MACD
        ax4.plot(hist_data.index, hist_data['MACD'], color='blue', linewidth=2, label='MACD')
        ax4.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        ax4.set_title('MACD (Moving Average Convergence Divergence)')
        ax4.set_ylabel('MACD')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        return hist_data
    
    except Exception as e:
        print(f"Error creating charts: {e}")
        return None

def get_fundamental_data(stock):
    """Get fundamental analysis data"""
    try:
        info = stock.info
        
        fundamentals = {
            'Market Cap': info.get('marketCap', 'N/A'),
            'P/E Ratio': info.get('trailingPE', 'N/A'),
            'P/B Ratio': info.get('priceToBook', 'N/A'),
            'Dividend Yield': info.get('dividendYield', 'N/A'),
            'ROE': info.get('returnOnEquity', 'N/A'),
            'ROA': info.get('returnOnAssets', 'N/A'),
            'Debt to Equity': info.get('debtToEquity', 'N/A'),
            'Current Ratio': info.get('currentRatio', 'N/A'),
            'Revenue Growth': info.get('revenueGrowth', 'N/A'),
            'Earnings Growth': info.get('earningsGrowth', 'N/A'),
            'Gross Margins': info.get('grossMargins', 'N/A'),
            'Operating Margins': info.get('operatingMargins', 'N/A'),
            'Profit Margins': info.get('profitMargins', 'N/A'),
            '52 Week High': info.get('fiftyTwoWeekHigh', 'N/A'),
            '52 Week Low': info.get('fiftyTwoWeekLow', 'N/A'),
            'Beta': info.get('beta', 'N/A'),
            'Book Value': info.get('bookValue', 'N/A'),
            'Enterprise Value': info.get('enterpriseValue', 'N/A'),
            'Forward P/E': info.get('forwardPE', 'N/A'),
            'PEG Ratio': info.get('pegRatio', 'N/A')
        }
        
        return fundamentals
    except Exception as e:
        print(f"Error getting fundamental data: {e}")
        return {}

def get_technical_analysis(hist_data):
    """Calculate and display technical analysis"""
    if hist_data is None or hist_data.empty:
        return {}
    
    try:
        latest = hist_data.iloc[-1]
        technical_data = {
            'Current RSI': f"{latest['RSI']:.2f}",
            'RSI Signal': 'Overbought' if latest['RSI'] > 70 else 'Oversold' if latest['RSI'] < 30 else 'Neutral',
            'MACD': f"{latest['MACD']:.2f}",
            'MACD Signal': 'Bullish' if latest['MACD'] > 0 else 'Bearish',
            'Price vs SMA20': 'Above' if latest['Close'] > latest['SMA_20'] else 'Below',
            'Price vs SMA50': 'Above' if latest['Close'] > latest['SMA_50'] else 'Below',
            'SMA20 vs SMA50': 'Golden Cross' if latest['SMA_20'] > latest['SMA_50'] else 'Death Cross',
            'Bollinger Position': 'Upper Band' if latest['Close'] > latest['BB_upper'] else 'Lower Band' if latest['Close'] < latest['BB_lower'] else 'Middle Range'
        }
        
        return technical_data
    except Exception as e:
        print(f"Error in technical analysis: {e}")
        return {}

def get_stock_news(stock, symbol):
    """Get recent news about the stock"""
    try:
        news = stock.news
        if not news:
            return []
        
        recent_news = []
        for item in news[:5]:  # Get latest 5 news items
            news_item = {
                'title': item.get('title', 'N/A'),
                'publisher': item.get('publisher', 'N/A'),
                'published': datetime.fromtimestamp(item.get('providerPublishTime', 0)).strftime('%Y-%m-%d %H:%M') if item.get('providerPublishTime') else 'N/A',
                'link': item.get('link', 'N/A')
            }
            recent_news.append(news_item)
        
        return recent_news
    except Exception as e:
        print(f"Error getting news: {e}")
        return []

def format_number(num):
    """Format large numbers for better readability"""
    if num == 'N/A' or num is None:
        return 'N/A'
    
    try:
        if isinstance(num, str):
            return num
        
        if num >= 1e12:
            return f"₹{num/1e12:.2f}T"
        elif num >= 1e9:
            return f"₹{num/1e9:.2f}B"
        elif num >= 1e7:
            return f"₹{num/1e7:.2f}Cr"
        elif num >= 1e5:
            return f"₹{num/1e5:.2f}L"
        else:
            return f"₹{num:.2f}"
    except:
        return str(num)

def print_analysis_report(symbol, price_info, fundamentals, technical_data, news):
    """Print comprehensive analysis report"""
    print("\n" + "="*80)
    print(f"📈 COMPREHENSIVE STOCK ANALYSIS REPORT - {symbol}")
    print("="*80)
    
    # Current Price Section
    if price_info:
        print(f"\n💰 CURRENT PRICE INFORMATION")
        print("-"*50)
        print(f"Company: {price_info['company_name']}")
        print(f"Current Price: ₹{price_info['current_price']:.2f}")
        print(f"Open: ₹{price_info['open_price']:.2f}")
        print(f"High: ₹{price_info['high_price']:.2f}")
        print(f"Low: ₹{price_info['low_price']:.2f}")
        print(f"Volume: {price_info['volume']:,}")
        change_symbol = "+" if price_info['change'] >= 0 else ""
        print(f"Change: {change_symbol}₹{price_info['change']:.2f} ({change_symbol}{price_info['change_percent']:.2f}%)")
    
    # Fundamental Analysis Section
    if fundamentals:
        print(f"\n📊 FUNDAMENTAL ANALYSIS")
        print("-"*50)
        
        # Valuation Metrics
        print("Valuation Metrics:")
        print(f"  Market Cap: {format_number(fundamentals.get('Market Cap'))}")
        print(f"  P/E Ratio: {fundamentals.get('P/E Ratio', 'N/A')}")
        print(f"  P/B Ratio: {fundamentals.get('P/B Ratio', 'N/A')}")
        print(f"  Forward P/E: {fundamentals.get('Forward P/E', 'N/A')}")
        print(f"  PEG Ratio: {fundamentals.get('PEG Ratio', 'N/A')}")
        
        # Profitability Metrics
        print("\nProfitability Metrics:")
        roe = fundamentals.get('ROE', 'N/A')
        if roe != 'N/A' and isinstance(roe, (int, float)):
            roe = f"{roe*100:.2f}%"
        print(f"  ROE: {roe}")
        
        roa = fundamentals.get('ROA', 'N/A')
        if roa != 'N/A' and isinstance(roa, (int, float)):
            roa = f"{roa*100:.2f}%"
        print(f"  ROA: {roa}")
        
        # Format margin percentages
        for margin_type in ['Gross Margins', 'Operating Margins', 'Profit Margins']:
            margin = fundamentals.get(margin_type, 'N/A')
            if margin != 'N/A' and isinstance(margin, (int, float)):
                margin = f"{margin*100:.2f}%"
            print(f"  {margin_type}: {margin}")
        
        # Financial Health
        print("\nFinancial Health:")
        print(f"  Debt to Equity: {fundamentals.get('Debt to Equity', 'N/A')}")
        print(f"  Current Ratio: {fundamentals.get('Current Ratio', 'N/A')}")
        print(f"  Beta: {fundamentals.get('Beta', 'N/A')}")
        
        # Growth Metrics
        print("\nGrowth Metrics:")
        rev_growth = fundamentals.get('Revenue Growth', 'N/A')
        if rev_growth != 'N/A' and isinstance(rev_growth, (int, float)):
            rev_growth = f"{rev_growth*100:.2f}%"
        print(f"  Revenue Growth: {rev_growth}")
        
        earn_growth = fundamentals.get('Earnings Growth', 'N/A')
        if earn_growth != 'N/A' and isinstance(earn_growth, (int, float)):
            earn_growth = f"{earn_growth*100:.2f}%"
        print(f"  Earnings Growth: {earn_growth}")
        
        # Price Range
        print("\nPrice Range:")
        print(f"  52 Week High: ₹{fundamentals.get('52 Week High', 'N/A')}")
        print(f"  52 Week Low: ₹{fundamentals.get('52 Week Low', 'N/A')}")
    
    # Technical Analysis Section
    if technical_data:
        print(f"\n📈 TECHNICAL ANALYSIS")
        print("-"*50)
        for indicator, value in technical_data.items():
            print(f"  {indicator}: {value}")
    
    # News Section
    if news:
        print(f"\n📰 RECENT NEWS")
        print("-"*50)
        for i, item in enumerate(news, 1):
            print(f"{i}. {item['title']}")
            print(f"   Publisher: {item['publisher']} | Date: {item['published']}")
            print(f"   Link: {item['link'][:80]}...")
            print()

def main():
    """Main function"""
    print("🔍 COMPREHENSIVE STOCK ANALYZER")
    print("="*50)
    print("Get current price, charts, fundamentals, technical analysis, and news!")
    print("Enter stock names like: 'tcs', 'reliance', 'infosys', 'hdfc', etc.")
    print()
    
    while True:
        user_input = input("Enter stock name (or 'quit' to exit): ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Thanks for using the Stock Analyzer!")
            break
        
        if not user_input:
            print("Please enter a stock name.")
            continue
        
        print(f"\n🔍 Analyzing '{user_input}'...")
        
        # Search for stock symbol
        symbol, matched_name = search_stock_symbol(user_input)
        stock = yf.Ticker(symbol)
        
        # Get all data
        print("📊 Fetching current price data...")
        price_info = get_current_price_info(stock)
        
        if price_info is None:
            print(f"❌ Unable to find data for '{user_input}'. Please try a different stock name.")
            continue
        
        print("📈 Generating historical charts...")
        hist_data = plot_historical_charts(stock, symbol)
        
        print("💼 Collecting fundamental data...")
        fundamentals = get_fundamental_data(stock)
        
        print("⚡ Calculating technical indicators...")
        technical_data = get_technical_analysis(hist_data)
        
        print("📰 Fetching latest news...")
        news = get_stock_news(stock, symbol)
        
        # Print comprehensive report
        print_analysis_report(symbol, price_info, fundamentals, technical_data, news)
        
        print("\n" + "="*80)
        print("Analysis completed! Charts should be displayed in a new window.")
        print("="*80)

if __name__ == "__main__":
    main()

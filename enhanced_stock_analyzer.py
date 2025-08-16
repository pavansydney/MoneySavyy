#!/usr/bin/env python3
"""
Enhanced Stock Analyzer with Charts and Analysis (Simplified Version)
"""

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
from difflib import get_close_matches
import ta

warnings.filterwarnings('ignore')
plt.style.use('default')

# Popular Indian stocks dictionary
INDIAN_STOCKS = {
    'tcs': 'TCS.NS', 'infosys': 'INFY.NS', 'wipro': 'WIPRO.NS',
    'reliance': 'RELIANCE.NS', 'hdfc': 'HDFCBANK.NS', 'icici': 'ICICIBANK.NS',
    'sbi': 'SBIN.NS', 'airtel': 'BHARTIARTL.NS', 'itc': 'ITC.NS',
    'maruti': 'MARUTI.NS', 'asian paints': 'ASIANPAINT.NS', 'titan': 'TITAN.NS'
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

def create_stock_chart(stock, symbol):
    """Create a comprehensive stock chart"""
    try:
        # Get 6 months of data
        hist = stock.history(period="6mo")
        if hist.empty:
            print("No historical data available")
            return None
        
        # Calculate technical indicators
        hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
        hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
        hist['RSI'] = ta.momentum.rsi(hist['Close'], window=14)
        
        # Create subplots
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
        fig.suptitle(f'{symbol} - Stock Analysis', fontsize=16, fontweight='bold')
        
        # Price chart with moving averages
        ax1.plot(hist.index, hist['Close'], label='Close Price', linewidth=2, color='blue')
        ax1.plot(hist.index, hist['SMA_20'], label='20-Day SMA', alpha=0.7, color='orange')
        ax1.plot(hist.index, hist['SMA_50'], label='50-Day SMA', alpha=0.7, color='red')
        ax1.set_title('Price Chart with Moving Averages')
        ax1.set_ylabel('Price (₹)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Volume chart
        ax2.bar(hist.index, hist['Volume'], alpha=0.7, color='green', width=1)
        ax2.set_title('Trading Volume')
        ax2.set_ylabel('Volume')
        ax2.grid(True, alpha=0.3)
        
        # RSI
        ax3.plot(hist.index, hist['RSI'], color='purple', linewidth=2)
        ax3.axhline(y=70, color='r', linestyle='--', alpha=0.7, label='Overbought')
        ax3.axhline(y=30, color='g', linestyle='--', alpha=0.7, label='Oversold')
        ax3.fill_between(hist.index, 30, 70, alpha=0.1, color='yellow')
        ax3.set_title('RSI (Relative Strength Index)')
        ax3.set_ylabel('RSI')
        ax3.set_ylim(0, 100)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        return hist
    except Exception as e:
        print(f"Error creating chart: {e}")
        return None

def analyze_stock(symbol):
    """Comprehensive stock analysis"""
    try:
        stock = yf.Ticker(symbol)
        
        # Get current data
        hist = stock.history(period="1d")
        info = stock.info
        
        if hist.empty:
            return None
        
        current_price = hist['Close'].iloc[-1]
        open_price = hist['Open'].iloc[-1]
        high_price = hist['High'].iloc[-1]
        low_price = hist['Low'].iloc[-1]
        volume = hist['Volume'].iloc[-1]
        
        change = current_price - open_price
        change_percent = (change / open_price) * 100
        
        # Get historical data for analysis
        hist_data = create_stock_chart(stock, symbol)
        
        # Display results
        print("\n" + "="*60)
        print(f"📈 STOCK ANALYSIS - {symbol}")
        print("="*60)
        
        print(f"\n💰 CURRENT PRICE")
        print("-"*30)
        print(f"Company: {info.get('longName', symbol)}")
        print(f"Current Price: ₹{current_price:.2f}")
        print(f"Open: ₹{open_price:.2f} | High: ₹{high_price:.2f} | Low: ₹{low_price:.2f}")
        print(f"Volume: {volume:,}")
        change_symbol = "+" if change >= 0 else ""
        print(f"Change: {change_symbol}₹{change:.2f} ({change_symbol}{change_percent:.2f}%)")
        
        # Key fundamentals
        print(f"\n📊 KEY FUNDAMENTALS")
        print("-"*30)
        market_cap = info.get('marketCap')
        if market_cap:
            if market_cap >= 1e12:
                mc_formatted = f"₹{market_cap/1e12:.2f}T"
            elif market_cap >= 1e9:
                mc_formatted = f"₹{market_cap/1e9:.2f}B"
            else:
                mc_formatted = f"₹{market_cap/1e7:.2f}Cr"
            print(f"Market Cap: {mc_formatted}")
        
        pe_ratio = info.get('trailingPE')
        if pe_ratio:
            print(f"P/E Ratio: {pe_ratio:.2f}")
        
        div_yield = info.get('dividendYield')
        if div_yield:
            print(f"Dividend Yield: {div_yield*100:.2f}%")
        
        week_52_high = info.get('fiftyTwoWeekHigh')
        week_52_low = info.get('fiftyTwoWeekLow')
        if week_52_high and week_52_low:
            print(f"52W Range: ₹{week_52_low:.2f} - ₹{week_52_high:.2f}")
        
        # Technical analysis
        if hist_data is not None and len(hist_data) > 0:
            latest_rsi = hist_data['RSI'].iloc[-1]
            print(f"\n⚡ TECHNICAL INDICATORS")
            print("-"*30)
            print(f"RSI: {latest_rsi:.2f} ({get_rsi_signal(latest_rsi)})")
            
            if not hist_data['SMA_20'].isna().iloc[-1]:
                sma20_signal = "Above" if current_price > hist_data['SMA_20'].iloc[-1] else "Below"
                print(f"Price vs 20-SMA: {sma20_signal}")
            
            if not hist_data['SMA_50'].isna().iloc[-1]:
                sma50_signal = "Above" if current_price > hist_data['SMA_50'].iloc[-1] else "Below"
                print(f"Price vs 50-SMA: {sma50_signal}")
        
        # Simple news alternative
        print(f"\n📰 COMPANY INFO")
        print("-"*30)
        sector = info.get('sector', 'N/A')
        industry = info.get('industry', 'N/A')
        print(f"Sector: {sector}")
        print(f"Industry: {industry}")
        
        website = info.get('website', '')
        if website:
            print(f"Website: {website}")
        
        print("\n" + "="*60)
        print("Chart displayed in a separate window!")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"Error analyzing stock: {e}")
        return False

def get_rsi_signal(rsi):
    """Get RSI signal interpretation"""
    if rsi > 70:
        return "Overbought"
    elif rsi < 30:
        return "Oversold" 
    else:
        return "Neutral"

def main():
    """Main function"""
    print("📈 ENHANCED STOCK ANALYZER")
    print("="*40)
    print("Get current price, charts, and key analysis!")
    print("Try: 'tcs', 'reliance', 'infosys', 'hdfc', etc.")
    print()
    
    while True:
        user_input = input("Enter stock name (or 'quit' to exit): ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Thanks for using the analyzer!")
            break
        
        if not user_input:
            print("Please enter a stock name.")
            continue
        
        print(f"\n🔍 Analyzing '{user_input}'...")
        
        symbol, matched_name = search_stock_symbol(user_input)
        
        success = analyze_stock(symbol)
        if not success:
            print(f"❌ Unable to analyze '{user_input}'. Try a different stock.")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Simple Python script to display current stock price of TCS (Tata Consultancy Services)
"""

import yfinance as yf
from datetime import datetime

def get_tcs_stock_price():
    """
    Fetch and display the current stock price of TCS
    """
    try:
        # TCS stock symbol on NSE (National Stock Exchange of India)
        tcs_symbol = "TCS.NS"
        
        # Create a Ticker object for TCS
        tcs = yf.Ticker(tcs_symbol)
        
        # Get current stock info
        info = tcs.info
        
        # Get historical data for the last day to get current price
        hist = tcs.history(period="1d")
        
        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
            open_price = hist['Open'].iloc[-1]
            high_price = hist['High'].iloc[-1]
            low_price = hist['Low'].iloc[-1]
            volume = hist['Volume'].iloc[-1]
            
            # Display the information
            print("=" * 50)
            print("TCS (Tata Consultancy Services) Stock Price")
            print("=" * 50)
            print(f"Symbol: {tcs_symbol}")
            print(f"Company: {info.get('longName', 'TCS Limited')}")
            print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 50)
            print(f"Current Price: ₹{current_price:.2f}")
            print(f"Open Price: ₹{open_price:.2f}")
            print(f"High Price: ₹{high_price:.2f}")
            print(f"Low Price: ₹{low_price:.2f}")
            print(f"Volume: {volume:,}")
            
            # Calculate change from open
            change = current_price - open_price
            change_percent = (change / open_price) * 100
            
            change_symbol = "+" if change >= 0 else ""
            print(f"Change: {change_symbol}₹{change:.2f} ({change_symbol}{change_percent:.2f}%)")
            print("=" * 50)
            
        else:
            print("Unable to fetch current stock data. Market might be closed.")
            
    except Exception as e:
        print(f"Error fetching TCS stock price: {e}")
        print("Please check your internet connection and try again.")

if __name__ == "__main__":
    print("Fetching TCS stock price...")
    get_tcs_stock_price()

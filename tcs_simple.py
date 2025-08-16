#!/usr/bin/env python3
"""
Enhanced Python script to display stock price with user input and wildcard search
"""

import yfinance as yf
import re
from difflib import get_close_matches

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
    'britannia': 'BRITANNIA.NS',
    'dabur': 'DABUR.NS',
    'eicher motors': 'EICHERMOT.NS',
    'eicher': 'EICHERMOT.NS',
    'bajaj auto': 'BAJAJ-AUTO.NS',
    'hero motocorp': 'HEROMOTOCO.NS',
    'hero': 'HEROMOTOCO.NS',
    'grasim': 'GRASIM.NS',
    'shree cement': 'SHREECEM.NS',
    'cipla': 'CIPLA.NS',
    'divis labs': 'DIVISLAB.NS',
    'biocon': 'BIOCON.NS'
}

def search_stock_symbol(user_input):
    """
    Search for stock symbol based on user input using wildcard/fuzzy matching
    """
    user_input = user_input.lower().strip()
    
    # First, try exact match
    if user_input in INDIAN_STOCKS:
        return INDIAN_STOCKS[user_input], user_input
    
    # Try partial matching (contains)
    for stock_name, symbol in INDIAN_STOCKS.items():
        if user_input in stock_name or stock_name in user_input:
            return symbol, stock_name
    
    # Try fuzzy matching using difflib
    close_matches = get_close_matches(user_input, INDIAN_STOCKS.keys(), n=3, cutoff=0.6)
    if close_matches:
        best_match = close_matches[0]
        return INDIAN_STOCKS[best_match], best_match
    
    # If no match found, try as direct symbol
    # Add .NS if not present and it's likely an Indian stock
    if not user_input.endswith('.ns') and not user_input.endswith('.bo'):
        test_symbol = user_input.upper() + '.NS'
    else:
        test_symbol = user_input.upper()
    
    return test_symbol, user_input

def get_stock_price(symbol):
    """
    Fetch stock price for given symbol
    """
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d")
        
        if not data.empty:
            current_price = data['Close'].iloc[-1]
            company_info = stock.info
            company_name = company_info.get('longName', company_info.get('shortName', symbol))
            return current_price, company_name
        else:
            return None, None
    except Exception as e:
        return None, None

def main():
    """
    Main function to handle user input and display stock price
    """
    print("=== Stock Price Checker ===")
    print("Enter a stock name (e.g., 'tcs', 'reliance', 'infosys', 'hdfc', etc.)")
    print("You can use partial names - the system will try to find the best match!")
    print()
    
    while True:
        user_input = input("Enter stock name (or 'quit' to exit): ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not user_input:
            print("Please enter a stock name.")
            continue
        
        print(f"Searching for '{user_input}'...")
        
        # Search for the stock symbol
        symbol, matched_name = search_stock_symbol(user_input)
        
        # Get stock price
        price, company_name = get_stock_price(symbol)
        
        if price is not None:
            print(f"✓ Found: {company_name}")
            print(f"Symbol: {symbol}")
            print(f"Current Price: ₹{price:.2f}")
            if matched_name != user_input.lower():
                print(f"(Matched '{user_input}' to '{matched_name}')")
            
            # Ask if user wants detailed analysis
            detail_choice = input("Would you like detailed analysis with charts? (y/n): ").strip().lower()
            if detail_choice in ['y', 'yes']:
                print("🔄 Loading enhanced analysis...")
                import subprocess
                import sys
                subprocess.run([sys.executable, "enhanced_stock_analyzer.py"], 
                             input=f"{user_input}\nquit\n", text=True, cwd="C:/POC Stand alone")
        else:
            print(f"✗ Unable to find stock price for '{user_input}'")
            print("Try using a different name or check if the stock symbol is correct.")
        
        print("-" * 50)

if __name__ == "__main__":
    main()

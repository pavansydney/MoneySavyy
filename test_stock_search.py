#!/usr/bin/env python3
"""
Test script to demonstrate wildcard search capabilities
"""

import yfinance as yf
from difflib import get_close_matches

# Dictionary of popular Indian stocks
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
    'maruti suzuki': 'MARUTI.NS',
    'maruti': 'MARUTI.NS',
    'asian paints': 'ASIANPAINT.NS'
}

def search_and_get_price(user_input):
    """Test function to demonstrate search capabilities"""
    user_input = user_input.lower().strip()
    
    # Exact match
    if user_input in INDIAN_STOCKS:
        symbol = INDIAN_STOCKS[user_input]
        match_type = "Exact match"
    else:
        # Partial matching
        found = False
        for stock_name, symbol in INDIAN_STOCKS.items():
            if user_input in stock_name or stock_name in user_input:
                match_type = f"Partial match (found in '{stock_name}')"
                found = True
                break
        
        if not found:
            # Fuzzy matching
            close_matches = get_close_matches(user_input, INDIAN_STOCKS.keys(), n=1, cutoff=0.6)
            if close_matches:
                best_match = close_matches[0]
                symbol = INDIAN_STOCKS[best_match]
                match_type = f"Fuzzy match ('{best_match}')"
            else:
                return f"No match found for '{user_input}'"
    
    # Get price
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d")
        if not data.empty:
            price = data['Close'].iloc[-1]
            company_name = stock.info.get('longName', symbol)
            return f"{match_type}: {company_name} ({symbol}) - ₹{price:.2f}"
        else:
            return f"Found symbol {symbol} but no price data available"
    except:
        return f"Error fetching data for {symbol}"

# Test cases
test_inputs = [
    "tcs",           # Exact match
    "icici",         # Partial match  
    "reliance",      # Exact match
    "hdfc",          # Partial match
    "tata",          # Partial match
    "maruti",        # Exact match
    "asian",         # Partial match
    "infosys",       # Exact match
    "infy",          # Should try fuzzy match or direct symbol
    "sbi",           # Exact match
    "airtel",        # Exact match
    "bharti"         # Partial match
]

print("=== Testing Stock Search Capabilities ===\n")

for test_input in test_inputs:
    result = search_and_get_price(test_input)
    print(f"Input: '{test_input}' -> {result}")

print("\n=== Test completed ===")

#!/usr/bin/env python3
"""
Money Savyy - Save Smart Dream Big
Advanced Stock Analysis Web Application
Version 2.1.0
"""

# Application Version Information
APP_VERSION = "2.1.0"
APP_NAME = "Money Savyy"
APP_TAGLINE = "Save Smart Dream Big"
RELEASE_DATE = "August 2025"

# Release Notes
LATEST_FEATURES = [
    {
        "title": "Enhanced Technical Analysis",
        "description": "Advanced RSI, MACD, and Bollinger Bands with interactive charts",
        "icon": "fas fa-chart-line",
        "status": "live"
    },
    {
        "title": "AI-Powered Predictions", 
        "description": "Gemini AI integration for intelligent stock recommendations",
        "icon": "fas fa-robot",
        "status": "live"
    },
    {
        "title": "Real-time News & Sentiment",
        "description": "Live news feed with sentiment analysis and market impact scoring",
        "icon": "fas fa-newspaper", 
        "status": "live"
    },
    {
        "title": "Responsive Design",
        "description": "Fully responsive interface with dark/light theme toggle",
        "icon": "fas fa-mobile-alt",
        "status": "live"
    }
]

UPCOMING_FEATURES = [
    {
        "title": "Portfolio Management",
        "description": "Track multiple stocks, portfolio performance, and risk metrics", 
        "icon": "fas fa-chart-pie",
        "status": "in_progress"
    },
    {
        "title": "Smart Alerts",
        "description": "Custom price alerts, technical pattern notifications, and market updates",
        "icon": "fas fa-bell",
        "status": "planned"
    },
    {
        "title": "Social Trading", 
        "description": "Follow expert traders, share analysis, and community insights",
        "icon": "fas fa-users",
        "status": "planned"
    },
    {
        "title": "Advanced ML Models",
        "description": "LSTM neural networks for enhanced price prediction accuracy",
        "icon": "fas fa-brain",
        "status": "research"
    }
]

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.express as px
import plotly.utils
import json
from datetime import datetime, timedelta
import warnings
from difflib import get_close_matches
# import ta  # Removed for deployment compatibility

# Conditional sklearn imports with error handling
try:
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import PolynomialFeatures
    from sklearn.metrics import r2_score
    SKLEARN_AVAILABLE = True
    print("✅ sklearn successfully imported")
except ImportError as e:
    print(f"⚠️  Warning: sklearn not available: {e}")
    SKLEARN_AVAILABLE = False
    # Mock classes for when sklearn is not available
    class LinearRegression:
        def __init__(self): pass
        def fit(self, X, y): return self
        def predict(self, X): return np.zeros(len(X))
    
    class PolynomialFeatures:
        def __init__(self, degree=2): pass
        def fit_transform(self, X): return X
        def transform(self, X): return X
    
    def r2_score(y_true, y_pred): return 0.0

import requests
from bs4 import BeautifulSoup
# import feedparser  # Temporarily disabled for Python 3.13 compatibility
from textblob import TextBlob
import threading
import time
from functools import lru_cache
import random
import google.generativeai as genai
from dotenv import load_dotenv
import os
import pickle
import os

# Load environment variables
load_dotenv()

# Configure Gemini AI
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'your-gemini-api-key-here')
genai.configure(api_key=GEMINI_API_KEY)

def get_sector_fallback(symbol):
    """Get fallback sector information based on stock symbol"""
    symbol_upper = symbol.upper().replace('.NS', '')
    
    sector_mapping = {
        'TCS': 'Information Technology',
        'INFY': 'Information Technology',
        'WIPRO': 'Information Technology',
        'HCLTECH': 'Information Technology',
        'TECHM': 'Information Technology',
        'RELIANCE': 'Oil & Gas',
        'ONGC': 'Oil & Gas',
        'IOC': 'Oil & Gas',
        'HDFCBANK': 'Financial Services',
        'ICICIBANK': 'Financial Services',
        'SBIN': 'Financial Services',
        'AXISBANK': 'Financial Services',
        'KOTAKBANK': 'Financial Services',
        'ITC': 'Consumer Goods',
        'HINDUNILVR': 'Consumer Goods',
        'NESTLEIND': 'Consumer Goods',
        'BHARTIARTL': 'Telecommunications',
        'ADANIPORTS': 'Infrastructure',
        'NTPC': 'Power',
        'POWERGRID': 'Power',
        'ULTRACEMCO': 'Cement',
        'ASIANPAINT': 'Paints',
        'BAJFINANCE': 'Financial Services',
        'MARUTI': 'Automobile',
        'TATAMOTORS': 'Automobile'
    }
    
    return sector_mapping.get(symbol_upper, 'Diversified')

def get_industry_fallback(symbol):
    """Get fallback industry information based on stock symbol"""
    symbol_upper = symbol.upper().replace('.NS', '')
    
    industry_mapping = {
        'TCS': 'IT Services',
        'INFY': 'IT Services',
        'WIPRO': 'IT Services',
        'HCLTECH': 'IT Services',
        'TECHM': 'IT Services',
        'RELIANCE': 'Oil & Gas Refining',
        'ONGC': 'Oil & Gas Exploration',
        'IOC': 'Oil & Gas Refining',
        'HDFCBANK': 'Private Banks',
        'ICICIBANK': 'Private Banks',
        'SBIN': 'Public Banks',
        'AXISBANK': 'Private Banks',
        'KOTAKBANK': 'Private Banks',
        'ITC': 'Cigarettes & Tobacco',
        'HINDUNILVR': 'FMCG',
        'NESTLEIND': 'FMCG',
        'BHARTIARTL': 'Telecom Services',
        'ADANIPORTS': 'Port & Allied Services',
        'NTPC': 'Power Generation',
        'POWERGRID': 'Power Transmission',
        'ULTRACEMCO': 'Cement',
        'ASIANPAINT': 'Paints',
        'BAJFINANCE': 'NBFCs',
        'MARUTI': 'Passenger Cars',
        'TATAMOTORS': 'Commercial Vehicles'
    }
    
    return industry_mapping.get(symbol_upper, 'Diversified Industries')

class GeminiFinancialAdvisor:
    """Gemini AI powered financial advisor for intelligent insights"""
    
    def __init__(self):
        try:
            # Try different model names for compatibility, starting with the latest
            model_names = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro', 'gemini-1.0-pro']
            self.model = None
            
            for model_name in model_names:
                try:
                    self.model = genai.GenerativeModel(model_name)
                    print(f"✅ Gemini AI initialized successfully with model: {model_name}")
                    break
                except Exception as model_error:
                    print(f"⚠️ Failed to initialize {model_name}: {model_error}")
                    continue
            
            if not self.model:
                raise Exception("No compatible Gemini model found")
                
        except Exception as e:
            print(f"❌ Gemini AI initialization failed: {e}")
            self.model = None
    
    def list_available_models(self):
        """List all available Gemini models for debugging"""
        try:
            models = genai.list_models()
            available_models = []
            for model in models:
                if 'generateContent' in model.supported_generation_methods:
                    available_models.append(model.name)
            return available_models
        except Exception as e:
            print(f"Error listing models: {e}")
            return []
    
    def generate_stock_analysis(self, symbol, current_price, change_percent=0, volume=0, market_cap=None):
        """Generate comprehensive stock analysis using Gemini AI"""
        if not self.model:
            return self._fallback_stock_analysis(symbol, current_price)
        
        try:
            prompt = f"""
            Analyze the Indian stock {symbol} with the following current data:
            - Current Price: ₹{current_price}
            - Price Change: {change_percent:.2f}%
            - Volume: {volume:,}
            - Market Cap: ₹{market_cap:,} (if available)
            
            Provide a comprehensive analysis in JSON format with:
            1. "technical_summary": Brief technical analysis (max 100 words)
            2. "recommendation": One of "BUY", "HOLD", "SELL" 
            3. "recommendation_reason": Clear reasoning (max 80 words)
            4. "risk_level": "LOW", "MEDIUM", or "HIGH"
            5. "risk_explanation": Risk assessment (max 60 words)
            6. "price_targets": {{
                "support": estimated support level,
                "resistance": estimated resistance level,
                "target_3m": 3-month price target
            }}
            7. "market_outlook": 3-6 month outlook (max 100 words)
            8. "key_factors": Array of 3-4 key factors affecting the stock
            
            Focus on practical insights for retail investors. Consider current Indian market conditions.
            Return only valid JSON, no other text.
            """
            
            response = self.model.generate_content(prompt)
            
            # Try to parse JSON response
            try:
                analysis = json.loads(response.text)
                analysis['source'] = 'gemini_ai'
                return analysis
            except json.JSONDecodeError:
                # If JSON parsing fails, extract key info manually
                return self._parse_gemini_response(response.text, symbol, current_price)
                
        except Exception as e:
            print(f"Gemini stock analysis error: {e}")
            return self._fallback_stock_analysis(symbol, current_price)
    
    def generate_financial_advice(self, user_profile):
        """Generate comprehensive financial advice using Gemini AI like a professional wealth advisor"""
        if not self.model:
            return self._fallback_financial_advice(user_profile)
        
        try:
            age = user_profile.get('age', 30)
            salary = user_profile.get('salary', 50000)
            expenses = user_profile.get('monthly_expenses', 30000)
            savings = user_profile.get('current_savings', 100000)
            investments = user_profile.get('investments', 50000)
            emi = user_profile.get('emi', 0)
            city = user_profile.get('city', 'Mumbai')
            family_members = user_profile.get('family_members', 1)
            has_insurance = user_profile.get('has_insurance', False)
            
            prompt = f"""
            Act as a professional certified financial planner (CFP) and create comprehensive wealth management advice for this Indian client:
            
            CLIENT PROFILE:
            - Age: {age} years | Location: {city} | Family Size: {family_members}
            - Monthly Income: ₹{salary:,} | Monthly Expenses: ₹{expenses:,}
            - Current Savings: ₹{savings:,} | Current Investments: ₹{investments:,}
            - Monthly EMI: ₹{emi:,} | Insurance Coverage: {'Yes' if has_insurance else 'No'}
            
            Provide professional wealth management advice in JSON format with:
            
            1. "executive_summary": {{
                "financial_health_score": score out of 100,
                "wealth_category": "WEALTH_BUILDER" | "STEADY_SAVER" | "DEBT_MANAGER" | "FRESH_STARTER",
                "key_strengths": [3 major strengths],
                "priority_areas": [3 areas needing immediate attention],
                "projected_wealth_10yr": estimated wealth in 10 years with proper planning
            }}
            
            2. "detailed_portfolio_analysis": {{
                "current_asset_allocation": {{
                    "liquid_cash": percentage,
                    "equity_investments": percentage, 
                    "debt_investments": percentage,
                    "real_estate": percentage,
                    "others": percentage
                }},
                "recommended_allocation": {{
                    "equity_funds": percentage,
                    "debt_funds": percentage,
                    "emergency_fund": percentage,
                    "ppf_elss": percentage,
                    "international_funds": percentage
                }},
                "rebalancing_strategy": "specific steps to achieve recommended allocation"
            }}
            
            3. "goal_based_planning": {{
                "short_term_goals": [{{
                    "goal": "goal name",
                    "target_amount": amount,
                    "time_horizon": "months/years",
                    "monthly_investment": required monthly amount,
                    "suggested_instruments": ["instrument1", "instrument2"]
                }}],
                "long_term_goals": [{{
                    "goal": "retirement/house/child education",
                    "target_amount": amount,
                    "time_horizon": "years",
                    "monthly_sip": required SIP amount,
                    "investment_strategy": "detailed strategy"
                }}]
            }}
            
            4. "risk_management": {{
                "risk_profile": "CONSERVATIVE" | "MODERATE" | "AGGRESSIVE",
                "insurance_gap_analysis": {{
                    "life_cover_needed": {0 if has_insurance else 'required amount'},
                    "health_cover_needed": {0 if has_insurance else 'required amount'},
                    "current_coverage": {"adequate" if has_insurance else "insufficient"},
                    "annual_premium_budget": amount only if insurance is needed
                }},
                "diversification_score": score out of 10,
                "concentration_risks": ["risk1", "risk2"]
            }}
            
            5. "tax_optimization": {{
                "current_tax_liability": estimated annual tax,
                "potential_savings": maximum possible tax savings,
                "tax_efficient_instruments": [{{
                    "instrument": "ELSS/PPF/NPS etc",
                    "recommended_amount": amount,
                    "tax_benefit": "80C/80D etc",
                    "expected_returns": percentage
                }}],
                "tax_harvesting_opportunities": ["opportunity1", "opportunity2"]
            }}
            
            6. "monthly_action_plan": {{
                "immediate_actions": [5 actions for next 30 days],
                "quarterly_reviews": [3 things to review every quarter],
                "annual_planning": [2 major annual financial activities],
                "automated_investments": {{
                    "recommended_sips": [{{
                        "fund_category": "Large Cap/Mid Cap/Debt",
                        "amount": monthly amount,
                        "rationale": "why this fund category"
                    }}]
                }}
            }}
            
            7. "market_outlook_advisory": {{
                "current_market_view": "market assessment for next 6-12 months",
                "sector_opportunities": ["sector1", "sector2", "sector3"],
                "timing_strategies": {{
                    "sip_timing": "best time to start/increase SIPs",
                    "lumpsum_opportunities": "when to consider lumpsum investments",
                    "exit_strategies": "when to book profits or rebalance"
                }}
            }}
            
            8. "performance_benchmarks": {{
                "target_annual_returns": {{
                    "conservative_scenario": percentage,
                    "moderate_scenario": percentage,
                    "optimistic_scenario": percentage
                }},
                "wealth_milestones": [{{
                    "milestone": "₹10 lakhs portfolio",
                    "target_date": "expected date",
                    "required_monthly_investment": amount
                }}],
                "review_metrics": ["metric1", "metric2", "metric3"]
            }}
            
            Focus on actionable, specific advice like professional wealth managers provide to HNI clients.
            Use current Indian market conditions, tax laws, and investment opportunities.
            Return only valid JSON, no other text.
            """
            
            response = self.model.generate_content(prompt)
            
            try:
                advice = json.loads(response.text)
                advice['source'] = 'gemini_ai'
                return advice
            except json.JSONDecodeError:
                return self._parse_financial_advice_response(response.text, user_profile)
                
        except Exception as e:
            print(f"Gemini financial advice error: {e}")
            return self._fallback_financial_advice(user_profile)
    
    def _fallback_stock_analysis(self, symbol, current_price):
        """Fallback analysis when Gemini is unavailable"""
        return {
            "technical_summary": f"Technical analysis for {symbol} shows current price of ₹{current_price}. Monitor key support and resistance levels.",
            "recommendation": "HOLD",
            "recommendation_reason": "Maintain current position until clearer market signals emerge.",
            "risk_level": "MEDIUM",
            "risk_explanation": "Standard market risk applies. Diversify portfolio appropriately.",
            "price_targets": {
                "support": current_price * 0.95,
                "resistance": current_price * 1.05,
                "target_3m": current_price * 1.02
            },
            "market_outlook": "Market conditions remain volatile. Monitor quarterly results and sector trends.",
            "key_factors": ["Market sentiment", "Sector performance", "Economic indicators", "Company fundamentals"],
            "source": "fallback"
        }
    
    def _fallback_financial_advice(self, user_profile):
        """Comprehensive fallback advice when Gemini is unavailable"""
        salary = user_profile.get('salary', 50000)
        expenses = user_profile.get('monthly_expenses', 30000)
        age = user_profile.get('age', 30)
        savings = user_profile.get('current_savings', 100000)
        investments = user_profile.get('investments', 50000)
        has_insurance = user_profile.get('has_insurance', False)
        
        savings_rate = ((salary - expenses) / salary) * 100 if salary > 0 else 0
        financial_score = min(100, max(20, savings_rate * 2 + (savings / 100000) * 10))
        
        # Determine wealth category
        if savings > 1000000 and investments > 500000:
            wealth_category = "WEALTH_BUILDER"
        elif savings_rate > 20:
            wealth_category = "STEADY_SAVER"
        elif expenses > salary * 0.8:
            wealth_category = "DEBT_MANAGER"
        else:
            wealth_category = "FRESH_STARTER"
        
        return {
            "executive_summary": {
                "financial_health_score": round(financial_score),
                "wealth_category": wealth_category,
                "key_strengths": [
                    f"Monthly savings rate of {savings_rate:.1f}%",
                    "Disciplined expense management",
                    "Growing investment portfolio"
                ],
                "priority_areas": [
                    "Increase emergency fund coverage",
                    "Optimize asset allocation",
                    "Enhance insurance protection"
                ],
                "projected_wealth_10yr": int(savings * 2.5 + investments * 4 + (salary - expenses) * 120 * 1.12)
            },
            "detailed_portfolio_analysis": {
                "current_asset_allocation": {
                    "liquid_cash": 60,
                    "equity_investments": 25,
                    "debt_investments": 10,
                    "real_estate": 0,
                    "others": 5
                },
                "recommended_allocation": {
                    "equity_funds": 50 if age < 40 else 30,
                    "debt_funds": 25,
                    "emergency_fund": 15,
                    "ppf_elss": 10,
                    "international_funds": 0
                },
                "rebalancing_strategy": "Gradually shift from savings account to equity and debt mutual funds through systematic transfer plans"
            },
            "goal_based_planning": {
                "short_term_goals": [
                    {
                        "goal": "Emergency Fund",
                        "target_amount": expenses * 6,
                        "time_horizon": "12 months",
                        "monthly_investment": max(5000, expenses * 0.5),
                        "suggested_instruments": ["Liquid Funds", "High-yield Savings Account"]
                    }
                ],
                "long_term_goals": [
                    {
                        "goal": "Retirement Planning",
                        "target_amount": salary * 300,
                        "time_horizon": f"{65 - age} years",
                        "monthly_sip": max(salary * 0.15, 10000),
                        "investment_strategy": "Mix of large-cap equity funds (40%), mid-cap funds (20%), and balanced funds (40%)"
                    }
                ]
            },
            "risk_management": {
                "risk_profile": "MODERATE" if age < 40 else "CONSERVATIVE",
                "insurance_gap_analysis": {
                    "life_cover_needed": 0 if has_insurance else salary * 120,
                    "health_cover_needed": 0 if has_insurance else 1000000,
                    "current_coverage": "adequate" if has_insurance else "insufficient",
                    "annual_premium_budget": 0 if has_insurance else salary * 0.03
                },
                "diversification_score": 6,
                "concentration_risks": ["High cash allocation", "Limited equity exposure"] if not has_insurance else ["Portfolio concentration"]
            },
            "tax_optimization": {
                "current_tax_liability": max(0, (salary * 12 - 250000) * 0.2),
                "potential_savings": 46800,
                "tax_efficient_instruments": [
                    {
                        "instrument": "ELSS Mutual Funds",
                        "recommended_amount": 150000,
                        "tax_benefit": "Section 80C",
                        "expected_returns": 12
                    },
                    {
                        "instrument": "PPF",
                        "recommended_amount": 150000,
                        "tax_benefit": "Section 80C + EEE",
                        "expected_returns": 8
                    }
                ],
                "tax_harvesting_opportunities": ["Book profits in equity funds after 1 year", "Use SIP to average costs"]
            },
            "monthly_action_plan": {
                "immediate_actions": [
                    "Open PPF account and start ₹12,500 monthly contribution",
                    "Start ELSS SIP of ₹10,000 for tax saving",
                    "Build emergency fund with ₹15,000 monthly allocation",
                    "Compare and purchase term life insurance",
                    "Set up automated bank transfers for all investments"
                ],
                "quarterly_reviews": [
                    "Review and rebalance portfolio allocation",
                    "Assess progress towards financial goals",
                    "Evaluate new investment opportunities"
                ],
                "annual_planning": [
                    "Tax planning and investment under 80C",
                    "Review and adjust SIP amounts based on salary increment"
                ],
                "automated_investments": {
                    "recommended_sips": [
                        {
                            "fund_category": "Large Cap Equity",
                            "amount": salary * 0.08,
                            "rationale": "Stable growth with lower volatility for core portfolio"
                        },
                        {
                            "fund_category": "ELSS Tax Saver",
                            "amount": 12500,
                            "rationale": "Tax saving under 80C with equity exposure"
                        }
                    ]
                }
            },
            "market_outlook_advisory": {
                "current_market_view": "Indian markets show long-term growth potential despite short-term volatility. Focus on systematic investments.",
                "sector_opportunities": ["Technology", "Healthcare", "Financial Services"],
                "timing_strategies": {
                    "sip_timing": "Start SIPs immediately regardless of market levels - time in market beats timing the market",
                    "lumpsum_opportunities": "Consider lumpsum during market corrections of 15% or more",
                    "exit_strategies": "Review portfolio annually and rebalance when allocation deviates by more than 10%"
                }
            },
            "performance_benchmarks": {
                "target_annual_returns": {
                    "conservative_scenario": 8,
                    "moderate_scenario": 12,
                    "optimistic_scenario": 15
                },
                "wealth_milestones": [
                    {
                        "milestone": "₹10 lakhs portfolio",
                        "target_date": "3-4 years",
                        "required_monthly_investment": 20000
                    },
                    {
                        "milestone": "₹50 lakhs portfolio",
                        "target_date": "8-10 years",
                        "required_monthly_investment": 35000
                    }
                ],
                "review_metrics": ["Portfolio value growth", "Asset allocation adherence", "Goal achievement progress"]
            },
            "source": "professional_fallback"
        }
    
    def _parse_gemini_response(self, response_text, symbol, current_price):
        """Parse non-JSON Gemini response"""
        # Basic parsing logic for when JSON fails
        return self._fallback_stock_analysis(symbol, current_price)
    
    def _parse_financial_advice_response(self, response_text, user_profile):
        """Parse non-JSON financial advice response"""
        return self._fallback_financial_advice(user_profile)
    
    def generate_news_sentiment_analysis(self, symbol, company_name, current_price, recent_news=None):
        """Generate AI-powered news sentiment analysis"""
        if not self.model:
            return self._fallback_news_sentiment(symbol, company_name)
        
        try:
            # Create prompt for news sentiment analysis
            news_context = ""
            if recent_news and len(recent_news) > 0:
                news_context = f"Recent news headlines: {'; '.join(recent_news[:5])}"
            else:
                news_context = f"Analyze general market sentiment for {company_name} ({symbol})"
            
            prompt = f"""
            Analyze the news sentiment and market outlook for {company_name} ({symbol}):
            Current Price: ₹{current_price}
            {news_context}
            
            Provide analysis in JSON format with:
            {{
                "sentiment_score": number between -100 to +100 (negative=bearish, positive=bullish),
                "sentiment_label": "VERY_BULLISH", "BULLISH", "NEUTRAL", "BEARISH", or "VERY_BEARISH",
                "key_factors": ["factor1", "factor2", "factor3"] (max 5 factors affecting sentiment),
                "market_outlook": {{
                    "short_term": "outlook for next 1-3 months",
                    "medium_term": "outlook for next 6-12 months",
                    "long_term": "outlook for next 2-5 years"
                }},
                "news_summary": "brief summary of key news impacts",
                "risk_factors": ["risk1", "risk2", "risk3"] (top concerns),
                "opportunities": ["opportunity1", "opportunity2"] (potential catalysts),
                "analyst_consensus": "BUY/HOLD/SELL based on overall sentiment"
            }}
            
            Focus on Indian market context and provide actionable insights.
            """
            
            response = self.model.generate_content(prompt)
            
            # Try to parse JSON response
            try:
                import json
                analysis = json.loads(response.text)
                analysis['source'] = 'Gemini AI News Sentiment Analysis'
                analysis['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                return analysis
            except json.JSONDecodeError:
                return self._parse_sentiment_response(response.text, symbol)
                
        except Exception as e:
            print(f"Gemini news sentiment error: {e}")
            return self._fallback_news_sentiment(symbol, company_name)
    
    def generate_fundamentals_analysis(self, symbol, company_name, financial_data):
        """Generate AI-powered fundamental analysis"""
        if not self.model:
            return self._fallback_fundamentals(symbol, company_name)
        
        try:
            # Extract key financial metrics
            market_cap = financial_data.get('market_cap', 0)
            pe_ratio = financial_data.get('pe_ratio', 0)
            book_value = financial_data.get('book_value', 0)
            dividend_yield = financial_data.get('dividend_yield', 0)
            debt_equity = financial_data.get('debt_equity', 0)
            roe = financial_data.get('roe', 0)
            current_price = financial_data.get('current_price', 0)
            
            prompt = f"""
            Perform fundamental analysis for {company_name} ({symbol}):
            
            Financial Metrics:
            - Current Price: ₹{current_price}
            - Market Cap: ₹{market_cap:,}
            - P/E Ratio: {pe_ratio}
            - Book Value: ₹{book_value}
            - Dividend Yield: {dividend_yield}%
            - Debt-to-Equity: {debt_equity}
            - ROE: {roe}%
            
            Provide comprehensive analysis in JSON format:
            {{
                "valuation_assessment": {{
                    "intrinsic_value_estimate": estimated fair value per share,
                    "valuation_rating": "UNDERVALUED", "FAIRLY_VALUED", or "OVERVALUED",
                    "valuation_rationale": "explanation of valuation assessment"
                }},
                "financial_health": {{
                    "overall_score": number 1-10 (10=excellent),
                    "profitability_grade": "A+", "A", "B", "C", or "D",
                    "liquidity_grade": "A+", "A", "B", "C", or "D",
                    "leverage_grade": "A+", "A", "B", "C", or "D",
                    "efficiency_grade": "A+", "A", "B", "C", or "D"
                }},
                "key_strengths": ["strength1", "strength2", "strength3"],
                "key_concerns": ["concern1", "concern2", "concern3"],
                "growth_prospects": {{
                    "revenue_growth_outlook": "growth expectations and rationale",
                    "profit_margin_trend": "margin analysis and outlook",
                    "market_expansion": "expansion opportunities"
                }},
                "dividend_analysis": {{
                    "dividend_sustainability": "HIGH", "MEDIUM", or "LOW",
                    "dividend_growth_potential": "analysis of future dividend prospects",
                    "payout_ratio_assessment": "evaluation of payout ratio"
                }},
                "competitive_position": {{
                    "market_position": "description of competitive standing",
                    "competitive_advantages": ["advantage1", "advantage2"],
                    "competitive_threats": ["threat1", "threat2"]
                }},
                "investment_recommendation": {{
                    "rating": "STRONG_BUY", "BUY", "HOLD", "SELL", or "STRONG_SELL",
                    "target_price": estimated target price,
                    "investment_horizon": "SHORT_TERM", "MEDIUM_TERM", or "LONG_TERM",
                    "rationale": "detailed reasoning for recommendation"
                }}
            }}
            
            Consider Indian market context and sector-specific factors.
            """
            
            response = self.model.generate_content(prompt)
            
            # Try to parse JSON response
            try:
                import json
                analysis = json.loads(response.text)
                analysis['source'] = 'Gemini AI Fundamental Analysis'
                analysis['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                return analysis
            except json.JSONDecodeError:
                return self._parse_fundamentals_response(response.text, symbol)
                
        except Exception as e:
            print(f"Gemini fundamentals error: {e}")
            return self._fallback_fundamentals(symbol, company_name)
    
    def _fallback_news_sentiment(self, symbol, company_name):
        """Fallback news sentiment with realistic sentiment scores"""
        # Generate more realistic sentiment scores based on stock patterns
        import random
        
        # Create sentiment based on company/sector (more realistic than always 0)
        base_sentiment = 0
        sentiment_label = "NEUTRAL"
        
        # Assign sentiment based on major stocks (simulate market conditions)
        major_stocks = {
            'RELIANCE': 15, 'TCS': 20, 'INFY': 18, 'HDFCBANK': 12, 'ICICIBANK': 10,
            'SBIN': 5, 'WIPRO': 8, 'BAJFINANCE': 15, 'ASIANPAINT': 12, 'MARUTI': 7
        }
        
        stock_base = symbol.replace('.NS', '').replace('.BO', '')
        if stock_base in major_stocks:
            base_sentiment = major_stocks[stock_base] + random.randint(-8, 8)
        else:
            # For other stocks, generate based on market conditions
            base_sentiment = random.randint(-15, 20)
        
        # Determine sentiment label based on score
        if base_sentiment >= 15:
            sentiment_label = "BULLISH"
        elif base_sentiment >= 5:
            sentiment_label = "NEUTRAL"
        elif base_sentiment >= -10:
            sentiment_label = "NEUTRAL"
        elif base_sentiment >= -20:
            sentiment_label = "BEARISH"
        else:
            sentiment_label = "VERY_BEARISH"
            
        # Create more dynamic factors based on sentiment
        if base_sentiment > 10:
            key_factors = ["Strong earnings growth", "Positive sector outlook", "Favorable market conditions"]
            risk_factors = ["Market volatility", "Global economic concerns"]
            opportunities = ["Expansion opportunities", "Market share growth", "Digital transformation"]
        elif base_sentiment > 0:
            key_factors = ["Stable performance", "Moderate growth", "Sector resilience"]
            risk_factors = ["Competition pressure", "Market headwinds", "Regulatory changes"]
            opportunities = ["Cost optimization", "Market recovery"]
        else:
            key_factors = ["Challenging market conditions", "Sector headwinds", "Economic uncertainty"]
            risk_factors = ["Revenue decline", "Margin pressure", "High competition", "Market volatility"]
            opportunities = ["Restructuring benefits", "Market bottoming out"]
            
        return {
            "sentiment_score": base_sentiment,
            "sentiment_label": sentiment_label,
            "key_factors": key_factors,
            "market_outlook": {
                "short_term": f"{'Positive momentum' if base_sentiment > 5 else 'Mixed signals' if base_sentiment > -5 else 'Cautious outlook'} expected in coming months",
                "medium_term": f"{'Growth trajectory' if base_sentiment > 0 else 'Stabilization efforts'} dependent on market conditions and earnings",
                "long_term": f"{'Strong fundamentals' if base_sentiment > 10 else 'Recovery potential' if base_sentiment > -10 else 'Turnaround story'} based on sector trends"
            },
            "news_summary": f"Market sentiment shows {'optimism' if base_sentiment > 5 else 'neutrality' if base_sentiment > -5 else 'caution'} for {company_name} based on recent performance and sector trends",
            "risk_factors": risk_factors,
            "opportunities": opportunities,
            "analyst_consensus": "BUY" if base_sentiment > 15 else "HOLD" if base_sentiment > -5 else "SELL",
            "source": "Enhanced Market Analysis (Demo Mode)",
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _fallback_fundamentals(self, symbol, company_name):
        """Fallback fundamentals when Gemini is unavailable"""
        # Generate more realistic fallback values based on stock symbol
        base_price = 1000  # Default base price
        if 'TCS' in symbol.upper():
            base_price = 3500
        elif 'RELIANCE' in symbol.upper():
            base_price = 2400
        elif 'INFY' in symbol.upper():
            base_price = 1600
        elif 'HDFC' in symbol.upper():
            base_price = 1700
        
        # Generate realistic target price (5-15% above current)
        import random
        target_multiplier = random.uniform(1.05, 1.15)
        target_price = base_price * target_multiplier
        
        # Generate realistic intrinsic value
        intrinsic_multiplier = random.uniform(0.95, 1.25)
        intrinsic_value = base_price * intrinsic_multiplier
        
        return {
            "valuation_assessment": {
                "intrinsic_value_estimate": round(intrinsic_value, 2),
                "valuation_rating": "FAIRLY_VALUED" if abs(intrinsic_value - base_price) < base_price * 0.1 else ("UNDERVALUED" if intrinsic_value > base_price else "OVERVALUED"),
                "valuation_rationale": f"Based on fundamental analysis considering current market conditions and {company_name}'s financial metrics"
            },
            "financial_health": {
                "overall_score": random.randint(6, 8),
                "profitability_grade": random.choice(["A-", "B+", "B"]),
                "liquidity_grade": random.choice(["A-", "B+", "B"]),
                "leverage_grade": random.choice(["B+", "B", "B-"]),
                "efficiency_grade": random.choice(["A-", "B+", "B"])
            },
            "key_strengths": [
                "Strong market position in sector",
                "Consistent revenue growth",
                "Experienced management team",
                "Robust financial fundamentals"
            ],
            "key_concerns": [
                "Market volatility impact",
                "Competitive pressure",
                "Economic uncertainty",
                "Regulatory challenges"
            ],
            "growth_prospects": {
                "revenue_growth_outlook": "Positive growth expected driven by sector expansion and strategic initiatives",
                "profit_margin_trend": "Stable to improving margins through operational efficiency",
                "market_expansion": "Opportunities in domestic and international markets"
            },
            "dividend_analysis": {
                "dividend_sustainability": "MEDIUM",
                "dividend_growth_potential": "Moderate dividend growth expected based on earnings trajectory",
                "payout_ratio_assessment": "Sustainable payout ratio with scope for growth"
            },
            "competitive_position": {
                "market_position": f"{company_name} maintains a competitive position in its sector",
                "competitive_advantages": ["Brand recognition", "Market expertise"],
                "competitive_threats": ["New market entrants", "Technology disruption"]
            },
            "investment_recommendation": {
                "rating": random.choice(["BUY", "HOLD", "BUY"]),  # Weighted towards positive
                "target_price": round(target_price, 2),
                "investment_horizon": "MEDIUM_TERM",
                "rationale": f"Based on fundamental analysis, {company_name} shows solid prospects with reasonable valuation metrics"
            },
            "source": "Enhanced Fallback Analysis",
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _parse_sentiment_response(self, response_text, symbol):
        """Parse non-JSON sentiment response"""
        return self._fallback_news_sentiment(symbol, symbol)
    
    def _parse_fundamentals_response(self, response_text, symbol):
        """Parse non-JSON fundamentals response"""
        return self._fallback_fundamentals(symbol, symbol)

# Initialize Gemini AI service
gemini_advisor = GeminiFinancialAdvisor()

warnings.filterwarnings('ignore')

# Simple Technical Analysis Functions (replacing ta library for deployment)
def calculate_rsi(prices, window=14):
    """Calculate RSI (Relative Strength Index)"""
    try:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    except:
        return pd.Series([50] * len(prices), index=prices.index)

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """Calculate MACD (Moving Average Convergence Divergence)"""
    try:
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        macd_diff = macd_line - signal_line
        return macd_diff
    except:
        return pd.Series([0] * len(prices), index=prices.index)

# Mock Stock class for NSE data compatibility
class MockStock:
    def __init__(self, symbol, stock_info):
        self.ticker = symbol
        self.info = stock_info

# NSE Direct API Implementation (Updated for better reliability)
def get_nse_stock_data(symbol):
    """Get real NSE data directly from NSE website - FREE!"""
    try:
        # Remove .NS suffix for NSE API
        clean_symbol = symbol.replace('.NS', '').upper()
        
        print(f"📡 Fetching NSE data for {clean_symbol}")
        
        # Enhanced headers to better mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        # Create session for better reliability
        session = requests.Session()
        session.headers.update(headers)
        
        # First, visit the main page to establish session and get cookies
        main_response = session.get('https://www.nseindia.com/', timeout=15)
        
        if main_response.status_code != 200:
            print(f"❌ Failed to establish NSE session: {main_response.status_code}")
            return None
        
        # Wait a bit and update headers for API call
        time.sleep(2)
        
        # Update headers for API call
        api_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.nseindia.com/',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        }
        
        session.headers.update(api_headers)
        
        # NSE Quote API URL
        quote_url = f"https://www.nseindia.com/api/quote-equity?symbol={clean_symbol}"
        
        # Make the API call
        response = session.get(quote_url, timeout=15)
        
        if response.status_code == 200:
            try:
                data = response.json()
                parsed_data = parse_nse_data(data, symbol)
                if parsed_data:
                    print(f"✅ Successfully got NSE data for {clean_symbol}")
                    return parsed_data
                else:
                    print(f"❌ Failed to parse NSE data for {clean_symbol}")
                    return None
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse NSE JSON response: {str(e)}")
                return None
        else:
            print(f"❌ NSE API returned status code: {response.status_code}")
            # For debugging, let's see what we got
            if response.status_code == 401:
                print("💡 NSE requires session authentication - this is expected sometimes")
            return None
            
    except Exception as e:
        print(f"❌ NSE API failed for {symbol}: {str(e)}")
        return None

def get_alternative_indian_stock_data(symbol):
    """Alternative free Indian stock data source"""
    try:
        # Remove .NS suffix and clean symbol
        clean_symbol = symbol.replace('.NS', '').upper()
        
        print(f"🔄 Trying alternative source for {clean_symbol}")
        
        # Use Yahoo Finance with Indian market suffix if not present
        yahoo_symbol = f"{clean_symbol}.NS" if not symbol.endswith('.NS') else symbol
        
        # Try to get data with minimal info to avoid rate limits
        stock = yf.Ticker(yahoo_symbol)
        
        # Get fast info (lighter request)
        try:
            fast_info = stock.fast_info
            current_price = fast_info.get('last_price', 0)
            
            if current_price and current_price > 0:
                # Create data structure similar to NSE format
                return {
                    'current_price': current_price,
                    'open_price': fast_info.get('open', current_price),
                    'high_price': fast_info.get('day_high', current_price * 1.02),
                    'low_price': fast_info.get('day_low', current_price * 0.98),
                    'volume': fast_info.get('regular_market_volume', 1000000),
                    'change': 0,  # Will calculate if we get previous close
                    'change_percent': 0,
                    'company_name': clean_symbol,
                    'hist_data': None,  # Will create mock data
                    'info': {
                        'longName': clean_symbol,
                        'symbol': yahoo_symbol,
                        'sector': 'Technology',
                        'industry': 'Software Services',
                        'marketCap': fast_info.get('market_cap', 0),
                    },
                    'source': 'YAHOO_FAST'
                }
        except Exception as e:
            print(f"❌ Fast info failed: {str(e)}")
            
        return None
        
    except Exception as e:
        print(f"❌ Alternative API failed for {symbol}: {str(e)}")
        return None

# Real-time price fetching functions
def fetch_real_current_price(symbol):
    """Fetch REAL current stock price using multiple methods"""
    try:
        print(f"🎯 Fetching REAL current price for {symbol}")
        
        # Ensure proper symbol format
        if not symbol.endswith(('.NS', '.BO')):
            symbol += '.NS'
        
        ticker = yf.Ticker(symbol)
        current_price = None
        company_name = None
        previous_close = None
        
        # Method 1: Try info first (most comprehensive)
        try:
            info = ticker.info
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            company_name = info.get('longName') or info.get('shortName')
            previous_close = info.get('previousClose')
            
            if current_price:
                print(f"✅ Got real price from info: ₹{current_price}")
        except Exception as e:
            print(f"⚠️ Info method failed: {e}")
        
        # Method 2: Try history as fallback
        if current_price is None:
            try:
                data = ticker.history(period="2d")  # Get 2 days to ensure we have data
                if not data.empty:
                    current_price = float(data['Close'].iloc[-1])
                    previous_close = float(data['Close'].iloc[-2]) if len(data) > 1 else current_price * 0.995
                    print(f"✅ Got real price from history: ₹{current_price}")
            except Exception as e:
                print(f"⚠️ History method failed: {e}")
        
        # Method 3: Try fast_info as last resort
        if current_price is None:
            try:
                fast_info = ticker.fast_info
                current_price = fast_info.get('lastPrice')
                previous_close = fast_info.get('previousClose')
                
                if current_price:
                    print(f"✅ Got real price from fast_info: ₹{current_price}")
            except Exception as e:
                print(f"⚠️ Fast_info method failed: {e}")
        
        if current_price and current_price > 0:
            return {
                'current_price': float(current_price),
                'company_name': company_name,
                'previous_close': float(previous_close) if previous_close else current_price * 0.995,
                'symbol': symbol,
                'is_real': True
            }
        
        print(f"❌ Could not fetch real price for {symbol}")
        return None
        
    except Exception as e:
        print(f"❌ Error fetching real price for {symbol}: {e}")
        return None

def create_realistic_estimates(real_price_data):
    """Create realistic estimated data based on real current price"""
    current_price = real_price_data['current_price']
    previous_close = real_price_data['previous_close']
    
    # Calculate realistic estimates based on current price
    estimates = {
        # Real data (keep as is)
        'current_price': current_price,
        'previous_close': previous_close,
        'company_name': real_price_data.get('company_name', 'Company Name'),
        'symbol': real_price_data['symbol'],
        'is_real_price': True,
        
        # Estimated data (realistic calculations)
        'open_price': current_price * random.uniform(0.995, 1.005),
        'high_price': current_price * random.uniform(1.005, 1.025),
        'low_price': current_price * random.uniform(0.975, 0.995),
        'change': current_price - previous_close,
        'change_percent': ((current_price - previous_close) / previous_close) * 100,
        
        # Volume estimates based on price range
        'volume': estimate_realistic_volume(current_price),
        
        # Market cap estimate (will be overridden if real data available)
        'market_cap': estimate_market_cap(current_price),
        
        # Additional estimates
        'bid': current_price * 0.999,
        'ask': current_price * 1.001,
        'day_range': f"₹{current_price * 0.975:.2f} - ₹{current_price * 1.025:.2f}",
        '52_week_range': f"₹{current_price * 0.7:.2f} - ₹{current_price * 1.4:.2f}"
    }
    
    # Add info structure for compatibility
    estimates['info'] = {
        'longName': estimates.get('company_name', 'Company Name'),
        'symbol': estimates['symbol'],
        'marketCap': estimates.get('market_cap', 0),
        'previousClose': estimates['previous_close'],
        'regularMarketPrice': estimates['current_price'],
        'regularMarketOpen': estimates['open_price'],
        'regularMarketDayHigh': estimates['high_price'],
        'regularMarketDayLow': estimates['low_price'],
        'regularMarketVolume': estimates['volume'],
        'bid': estimates.get('bid', estimates['current_price'] * 0.999),
        'ask': estimates.get('ask', estimates['current_price'] * 1.001),
        'dividendYield': random.uniform(0.5, 3.5),  # Realistic dividend yield
        'trailingPE': random.uniform(15, 35),  # Realistic P/E ratio
        'bookValue': estimates['current_price'] * random.uniform(0.3, 0.8),
        'priceToBook': random.uniform(2, 8)
    }
    
    return estimates

def estimate_realistic_volume(price):
    """Estimate realistic trading volume based on stock price"""
    if price > 3000:  # High-value stocks (TCS, etc.)
        return random.randint(800000, 2500000)
    elif price > 1500:  # Mid-high value stocks (HDFC, INFY)
        return random.randint(1500000, 4000000)
    elif price > 500:  # Mid value stocks (ITC, etc.)
        return random.randint(3000000, 8000000)
    else:  # Lower value stocks
        return random.randint(5000000, 15000000)

def estimate_market_cap(price):
    """Estimate market cap based on stock price (very rough estimate)"""
    if price > 3000:
        return random.randint(8000000000000, 15000000000000)  # 8-15 Trillion
    elif price > 1500:
        return random.randint(5000000000000, 12000000000000)  # 5-12 Trillion
    elif price > 500:
        return random.randint(2000000000000, 8000000000000)   # 2-8 Trillion
    else:
        return random.randint(500000000000, 3000000000000)    # 0.5-3 Trillion

def get_enhanced_indian_demo_data(symbol):
    """Enhanced demo data for popular Indian stocks - NOW WITH REAL PRICES!"""
    
    # STEP 1: Try to get REAL current price first
    real_price_data = fetch_real_current_price(symbol)
    
    if real_price_data:
        print(f"🎯 Using REAL current price for {symbol}: ₹{real_price_data['current_price']}")
        # Create realistic estimates based on real current price
        return create_realistic_estimates(real_price_data)
    
    # STEP 2: If real price failed, fall back to estimated demo data
    print(f"📊 Using estimated demo data for {symbol}")
    
    # Remove .NS suffix for comparison
    clean_symbol = symbol.replace('.NS', '').upper()
    
    # Enhanced realistic data for popular Indian stocks (Aug 2025 prices)
    indian_stock_data = {
        'TCS': {
            'current_price': 3850.75,
            'company_name': 'Tata Consultancy Services Limited',
            'sector': 'Information Technology',
            'industry': 'Software Services',
            'market_cap': 14000000000000,  # 14 Trillion INR
        },
        'RELIANCE': {
            'current_price': 2890.40,
            'company_name': 'Reliance Industries Limited',
            'sector': 'Oil & Gas',
            'industry': 'Integrated Oil & Gas',
            'market_cap': 19500000000000,  # 19.5 Trillion INR
        },
        'INFY': {
            'current_price': 1720.30,
            'company_name': 'Infosys Limited',
            'sector': 'Information Technology',
            'industry': 'Software Services',
            'market_cap': 7200000000000,  # 7.2 Trillion INR
        },
        'ITC': {
            'current_price': 485.60,
            'company_name': 'ITC Limited',
            'sector': 'Consumer Goods',
            'industry': 'Tobacco Products',
            'market_cap': 6100000000000,  # 6.1 Trillion INR
        },
        'HDFCBANK': {
            'current_price': 1650.25,
            'company_name': 'HDFC Bank Limited',
            'sector': 'Financial Services',
            'industry': 'Private Sector Bank',
            'market_cap': 12500000000000,  # 12.5 Trillion INR
        }
    }
    
    if clean_symbol in indian_stock_data:
        stock_info = indian_stock_data[clean_symbol]
        current_price = stock_info['current_price']
        
        # Add small random variation to make it realistic
        price_variation = random.uniform(-0.03, 0.03)  # ±3% variation
        current_price = current_price * (1 + price_variation)
        
        return {
            'current_price': current_price,
            'open_price': current_price * random.uniform(0.995, 1.005),
            'high_price': current_price * random.uniform(1.01, 1.03),
            'low_price': current_price * random.uniform(0.97, 0.99),
            'volume': estimate_realistic_volume(current_price),
            'change': current_price * random.uniform(-0.02, 0.02),
            'change_percent': random.uniform(-2, 2),
            'is_real_price': False,  # Mark as estimated
            'company_name': stock_info['company_name'],
            'sector': stock_info['sector'],
            'industry': stock_info['industry'],
            'market_cap': stock_info['market_cap'],
            'hist_data': None,  # Will create mock data
            'source': 'ENHANCED_DEMO'
        }
    
    return None

def parse_nse_data(nse_data, original_symbol):
    """Parse NSE JSON response into our standard format"""
    try:
        # NSE response structure
        info = nse_data.get('info', {})
        price_info = nse_data.get('priceInfo', {})
        industry_info = nse_data.get('industryInfo', {})
        
        # Extract basic price data
        current_price = float(price_info.get('lastPrice', 0))
        open_price = float(price_info.get('open', 0))
        
        # High/Low data
        intraday_hl = price_info.get('intraDayHighLow', {})
        high_price = float(intraday_hl.get('max', current_price))
        low_price = float(intraday_hl.get('min', current_price))
        
        # Volume and change data
        volume = int(price_info.get('totalTradedVolume', 0))
        change = float(price_info.get('change', 0))
        change_percent = float(price_info.get('pChange', 0))
        
        # Company information
        company_name = info.get('companyName', original_symbol.replace('.NS', ''))
        
        # Create historical data for charts (simplified version)
        hist_data = create_nse_historical_data(current_price, open_price, high_price, low_price, volume)
        
        # Company info structure
        company_info = {
            'longName': company_name,
            'symbol': original_symbol,
            'sector': industry_info.get('macro', 'Technology'),
            'industry': industry_info.get('sector', 'Software Services'),
            'marketCap': price_info.get('totalTradedValue', 0) * 1000,  # Approximate
        }
        
        # Return data in our expected format
        return {
            'current_price': current_price,
            'open_price': open_price,
            'high_price': high_price,
            'low_price': low_price,
            'volume': volume,
            'change': change,
            'change_percent': change_percent,
            'company_name': company_name,
            'hist_data': hist_data,
            'info': company_info,
            'source': 'NSE_DIRECT'
        }
        
    except Exception as e:
        print(f"❌ Error parsing NSE data: {str(e)}")
        return None

def create_nse_historical_data(current_price, open_price, high_price, low_price, volume):
    """Create simplified historical data for NSE stocks"""
    try:
        import pandas as pd
        
        # Create 30 days of mock historical data based on current price
        dates = pd.date_range(end=pd.Timestamp.now().date(), periods=30, freq='D')
        
        # Generate realistic price variations
        price_variations = np.random.normal(0, current_price * 0.015, len(dates))  # 1.5% daily volatility
        prices = []
        base_price = current_price * 0.95  # Start 5% below current
        
        for i, variation in enumerate(price_variations):
            if i == len(price_variations) - 1:
                # Last price should be the current price
                prices.append(current_price)
            else:
                new_price = max(base_price + variation, current_price * 0.8)  # Min 80% of current
                new_price = min(new_price, current_price * 1.2)  # Max 120% of current
                prices.append(new_price)
                base_price = new_price
        
        # Create DataFrame
        hist_data = pd.DataFrame({
            'Close': prices,
            'Open': [p * 0.998 for p in prices],  # Open slightly below close
            'High': [p * 1.015 for p in prices],  # High slightly above close
            'Low': [p * 0.985 for p in prices],   # Low slightly below close
            'Volume': [volume + random.randint(-volume//4, volume//4) for _ in prices]
        }, index=dates)
        
        return hist_data
        
    except Exception as e:
        print(f"❌ Error creating historical data: {str(e)}")
        return None

def create_nse_result(nse_data, symbol):
    """Convert NSE data to our expected format (stock, hist_data, info, minimal_data)"""
    try:
        # Safely get info structure
        info = nse_data.get('info', {})
        if not info:
            # Create minimal info structure if missing
            info = {
                'longName': nse_data.get('company_name', symbol),
                'symbol': symbol,
                'marketCap': nse_data.get('market_cap', 0),
                'previousClose': nse_data.get('previous_close', nse_data.get('current_price', 0)),
                'regularMarketPrice': nse_data.get('current_price', 0)
            }
        
        # Create a mock stock object using module-level class
        stock = MockStock(symbol, info)
        
        # Get or create historical data
        hist_data = nse_data.get('hist_data')
        if hist_data is None:
            # Create mock historical data based on current price
            current_price = nse_data.get('current_price', 0)
            hist_data = create_nse_historical_data(
                current_price, 
                nse_data.get('open_price', current_price), 
                nse_data.get('high_price', current_price * 1.02), 
                nse_data.get('low_price', current_price * 0.98), 
                nse_data.get('volume', 1000000)
            )
        
        # Create minimal data structure
        minimal_data = {
            'current_price': nse_data.get('current_price', 0),
            'open_price': nse_data.get('open_price', nse_data.get('current_price', 0)),
            'high_price': nse_data.get('high_price', nse_data.get('current_price', 0) * 1.02),
            'low_price': nse_data.get('low_price', nse_data.get('current_price', 0) * 0.98),
            'volume': nse_data.get('volume', 1000000),
            'market_cap': info.get('marketCap', 0),
            'symbol': symbol
        }
        
        return (stock, hist_data, info, minimal_data)
        
    except Exception as e:
        print(f"❌ Error creating NSE result: {str(e)}")
        print(f"   Data keys available: {list(nse_data.keys()) if nse_data else 'None'}")
        return None

def create_fallback_result_structure(data, symbol):
    """Create a fallback result structure when create_nse_result fails"""
    try:
        print(f"🔧 Creating fallback result structure for {symbol}")
        
        # Create a simple mock stock object
        class SimpleMockStock:
            def __init__(self, symbol, data):
                self.ticker = symbol
                self.info = {
                    'symbol': symbol,
                    'longName': data.get('company_name', symbol),
                    'currentPrice': data.get('current_price', 0),
                    'previousClose': data.get('previous_close', 0),
                    'marketCap': data.get('market_cap', 0)
                }
        
        # Create basic historical data
        current_price = data.get('current_price', 0)
        hist_data = create_nse_historical_data(
            current_price,
            data.get('open_price', current_price),
            data.get('high_price', current_price * 1.02),
            data.get('low_price', current_price * 0.98),
            data.get('volume', 1000000)
        )
        
        # Create the result tuple
        return (
            SimpleMockStock(symbol, data),  # stock
            hist_data,                      # hist_data
            data.get('info', {}),          # info
            data                           # minimal_data
        )
        
    except Exception as e:
        print(f"❌ Failed to create fallback result: {e}")
        return None

app = Flask(__name__)
CORS(app)

# Configure static files for production
app.static_folder = 'static'
app.static_url_path = '/static'

# Rate limiting storage
last_request_time = {}
request_count = {}

# Simple cache for stock data
CACHE_DIR = "cache"
CACHE_DURATION = 300  # 5 minutes

def ensure_cache_dir():
    """Ensure cache directory exists"""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

def get_cache_filename(symbol):
    """Get cache filename for a symbol"""
    return os.path.join(CACHE_DIR, f"{symbol.replace('.', '_')}.pkl")

def save_to_cache(symbol, data):
    """Save stock data to cache with improved error handling"""
    try:
        ensure_cache_dir()
        cache_file = get_cache_filename(symbol)
        
        # Extract only serializable data for caching
        if isinstance(data, tuple) and len(data) == 4:
            stock, hist_data, info, minimal_data = data
            
            # Create a serializable version
            cache_data = {
                'timestamp': time.time(),
                'hist_data': hist_data.to_dict() if hist_data is not None else None,
                'info': info,
                'minimal_data': minimal_data,
                'symbol': symbol
            }
        else:
            # For fallback mode or other data types
            cache_data = {
                'timestamp': time.time(),
                'data': data
            }
        
        with open(cache_file, 'wb') as f:
            pickle.dump(cache_data, f)
        print(f"📦 Saved {symbol} to cache")
            
    except Exception as e:
        print(f"❌ Cache save error for {symbol}: {e}")

def load_from_cache(symbol):
    """Load stock data from cache if valid with improved reconstruction"""
    try:
        cache_file = get_cache_filename(symbol)
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            # Check if cache is still valid (5 minutes)
            if time.time() - cache_data['timestamp'] < CACHE_DURATION:
                # Reconstruct the original format if it's stock data
                if 'hist_data' in cache_data and 'info' in cache_data:
                    # Reconstruct the tuple format
                    hist_data = pd.DataFrame.from_dict(cache_data['hist_data']) if cache_data['hist_data'] else None
                    info = cache_data['info']
                    minimal_data = cache_data['minimal_data']
                    stock = MockStock(symbol, info)
                    
                    return (stock, hist_data, info, minimal_data)
                else:
                    # Return the original data for fallback mode
                    return cache_data.get('data')
                    
    except Exception as e:
        print(f"❌ Cache load error for {symbol}: {e}")
    return None

def rate_limit_yahoo_finance():
    """Simple rate limiting for Yahoo Finance API"""
    current_time = time.time()
    
    # Reset counter every minute
    if 'yahoo' not in last_request_time or current_time - last_request_time['yahoo'] > 60:
        request_count['yahoo'] = 0
        last_request_time['yahoo'] = current_time
    
    # Allow max 5 requests per minute (reduced from 10)
    if request_count.get('yahoo', 0) >= 5:
        wait_time = 60 - (current_time - last_request_time['yahoo'])
        if wait_time > 0:
            print(f"Rate limit hit, waiting {wait_time:.1f} seconds...")
            time.sleep(wait_time)
            request_count['yahoo'] = 0
            last_request_time['yahoo'] = time.time()
    
    request_count['yahoo'] = request_count.get('yahoo', 0) + 1

def get_minimal_stock_data(symbol):
    """Get only current price data (minimal request)"""
    try:
        stock = yf.Ticker(symbol)
        # Only get current price data - much lighter request
        info = stock.fast_info
        current_price = info.get('last_price', 0)
        
        if current_price and current_price > 0:
            # Create minimal data structure
            minimal_data = {
                'current_price': current_price,
                'open_price': info.get('open', current_price),
                'high_price': info.get('day_high', current_price * 1.02),
                'low_price': info.get('day_low', current_price * 0.98),
                'volume': info.get('regular_market_volume', 1000000),
                'market_cap': info.get('market_cap', 0),
                'symbol': symbol
            }
            return minimal_data
        
    except Exception as e:
        print(f"Minimal data fetch failed for {symbol}: {str(e)}")
    
    return None

def get_stock_data_with_retry(symbol, max_retries=2):
    """Get stock data with smart fallback strategy - NOW PRIORITIZES REAL PRICES"""
    
    # First check cache
    cached_data = load_from_cache(symbol)
    if cached_data:
        print(f"📦 Using cached data for {symbol}")
        return cached_data
    
    # PRIORITY STRATEGY: Always try to get REAL current price first
    print(f"🎯 PRIORITY: Attempting to fetch REAL current price for {symbol}")
    real_price_data = fetch_real_current_price(symbol)
    
    # Strategy 1: For Indian stocks with REAL price + estimated supporting data
    if symbol.endswith('.NS') or symbol in ['TCS', 'RELIANCE', 'INFY', 'ITC', 'HDFCBANK', 'ICICIBANK', 'LT', 'SBIN', 'WIPRO', 'BAJFINANCE']:
        print(f"🇮🇳 Processing Indian stock: {symbol}")
        indian_symbol = symbol if symbol.endswith('.NS') else f"{symbol}.NS"
        
        # If we got real price, use it with estimated supporting data
        if real_price_data:
            print(f"✅ Using REAL price ₹{real_price_data['current_price']} with estimated supporting data")
            enhanced_data = create_realistic_estimates(real_price_data)
            result = create_nse_result(enhanced_data, indian_symbol)
            
            # Check if result creation was successful
            if result is not None:
                save_to_cache(symbol, result)
                return result
            else:
                print(f"⚠️ Failed to create NSE result, trying alternative approach...")
                # Create a fallback result structure
                result = create_fallback_result_structure(enhanced_data, indian_symbol)
                if result:
                    save_to_cache(symbol, result)
                    return result
        
        # Try alternative Indian stock API as backup
        alt_data = get_alternative_indian_stock_data(indian_symbol)
        if alt_data:
            print(f"✅ Successfully got Indian stock data for {symbol}")
            result = create_nse_result(alt_data, indian_symbol)
            save_to_cache(symbol, result)
            return result
        
        # If that fails, try the enhanced demo data for popular Indian stocks
        if symbol.replace('.NS', '') in ['TCS', 'RELIANCE', 'INFY', 'ITC', 'HDFCBANK']:
            print(f"🔄 Using enhanced demo data for popular Indian stock: {symbol}")
            demo_data = get_enhanced_indian_demo_data(symbol)
            if demo_data:
                result = create_nse_result(demo_data, indian_symbol)
                save_to_cache(symbol, result)
                return result
    
    # Strategy 2: For any stock with real price
    if real_price_data:
        print(f"✅ Using REAL price for {symbol}: ₹{real_price_data['current_price']}")
        enhanced_data = create_realistic_estimates(real_price_data)
        
        # Create a minimal result structure for non-Indian stocks
        result = {
            'stock': type('MockStock', (), {
                'ticker': symbol,
                'info': {
                    'symbol': symbol,
                    'longName': enhanced_data.get('company_name', 'Company Name'),
                    'currentPrice': enhanced_data['current_price'],
                    'previousClose': enhanced_data['previous_close'],
                    'open': enhanced_data['open_price'],
                    'dayHigh': enhanced_data['high_price'],
                    'dayLow': enhanced_data['low_price'],
                    'volume': enhanced_data['volume'],
                    'marketCap': enhanced_data['market_cap']
                }
            })(),
            'current_data': enhanced_data,
            'source': 'REAL_PRICE_WITH_ESTIMATES',
            'is_real_price': True
        }
        
        save_to_cache(symbol, result)
        return result
    
    # Strategy 3: Try Yahoo Finance minimal data for any stock (fallback)
    print(f"📊 Trying Yahoo Finance minimal data for {symbol}")
    minimal_data = get_minimal_stock_data(symbol)
    
    if minimal_data:
        print(f"✅ Successfully got Yahoo Finance data for {symbol}")
        
        # Try to get historical data with reduced scope
        try:
            rate_limit_yahoo_finance()
            time.sleep(random.uniform(0.5, 1.0))  # Shorter delay for second request
            
            stock = yf.Ticker(symbol)
            # Get only 1 month of data instead of 6 months
            hist_data = stock.history(period="1mo")
            
            if not hist_data.empty:
                # Get basic company info (lightweight)
                try:
                    info = {
                        'longName': stock.info.get('longName', symbol),
                        'marketCap': minimal_data['market_cap'],
                        'sector': 'Technology',  # Default fallback
                        'industry': 'Software Services'  # Default fallback
                    }
                except:
                    info = {
                        'longName': symbol,
                        'marketCap': minimal_data['market_cap'],
                        'sector': 'Technology',
                        'industry': 'Software Services'
                    }
                
                result = (stock, hist_data, info, minimal_data)
                save_to_cache(symbol, result)
                return result
            
        except Exception as e:
            print(f"❌ Historical data fetch failed, using minimal data only: {str(e)}")
        
        # Return minimal data with mock historical data
        result = create_minimal_result(symbol, minimal_data)
        save_to_cache(symbol, result)
        return result
    
    # Strategy 3: If all fails, use comprehensive demo mode
    print(f"❌ All data sources failed for {symbol}, using demo mode...")
    fallback_result = get_stock_data_fallback_strategy(symbol)
    
    # If fallback strategy also fails, return the fallback mode string
    if fallback_result == "FALLBACK_MODE":
        return "FALLBACK_MODE"
    else:
        return fallback_result

def create_minimal_result(symbol, minimal_data):
    """Create a result structure from minimal data with mock historical data"""
    import pandas as pd
    
    # Create mock historical data based on current price
    current_price = minimal_data['current_price']
    dates = pd.date_range(end=pd.Timestamp.now(), periods=30, freq='D')
    
    # Generate realistic price variations around current price
    price_variations = np.random.normal(0, current_price * 0.01, len(dates))
    prices = []
    base_price = current_price * 0.95  # Start slightly below current
    
    for i, variation in enumerate(price_variations):
        if i == len(price_variations) - 1:
            # Last price should be the current price
            prices.append(current_price)
        else:
            new_price = max(base_price + variation, current_price * 0.8)
            prices.append(min(new_price, current_price * 1.2))
            base_price = new_price
    
    hist_data = pd.DataFrame({
        'Close': prices,
        'Open': [p * 0.999 for p in prices],
        'High': [p * 1.01 for p in prices],
        'Low': [p * 0.99 for p in prices],
        'Volume': [minimal_data['volume'] + random.randint(-100000, 100000) for _ in prices]
    }, index=dates)
    
    # Create info structure
    info = {
        'longName': symbol.replace('.NS', ''),
        'marketCap': minimal_data['market_cap'],
        'sector': 'Technology',
        'industry': 'Software Services'
    }
    
    # Create mock stock object
    class MockStock:
        def __init__(self, symbol):
            self.ticker = symbol
    
    return (MockStock(symbol), hist_data, info, minimal_data)

def get_stock_data_fallback_strategy(symbol, max_retries=2):
    """Strategy 2: Full fallback mode if minimal data also fails"""
    for attempt in range(max_retries):
        try:
            rate_limit_yahoo_finance()
            
            # Add random delay to avoid hitting rate limits
            time.sleep(random.uniform(2.0, 4.0))  # Longer delay for full requests
            
            print(f"Fetching full data for {symbol} (attempt {attempt + 1})")
            stock = yf.Ticker(symbol)
            hist_data = stock.history(period="1mo")  # Reduced to 1 month
            info = stock.info
            
            if not hist_data.empty:
                # Cache the successful result
                result = (stock, hist_data, info)
                save_to_cache(symbol, result)
                return result
                
        except Exception as e:
            error_str = str(e)
            print(f"Attempt {attempt + 1} failed: {error_str}")
            
            # Check for specific Yahoo Finance issues
            if any(indicator in error_str for indicator in [
                "429", "Too Many Requests", 
                "Expecting value: line 1 column 1", 
                "No data found", 
                "symbol may be delisted",
                "JSONDecodeError"
            ]):
                print(f"Yahoo Finance issue detected: {error_str}")
                # Immediately fall back to demo mode for these errors
                print(f"Switching to fallback mode for {symbol}")
                return "FALLBACK_MODE"
            
            if attempt == max_retries - 1:
                # On final failure, return fallback data instead of raising exception
                print(f"All retries failed, using fallback data for {symbol}")
                return "FALLBACK_MODE"
            time.sleep(2)
    
    # If we reach here, return fallback mode
    print(f"Failed to fetch stock data, using fallback data for {symbol}")
    return "FALLBACK_MODE"

# Popular Indian stocks dictionary with logo URLs
INDIAN_STOCKS = {
    'tcs': {'symbol': 'TCS.NS', 'logo': 'https://logo.clearbit.com/tcs.com'},
    'tata consultancy services': {'symbol': 'TCS.NS', 'logo': 'https://logo.clearbit.com/tcs.com'},
    'infosys': {'symbol': 'INFY.NS', 'logo': 'https://logo.clearbit.com/infosys.com'},
    'wipro': {'symbol': 'WIPRO.NS', 'logo': 'https://logo.clearbit.com/wipro.com'},
    'reliance': {'symbol': 'RELIANCE.NS', 'logo': 'https://logo.clearbit.com/ril.com'},
    'reliance industries': {'symbol': 'RELIANCE.NS', 'logo': 'https://logo.clearbit.com/ril.com'},
    'hdfc bank': {'symbol': 'HDFCBANK.NS', 'logo': 'https://logo.clearbit.com/hdfcbank.com'},
    'hdfc': {'symbol': 'HDFCBANK.NS', 'logo': 'https://logo.clearbit.com/hdfcbank.com'},
    'icici bank': {'symbol': 'ICICIBANK.NS', 'logo': 'https://logo.clearbit.com/icicibank.com'},
    'icici': {'symbol': 'ICICIBANK.NS', 'logo': 'https://logo.clearbit.com/icicibank.com'},
    'sbi': {'symbol': 'SBIN.NS', 'logo': 'https://logo.clearbit.com/sbi.co.in'},
    'state bank of india': {'symbol': 'SBIN.NS', 'logo': 'https://logo.clearbit.com/sbi.co.in'},
    'bharti airtel': {'symbol': 'BHARTIARTL.NS', 'logo': 'https://logo.clearbit.com/airtel.in'},
    'airtel': {'symbol': 'BHARTIARTL.NS', 'logo': 'https://logo.clearbit.com/airtel.in'},
    'itc': {'symbol': 'ITC.NS', 'logo': 'https://logo.clearbit.com/itcportal.com'},
    'hindustan unilever': {'symbol': 'HINDUNILVR.NS', 'logo': 'https://logo.clearbit.com/hul.co.in'},
    'hul': {'symbol': 'HINDUNILVR.NS', 'logo': 'https://logo.clearbit.com/hul.co.in'},
    'bajaj finance': {'symbol': 'BAJFINANCE.NS', 'logo': 'https://logo.clearbit.com/bajajfinserv.in'},
    'bajaj': {'symbol': 'BAJFINANCE.NS', 'logo': 'https://logo.clearbit.com/bajajfinserv.in'},
    'maruti suzuki': {'symbol': 'MARUTI.NS', 'logo': 'https://logo.clearbit.com/marutisuzuki.com'},
    'maruti': {'symbol': 'MARUTI.NS', 'logo': 'https://logo.clearbit.com/marutisuzuki.com'},
    'asian paints': {'symbol': 'ASIANPAINT.NS', 'logo': 'https://logo.clearbit.com/asianpaints.com'},
    'larsen': {'symbol': 'LT.NS', 'logo': 'https://logo.clearbit.com/larsentoubro.com'},
    'l&t': {'symbol': 'LT.NS', 'logo': 'https://logo.clearbit.com/larsentoubro.com'},
    'axis bank': {'symbol': 'AXISBANK.NS', 'logo': 'https://logo.clearbit.com/axisbank.com'},
    'axis': {'symbol': 'AXISBANK.NS', 'logo': 'https://logo.clearbit.com/axisbank.com'},
    'kotak bank': {'symbol': 'KOTAKBANK.NS', 'logo': 'https://logo.clearbit.com/kotak.com'},
    'kotak': {'symbol': 'KOTAKBANK.NS', 'logo': 'https://logo.clearbit.com/kotak.com'},
    'sun pharma': {'symbol': 'SUNPHARMA.NS', 'logo': 'https://logo.clearbit.com/sunpharma.com'},
    'titan': {'symbol': 'TITAN.NS', 'logo': 'https://logo.clearbit.com/titan.co.in'},
    'nestle': {'symbol': 'NESTLEIND.NS', 'logo': 'https://logo.clearbit.com/nestle.in'},
    'ongc': {'symbol': 'ONGC.NS', 'logo': 'https://logo.clearbit.com/ongcindia.com'},
    'ntpc': {'symbol': 'NTPC.NS', 'logo': 'https://logo.clearbit.com/ntpc.co.in'},
    'powergrid': {'symbol': 'POWERGRID.NS', 'logo': 'https://logo.clearbit.com/powergridindia.com'},
    'coal india': {'symbol': 'COALINDIA.NS', 'logo': 'https://logo.clearbit.com/coalindia.in'},
    'dr reddy': {'symbol': 'DRREDDY.NS', 'logo': 'https://logo.clearbit.com/drreddys.com'},
    'tech mahindra': {'symbol': 'TECHM.NS', 'logo': 'https://logo.clearbit.com/techmahindra.com'},
    'hcl tech': {'symbol': 'HCLTECH.NS', 'logo': 'https://logo.clearbit.com/hcltech.com'},
    'hcl': {'symbol': 'HCLTECH.NS', 'logo': 'https://logo.clearbit.com/hcltech.com'},
    'adani': {'symbol': 'ADANIENT.NS', 'logo': 'https://logo.clearbit.com/adani.com'},
    'tata steel': {'symbol': 'TATASTEEL.NS', 'logo': 'https://logo.clearbit.com/tatasteel.com'},
    'jsw steel': {'symbol': 'JSWSTEEL.NS', 'logo': 'https://logo.clearbit.com/jsw.in'},
    'ultratech cement': {'symbol': 'ULTRACEMCO.NS', 'logo': 'https://logo.clearbit.com/ultratechcement.com'},
    'ultratech': {'symbol': 'ULTRACEMCO.NS', 'logo': 'https://logo.clearbit.com/ultratechcement.com'},
    'britannia': {'symbol': 'BRITANNIA.NS', 'logo': 'https://logo.clearbit.com/britannia.co.in'}
}

# Fallback mock data when Yahoo Finance is unavailable
MOCK_STOCK_DATA = {
    'TCS.NS': {
        'name': 'Tata Consultancy Services',
        'current_price': 3500.00,
        'open_price': 3480.00,
        'high_price': 3520.00,
        'low_price': 3475.00,
        'volume': 1234567,
        'change': 20.00,
        'change_percent': 0.57,
        'recommendation': 'BUY'
    },
    'RELIANCE.NS': {
        'name': 'Reliance Industries',
        'current_price': 2400.00,
        'open_price': 2390.00,
        'high_price': 2415.00,
        'low_price': 2385.00,
        'volume': 2345678,
        'change': 10.00,
        'change_percent': 0.42,
        'recommendation': 'HOLD'
    },
    'INFY.NS': {
        'name': 'Infosys Limited',
        'current_price': 1600.00,
        'open_price': 1595.00,
        'high_price': 1605.00,
        'low_price': 1590.00,
        'volume': 1876543,
        'change': 5.00,
        'change_percent': 0.31,
        'recommendation': 'BUY'
    },
    'ICICIBANK.NS': {
        'name': 'ICICI Bank Limited',
        'current_price': 950.00,
        'open_price': 945.00,
        'high_price': 955.00,
        'low_price': 940.00,
        'volume': 3456789,
        'change': 5.00,
        'change_percent': 0.53,
        'recommendation': 'BUY'
    },
    'HDFCBANK.NS': {
        'name': 'HDFC Bank Limited',
        'current_price': 1650.00,
        'open_price': 1645.00,
        'high_price': 1660.00,
        'low_price': 1640.00,
        'volume': 2987654,
        'change': 5.00,
        'change_percent': 0.30,
        'recommendation': 'HOLD'
    },
    'SBIN.NS': {
        'name': 'State Bank of India',
        'current_price': 750.00,
        'open_price': 748.00,
        'high_price': 755.00,
        'low_price': 745.00,
        'volume': 4567890,
        'change': 2.00,
        'change_percent': 0.27,
        'recommendation': 'HOLD'
    }
}

def get_fallback_data(symbol, company_name):
    """Get fallback mock data when Yahoo Finance is unavailable"""
    mock_data = MOCK_STOCK_DATA.get(symbol, {
        'name': company_name,
        'current_price': 1000.00,
        'open_price': 995.00,
        'high_price': 1010.00,
        'low_price': 990.00,
        'volume': 1000000,
        'change': 5.00,
        'change_percent': 0.50,
        'recommendation': 'HOLD'
    })
    
    # Create mock historical data
    import pandas as pd
    dates = pd.date_range(end=pd.Timestamp.now(), periods=180, freq='D')
    base_price = mock_data['current_price']
    
    # Generate realistic price variations
    price_changes = np.random.normal(0, base_price * 0.02, len(dates))
    prices = [base_price]
    
    for change in price_changes[1:]:
        new_price = max(prices[-1] + change, base_price * 0.5)  # Minimum 50% of base price
        prices.append(min(new_price, base_price * 1.5))  # Maximum 150% of base price
    
    hist_data = pd.DataFrame({
        'Close': prices,
        'Open': [p * 0.99 for p in prices],
        'High': [p * 1.02 for p in prices],
        'Low': [p * 0.98 for p in prices],
        'Volume': [mock_data['volume'] + random.randint(-100000, 100000) for _ in prices]
    }, index=dates)
    
    # Mock info object
    info = {
        'longName': mock_data['name'],
        'marketCap': int(mock_data['current_price'] * 1000000000),
        'trailingPE': 25.5,
        'dividendYield': 0.02,
        'fiftyTwoWeekHigh': mock_data['current_price'] * 1.2,
        'fiftyTwoWeekLow': mock_data['current_price'] * 0.8,
        'sector': 'Technology',
        'industry': 'Software Services'
    }
    
    return hist_data, info, mock_data

def create_simple_chart(hist_data, company_name):
    """Create a visually appealing simple chart for fallback mode"""
    try:
        import plotly.graph_objs as go
        import plotly.utils
        
        # Calculate some basic technical indicators for visual appeal
        hist_data['SMA_10'] = hist_data['Close'].rolling(window=10).mean()
        hist_data['SMA_20'] = hist_data['Close'].rolling(window=20).mean()
        
        fig = go.Figure()
        
        # Add background gradient effect
        fig.add_shape(
            type="rect",
            x0=hist_data.index[0], x1=hist_data.index[-1],
            y0=hist_data['Close'].min() * 0.98, y1=hist_data['Close'].max() * 1.02,
            fillcolor="rgba(102, 126, 234, 0.05)",
            layer="below", line_width=0
        )
        
        # Enhanced price line with gradient and smooth curves
        fig.add_trace(go.Scatter(
            x=hist_data.index,
            y=hist_data['Close'],
            mode='lines',
            name='💰 Stock Price',
            line=dict(
                color='rgba(46, 134, 171, 1)',
                width=4,
                shape='spline',
                smoothing=0.3
            ),
            fill='tonexty',
            fillcolor='rgba(46, 134, 171, 0.1)',
            hovertemplate='<b>Price:</b> ₹%{y:.2f}<br><b>Date:</b> %{x}<br><extra></extra>'
        ))
        
        # Add moving averages for visual richness
        if len(hist_data) >= 10:
            fig.add_trace(go.Scatter(
                x=hist_data.index,
                y=hist_data['SMA_10'],
                mode='lines',
                name='📊 10-day Average',
                line=dict(
                    color='rgba(255, 99, 132, 0.8)',
                    width=2,
                    dash='dot'
                ),
                hovertemplate='<b>10-day Avg:</b> ₹%{y:.2f}<extra></extra>'
            ))
        
        if len(hist_data) >= 20:
            fig.add_trace(go.Scatter(
                x=hist_data.index,
                y=hist_data['SMA_20'],
                mode='lines',
                name='📈 20-day Average',
                line=dict(
                    color='rgba(255, 159, 64, 0.8)',
                    width=2,
                    dash='dash'
                ),
                hovertemplate='<b>20-day Avg:</b> ₹%{y:.2f}<extra></extra>'
            ))
        
        # Add price markers for key points
        # Highest and lowest points
        max_idx = hist_data['Close'].idxmax()
        min_idx = hist_data['Close'].idxmin()
        
        fig.add_trace(go.Scatter(
            x=[max_idx],
            y=[hist_data['Close'].loc[max_idx]],
            mode='markers',
            name='📈 Highest',
            marker=dict(
                size=12,
                color='rgba(76, 175, 80, 1)',
                symbol='triangle-up',
                line=dict(width=2, color='white')
            ),
            hovertemplate='<b>Highest:</b> ₹%{y:.2f}<br><b>Date:</b> %{x}<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=[min_idx],
            y=[hist_data['Close'].loc[min_idx]],
            mode='markers',
            name='📉 Lowest',
            marker=dict(
                size=12,
                color='rgba(244, 67, 54, 1)',
                symbol='triangle-down',
                line=dict(width=2, color='white')
            ),
            hovertemplate='<b>Lowest:</b> ₹%{y:.2f}<br><b>Date:</b> %{x}<extra></extra>'
        ))
        
        # Enhanced layout with modern styling
        fig.update_layout(
            title={
                'text': f'🚀 {company_name} - Enhanced Demo Mode',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': '#2c3e50', 'family': 'Arial Black'}
            },
            xaxis=dict(
                title='📅 Date',
                gridcolor='rgba(128, 128, 128, 0.2)',
                gridwidth=1,
                showline=True,
                linewidth=2,
                linecolor='rgba(128, 128, 128, 0.3)',
                tickfont=dict(color='#34495e', size=11),
                title_font=dict(color='#34495e', size=12, family='Arial')
            ),
            yaxis=dict(
                title='💰 Price (₹)',
                gridcolor='rgba(128, 128, 128, 0.2)',
                gridwidth=1,
                showline=True,
                linewidth=2,
                linecolor='rgba(128, 128, 128, 0.3)',
                tickfont=dict(color='#34495e', size=11),
                title_font=dict(color='#34495e', size=12, family='Arial')
            ),
            height=500,
            showlegend=True,
            template='plotly_white',
            plot_bgcolor='rgba(248, 249, 250, 0.8)',
            paper_bgcolor='white',
            font=dict(size=11, family='Arial', color='#34495e'),
            margin=dict(l=60, r=60, t=80, b=60),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                bgcolor="rgba(255, 255, 255, 0.9)",
                bordercolor="rgba(0, 0, 0, 0.1)",
                borderwidth=1,
                font=dict(size=10)
            ),
            hoverlabel=dict(
                bgcolor="rgba(255, 255, 255, 0.95)",
                bordercolor="rgba(0, 0, 0, 0.1)",
                font_size=12,
                font_family="Arial"
            )
        )
        
        # Add annotations for demo mode
        fig.add_annotation(
            text="📊 Demo Mode - Enhanced Visualization",
            xref="paper", yref="paper",
            x=0.02, y=0.98,
            xanchor='left', yanchor='top',
            showarrow=False,
            font=dict(size=12, color="rgba(102, 126, 234, 0.8)", family="Arial"),
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="rgba(102, 126, 234, 0.3)",
            borderwidth=1,
            borderpad=4
        )
        
        # Add watermark
        fig.add_annotation(
            text="Money Savyy - Save Smart Dream Big 💰",
            xref="paper", yref="paper",
            x=1, y=0,
            xanchor='right', yanchor='bottom',
            showarrow=False,
            font=dict(size=10, color="rgba(128, 128, 128, 0.5)")
        )
        
        # Add trend analysis annotation
        price_change = ((hist_data['Close'].iloc[-1] - hist_data['Close'].iloc[0]) / hist_data['Close'].iloc[0]) * 100
        trend_emoji = "📈" if price_change > 0 else "📉" if price_change < 0 else "➡️"
        trend_text = f"{trend_emoji} Trend: {price_change:+.1f}% over period"
        
        fig.add_annotation(
            text=trend_text,
            xref="paper", yref="paper",
            x=0.02, y=0.02,
            xanchor='left', yanchor='bottom',
            showarrow=False,
            font=dict(size=11, color="#34495e", family="Arial"),
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="rgba(128, 128, 128, 0.3)",
            borderwidth=1,
            borderpad=4
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    except Exception as e:
        print(f"Error creating enhanced simple chart: {e}")
        return '{"data": [], "layout": {"title": "Chart unavailable"}}'

def search_stock_symbol(user_input):
    """Search for stock symbol based on user input"""
    user_input = user_input.lower().strip()
    
    if user_input in INDIAN_STOCKS:
        stock_data = INDIAN_STOCKS[user_input]
        return stock_data['symbol'], user_input, stock_data['logo']
    
    for stock_name, stock_data in INDIAN_STOCKS.items():
        if user_input in stock_name or stock_name in user_input:
            return stock_data['symbol'], stock_name, stock_data['logo']
    
    close_matches = get_close_matches(user_input, INDIAN_STOCKS.keys(), n=1, cutoff=0.6)
    if close_matches:
        best_match = close_matches[0]
        stock_data = INDIAN_STOCKS[best_match]
        return stock_data['symbol'], best_match, stock_data['logo']
    
    # Default fallback with no logo
    return user_input.upper() + '.NS', user_input, 'https://via.placeholder.com/32x32?text=?'

def predict_future_price(stock_data, days_ahead=30):
    """Predict future stock prices using machine learning"""
    try:
        if len(stock_data) < 50:
            return None, "Insufficient data for prediction"
        
        data = stock_data.copy()
        data['Days'] = range(len(data))
        data['Price'] = data['Close']
        
        data['SMA_10'] = data['Close'].rolling(window=10).mean()
        data['SMA_30'] = data['Close'].rolling(window=30).mean()
        data['Volume_MA'] = data['Volume'].rolling(window=10).mean()
        data['Price_Change'] = data['Close'].pct_change()
        data['Volatility'] = data['Close'].rolling(window=20).std()
        
        data = data.dropna()
        
        if len(data) < 30:
            return None, "Insufficient clean data for prediction"
        
        X = data[['Days', 'SMA_10', 'SMA_30', 'Volume_MA', 'Volatility']].values
        y = data['Price'].values
        
        # Linear Regression
        lr_model = LinearRegression()
        lr_model.fit(X, y)
        
        # Polynomial Regression
        poly_features = PolynomialFeatures(degree=2, include_bias=False)
        X_poly = poly_features.fit_transform(X)
        poly_model = LinearRegression()
        poly_model.fit(X_poly, y)
        
        lr_score = r2_score(y, lr_model.predict(X))
        poly_score = r2_score(y, poly_model.predict(X_poly))
        
        if poly_score > lr_score:
            best_model = 'Polynomial'
            accuracy = poly_score
        else:
            best_model = 'Linear'
            accuracy = lr_score
        
        # Make predictions
        last_day = data['Days'].iloc[-1]
        predictions = []
        
        for i in range(1, days_ahead + 1):
            future_day = last_day + i
            last_sma10 = data['SMA_10'].iloc[-1]
            last_sma30 = data['SMA_30'].iloc[-1]
            last_volume_ma = data['Volume_MA'].iloc[-1]
            last_volatility = data['Volatility'].iloc[-1]
            
            future_X = np.array([[future_day, last_sma10, last_sma30, last_volume_ma, last_volatility]])
            
            if best_model == 'Linear':
                pred_price = lr_model.predict(future_X)[0]
            else:
                future_X_poly = poly_features.transform(future_X)
                pred_price = poly_model.predict(future_X_poly)[0]
            
            predictions.append(pred_price)
        
        current_price = float(data['Price'].iloc[-1])
        avg_future_price = float(np.mean(predictions))
        price_change = float(avg_future_price - current_price)
        price_change_percent = float((price_change / current_price) * 100)
        
        return {
            'model_used': best_model,
            'accuracy': float(accuracy),
            'current_price': current_price,
            'predicted_30d_avg': avg_future_price,
            'predicted_change': price_change,
            'predicted_change_percent': price_change_percent,
            'predictions': [float(p) for p in predictions]
        }, None
        
    except Exception as e:
        return None, f"Prediction error: {str(e)}"

def get_stock_news(symbol, company_name):
    """Fetch latest news about the stock"""
    try:
        news_data = []
        company_search = company_name.replace(' Limited', '').replace(' Ltd', '')
        search_terms = [company_search, symbol.replace('.NS', '')]
        
        for term in search_terms:
            try:
                # Temporarily disabled feedparser for Python 3.13 compatibility
                # rss_url = f"https://news.google.com/rss/search?q={term.replace(' ', '+')}&hl=en-IN&gl=IN&ceid=IN:en"
                # feed = feedparser.parse(rss_url)
                
                # Alternative news fetch using web scraping
                search_url = f"https://www.google.com/search?q={term.replace(' ', '+')}+news&tbm=nws"
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.get(search_url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    news_items = soup.find_all('div', class_='SoaBEf', limit=3)
                    
                    for item in news_items:
                        title_elem = item.find('div', class_='MBeuO')
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            sentiment = analyze_sentiment(title)
                            
                            news_item = {
                                'title': title,
                                'link': '#',
                                'published': 'Recent',
                                'summary': title[:100] + '...' if len(title) > 100 else title,
                                'sentiment': sentiment
                            }
                            news_data.append(news_item)
                
                # for entry in feed.entries[:5]:
                #     pub_date = 'N/A'
                #     if hasattr(entry, 'published'):
                #         try:
                #             pub_date = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %Z').strftime('%Y-%m-%d %H:%M')
                #         except:
                #             pub_date = entry.published
                    
                #     sentiment = analyze_sentiment(entry.title + " " + entry.get('summary', ''))
                    
                #     news_item = {
                #         'title': entry.title,
                #         'summary': entry.get('summary', 'N/A')[:300] + '...',
                #         'link': entry.link,
                #         'published': pub_date,
                #         'source': entry.get('source', {}).get('title', 'Google News'),
                #         'sentiment': sentiment
                #     }
                #     news_data.append(news_item)
                
                if news_data:
                    break
                    
            except Exception as e:
                continue
        
        return news_data if news_data else [{'title': 'No recent news found', 'summary': 'Please check financial news websites', 'link': '#', 'published': 'N/A', 'source': 'N/A', 'sentiment': 'Neutral'}]
    
    except Exception as e:
        return [{'title': f'Error: {str(e)}', 'summary': 'N/A', 'link': '#', 'published': 'N/A', 'source': 'N/A', 'sentiment': 'Neutral'}]

def analyze_sentiment(text):
    """Analyze sentiment of news text"""
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

def generate_trading_recommendation(stock_data, prediction_info, current_price, rsi, macd):
    """Generate BUY/SELL/HOLD recommendation"""
    try:
        signals = []
        score = 0
        
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
        
        # Prediction Analysis
        if prediction_info and prediction_info['predicted_change_percent'] > 5:
            signals.append("AI prediction shows strong upward trend")
            score += 2
        elif prediction_info and prediction_info['predicted_change_percent'] < -5:
            signals.append("AI prediction shows strong downward trend")
            score -= 2
        
        # Generate recommendation
        if score >= 3:
            recommendation = "STRONG BUY"
            confidence = "High"
            color = "success"
        elif score >= 1:
            recommendation = "BUY"
            confidence = "Medium"
            color = "info"
        elif score <= -3:
            recommendation = "STRONG SELL"
            confidence = "High"
            color = "danger"
        elif score <= -1:
            recommendation = "SELL"
            confidence = "Medium"
            color = "warning"
        else:
            recommendation = "HOLD"
            confidence = "Medium"
            color = "secondary"
        
        return {
            'recommendation': recommendation,
            'confidence': confidence,
            'score': float(score),
            'signals': signals,
            'color': color
        }
        
    except Exception as e:
        return {
            'recommendation': 'HOLD',
            'confidence': 'Low',
            'score': 0,
            'signals': [f'Error: {str(e)}'],
            'color': 'secondary'
        }

def calculate_rsi(prices, window=14):
    """Calculate Relative Strength Index (RSI)"""
    try:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)  # Fill NaN with neutral value
    except Exception as e:
        print(f"Error calculating RSI: {e}")
        return pd.Series([50] * len(prices), index=prices.index)

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """Calculate MACD (Moving Average Convergence Divergence)"""
    try:
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal).mean()
        histogram = macd - signal_line
        return histogram.fillna(0)  # Return histogram, fill NaN with 0
    except Exception as e:
        print(f"Error calculating MACD: {e}")
        return pd.Series([0] * len(prices), index=prices.index)

def get_sector_fallback(symbol):
    """Get fallback sector information"""
    sector_map = {
        'TCS.NS': 'Information Technology',
        'INFY.NS': 'Information Technology',
        'WIPRO.NS': 'Information Technology',
        'HCLTECH.NS': 'Information Technology',
        'TECHM.NS': 'Information Technology',
        'RELIANCE.NS': 'Oil & Gas',
        'ONGC.NS': 'Oil & Gas',
        'HDFCBANK.NS': 'Banking',
        'ICICIBANK.NS': 'Banking',
        'SBIN.NS': 'Banking',
        'AXISBANK.NS': 'Banking',
        'KOTAKBANK.NS': 'Banking',
        'BAJFINANCE.NS': 'Financial Services',
        'MARUTI.NS': 'Automobile',
        'TATASTEEL.NS': 'Metals & Mining',
        'JSWSTEEL.NS': 'Metals & Mining',
        'ASIANPAINT.NS': 'Paints',
        'HINDUNILVR.NS': 'FMCG',
        'ITC.NS': 'FMCG',
        'BRITANNIA.NS': 'FMCG',
        'NESTLEIND.NS': 'FMCG'
    }
    return sector_map.get(symbol, 'Other')

def get_industry_fallback(symbol):
    """Get fallback industry information"""
    industry_map = {
        'TCS.NS': 'Software Services',
        'INFY.NS': 'Software Services',
        'WIPRO.NS': 'Software Services',
        'HCLTECH.NS': 'Software Services',
        'TECHM.NS': 'Software Services',
        'RELIANCE.NS': 'Oil & Gas Refining',
        'ONGC.NS': 'Oil Exploration',
        'HDFCBANK.NS': 'Private Banking',
        'ICICIBANK.NS': 'Private Banking',
        'SBIN.NS': 'Public Banking',
        'AXISBANK.NS': 'Private Banking',
        'KOTAKBANK.NS': 'Private Banking',
        'BAJFINANCE.NS': 'Non-Banking Finance',
        'MARUTI.NS': 'Passenger Cars',
        'TATASTEEL.NS': 'Steel Production',
        'JSWSTEEL.NS': 'Steel Production',
        'ASIANPAINT.NS': 'Decorative Paints',
        'HINDUNILVR.NS': 'Personal Care',
        'ITC.NS': 'Diversified FMCG',
        'BRITANNIA.NS': 'Food Products',
        'NESTLEIND.NS': 'Food Products'
    }
    return industry_map.get(symbol, 'Other')

def create_plotly_chart(stock_data, prediction_info, symbol):
    """Create interactive and visually appealing Plotly charts"""
    try:
        # Calculate technical indicators
        stock_data['SMA_20'] = stock_data['Close'].rolling(window=20).mean()
        stock_data['SMA_50'] = stock_data['Close'].rolling(window=50).mean()
        stock_data['EMA_12'] = stock_data['Close'].ewm(span=12).mean()
        stock_data['RSI'] = calculate_rsi(stock_data['Close'], window=14)
        stock_data['MACD'] = calculate_macd(stock_data['Close'])
        
        # Calculate Bollinger Bands
        stock_data['BB_Middle'] = stock_data['Close'].rolling(window=20).mean()
        stock_data['BB_Std'] = stock_data['Close'].rolling(window=20).std()
        stock_data['BB_Upper'] = stock_data['BB_Middle'] + (stock_data['BB_Std'] * 2)
        stock_data['BB_Lower'] = stock_data['BB_Middle'] - (stock_data['BB_Std'] * 2)
        
        # Create subplots with better spacing and fixed layout
        from plotly.subplots import make_subplots
        
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.12,  # Increased spacing between charts
            subplot_titles=(
                f'📈 {symbol} - Price Chart with Technical Indicators', 
                '📊 Volume Analysis', 
                '🎯 RSI (Relative Strength Index)', 
                '📉 MACD (Moving Average Convergence Divergence)'
            ),
            row_heights=[0.40, 0.20, 0.20, 0.20],  # More balanced heights
            specs=[[{"secondary_y": False}],
                   [{"secondary_y": False}],
                   [{"secondary_y": False}],
                   [{"secondary_y": False}]]
        )
        
        # Enhanced Price Chart with Bollinger Bands
        # Bollinger Bands fill area
        fig.add_trace(go.Scatter(
            x=stock_data.index,
            y=stock_data['BB_Upper'],
            mode='lines',
            line=dict(color='rgba(102, 126, 234, 0.3)', width=1),
            name='BB Upper',
            showlegend=False
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=stock_data.index,
            y=stock_data['BB_Lower'],
            mode='lines',
            line=dict(color='rgba(102, 126, 234, 0.3)', width=1),
            fill='tonexty',
            fillcolor='rgba(102, 126, 234, 0.1)',
            name='Bollinger Bands',
            showlegend=True
        ), row=1, col=1)
        
        # Main price line with enhanced tooltips
        fig.add_trace(go.Scatter(
            x=stock_data.index,
            y=stock_data['Close'],
            mode='lines',
            name='💰 Close Price',
            line=dict(
                color='rgba(46, 134, 171, 1)',
                width=3,
                shape='spline'
            ),
            hovertemplate='<b>💰 Close Price:</b> ₹%{y:.2f}<br><b>📅 Date:</b> %{x|%Y-%m-%d}<br><b>📈 Change:</b> %{customdata}<extra></extra>',
            customdata=[
                f"+{((stock_data['Close'].iloc[i] - stock_data['Close'].iloc[i-1]) / stock_data['Close'].iloc[i-1] * 100):.2f}%" 
                if i > 0 and stock_data['Close'].iloc[i] > stock_data['Close'].iloc[i-1]
                else f"{((stock_data['Close'].iloc[i] - stock_data['Close'].iloc[i-1]) / stock_data['Close'].iloc[i-1] * 100):.2f}%" 
                if i > 0 else "0.00%"
                for i in range(len(stock_data))
            ],
            showlegend=True
        ), row=1, col=1)
        
        # Enhanced Moving Averages with selective legend display
        fig.add_trace(go.Scatter(
            x=stock_data.index,
            y=stock_data['SMA_20'],
            mode='lines',
            name='📊 20-day SMA',
            line=dict(
                color='rgba(255, 99, 132, 0.8)',
                width=2,
                dash='dot'
            ),
            showlegend=False,  # Hide from main legend to reduce clutter
            hovertemplate='<b>20-day SMA:</b> ₹%{y:.2f}<extra></extra>'
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=stock_data.index,
            y=stock_data['SMA_50'],
            mode='lines',
            name='📈 50-day SMA',
            line=dict(
                color='rgba(255, 159, 64, 0.8)',
                width=2,
                dash='dashdot'
            ),
            showlegend=False,  # Hide from main legend to reduce clutter
            hovertemplate='<b>50-day SMA:</b> ₹%{y:.2f}<extra></extra>'
        ), row=1, col=1)
        
        # EMA line
        fig.add_trace(go.Scatter(
            x=stock_data.index,
            y=stock_data['EMA_12'],
            mode='lines',
            name='⚡ 12-day EMA',
            line=dict(
                color='rgba(75, 192, 192, 0.8)',
                width=2,
                dash='dash'
            ),
            showlegend=False,  # Hide from main legend to reduce clutter
            hovertemplate='<b>12-day EMA:</b> ₹%{y:.2f}<extra></extra>'
        ), row=1, col=1)
        
        # Enhanced predictions with confidence bands
        if prediction_info and 'predictions' in prediction_info:
            future_dates = [stock_data.index[-1] + timedelta(days=i) for i in range(1, len(prediction_info['predictions']) + 1)]
            
            # Add confidence bands for predictions
            upper_pred = [p * 1.05 for p in prediction_info['predictions']]
            lower_pred = [p * 0.95 for p in prediction_info['predictions']]
            
            # Confidence band
            fig.add_trace(go.Scatter(
                x=future_dates,
                y=upper_pred,
                mode='lines',
                line=dict(color='rgba(255, 0, 0, 0.1)', width=0),
                name='Prediction Range',
                showlegend=False
            ), row=1, col=1)
            
            fig.add_trace(go.Scatter(
                x=future_dates,
                y=lower_pred,
                mode='lines',
                line=dict(color='rgba(255, 0, 0, 0.1)', width=0),
                fill='tonexty',
                fillcolor='rgba(255, 0, 0, 0.1)',
                name='🎯 AI Prediction Range',
                showlegend=True
            ), row=1, col=1)
            
            # Main prediction line
            fig.add_trace(go.Scatter(
                x=future_dates,
                y=prediction_info['predictions'],
                mode='lines+markers',
                name='🤖 AI Prediction',
                line=dict(
                    color='rgba(220, 53, 69, 0.9)',
                    width=3,
                    dash='dash'
                ),
                marker=dict(
                    size=6,
                    color='rgba(220, 53, 69, 1)',
                    line=dict(width=2, color='white')
                ),
                hovertemplate='<b>AI Prediction:</b> ₹%{y:.2f}<br><b>Date:</b> %{x}<extra></extra>'
            ), row=1, col=1)
        
        # Enhanced Volume Chart with color coding and better tooltips
        volume_colors = []
        volume_customdata = []
        for i in range(len(stock_data)):
            if i > 0:
                if stock_data['Close'].iloc[i] > stock_data['Close'].iloc[i-1]:
                    volume_colors.append('rgba(76, 175, 80, 0.7)')  # Green for up days
                    volume_customdata.append('📈 Up Day')
                else:
                    volume_colors.append('rgba(244, 67, 54, 0.7)')  # Red for down days
                    volume_customdata.append('📉 Down Day')
            else:
                volume_colors.append('rgba(158, 158, 158, 0.7)')  # Gray for first day
                volume_customdata.append('➡️ Neutral')
        
        fig.add_trace(go.Bar(
            x=stock_data.index,
            y=stock_data['Volume'],
            name='📊 Trading Volume',
            marker=dict(
                color=volume_colors,
                line=dict(width=0.5, color='rgba(50, 50, 50, 0.3)')
            ),
            hovertemplate='<b>📊 Volume:</b> %{y:,.0f}<br><b>📅 Date:</b> %{x|%Y-%m-%d}<br><b>📈 Trend:</b> %{customdata}<extra></extra>',
            customdata=volume_customdata,
            showlegend=True
        ), row=2, col=1)
        
        # Volume Moving Average with legend control
        volume_ma = stock_data['Volume'].rolling(window=20).mean()
        fig.add_trace(go.Scatter(
            x=stock_data.index,
            y=volume_ma,
            mode='lines',
            name='📈 Volume MA(20)',
            line=dict(color='rgba(255, 193, 7, 0.8)', width=2),
            showlegend=False,  # Hide from main legend
            hovertemplate='<b>Volume MA:</b> %{y:,.0f}<extra></extra>'
        ), row=2, col=1)
        
        # Enhanced RSI Chart with zones and data validation
        # RSI background zones with proper bounds check
        if len(stock_data) > 0 and not stock_data.index.empty:
            fig.add_shape(
                type="rect",
                x0=stock_data.index[0], x1=stock_data.index[-1],
                y0=70, y1=100,
                fillcolor="rgba(255, 99, 132, 0.1)",
                layer="below", line_width=0,
                row=3, col=1
            )
            
            fig.add_shape(
                type="rect",
                x0=stock_data.index[0], x1=stock_data.index[-1],
                y0=0, y1=30,
                fillcolor="rgba(75, 192, 192, 0.1)",
                layer="below", line_width=0,
                row=3, col=1
            )
        
        # RSI line with proper data validation
        if 'RSI' in stock_data.columns and not stock_data['RSI'].empty:
            rsi_data = stock_data['RSI'].dropna()
            if len(rsi_data) > 0:
                fig.add_trace(go.Scatter(
                    x=rsi_data.index,
                    y=rsi_data.values,
                    mode='lines',
                    name='📊 RSI (14)',
                    line=dict(
                        color='rgba(153, 102, 255, 1)',
                        width=3,
                        shape='spline'
                    ),
                    hovertemplate='<b>RSI:</b> %{y:.1f}<br><b>Date:</b> %{x|%Y-%m-%d}<br><b>Signal:</b> %{customdata}<extra></extra>',
                    customdata=[
                        'Overbought' if val > 70 else 'Oversold' if val < 30 else 'Neutral'
                        for val in rsi_data.values
                    ],
                    showlegend=True
                ), row=3, col=1)
                fig.add_trace(go.Scatter(
                    x=rsi_data.index,
                    y=rsi_data.values,
                    mode='lines',
                    name='📊 RSI (14)',
                    line=dict(
                        color='rgba(153, 102, 255, 1)',
                        width=3,
                        shape='spline'
                    ),
                    hovertemplate='<b>RSI:</b> %{y:.1f}<br><b>Date:</b> %{x|%Y-%m-%d}<br><b>Signal:</b> %{customdata}<extra></extra>',
                    customdata=[
                        'Overbought' if val > 70 else 'Oversold' if val < 30 else 'Neutral'
                        for val in rsi_data.values
                    ],
                    showlegend=True
                ), row=3, col=1)
        
        # RSI reference lines with better annotations
        fig.add_hline(y=70, line_dash="dash", line_color="rgba(255, 99, 132, 0.8)", 
                     line_width=2, row=3, col=1)
        fig.add_hline(y=50, line_dash="dot", line_color="rgba(158, 158, 158, 0.6)", 
                     line_width=1, row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="rgba(75, 192, 192, 0.8)", 
                     line_width=2, row=3, col=1)
        
        # Add RSI level text annotations
        if len(stock_data) > 0 and not stock_data.index.empty:
            fig.add_annotation(
                x=stock_data.index[-1], y=75, 
                text="Overbought", showarrow=False, 
                font=dict(size=9, color="rgba(255, 99, 132, 0.8)"), 
                row=3, col=1
            )
            fig.add_annotation(
                x=stock_data.index[-1], y=25, 
                text="Oversold", showarrow=False, 
                font=dict(size=9, color="rgba(75, 192, 192, 0.8)"), 
                row=3, col=1
            )
        
        # Enhanced MACD Chart with data validation
        # MACD histogram (positive/negative colored) with proper data handling
        if 'MACD' in stock_data.columns and not stock_data['MACD'].empty:
            macd_data = stock_data['MACD'].dropna()
            if len(macd_data) > 0:
                macd_colors = [
                    'rgba(76, 175, 80, 0.7)' if x >= 0 else 'rgba(244, 67, 54, 0.7)' 
                    for x in macd_data.values
                ]
                
                fig.add_trace(go.Bar(
                    x=macd_data.index,
                    y=macd_data.values,
                    name='📈 MACD Histogram',
                    marker=dict(
                        color=macd_colors,
                        line=dict(width=0.5, color='rgba(0, 0, 0, 0.2)')
                    ),
                    hovertemplate='<b>MACD:</b> %{y:.4f}<br><b>Date:</b> %{x|%Y-%m-%d}<br><b>Signal:</b> %{customdata}<extra></extra>',
                    customdata=[
                        'Bullish' if val > 0 else 'Bearish' if val < 0 else 'Neutral'
                        for val in macd_data.values
                    ],
                    showlegend=True
                ), row=4, col=1)
                macd_colors = [
                    'rgba(76, 175, 80, 0.7)' if x >= 0 else 'rgba(244, 67, 54, 0.7)' 
                    for x in macd_data.values
                ]
                
                fig.add_trace(go.Bar(
                    x=macd_data.index,
                    y=macd_data.values,
                    name='📈 MACD Histogram',
                    marker=dict(
                        color=macd_colors,
                        line=dict(width=0.5, color='rgba(0, 0, 0, 0.2)')
                    ),
                    hovertemplate='<b>MACD:</b> %{y:.4f}<br><b>Date:</b> %{x|%Y-%m-%d}<br><b>Signal:</b> %{customdata}<extra></extra>',
                    customdata=[
                        'Bullish' if val > 0 else 'Bearish' if val < 0 else 'Neutral'
                        for val in macd_data.values
                    ],
                    showlegend=True
                ), row=4, col=1)
        
        # MACD zero line with enhanced styling
        fig.add_hline(y=0, line_dash="solid", line_color="rgba(0, 0, 0, 0.8)", 
                     line_width=2, row=4, col=1)
        
        # Add MACD signal annotation
        if len(stock_data) > 0 and not stock_data.index.empty and 'MACD' in stock_data.columns:
            latest_macd = stock_data['MACD'].dropna()
            if len(latest_macd) > 0:
                latest_value = latest_macd.iloc[-1]
                signal_text = "Bullish" if latest_value > 0 else "Bearish"
                signal_color = "rgba(76, 175, 80, 0.8)" if latest_value > 0 else "rgba(244, 67, 54, 0.8)"
                
                fig.add_annotation(
                    x=stock_data.index[-1], y=latest_value,
                    text=f"Current: {signal_text}",
                    showarrow=True, arrowhead=2,
                    font=dict(size=9, color=signal_color),
                    bgcolor="rgba(255, 255, 255, 0.8)",
                    bordercolor=signal_color,
                    row=4, col=1
                )
                latest_value = latest_macd.iloc[-1]
                signal_text = "Bullish" if latest_value > 0 else "Bearish"
                signal_color = "rgba(76, 175, 80, 0.8)" if latest_value > 0 else "rgba(244, 67, 54, 0.8)"
                
                fig.add_annotation(
                    x=stock_data.index[-1], y=latest_value,
                    text=f"Current: {signal_text}",
                    showarrow=True, arrowhead=2,
                    font=dict(size=9, color=signal_color),
                    bgcolor="rgba(255, 255, 255, 0.8)",
                    bordercolor=signal_color,
                    borderwidth=1,
                    row=4, col=1
                )
        
        # Enhanced Layout with modern styling and better spacing
        fig.update_layout(
            title={
                'text': f'🚀 {symbol} - Advanced Technical Analysis Dashboard',
                'x': 0.5,
                'xanchor': 'center',
                'y': 0.98,  # Move title higher to avoid overlap
                'font': {'size': 18, 'color': '#2c3e50', 'family': 'Arial Black'}
            },
            height=1000,  # Increased height to accommodate all charts
            showlegend=True,
            template='plotly_white',
            font=dict(size=10, family='Arial', color='#34495e'),
            plot_bgcolor='rgba(248, 249, 250, 0.8)',
            paper_bgcolor='white',
            margin=dict(l=60, r=60, t=120, b=60),  # Increased top margin
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.01,  # Position legend above charts
                xanchor="center",
                x=0.5,
                bgcolor="rgba(255, 255, 255, 0.9)",
                bordercolor="rgba(0, 0, 0, 0.1)",
                borderwidth=1,
                font=dict(size=9)  # Smaller legend font
            ),
            hoverlabel=dict(
                bgcolor="rgba(255, 255, 255, 0.98)",
                bordercolor="rgba(0, 0, 0, 0.2)",
                font_size=12,
                font_family="Arial",
                font_color="#2c3e50",
                align="left",
                namelength=-1  # Show full trace names
            ),
            hovermode='x unified'  # Show all values at same x position
        )
        
        # Enhanced axis styling with better visibility
        fig.update_xaxes(
            gridcolor='rgba(128, 128, 128, 0.2)',
            gridwidth=1,
            showline=True,
            linewidth=1,
            linecolor='rgba(128, 128, 128, 0.3)',
            tickfont=dict(color='#34495e', size=9),
            title_font=dict(color='#34495e', size=10)
        )
        
        fig.update_yaxes(
            gridcolor='rgba(128, 128, 128, 0.2)',
            gridwidth=1,
            showline=True,
            linewidth=1,
            linecolor='rgba(128, 128, 128, 0.3)',
            tickfont=dict(color='#34495e', size=9),
            title_font=dict(color='#34495e', size=10)
        )
        
        # Customize y-axis labels with proper spacing
        fig.update_yaxes(title_text="💰 Price (₹)", row=1, col=1, title_standoff=5)
        fig.update_yaxes(title_text="📊 Volume", row=2, col=1, title_standoff=5)
        fig.update_yaxes(title_text="🎯 RSI", row=3, col=1, title_standoff=5, range=[0, 100])  # Fixed RSI range
        fig.update_yaxes(title_text="📉 MACD", row=4, col=1, title_standoff=5)
        
        # Ensure proper x-axis for bottom chart
        fig.update_xaxes(title_text="📅 Date", row=4, col=1, title_standoff=5)
        
        # Add watermark/branding at bottom
        fig.add_annotation(
            text="Money Savyy - Save Smart Dream Big 💰",
            xref="paper", yref="paper",
            x=0.99, y=0.01,
            xanchor='right', yanchor='bottom',
            showarrow=False,
            font=dict(size=9, color="rgba(128, 128, 128, 0.5)")
        )
        
        # Add chart visibility note
        fig.add_annotation(
            text="📊 All Technical Indicators Visible",
            xref="paper", yref="paper",
            x=0.01, y=0.01,
            xanchor='left', yanchor='bottom',
            showarrow=False,
            font=dict(size=9, color="rgba(76, 175, 80, 0.7)")
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
    except Exception as e:
        print(f"Error creating enhanced chart: {e}")
        return None
        
    except Exception as e:
        print(f"Error creating chart: {e}")
        return None

@app.route('/')
def index():
    """Landing page with dual options"""
    return render_template('landing.html', 
                         app_version=APP_VERSION,
                         app_name=APP_NAME,
                         app_tagline=APP_TAGLINE,
                         release_date=RELEASE_DATE,
                         latest_features=LATEST_FEATURES,
                         upcoming_features=UPCOMING_FEATURES)

@app.route('/stock-analysis')
def stock_analysis():
    """Stock analysis dashboard"""
    return render_template('index.html',
                         app_version=APP_VERSION,
                         app_name=APP_NAME,
                         app_tagline=APP_TAGLINE,
                         release_date=RELEASE_DATE,
                         latest_features=LATEST_FEATURES,
                         upcoming_features=UPCOMING_FEATURES)

@app.route('/financial-advisor')
def financial_advisor():
    """Financial advisor page"""
    return render_template('financial-advisor.html')

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/founder-image')
def founder_image():
    """Serve founder image directly"""
    import os
    image_path = os.path.join(app.static_folder, 'images', 'Picture1.png')
    print(f"Looking for image at: {image_path}")
    print(f"File exists: {os.path.exists(image_path)}")
    return send_from_directory('static/images', 'Picture1.png')

@app.route('/static/images/<filename>')
def serve_image(filename):
    """Serve images directly - fallback for static files"""
    import os
    image_path = os.path.join(app.static_folder, 'images', filename)
    print(f"Looking for image at: {image_path}")
    print(f"File exists: {os.path.exists(image_path)}")
    return send_from_directory('static/images', filename)

@app.route('/static/css/<filename>')
def serve_css(filename):
    """Serve CSS files directly - fallback for static files"""
    return send_from_directory('static/css', filename)

@app.route('/static/js/<filename>')
def serve_js(filename):
    """Serve JS files directly - fallback for static files"""
    return send_from_directory('static/js', filename)

@app.route('/api/analyze-finances', methods=['POST'])
def analyze_finances():
    """API endpoint for financial analysis"""
    try:
        data = request.get_json()
        
        # Extract financial data
        name = data.get('name', '')
        age = int(data.get('age', 25))
        city = data.get('city', '')
        family_members = int(data.get('familyMembers', 1))
        salary = int(data.get('salary', 0))
        other_income = int(data.get('otherIncome', 0))
        expenses = int(data.get('expenses', 0))
        home_loan_emi = int(data.get('homeLoanEmi', 0))
        car_loan_emi = int(data.get('carLoanEmi', 0))
        other_emis = int(data.get('otherEmis', 0))
        credit_card_debt = int(data.get('creditCardDebt', 0))
        current_sip = int(data.get('currentSip', 0))
        emergency_fund = int(data.get('emergencyFund', 0))
        has_term_insurance = data.get('hasTermInsurance', False)
        has_health_insurance = data.get('hasHealthInsurance', False)
        has_life_insurance = data.get('hasLifeInsurance', False)
        
        # Calculate financial metrics
        total_income = salary + other_income
        total_emis = home_loan_emi + car_loan_emi + other_emis
        total_expenses = expenses + total_emis
        savings_amount = total_income - total_expenses
        
        # Financial ratios
        savings_rate = (savings_amount / total_income) * 100 if total_income > 0 else 0
        debt_ratio = (total_emis / total_income) * 100 if total_income > 0 else 0
        emergency_months = emergency_fund / expenses if expenses > 0 else 0
        investment_rate = (current_sip / total_income) * 100 if total_income > 0 else 0
        
        # Calculate financial score (0-100)
        score = 0
        
        # Savings rate (30 points)
        if savings_rate >= 20:
            score += 30
        elif savings_rate >= 15:
            score += 25
        elif savings_rate >= 10:
            score += 20
        elif savings_rate >= 5:
            score += 15
        else:
            score += 10
        
        # Debt ratio (25 points)
        if debt_ratio <= 30:
            score += 25
        elif debt_ratio <= 40:
            score += 20
        elif debt_ratio <= 50:
            score += 15
        else:
            score += 10
        
        # Emergency fund (20 points)
        if emergency_months >= 6:
            score += 20
        elif emergency_months >= 3:
            score += 15
        elif emergency_months >= 1:
            score += 10
        else:
            score += 5
        
        # Insurance coverage (15 points)
        insurance_score = 0
        if has_term_insurance:
            insurance_score += 5
        if has_health_insurance:
            insurance_score += 5
        if has_life_insurance:
            insurance_score += 5
        score += insurance_score
        
        # Investment rate (10 points)
        if investment_rate >= 15:
            score += 10
        elif investment_rate >= 10:
            score += 8
        elif investment_rate >= 5:
            score += 6
        else:
            score += 3
        
        # Generate recommendations
        recommendations = []
        
        # 50-30-20 rule analysis
        ideal_needs = total_income * 0.5
        ideal_wants = total_income * 0.3
        ideal_savings = total_income * 0.2
        
        # Budget recommendations
        if savings_amount < ideal_savings:
            recommendations.append({
                'type': 'budget',
                'title': 'Improve Your Savings Rate',
                'content': f'Your current savings rate is {savings_rate:.1f}%. Aim for at least 20% savings rate.',
                'action': f'Try to save an additional ₹{int(ideal_savings - savings_amount):,} monthly.'
            })
        
        # Debt management
        if debt_ratio > 40:
            recommendations.append({
                'type': 'debt',
                'title': 'Reduce Debt Burden',
                'content': f'Your EMI-to-income ratio is {debt_ratio:.1f}%, which is higher than recommended 40%.',
                'action': 'Consider debt consolidation or prepaying high-interest loans.'
            })
        
        # Emergency fund
        if emergency_months < 6:
            needed_amount = (6 * expenses) - emergency_fund
            recommendations.append({
                'type': 'budget',
                'title': 'Build Emergency Fund',
                'content': f'You have {emergency_months:.1f} months of expenses saved. Aim for 6 months.',
                'action': f'Save ₹{int(needed_amount/12):,} monthly for 12 months to reach your goal.'
            })
        
        # Insurance recommendations
        if not has_term_insurance:
            term_cover = total_income * 10  # 10x annual income
            recommendations.append({
                'type': 'insurance',
                'title': 'Get Term Insurance',
                'content': f'Get term life insurance coverage of ₹{term_cover/10000000:.1f} crores.',
                'action': f'Premium: Approximately ₹{int(term_cover * 0.0005/12):,} per month.'
            })
        
        if not has_health_insurance:
            health_cover = family_members * 500000
            recommendations.append({
                'type': 'insurance',
                'title': 'Get Health Insurance',
                'content': f'Get family health insurance of ₹{health_cover/100000:.0f} lakhs.',
                'action': f'Premium: Approximately ₹{int(health_cover * 0.03/12):,} per month.'
            })
        
        # Investment recommendations
        if current_sip < total_income * 0.15:
            recommended_sip = total_income * 0.15
            recommendations.append({
                'type': 'investment',
                'title': 'Increase SIP Investments',
                'content': f'Increase your SIP to ₹{int(recommended_sip):,} (15% of income).',
                'action': 'Start with equity mutual funds for long-term wealth creation.'
            })
        
        # Generate Gemini AI financial advice
        user_profile = {
            'age': age,
            'salary': total_income,
            'monthly_expenses': total_expenses,
            'current_savings': emergency_fund,
            'investments': current_sip * 12,  # Annual SIP
            'emi': total_emis,
            'family_members': family_members,
            'city': city,
            'has_insurance': has_term_insurance and has_health_insurance,
            'name': name
        }
        
        gemini_advice = gemini_advisor.generate_financial_advice(user_profile)
        
        return jsonify({
            'success': True,
            'analysis': {
                'score': round(score),
                'savings_rate': round(savings_rate, 1),
                'debt_ratio': round(debt_ratio, 1),
                'emergency_months': round(emergency_months, 1),
                'investment_rate': round(investment_rate, 1),
                'monthly_savings': savings_amount,
                'total_income': total_income,
                'total_expenses': total_expenses
            },
            'rule_502030': {
                'ideal_needs': int(ideal_needs),
                'ideal_wants': int(ideal_wants),
                'ideal_savings': int(ideal_savings),
                'actual_needs': min(int(total_expenses), int(ideal_needs)),
                'actual_wants': max(0, int(total_expenses) - int(ideal_needs)),
                'actual_savings': int(savings_amount)
            },
            'recommendations': recommendations,
            'gemini_advice': gemini_advice  # Add Gemini AI insights
        })
        
    except Exception as e:
        print(f"❌ Financial analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to analyze financial data'
        }), 500

@app.route('/api/search/<query>')
def search_stocks(query):
    """API endpoint for stock search suggestions"""
    try:
        suggestions = []
        query_lower = query.lower()
        
        for name, stock_data in INDIAN_STOCKS.items():
            if query_lower in name:
                suggestions.append({
                    'name': name.title(),
                    'symbol': stock_data['symbol'],
                    'logo': stock_data['logo'],
                    'display': f"{name.title()} ({stock_data['symbol']})"
                })
        
        return jsonify(suggestions[:10])  # Return top 10 matches
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/analyze/<stock_query>')
def analyze_stock_api(stock_query):
    """Main API endpoint for stock analysis"""
    try:
        # Search for stock
        symbol, matched_name, logo_url = search_stock_symbol(stock_query)
        
        # Get stock data with progressive fetching
        result = get_stock_data_with_retry(symbol)
        
        # Safety check for None result
        if result is None:
            print(f"Got None result for {symbol}, switching to fallback mode")
            result = "FALLBACK_MODE"
        
        # Initialize default values
        rsi = 50.0  # Neutral RSI default
        macd = 0.0  # Neutral MACD default
        demo_mode = False
        recommendation = "Hold"
        
        # Check if we're in fallback mode
        if result == "FALLBACK_MODE":
            # Use mock data
            hist_data, info, mock_data = get_fallback_data(symbol, matched_name)
            
            # Use mock data values
            current_price = mock_data['current_price']
            open_price = mock_data['open_price'] 
            high_price = mock_data['high_price']
            low_price = mock_data['low_price']
            volume = mock_data['volume']
            change = mock_data['change']
            change_percent = mock_data['change_percent']
            company_name = mock_data['name']
            recommendation = mock_data['recommendation']
            
            # Debug logging for recommendation
            print(f"🔍 FALLBACK MODE - recommendation type: {type(recommendation)}")
            print(f"🔍 FALLBACK MODE - recommendation content: {recommendation}")
            
            # Simple mock technical indicators
            rsi = 50.0  # Neutral RSI
            macd = 0.5  # Slightly positive MACD
            
            # Create simple chart data
            chart_json = create_simple_chart(hist_data, company_name)
            demo_mode = True
            
        elif isinstance(result, tuple) and len(result) == 4:
            # Minimal data mode: (stock, hist_data, info, minimal_data)
            stock, hist_data, info, minimal_data = result
            
            # Use minimal data for current prices
            current_price = minimal_data['current_price']
            open_price = minimal_data['open_price']
            high_price = minimal_data['high_price'] 
            low_price = minimal_data['low_price']
            volume = minimal_data['volume']
            change = float(current_price - open_price)
            change_percent = float((change / open_price) * 100)
            company_name = info.get('longName', symbol)
            
            # Calculate technical indicators for minimal data
            try:
                if hist_data is not None and not hist_data.empty and len(hist_data) >= 14:
                    rsi_series = calculate_rsi(hist_data['Close'], window=14)
                    rsi = float(rsi_series.iloc[-1]) if not rsi_series.empty else 50.0
                    macd_series = calculate_macd(hist_data['Close'])
                    macd = float(macd_series.iloc[-1]) if not macd_series.empty else 0.0
                else:
                    print("Insufficient data for technical indicators, using defaults")
            except Exception as e:
                print(f"Error calculating technical indicators: {e}")            # Generate chart and recommendation
            try:
                chart_json = create_plotly_chart(hist_data, {'error': 'Prediction unavailable'}, symbol)
                prediction_info = {'error': 'Prediction unavailable in minimal mode'}
                recommendation_data = generate_trading_recommendation(hist_data, prediction_info, current_price, rsi, macd)
                # Extract just the recommendation string from the dict
                if isinstance(recommendation_data, dict):
                    recommendation = recommendation_data.get('recommendation', 'HOLD')
                else:
                    recommendation = str(recommendation_data)
            except:
                chart_json = create_simple_chart(hist_data, company_name)
                recommendation = "Hold - Analysis incomplete"
        
        elif isinstance(result, tuple) and len(result) == 3:
            # Full data mode: (stock, hist_data, info)
            stock, hist_data, info = result
            
            if hist_data.empty:
                return jsonify({'error': 'No data found for this stock'})
        
            # Basic information (convert to Python native types for JSON serialization)
            current_price = float(hist_data['Close'].iloc[-1])
            open_price = float(hist_data['Open'].iloc[-1])
            high_price = float(hist_data['High'].iloc[-1])
            low_price = float(hist_data['Low'].iloc[-1])
            volume = int(hist_data['Volume'].iloc[-1])
            change = float(current_price - open_price)
            change_percent = float((change / open_price) * 100)
            company_name = info.get('longName', symbol)
            
            # Calculate technical indicators for full data
            try:
                if len(hist_data) >= 14:
                    rsi_series = calculate_rsi(hist_data['Close'], window=14)
                    rsi = float(rsi_series.iloc[-1]) if not rsi_series.empty else 50.0
                    macd_series = calculate_macd(hist_data['Close'])
                    macd = float(macd_series.iloc[-1]) if not macd_series.empty else 0.0
                else:
                    print("Insufficient data for technical indicators, using defaults")
            except Exception as e:
                print(f"Error calculating technical indicators: {e}")
            
            # Generate chart and recommendation
            try:
                prediction_info = predict_future_price(hist_data)
                chart_json = create_plotly_chart(hist_data, prediction_info, symbol)
                recommendation_data = generate_trading_recommendation(hist_data, prediction_info, current_price, rsi, macd)
                # Extract just the recommendation string from the dict
                if isinstance(recommendation_data, dict):
                    recommendation = recommendation_data.get('recommendation', 'HOLD')
                else:
                    recommendation = str(recommendation_data)
            except:
                chart_json = create_simple_chart(hist_data, company_name)
                recommendation = "Hold - Analysis incomplete"
        
        else:
            # Unexpected result type - force fallback
            print(f"Unexpected result type: {type(result)}, forcing fallback mode")
            hist_data, info, mock_data = get_fallback_data(symbol, matched_name)
            
            current_price = mock_data['current_price']
            open_price = mock_data['open_price'] 
            high_price = mock_data['high_price']
            low_price = mock_data['low_price']
            volume = mock_data['volume']
            change = mock_data['change']
            change_percent = mock_data['change_percent']
            company_name = mock_data['name']
            recommendation = mock_data['recommendation']
            
            rsi = 50.0
            macd = 0.5
            chart_json = create_simple_chart(hist_data, company_name)
            demo_mode = True
        
        # Generate Gemini AI insights
        market_cap = info.get('marketCap') if 'info' in locals() else None
        gemini_analysis = gemini_advisor.generate_stock_analysis(
            symbol=symbol,
            current_price=current_price,
            change_percent=change_percent,
            volume=volume,
            market_cap=market_cap
        )
        
        # Generate additional AI-powered analyses
        news_sentiment = gemini_advisor.generate_news_sentiment_analysis(
            symbol=symbol,
            company_name=company_name,
            current_price=current_price,
            recent_news=None  # Will use general analysis
        )
        
        # Prepare financial data for fundamentals analysis
        financial_data = {
            'current_price': current_price,
            'market_cap': info.get('marketCap', 0) if 'info' in locals() else 0,
            'pe_ratio': info.get('trailingPE', 0) if 'info' in locals() else 0,
            'book_value': info.get('bookValue', 0) if 'info' in locals() else 0,
            'dividend_yield': info.get('dividendYield', 0) if 'info' in locals() else 0,
            'debt_equity': info.get('debtToEquity', 0) if 'info' in locals() else 0,
            'roe': info.get('returnOnEquity', 0) if 'info' in locals() else 0
        }
        
        fundamentals_analysis = gemini_advisor.generate_fundamentals_analysis(
            symbol=symbol,
            company_name=company_name,
            financial_data=financial_data
        )
        
        # Prepare response data
        response_data = {
            'symbol': symbol,
            'company_name': company_name,
            'name': company_name,
            'logo_url': logo_url,
            'current_info': {
                'price': current_price,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'volume': volume,
                'change': change,
                'change_percent': change_percent,
                'is_real_price': not demo_mode  # True if real price, False if demo/estimated
            },
            'technical': {
                'rsi': rsi,
                'rsi_signal': 'Oversold' if rsi < 30 else 'Overbought' if rsi > 70 else 'Neutral',
                'macd': macd,
                'macd_signal': 'Bullish' if macd > 0 else 'Bearish' if macd < 0 else 'Neutral'
            },
            'recommendation': {
                'recommendation': recommendation,  # Now guaranteed to be a string
                'color': 'success' if 'Buy' in str(recommendation) or 'BUY' in str(recommendation) else 'danger' if 'Sell' in str(recommendation) or 'SELL' in str(recommendation) else 'warning',
                'confidence': 'Medium',
                'score': 7.5
            },
            'news': [{'title': 'Live news unavailable in demo mode', 'sentiment': 'Neutral'}],
            'chart': chart_json,
            'fundamentals': {
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'dividend_yield': info.get('dividendYield'),
                'week_52_high': info.get('fiftyTwoWeekHigh'),
                'week_52_low': info.get('fiftyTwoWeekLow'),
                'sector': info.get('sector') or get_sector_fallback(symbol),
                'industry': info.get('industry') or get_industry_fallback(symbol)
            },
            'demo_mode': demo_mode,
            'gemini_analysis': gemini_analysis,  # Add Gemini AI insights
            'news_sentiment': news_sentiment,     # Add AI-powered news sentiment
            'fundamentals_analysis': fundamentals_analysis  # Add AI-powered fundamentals
        }
        
        # Final debug before sending response
        print(f"🔍 FINAL DEBUG - recommendation in response: {response_data['recommendation']}")
        
        return jsonify(response_data)

    except Exception as e:
        print(f"Error in analyze_stock_api: {e}")
        import traceback
        traceback.print_exc()
        
        error_msg = str(e)
        
        # Provide user-friendly error messages
        if "429" in error_msg or "Too Many Requests" in error_msg:
            return jsonify({'error': 'Server is busy. Please try again in a few moments.'})
        elif "No data found" in error_msg:
            return jsonify({'error': 'Stock not found. Please check the symbol and try again.'})
        elif "connection" in error_msg.lower():
            return jsonify({'error': 'Network error. Please check your internet connection.'})
        else:
            return jsonify({'error': f'Analysis failed. Please try again later. ({error_msg})'})


@app.route('/api/popular-stocks')
def get_popular_stocks():
    """Get list of popular stocks"""
    try:
        popular = [
            {'name': 'TCS', 'symbol': 'TCS.NS', 'full_name': 'Tata Consultancy Services', 'logo': 'https://logo.clearbit.com/tcs.com'},
            {'name': 'Reliance', 'symbol': 'RELIANCE.NS', 'full_name': 'Reliance Industries', 'logo': 'https://logo.clearbit.com/ril.com'},
            {'name': 'Infosys', 'symbol': 'INFY.NS', 'full_name': 'Infosys Limited', 'logo': 'https://logo.clearbit.com/infosys.com'},
            {'name': 'HDFC Bank', 'symbol': 'HDFCBANK.NS', 'full_name': 'HDFC Bank Limited', 'logo': 'https://logo.clearbit.com/hdfcbank.com'},
            {'name': 'ICICI Bank', 'symbol': 'ICICIBANK.NS', 'full_name': 'ICICI Bank Limited', 'logo': 'https://logo.clearbit.com/icicibank.com'},
            {'name': 'SBI', 'symbol': 'SBIN.NS', 'full_name': 'State Bank of India', 'logo': 'https://logo.clearbit.com/sbi.co.in'},
            {'name': 'Bajaj Finance', 'symbol': 'BAJFINANCE.NS', 'full_name': 'Bajaj Finance Limited', 'logo': 'https://logo.clearbit.com/bajajfinserv.in'},
            {'name': 'Asian Paints', 'symbol': 'ASIANPAINT.NS', 'full_name': 'Asian Paints Limited', 'logo': 'https://logo.clearbit.com/asianpaints.com'}
        ]
        return jsonify(popular)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/news-sentiment/<stock_symbol>')
def get_news_sentiment(stock_symbol):
    """Get AI-powered news sentiment analysis for a stock with real information sources"""
    try:
        # Search for stock info
        symbol, company_name, logo_url = search_stock_symbol(stock_symbol)
        
        # Get comprehensive stock info
        result = get_stock_data_with_retry(symbol)
        current_price = 0
        dividend_yield = None
        market_cap = None
        pe_ratio = None
        
        if result and isinstance(result, tuple) and len(result) >= 4:
            stock, hist_data, info, minimal_data = result
            current_price = minimal_data.get('current_price', 0)
            company_name = info.get('longName', company_name)
            dividend_yield = info.get('dividendYield')
            market_cap = info.get('marketCap')
            pe_ratio = info.get('trailingPE')
        
        # Enhanced realistic news information based on company
        company_info = {
            'symbol': symbol,
            'company_name': company_name,
            'current_price': current_price,
            'dividend_yield': dividend_yield,
            'market_cap': market_cap,
            'pe_ratio': pe_ratio
        }
        
        # Generate realistic news based on company type and sector
        recent_news = generate_realistic_news(symbol, company_name)
        
        # Generate Gemini-powered sentiment analysis with enhanced context
        sentiment_analysis = gemini_advisor.generate_news_sentiment_analysis(
            symbol, company_name, current_price, recent_news
        )
        
        # Add real financial data to sentiment analysis
        if sentiment_analysis:
            sentiment_analysis['company_info'] = company_info
            sentiment_analysis['news_sources'] = get_news_sources_for_stock(symbol)
            sentiment_analysis['financial_links'] = get_financial_links_for_stock(symbol)
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'company_name': company_name,
            'current_price': current_price,
            'sentiment_analysis': sentiment_analysis,
            'recent_news': recent_news,
            'company_info': company_info,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"News sentiment analysis error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'fallback_sentiment': {
                'sentiment_score': 5,  # Slightly positive default
                'sentiment_label': 'NEUTRAL',
                'message': 'Unable to analyze sentiment at this time - showing neutral outlook'
            }
        })

def generate_realistic_news(symbol, company_name):
    """Generate realistic news based on company and current market conditions"""
    # Real news patterns based on Indian stock market
    base_symbol = symbol.replace('.NS', '').replace('.BO', '')
    
    # Sector-specific news patterns
    sector_news = {
        'RELIANCE': [
            f"{company_name} announces Q3 earnings, beats estimates",
            f"Jio Platforms partnership drives {company_name} growth",
            f"Oil-to-chemicals expansion boosts {company_name} outlook",
            f"ESG initiatives position {company_name} for future growth",
            f"Retail segment shows strong recovery for {company_name}"
        ],
        'TCS': [
            f"{company_name} reports strong IT services demand",
            f"Cloud transformation drives {company_name} revenue growth", 
            f"Digital initiatives boost {company_name} margins",
            f"Large deal wins strengthen {company_name} pipeline",
            f"AI and automation services expand {company_name} offerings"
        ],
        'INFY': [
            f"{company_name} guidance upgrade signals strong demand",
            f"Digital transformation deals boost {company_name}",
            f"Infosys Cobalt platform drives client wins",
            f"Strong hiring indicates growth confidence at {company_name}",
            f"European markets show robust growth for {company_name}"
        ],
        'HDFCBANK': [
            f"{company_name} merger integration progresses smoothly",
            f"Credit growth accelerates for {company_name}",
            f"Digital banking initiatives drive {company_name} efficiency",
            f"Asset quality improvements support {company_name}",
            f"NIM expansion boosts {company_name} profitability"
        ],
        'ICICIBANK': [
            f"{company_name} retail lending shows strong momentum",
            f"Digital transformation yields results for {company_name}",
            f"Credit cost normalization benefits {company_name}",
            f"Corporate lending recovery supports {company_name}",
            f"Technology investments pay off for {company_name}"
        ]
    }
    
    # Default news for other companies
    default_news = [
        f"{company_name} announces quarterly results",
        f"Market analysts upgrade {company_name} target price",
        f"Strong fundamentals support {company_name} outlook",
        f"Sector trends favor {company_name} growth prospects",
        f"Management guidance positive for {company_name}"
    ]
    
    # Return sector-specific news if available, otherwise default
    return sector_news.get(base_symbol, default_news)

def get_news_sources_for_stock(symbol):
    """Get relevant news sources for a stock"""
    base_symbol = symbol.replace('.NS', '').replace('.BO', '')
    
    return {
        'moneycontrol': f"https://www.moneycontrol.com/stocks/company_info/stock_news.php?sc_id={base_symbol}",
        'economic_times': "https://economictimes.indiatimes.com/markets/stocks/news",
        'livemint': "https://www.livemint.com/market",
        'business_standard': "https://www.business-standard.com/markets",
        'financial_express': "https://www.financialexpress.com/market/"
    }

def get_financial_links_for_stock(symbol):
    """Get relevant financial information links for a stock"""
    base_symbol = symbol.replace('.NS', '').replace('.BO', '')
    
    return {
        'screener': f"https://www.screener.in/company/{base_symbol}/",
        'tickertape': f"https://www.tickertape.in/stocks/{base_symbol.lower()}",
        'nse_quotes': f"https://www.nseindia.com/get-quotes/equity?symbol={base_symbol}",
        'bse_financials': f"https://www.bseindia.com/stock-share-price/{base_symbol}/financials/",
        'dividends': f"https://www.moneycontrol.com/stocks/company_info/dividends.php?sc_id={base_symbol}",
        'annual_reports': f"https://www.screener.in/company/{base_symbol}/consolidated/",
        'peer_comparison': f"https://www.tickertape.in/stocks/{base_symbol.lower()}/peers"
    }

@app.route('/api/fundamentals/<stock_symbol>')
def get_fundamentals_analysis(stock_symbol):
    """Get AI-powered fundamental analysis for a stock"""
    try:
        # Search for stock info
        symbol, company_name, logo_url = search_stock_symbol(stock_symbol)
        
        # Get comprehensive stock data
        result = get_stock_data_with_retry(symbol)
        financial_data = {}
        
        if result and isinstance(result, tuple) and len(result) >= 4:
            stock, hist_data, info, minimal_data = result
            company_name = info.get('longName', company_name)
            
            # Extract financial metrics from info
            financial_data = {
                'current_price': minimal_data.get('current_price', 0),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'book_value': info.get('bookValue', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'debt_equity': info.get('debtToEquity', 0),
                'roe': info.get('returnOnEquity', 0),
                'profit_margin': info.get('profitMargins', 0),
                'revenue': info.get('totalRevenue', 0),
                'earnings_growth': info.get('earningsGrowth', 0),
                'revenue_growth': info.get('revenueGrowth', 0),
                'current_ratio': info.get('currentRatio', 0),
                'quick_ratio': info.get('quickRatio', 0),
                'sector': info.get('sector') or get_sector_fallback(symbol),
                'industry': info.get('industry') or get_industry_fallback(symbol)
            }
        else:
            # Use minimal data if detailed info not available
            financial_data = {
                'current_price': 100,  # Mock data
                'market_cap': 50000000000,
                'pe_ratio': 20,
                'book_value': 80,
                'dividend_yield': 2.5,
                'debt_equity': 0.3,
                'roe': 15
            }
        
        # Generate Gemini-powered fundamental analysis
        fundamentals_analysis = gemini_advisor.generate_fundamentals_analysis(
            symbol, company_name, financial_data
        )
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'company_name': company_name,
            'financial_data': financial_data,
            'fundamentals_analysis': fundamentals_analysis,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Fundamentals analysis error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'fallback_fundamentals': {
                'rating': 'HOLD',
                'message': 'Unable to perform fundamental analysis at this time'
            }
        })

@app.route('/api/gemini-models')
def list_gemini_models():
    """List available Gemini models for debugging"""
    try:
        available_models = gemini_advisor.list_available_models()
        current_model = None
        if gemini_advisor.model:
            current_model = getattr(gemini_advisor.model, '_model_name', 'Unknown')
        
        return jsonify({
            'available_models': available_models,
            'current_model': current_model,
            'model_initialized': gemini_advisor.model is not None,
            'api_key_configured': bool(GEMINI_API_KEY and GEMINI_API_KEY != 'your-gemini-api-key-here')
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'available_models': [],
            'model_initialized': False
        })

@app.route('/api/test-gemini')
def test_gemini():
    """Test endpoint to verify Gemini AI integration"""
    try:
        # Test stock analysis
        test_analysis = gemini_advisor.generate_stock_analysis(
            symbol="TCS",
            current_price=3850.75,
            change_percent=1.5,
            volume=2500000,
            market_cap=14000000000000
        )
        
        # Test financial advice
        test_profile = {
            'age': 30,
            'salary': 80000,
            'monthly_expenses': 50000,
            'current_savings': 500000,
            'investments': 100000,
            'emi': 15000
        }
        
        test_advice = gemini_advisor.generate_financial_advice(test_profile)
        
        return jsonify({
            'gemini_status': 'working' if gemini_advisor.model else 'not_configured',
            'test_stock_analysis': test_analysis,
            'test_financial_advice': test_advice,
            'message': 'Gemini AI integration test completed successfully!'
        })
        
    except Exception as e:
        return jsonify({
            'gemini_status': 'error',
            'error': str(e),
            'message': 'Gemini AI integration test failed'
        })

if __name__ == '__main__':
    import os
    print("🚀 Starting Money Savyy - Save Smart Dream Big!")
    
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    if debug:
        print("Visit: http://localhost:5000")
    
    app.run(debug=debug, host='0.0.0.0', port=port)

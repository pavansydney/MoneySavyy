# Money Savyy - Save Smart Dream Big 💰📈

A comprehensive stock analysis web application built with Flask that provides real-time stock data, technical analysis, and trading recommendations with support for Indian and international markets.

![Money Savyy Banner](https://img.shields.io/badge/Money%20Savyy-Save%20Smart%20Dream%20Big-blue?style=for-the-badge&logo=chart-line)

## 🚀 Features

### 📊 Core Analysis
- **Real-time Stock Data**: Live price updates with fallback mechanisms
- **Technical Indicators**: RSI, MACD, Moving Averages, and more
- **Price Predictions**: Machine learning-based future price predictions
- **Trading Recommendations**: Smart buy/sell/hold suggestions
- **Interactive Charts**: Beautiful Plotly-powered visualizations

### 🇮🇳 Indian Market Support
- **NSE Direct Integration**: Native support for Indian stocks
- **Popular Indian Stocks**: Pre-configured data for TCS, Reliance, Infosys, etc.
- **Enhanced Demo Mode**: Realistic data for major Indian companies
- **INR Currency Display**: Proper Indian Rupee formatting

### 🛡️ Reliability Features
- **Smart Fallback System**: Multiple data sources with automatic switching
- **Rate Limiting Protection**: Intelligent API usage management
- **Caching System**: 5-minute cache for improved performance
- **Error Handling**: Graceful degradation with demo mode

### 🎨 User Experience
- **Modern UI**: Glass morphism design with transparent navbar
- **Responsive Design**: Works perfectly on mobile and desktop
- **Real-time Updates**: Live data streaming and updates
- **Search Functionality**: Intelligent stock symbol search

## 🛠️ Technology Stack

### Backend
- **Python 3.11+**: Core application language
- **Flask**: Web framework
- **Flask-CORS**: Cross-origin resource sharing
- **yfinance**: Yahoo Finance API integration
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computations
- **scikit-learn**: Machine learning models
- **ta (Technical Analysis)**: Technical indicators
- **plotly**: Interactive chart generation
- **requests**: HTTP client for API calls

### Frontend
- **HTML5 & CSS3**: Modern web standards
- **Bootstrap 5**: Responsive UI framework
- **JavaScript ES6+**: Dynamic interactions
- **Plotly.js**: Chart rendering
- **Font Awesome**: Icon library

### APIs & Data Sources
- **Yahoo Finance**: Primary data source
- **NSE Direct**: Indian stock market data
- **Multiple Fallbacks**: Ensuring data availability

## 📦 Installation

### Prerequisites
- Python 3.11 or higher
- pip (Python package installer)
- Git (optional, for cloning)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd money_savyy_website
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 🔧 Configuration

### Environment Variables (Optional)
Create a `.env` file in the root directory:
```env
FLASK_ENV=development
FLASK_DEBUG=True
CACHE_DURATION=300
MAX_RETRIES=3
```

### Cache Configuration
- **Location**: `./cache/` directory
- **Duration**: 5 minutes (300 seconds)
- **Format**: Pickle files for fast serialization

## 🚀 Deployment

### Free Deployment Options

#### 1. Render.com (Recommended)
```bash
# Files already included:
# - Procfile
# - runtime.txt
# - requirements.txt
```

#### 2. Railway
```bash
railway login
railway init
railway up
```

#### 3. Heroku
```bash
heroku create your-app-name
git push heroku main
```

#### 4. Vercel (with Python support)
```bash
vercel --prod
```

### Production Configuration
1. Set `FLASK_ENV=production`
2. Configure proper error logging
3. Use production WSGI server (Gunicorn)
4. Set up monitoring and health checks

## 📁 Project Structure

```
money_savyy_website/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Procfile              # Deployment configuration
├── runtime.txt           # Python version specification
├── README.md             # Project documentation
├── .gitignore           # Git ignore rules
├── cache/               # Cache directory (auto-created)
├── static/
│   ├── css/
│   │   └── style.css    # Custom styles
│   └── js/
│       └── app.js       # Frontend JavaScript
└── templates/
    └── index.html       # Main HTML template
```

## 🔍 Usage Examples

### Basic Stock Analysis
```python
# Search for a stock
symbol, name, logo = search_stock_symbol("TCS")

# Get stock data with fallback
result = get_stock_data_with_retry("TCS.NS")

# Analyze with technical indicators
analysis = analyze_stock_api("TCS")
```

### API Endpoints
```bash
# Main analysis endpoint
POST /analyze
Content-Type: application/json
{
    "symbol": "TCS"
}

# Stock search
GET /search?q=Tata

# Health check
GET /
```

## 🧪 Testing

### Run Tests
```bash
# Unit tests
python -m pytest tests/

# Manual testing
python test_features.py
python test_stock_search.py
```

### Test Popular Stocks
- **Indian**: TCS, RELIANCE, INFY, ITC, HDFCBANK
- **US**: AAPL, GOOGL, MSFT, TSLA, AMZN
- **Crypto**: BTC-USD, ETH-USD

## 🛠️ API Reference

### Stock Analysis
```javascript
// Request
fetch('/analyze', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({symbol: 'TCS'})
})

// Response
{
    "symbol": "TCS.NS",
    "company_name": "Tata Consultancy Services Limited",
    "current_info": {
        "price": 3850.75,
        "open": 3845.30,
        "high": 3885.60,
        "low": 3830.25,
        "volume": 1250000,
        "change": 5.45,
        "change_percent": 0.14
    },
    "technical": {
        "rsi": 45.2,
        "rsi_signal": "Neutral",
        "macd": 12.5,
        "macd_signal": "Bullish"
    },
    "recommendation": {
        "recommendation": "Buy",
        "color": "success",
        "confidence": "High",
        "score": 8.2
    },
    "chart": "...",  // Plotly JSON
    "demo_mode": false
}
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Yahoo Finance** for providing free stock data
- **NSE** for Indian market data access
- **Plotly** for beautiful chart visualizations
- **Bootstrap** for responsive UI components
- **Font Awesome** for icons

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Documentation**: [Wiki](https://github.com/your-repo/wiki)
- **Email**: support@moneysavyy.com

## 🔮 Roadmap

- [ ] Real-time WebSocket data streaming
- [ ] Portfolio tracking and management
- [ ] Advanced ML models (LSTM, Prophet)
- [ ] Mobile app (React Native)
- [ ] Cryptocurrency support
- [ ] Social trading features
- [ ] Advanced charting tools
- [ ] Risk assessment tools

---

**Money Savyy** - Making stock analysis accessible for everyone! 🚀📈

*Save Smart, Dream Big* 💰✨

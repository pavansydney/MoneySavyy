// Money Savyy - Main JavaScript Application

// Navbar scroll effect
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

class MoneySavyy {
    constructor() {
        this.currentStock = null;
        this.searchTimeout = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadPopularStocks();
        this.setupSearchAutocomplete();
    }

    bindEvents() {
        // Search button click
        document.getElementById('searchBtn').addEventListener('click', () => {
            this.performSearch();
        });

        // Enter key in search input
        document.getElementById('stockSearch').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.performSearch();
            }
        });

        // Search input for autocomplete
        document.getElementById('stockSearch').addEventListener('input', (e) => {
            this.handleSearchInput(e.target.value);
        });

        // Hide suggestions when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-container')) {
                this.hideSuggestions();
            }
        });
    }

    async loadPopularStocks() {
        try {
            const response = await fetch('/api/popular-stocks');
            const stocks = await response.json();
            
            const container = document.getElementById('popularStocks');
            container.innerHTML = '';
            
            stocks.forEach(stock => {
                const btn = document.createElement('button');
                btn.className = 'btn btn-outline-light btn-sm d-flex align-items-center me-2 mb-2';
                
                // Create fallback logo with company initial
                const logoFallback = `https://ui-avatars.com/api/?name=${stock.name}&size=20&background=28a745&color=fff&rounded=true`;
                
                btn.innerHTML = `
                    <img src="${stock.logo}" alt="${stock.name}" class="company-logo-small me-2" 
                         onerror="this.src='${logoFallback}'" />
                    ${stock.name}
                `;
                btn.onclick = () => this.selectStock(stock.symbol);
                container.appendChild(btn);
            });
        } catch (error) {
            console.error('Error loading popular stocks:', error);
        }
    }

    setupSearchAutocomplete() {
        const searchInput = document.getElementById('stockSearch');
        const suggestionsDiv = document.getElementById('searchSuggestions');
        
        searchInput.addEventListener('focus', () => {
            if (searchInput.value.length > 0) {
                this.showSuggestions();
            }
        });
    }

    handleSearchInput(query) {
        clearTimeout(this.searchTimeout);
        
        if (query.length < 2) {
            this.hideSuggestions();
            return;
        }

        this.searchTimeout = setTimeout(() => {
            this.fetchSuggestions(query);
        }, 300);
    }

    async fetchSuggestions(query) {
        try {
            const response = await fetch(`/api/search/${encodeURIComponent(query)}`);
            const suggestions = await response.json();
            
            this.displaySuggestions(suggestions);
        } catch (error) {
            console.error('Error fetching suggestions:', error);
        }
    }

    displaySuggestions(suggestions) {
        const suggestionsDiv = document.getElementById('searchSuggestions');
        
        if (suggestions.length === 0) {
            this.hideSuggestions();
            return;
        }

        suggestionsDiv.innerHTML = '';
        
        suggestions.forEach(suggestion => {
            const item = document.createElement('div');
            item.className = 'suggestion-item d-flex align-items-center';
            
            // Create fallback logo with company initial
            const logoFallback = `https://ui-avatars.com/api/?name=${suggestion.name}&size=32&background=007bff&color=fff&rounded=true`;
            
            item.innerHTML = `
                <img src="${suggestion.logo}" alt="${suggestion.name}" class="company-logo me-3" 
                     onerror="this.src='${logoFallback}'" />
                <div>
                    <strong>${suggestion.name}</strong>
                    <small class="text-muted d-block">${suggestion.symbol}</small>
                </div>
            `;
            item.onclick = () => this.selectSuggestion(suggestion);
            suggestionsDiv.appendChild(item);
        });

        this.showSuggestions();
    }

    selectSuggestion(suggestion) {
        document.getElementById('stockSearch').value = suggestion.name;
        this.hideSuggestions();
        this.analyzeStock(suggestion.symbol);
    }

    selectStock(symbol) {
        this.analyzeStock(symbol);
    }

    showSuggestions() {
        document.getElementById('searchSuggestions').style.display = 'block';
    }

    hideSuggestions() {
        document.getElementById('searchSuggestions').style.display = 'none';
    }

    performSearch() {
        const query = document.getElementById('stockSearch').value.trim();
        if (query) {
            this.analyzeStock(query);
        }
    }

    async analyzeStock(stockQuery) {
        this.showLoading();
        this.hideError();
        this.scrollToAnalysis();

        try {
            const response = await fetch(`/api/analyze/${encodeURIComponent(stockQuery)}`);
            const data = await response.json();

            if (data.error) {
                this.showError(data.error);
                return;
            }

            this.currentStock = data.symbol || stockQuery;
            this.displayAnalysis(data);
            this.hideLoading();

        } catch (error) {
            this.showError('Failed to analyze stock. Please try again.');
            console.error('Analysis error:', error);
        }
    }

    displayAnalysis(data) {
        // Debug logging to help track data structure issues
        console.log('📊 Analysis data received:', data);
        console.log('🎯 Recommendation structure:', data.recommendation);
        
        // Update stock header with logo
        const stockLogo = document.getElementById('stockLogo');
        const stockName = document.getElementById('stockName');
        const stockSymbol = document.getElementById('stockSymbol');
        
        // Create fallback logo with company initial
        const logoFallback = `https://ui-avatars.com/api/?name=${data.company_name}&size=48&background=007bff&color=fff&rounded=true`;
        
        if (data.logo_url) {
            stockLogo.src = data.logo_url;
            stockLogo.onerror = () => { stockLogo.src = logoFallback; };
            stockLogo.style.display = 'block';
        } else {
            stockLogo.src = logoFallback;
            stockLogo.style.display = 'block';
        }
        
        stockName.textContent = data.company_name;
        stockSymbol.textContent = data.symbol;

        // Update current price info
        this.updatePriceInfo(data.current_info);

        // Update recommendation
        console.log('🎯 Recommendation data type:', typeof data.recommendation);
        console.log('🎯 Recommendation content:', data.recommendation);
        this.updateRecommendation(data.recommendation);

        // Update chart
        this.updateChart(data.chart);

        // Update news tab with AI sentiment
        this.updateNews(data.news, data.news_sentiment);

        // Update fundamentals tab with AI analysis
        this.updateFundamentals(data.fundamentals, data.fundamentals_analysis);

        // Update Gemini AI insights tab
        this.updateGeminiInsights(data.gemini_analysis);

        // Show results
        document.getElementById('analysisResults').classList.remove('d-none');
        document.getElementById('analysisResults').classList.add('fade-in');
    }

    updatePriceInfo(info) {
        document.getElementById('currentPrice').textContent = `₹${info.price.toFixed(2)}`;
        document.getElementById('openPrice').textContent = `₹${info.open.toFixed(2)}`;
        document.getElementById('highPrice').textContent = `₹${info.high.toFixed(2)}`;
        document.getElementById('lowPrice').textContent = `₹${info.low.toFixed(2)}`;
        document.getElementById('volume').textContent = this.formatNumber(info.volume);

        const changeEl = document.getElementById('priceChange');
        const change = info.change;
        const changePercent = info.change_percent;
        
        changeEl.textContent = `${change >= 0 ? '+' : ''}₹${change.toFixed(2)} (${change >= 0 ? '+' : ''}${changePercent.toFixed(2)}%)`;
        changeEl.className = `mb-1 ${change >= 0 ? 'text-success' : 'text-danger'}`;
        
        // Show real price indicator if available
        const priceIndicator = document.getElementById('priceIndicator');
        if (info.is_real_price) {
            priceIndicator.innerHTML = `
                <span class="badge bg-success text-white">
                    <i class="fas fa-wifi"></i> Live Price
                </span>
            `;
            priceIndicator.style.display = 'block';
        } else {
            priceIndicator.innerHTML = `
                <span class="badge bg-warning text-dark">
                    <i class="fas fa-calculator"></i> Estimated
                </span>
            `;
            priceIndicator.style.display = 'block';
        }
    }

    updateRecommendation(rec) {
        const recDiv = document.getElementById('recommendation');
        
        console.log('🔍 updateRecommendation called with:', rec);
        console.log('🔍 Type of rec:', typeof rec);
        
        // Handle both old format (direct string) and new format (object)
        let recommendationText, color, confidence, score;
        
        if (typeof rec === 'object' && rec !== null) {
            if (rec.recommendation) {
                // New format with nested structure
                recommendationText = rec.recommendation;
                color = rec.color || 'secondary';
                confidence = rec.confidence || 'Medium';
                score = rec.score || 0;
            } else if (rec.text || rec.value) {
                // Alternative object formats
                recommendationText = rec.text || rec.value || 'Hold';
                color = rec.color || 'warning';
                confidence = rec.confidence || 'Medium';
                score = rec.score || 5.0;
            } else {
                // Object without expected properties - convert to string
                console.warn('⚠️ Unexpected recommendation object structure:', rec);
                recommendationText = JSON.stringify(rec);
                color = 'warning';
                confidence = 'Low';
                score = 0;
            }
        } else if (typeof rec === 'string') {
            // Old format (direct string)
            recommendationText = rec;
            color = rec.includes('Buy') || rec.includes('BUY') ? 'success' : 
                   rec.includes('Sell') || rec.includes('SELL') ? 'danger' : 'warning';
            confidence = 'Medium';
            score = 7.0;
        } else {
            // Fallback for undefined/null/other types
            console.warn('⚠️ Invalid recommendation data:', rec);
            recommendationText = 'Hold';
            color = 'warning';
            confidence = 'Low';
            score = 5.0;
        }
        
        const badgeClass = `badge bg-${color}`;
        
        recDiv.innerHTML = `
            <span class="${badgeClass}">
                <i class="fas fa-chart-line me-1"></i>
                ${recommendationText}
            </span>
            <small class="d-block mt-1 text-muted">
                Confidence: ${confidence} | Score: ${typeof score === 'number' ? score.toFixed(1) : score}
            </small>
        `;
        
        console.log('✅ Recommendation updated with text:', recommendationText);
    }

    updateChart(chartJson) {
        if (chartJson) {
            const chartData = JSON.parse(chartJson);
            Plotly.newPlot('stockChart', chartData.data, chartData.layout, {
                responsive: true,
                displayModeBar: false
            });
        }
    }

    updateNews(newsData, sentimentAnalysis) {
        const container = document.getElementById('newsContent');
        
        if (!sentimentAnalysis) {
            container.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    News sentiment analysis temporarily unavailable.
                </div>
            `;
            return;
        }

        const getSentimentColor = (label) => {
            switch(label) {
                case 'VERY_BULLISH': return 'success';
                case 'BULLISH': return 'success';
                case 'NEUTRAL': return 'warning';
                case 'BEARISH': return 'danger';
                case 'VERY_BEARISH': return 'danger';
                default: return 'secondary';
            }
        };

        const getSentimentIcon = (label) => {
            switch(label) {
                case 'VERY_BULLISH': return 'fa-arrow-up';
                case 'BULLISH': return 'fa-thumbs-up';
                case 'NEUTRAL': return 'fa-minus';
                case 'BEARISH': return 'fa-thumbs-down';
                case 'VERY_BEARISH': return 'fa-arrow-down';
                default: return 'fa-question';
            }
        };

        // Enhanced news data with real links and information
        const stockSymbol = (typeof this.currentStock === 'string' ? this.currentStock : 'RELIANCE.NS') || 'RELIANCE.NS';
        const companyName = sentimentAnalysis.company_name || 'Reliance Industries';
        
        // Ensure stockSymbol is a valid string before using replace
        const safeStockSymbol = String(stockSymbol).includes('.NS') ? stockSymbol : stockSymbol + '.NS';
        
        const newsHtml = `
            <div class="row g-4">
                <!-- Sentiment Overview -->
                <div class="col-12">
                    <div class="card border-0 shadow-sm">
                        <div class="card-header bg-light">
                            <h5 class="mb-0"><i class="fas fa-chart-line text-primary me-2"></i>Market Sentiment Overview</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-4 text-center">
                                    <div class="sentiment-score-circle mb-3" title="Sentiment Score: ${sentimentAnalysis.sentiment_score}/100 (Negative=Bearish, Positive=Bullish)">
                                        <span class="sentiment-score text-${getSentimentColor(sentimentAnalysis.sentiment_label)}">
                                            ${sentimentAnalysis.sentiment_score > 0 ? '+' : ''}${sentimentAnalysis.sentiment_score}
                                        </span>
                                    </div>
                                    <small class="text-muted d-block mb-2">Score: -100 (Very Bearish) to +100 (Very Bullish)</small>
                                    <span class="badge bg-${getSentimentColor(sentimentAnalysis.sentiment_label)} fs-6 px-3 py-2">
                                        <i class="fas ${getSentimentIcon(sentimentAnalysis.sentiment_label)} me-2"></i>
                                        ${sentimentAnalysis.sentiment_label}
                                    </span>
                                </div>
                                <div class="col-md-8">
                                    <h6>Key Factors:</h6>
                                    <ul class="list-unstyled">
                                        ${sentimentAnalysis.key_factors.map(factor => `
                                            <li><i class="fas fa-check-circle text-success me-2"></i>${factor}</li>
                                        `).join('')}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Real News & Information Sources -->
                <div class="col-12">
                    <div class="card border-0 shadow-sm">
                        <div class="card-header bg-light d-flex justify-content-between align-items-center">
                            <h5 class="mb-0"><i class="fas fa-newspaper text-primary me-2"></i>Latest News & Information Sources</h5>
                            <small class="text-muted">Real-time information</small>
                        </div>
                        <div class="card-body">
                            <div class="row g-3">
                                <!-- News Sources -->
                                <div class="col-md-6">
                                    <h6><i class="fas fa-globe text-info me-2"></i>Financial News</h6>
                                    <div class="list-group list-group-flush">
                                        <a href="https://www.moneycontrol.com/stocks/company_info/stock_news.php?sc_id=${safeStockSymbol.replace('.NS', '')}" 
                                           target="_blank" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
                                            <span><i class="fas fa-chart-line text-primary me-2"></i>MoneyControl News</span>
                                            <i class="fas fa-external-link-alt text-muted"></i>
                                        </a>
                                        <a href="https://economictimes.indiatimes.com/markets/stocks/news" 
                                           target="_blank" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
                                            <span><i class="fas fa-newspaper text-info me-2"></i>Economic Times</span>
                                            <i class="fas fa-external-link-alt text-muted"></i>
                                        </a>
                                        <a href="https://www.livemint.com/market" 
                                           target="_blank" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
                                            <span><i class="fas fa-coins text-success me-2"></i>LiveMint Markets</span>
                                            <i class="fas fa-external-link-alt text-muted"></i>
                                        </a>
                                        <a href="https://www.business-standard.com/markets" 
                                           target="_blank" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
                                            <span><i class="fas fa-building text-secondary me-2"></i>Business Standard</span>
                                            <i class="fas fa-external-link-alt text-muted"></i>
                                        </a>
                                    </div>
                                </div>
                                
                                <!-- Company Information -->
                                <div class="col-md-6">
                                    <h6><i class="fas fa-building text-success me-2"></i>Company Information</h6>
                                    <div class="list-group list-group-flush">
                                        <a href="https://www.screener.in/company/${safeStockSymbol.replace('.NS', '')}/" 
                                           target="_blank" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
                                            <span><i class="fas fa-search text-primary me-2"></i>Screener Analysis</span>
                                            <i class="fas fa-external-link-alt text-muted"></i>
                                        </a>
                                        <a href="https://www.tickertape.in/stocks/${safeStockSymbol.replace('.NS', '').toLowerCase()}" 
                                           target="_blank" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
                                            <span><i class="fas fa-tape text-warning me-2"></i>TickerTape Profile</span>
                                            <i class="fas fa-external-link-alt text-muted"></i>
                                        </a>
                                        <a href="https://www.nseindia.com/get-quotes/equity?symbol=${safeStockSymbol.replace('.NS', '')}" 
                                           target="_blank" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
                                            <span><i class="fas fa-chart-bar text-info me-2"></i>NSE Official</span>
                                            <i class="fas fa-external-link-alt text-muted"></i>
                                        </a>
                                        <a href="https://www.bseindia.com/stock-share-price/${safeStockSymbol.replace('.NS', '')}/financials/" 
                                           target="_blank" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
                                            <span><i class="fas fa-calculator text-success me-2"></i>BSE Financials</span>
                                            <i class="fas fa-external-link-alt text-muted"></i>
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Dividend & Corporate Actions -->
                <div class="col-md-6">
                    <div class="card border-0 shadow-sm h-100">
                        <div class="card-header bg-light">
                            <h6><i class="fas fa-coins text-warning me-2"></i>Dividend & Corporate Actions</h6>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <strong>Dividend Information:</strong>
                                <div class="mt-2">
                                    <a href="https://www.moneycontrol.com/stocks/company_info/dividends.php?sc_id=${safeStockSymbol.replace('.NS', '')}" 
                                       target="_blank" class="btn btn-outline-primary btn-sm">
                                        <i class="fas fa-percentage me-1"></i>Dividend History
                                    </a>
                                </div>
                            </div>
                            <div class="mb-3">
                                <strong>Corporate Actions:</strong>
                                <div class="mt-2">
                                    <a href="https://www.nseindia.com/companies-listing/corporate-disclosure/disclosures" 
                                       target="_blank" class="btn btn-outline-info btn-sm">
                                        <i class="fas fa-file-alt me-1"></i>NSE Disclosures
                                    </a>
                                </div>
                            </div>
                            <div class="mb-0">
                                <strong>Annual Reports:</strong>
                                <div class="mt-2">
                                    <a href="https://www.screener.in/company/${safeStockSymbol.replace('.NS', '')}/consolidated/" 
                                       target="_blank" class="btn btn-outline-success btn-sm">
                                        <i class="fas fa-file-pdf me-1"></i>Financial Reports
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Market Outlook -->
                <div class="col-md-6">
                    <div class="card border-0 shadow-sm h-100">
                        <div class="card-header bg-light">
                            <h6><i class="fas fa-calendar-alt text-info me-2"></i>Market Outlook</h6>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <strong>Short Term (1-3 months):</strong>
                                <p class="text-muted mb-1">${sentimentAnalysis.market_outlook.short_term}</p>
                            </div>
                            <div class="mb-3">
                                <strong>Medium Term (6-12 months):</strong>
                                <p class="text-muted mb-1">${sentimentAnalysis.market_outlook.medium_term}</p>
                            </div>
                            <div class="mb-0">
                                <strong>Long Term (2-5 years):</strong>
                                <p class="text-muted mb-0">${sentimentAnalysis.market_outlook.long_term}</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Analyst Research & Reports -->
                <div class="col-12">
                    <div class="card border-0 shadow-sm">
                        <div class="card-header bg-light">
                            <h6><i class="fas fa-users text-primary me-2"></i>Analyst Research & Reports</h6>
                        </div>
                        <div class="card-body">
                            <div class="row g-3">
                                <div class="col-md-4">
                                    <h6>Research Reports:</h6>
                                    <div class="d-grid gap-2">
                                        <a href="https://www.icicidirect.com/idirectcontent/Markets/CompanyResearch.aspx" 
                                           target="_blank" class="btn btn-outline-primary btn-sm">
                                            <i class="fas fa-chart-area me-1"></i>ICICI Direct Research
                                        </a>
                                        <a href="https://www.hdfcsec.com/hsl.research.homepage" 
                                           target="_blank" class="btn btn-outline-info btn-sm">
                                            <i class="fas fa-file-chart me-1"></i>HDFC Securities
                                        </a>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <h6>Price Targets:</h6>
                                    <div class="d-grid gap-2">
                                        <a href="https://www.tickertape.in/stocks/${safeStockSymbol.replace('.NS', '').toLowerCase()}/price-targets" 
                                           target="_blank" class="btn btn-outline-warning btn-sm">
                                            <i class="fas fa-bullseye me-1"></i>Analyst Targets
                                        </a>
                                        <a href="https://www.moneycontrol.com/stocks/company_info/stock_news.php?sc_id=${safeStockSymbol.replace('.NS', '')}" 
                                           target="_blank" class="btn btn-outline-success btn-sm">
                                            <i class="fas fa-star me-1"></i>Ratings & Reviews
                                        </a>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <h6>Earnings & Results:</h6>
                                    <div class="d-grid gap-2">
                                        <a href="https://www.screener.in/company/${safeStockSymbol.replace('.NS', '')}/quarterly-results/" 
                                           target="_blank" class="btn btn-outline-danger btn-sm">
                                            <i class="fas fa-calendar me-1"></i>Quarterly Results
                                        </a>
                                        <a href="https://www.nseindia.com/companies-listing/corporate-disclosure/disclosures" 
                                           target="_blank" class="btn btn-outline-dark btn-sm">
                                            <i class="fas fa-microphone me-1"></i>Earnings Call
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Risk & Opportunities -->
                <div class="col-md-6">
                    <div class="card border-0 shadow-sm h-100">
                        <div class="card-header bg-light">
                            <h6><i class="fas fa-balance-scale text-warning me-2"></i>Risk & Opportunities</h6>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <strong class="text-danger">Risk Factors:</strong>
                                <ul class="list-unstyled mt-2">
                                    ${sentimentAnalysis.risk_factors.map(risk => `
                                        <li class="mb-1"><i class="fas fa-exclamation-triangle text-danger me-2"></i>${risk}</li>
                                    `).join('')}
                                </ul>
                            </div>
                            <div class="mb-0">
                                <strong class="text-success">Opportunities:</strong>
                                <ul class="list-unstyled mt-2">
                                    ${sentimentAnalysis.opportunities.map(opp => `
                                        <li class="mb-1"><i class="fas fa-star text-success me-2"></i>${opp}</li>
                                    `).join('')}
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Peer Comparison -->
                <div class="col-md-6">
                    <div class="card border-0 shadow-sm h-100">
                        <div class="card-header bg-light">
                            <h6><i class="fas fa-chart-line text-success me-2"></i>Peer Comparison & Sector</h6>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <strong>Sector Analysis:</strong>
                                <div class="mt-2">
                                    <a href="https://www.screener.in/screens/71069/all-stocks/?sort=name&order=asc" 
                                       target="_blank" class="btn btn-outline-primary btn-sm">
                                        <i class="fas fa-industry me-1"></i>Sector Comparison
                                    </a>
                                </div>
                            </div>
                            <div class="mb-3">
                                <strong>Peer Analysis:</strong>
                                <div class="mt-2">
                                    <a href="https://www.tickertape.in/stocks/${safeStockSymbol.replace('.NS', '').toLowerCase()}/peers" 
                                       target="_blank" class="btn btn-outline-info btn-sm">
                                        <i class="fas fa-users me-1"></i>Peer Stocks
                                    </a>
                                </div>
                            </div>
                            <div class="mb-0">
                                <strong>Market Trends:</strong>
                                <div class="mt-2">
                                    <a href="https://www.nseindia.com/market-data/securities-available-for-trading" 
                                       target="_blank" class="btn btn-outline-success btn-sm">
                                        <i class="fas fa-trending-up me-1"></i>Market Trends
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- News Summary & Consensus -->
                <div class="col-12">
                    <div class="card border-0 shadow-sm">
                        <div class="card-header bg-light">
                            <h6><i class="fas fa-newspaper text-primary me-2"></i>News Summary & Analyst Consensus</h6>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-8">
                                    <h6>News Impact Summary:</h6>
                                    <p class="text-muted">${sentimentAnalysis.news_summary}</p>
                                </div>
                                <div class="col-md-4 text-center">
                                    <h6>Analyst Consensus:</h6>
                                    <span class="badge bg-${getSentimentColor(sentimentAnalysis.analyst_consensus)} fs-5 px-4 py-3">
                                        ${sentimentAnalysis.analyst_consensus}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- AI Source & Disclaimer -->
                <div class="col-12">
                    <div class="card border-0 bg-light">
                        <div class="card-body">
                            <div class="row align-items-center">
                                <div class="col-md-8">
                                    <small class="text-muted">
                                        <i class="fas fa-robot me-1"></i>
                                        Analysis powered by Google Gemini AI • 
                                        Source: ${sentimentAnalysis.source} • 
                                        Updated: ${sentimentAnalysis.timestamp}
                                    </small>
                                </div>
                                <div class="col-md-4 text-end">
                                    <small class="text-warning">
                                        <i class="fas fa-exclamation-circle me-1"></i>
                                        <strong>Disclaimer:</strong> For informational purposes only. Not investment advice.
                                    </small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                        </small>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = newsHtml;
    }

    updateFundamentals(fundamentals, fundamentalsAnalysis) {
        const container = document.getElementById('fundamentalsContent');
        
        if (!fundamentalsAnalysis) {
            container.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Fundamental analysis temporarily unavailable.
                </div>
            `;
            return;
        }

        const getGradeColor = (grade) => {
            switch(grade) {
                case 'A+': case 'A': return 'success';
                case 'B': return 'primary';
                case 'C': return 'warning';
                case 'D': return 'danger';
                default: return 'secondary';
            }
        };

        const getRatingColor = (rating) => {
            switch(rating) {
                case 'STRONG_BUY': return 'success';
                case 'BUY': return 'success';
                case 'HOLD': return 'warning';
                case 'SELL': return 'danger';
                case 'STRONG_SELL': return 'danger';
                default: return 'secondary';
            }
        };

        const fundamentalsHtml = `
            <div class="row g-4">
                <!-- Valuation Assessment -->
                <div class="col-12">
                    <div class="card border-0 shadow-sm">
                        <div class="card-header bg-light">
                            <h5 class="mb-0"><i class="fas fa-chart-pie text-primary me-2"></i>Valuation Assessment</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-4 text-center">
                                    <h3 class="text-primary">₹${fundamentalsAnalysis.valuation_assessment.intrinsic_value_estimate || 'N/A'}</h3>
                                    <p class="text-muted mb-0">Estimated Fair Value</p>
                                    <span class="badge bg-${fundamentalsAnalysis.valuation_assessment.valuation_rating === 'UNDERVALUED' ? 'success' : fundamentalsAnalysis.valuation_assessment.valuation_rating === 'OVERVALUED' ? 'danger' : 'warning'} mt-2">
                                        ${fundamentalsAnalysis.valuation_assessment.valuation_rating}
                                    </span>
                                </div>
                                <div class="col-md-8">
                                    <h6>Valuation Rationale:</h6>
                                    <p class="text-muted">${fundamentalsAnalysis.valuation_assessment.valuation_rationale}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Financial Health Scorecard -->
                <div class="col-md-6">
                    <div class="card border-0 shadow-sm h-100">
                        <div class="card-header bg-light">
                            <h6><i class="fas fa-heartbeat text-danger me-2"></i>Financial Health Score</h6>
                        </div>
                        <div class="card-body">
                            <div class="text-center mb-3">
                                <div class="financial-score-circle">
                                    <span class="score-number">${fundamentalsAnalysis.financial_health.overall_score}</span>
                                    <span class="score-total">/10</span>
                                </div>
                            </div>
                            <div class="grade-breakdown">
                                <div class="d-flex justify-content-between mb-2">
                                    <span>Profitability:</span>
                                    <span class="badge bg-${getGradeColor(fundamentalsAnalysis.financial_health.profitability_grade)}">${fundamentalsAnalysis.financial_health.profitability_grade}</span>
                                </div>
                                <div class="d-flex justify-content-between mb-2">
                                    <span>Liquidity:</span>
                                    <span class="badge bg-${getGradeColor(fundamentalsAnalysis.financial_health.liquidity_grade)}">${fundamentalsAnalysis.financial_health.liquidity_grade}</span>
                                </div>
                                <div class="d-flex justify-content-between mb-2">
                                    <span>Leverage:</span>
                                    <span class="badge bg-${getGradeColor(fundamentalsAnalysis.financial_health.leverage_grade)}">${fundamentalsAnalysis.financial_health.leverage_grade}</span>
                                </div>
                                <div class="d-flex justify-content-between">
                                    <span>Efficiency:</span>
                                    <span class="badge bg-${getGradeColor(fundamentalsAnalysis.financial_health.efficiency_grade)}">${fundamentalsAnalysis.financial_health.efficiency_grade}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Key Metrics -->
                <div class="col-md-6">
                    <div class="card border-0 shadow-sm h-100">
                        <div class="card-header bg-light">
                            <h6><i class="fas fa-calculator text-success me-2"></i>Key Financial Metrics</h6>
                        </div>
                        <div class="card-body">
                            <div class="fundamental-metrics">
                                <div class="metric-item d-flex justify-content-between mb-2">
                                    <span>Market Cap:</span>
                                    <strong>${this.formatLargeNumber(fundamentals.market_cap)}</strong>
                                </div>
                                <div class="metric-item d-flex justify-content-between mb-2">
                                    <span>P/E Ratio:</span>
                                    <strong>${fundamentals.pe_ratio ? fundamentals.pe_ratio.toFixed(2) : 'N/A'}</strong>
                                </div>
                                <div class="metric-item d-flex justify-content-between mb-2">
                                    <span>Dividend Yield:</span>
                                    <strong>${fundamentals.dividend_yield ? (fundamentals.dividend_yield * 100).toFixed(2) + '%' : 'N/A'}</strong>
                                </div>
                                <div class="metric-item d-flex justify-content-between mb-2">
                                    <span>Sector:</span>
                                    <strong>${fundamentals.sector || 'N/A'}</strong>
                                </div>
                                <div class="metric-item d-flex justify-content-between">
                                    <span>Industry:</span>
                                    <strong>${fundamentals.industry || 'N/A'}</strong>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Strengths & Concerns -->
                <div class="col-md-6">
                    <div class="card border-0 shadow-sm h-100">
                        <div class="card-header bg-light">
                            <h6><i class="fas fa-thumbs-up text-success me-2"></i>Key Strengths</h6>
                        </div>
                        <div class="card-body">
                            <ul class="list-unstyled mb-0">
                                ${fundamentalsAnalysis.key_strengths.map(strength => `
                                    <li class="mb-2"><i class="fas fa-check-circle text-success me-2"></i>${strength}</li>
                                `).join('')}
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="col-md-6">
                    <div class="card border-0 shadow-sm h-100">
                        <div class="card-header bg-light">
                            <h6><i class="fas fa-exclamation-triangle text-warning me-2"></i>Key Concerns</h6>
                        </div>
                        <div class="card-body">
                            <ul class="list-unstyled mb-0">
                                ${fundamentalsAnalysis.key_concerns.map(concern => `
                                    <li class="mb-2"><i class="fas fa-times-circle text-warning me-2"></i>${concern}</li>
                                `).join('')}
                            </ul>
                        </div>
                    </div>
                </div>

                <!-- Growth Prospects -->
                <div class="col-12">
                    <div class="card border-0 shadow-sm">
                        <div class="card-header bg-light">
                            <h6><i class="fas fa-chart-line text-info me-2"></i>Growth Prospects</h6>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-4">
                                    <h6>Revenue Growth Outlook:</h6>
                                    <p class="text-muted">${fundamentalsAnalysis.growth_prospects.revenue_growth_outlook}</p>
                                </div>
                                <div class="col-md-4">
                                    <h6>Profit Margin Trend:</h6>
                                    <p class="text-muted">${fundamentalsAnalysis.growth_prospects.profit_margin_trend}</p>
                                </div>
                                <div class="col-md-4">
                                    <h6>Market Expansion:</h6>
                                    <p class="text-muted">${fundamentalsAnalysis.growth_prospects.market_expansion}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Investment Recommendation -->
                <div class="col-12">
                    <div class="card border-0 shadow-sm">
                        <div class="card-header bg-light">
                            <h6><i class="fas fa-bullseye text-primary me-2"></i>Investment Recommendation</h6>
                        </div>
                        <div class="card-body">
                            <div class="row align-items-center">
                                <div class="col-md-3 text-center">
                                    <span class="badge bg-${getRatingColor(fundamentalsAnalysis.investment_recommendation.rating)} fs-4 px-4 py-3">
                                        ${fundamentalsAnalysis.investment_recommendation.rating}
                                    </span>
                                </div>
                                <div class="col-md-3 text-center">
                                    <h5 class="text-primary mb-0">₹${fundamentalsAnalysis.investment_recommendation.target_price || 'N/A'}</h5>
                                    <small class="text-muted">Target Price</small>
                                </div>
                                <div class="col-md-3 text-center">
                                    <h6 class="mb-0">${fundamentalsAnalysis.investment_recommendation.investment_horizon}</h6>
                                    <small class="text-muted">Investment Horizon</small>
                                </div>
                                <div class="col-md-3">
                                    <h6>Rationale:</h6>
                                    <p class="text-muted mb-0">${fundamentalsAnalysis.investment_recommendation.rationale}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- AI Source -->
                <div class="col-12">
                    <div class="text-center">
                        <small class="text-muted">
                            <i class="fas fa-robot me-1"></i>
                            Analysis powered by Google Gemini AI • 
                            Source: ${fundamentalsAnalysis.source} • 
                            Updated: ${fundamentalsAnalysis.timestamp}
                        </small>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = fundamentalsHtml;
    }

    updateGeminiInsights(geminiAnalysis) {
        const container = document.getElementById('geminiContent');
        
        if (!geminiAnalysis) {
            container.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Gemini AI insights are temporarily unavailable.
                </div>
            `;
            return;
        }

        const getRecommendationColor = (rec) => {
            switch(rec) {
                case 'BUY': return 'success';
                case 'SELL': return 'danger';
                case 'HOLD': return 'warning';
                default: return 'secondary';
            }
        };

        const getRiskLevelColor = (risk) => {
            switch(risk) {
                case 'LOW': return 'success';
                case 'MEDIUM': return 'warning';
                case 'HIGH': return 'danger';
                default: return 'secondary';
            }
        };

        const geminiHtml = `
            <div class="row g-4">
                <!-- Technical Summary -->
                <div class="col-12">
                    <div class="card border-0 bg-light">
                        <div class="card-body">
                            <h6><i class="fas fa-chart-line text-primary me-2"></i>Technical Analysis</h6>
                            <p class="mb-0">${geminiAnalysis.technical_summary || 'Analysis not available'}</p>
                        </div>
                    </div>
                </div>

                <!-- Recommendation and Risk -->
                <div class="col-md-6">
                    <div class="card border-0 h-100">
                        <div class="card-body text-center">
                            <h6><i class="fas fa-thumbs-up text-primary me-2"></i>AI Recommendation</h6>
                            <div class="mb-3">
                                <span class="badge bg-${getRecommendationColor(geminiAnalysis.recommendation)} fs-6 px-3 py-2">
                                    ${geminiAnalysis.recommendation || 'HOLD'}
                                </span>
                            </div>
                            <small class="text-muted">${geminiAnalysis.recommendation_reason || 'No specific reason provided'}</small>
                        </div>
                    </div>
                </div>

                <div class="col-md-6">
                    <div class="card border-0 h-100">
                        <div class="card-body text-center">
                            <h6><i class="fas fa-shield-alt text-primary me-2"></i>Risk Assessment</h6>
                            <div class="mb-3">
                                <span class="badge bg-${getRiskLevelColor(geminiAnalysis.risk_level)} fs-6 px-3 py-2">
                                    ${geminiAnalysis.risk_level || 'MEDIUM'} RISK
                                </span>
                            </div>
                            <small class="text-muted">${geminiAnalysis.risk_explanation || 'Standard market risk applies'}</small>
                        </div>
                    </div>
                </div>

                <!-- Price Targets -->
                ${geminiAnalysis.price_targets ? `
                <div class="col-12">
                    <div class="card border-0">
                        <div class="card-body">
                            <h6><i class="fas fa-target text-primary me-2"></i>Price Targets</h6>
                            <div class="row text-center">
                                <div class="col-4">
                                    <div class="border-end pe-3">
                                        <h5 class="text-danger">₹${geminiAnalysis.price_targets.support?.toFixed(2) || 'N/A'}</h5>
                                        <small class="text-muted">Support</small>
                                    </div>
                                </div>
                                <div class="col-4">
                                    <div class="border-end pe-3">
                                        <h5 class="text-success">₹${geminiAnalysis.price_targets.resistance?.toFixed(2) || 'N/A'}</h5>
                                        <small class="text-muted">Resistance</small>
                                    </div>
                                </div>
                                <div class="col-4">
                                    <h5 class="text-primary">₹${geminiAnalysis.price_targets.target_3m?.toFixed(2) || 'N/A'}</h5>
                                    <small class="text-muted">3M Target</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                ` : ''}

                <!-- Market Outlook -->
                <div class="col-12">
                    <div class="card border-0 bg-light">
                        <div class="card-body">
                            <h6><i class="fas fa-crystal-ball text-primary me-2"></i>Market Outlook</h6>
                            <p class="mb-0">${geminiAnalysis.market_outlook || 'Market outlook analysis not available'}</p>
                        </div>
                    </div>
                </div>

                <!-- Key Factors -->
                ${geminiAnalysis.key_factors && geminiAnalysis.key_factors.length > 0 ? `
                <div class="col-12">
                    <div class="card border-0">
                        <div class="card-body">
                            <h6><i class="fas fa-key text-primary me-2"></i>Key Factors</h6>
                            <div class="row">
                                ${geminiAnalysis.key_factors.map((factor, index) => `
                                    <div class="col-md-6 mb-2">
                                        <div class="d-flex align-items-center">
                                            <i class="fas fa-dot-circle text-primary me-2"></i>
                                            <span>${factor}</span>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                </div>
                ` : ''}

                <!-- AI Source Badge -->
                <div class="col-12">
                    <div class="text-center">
                        <small class="text-muted">
                            <i class="fas fa-robot me-1"></i>
                            Generated by Google Gemini AI • 
                            Source: ${geminiAnalysis.source || 'AI Analysis'}
                        </small>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = geminiHtml;
    }

    formatNumber(num) {
        if (num >= 1e7) {
            return (num / 1e7).toFixed(1) + 'Cr';
        } else if (num >= 1e5) {
            return (num / 1e5).toFixed(1) + 'L';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    formatLargeNumber(num) {
        if (!num) return 'N/A';
        
        if (num >= 1e12) {
            return `₹${(num / 1e12).toFixed(2)}T`;
        } else if (num >= 1e9) {
            return `₹${(num / 1e9).toFixed(2)}B`;
        } else if (num >= 1e7) {
            return `₹${(num / 1e7).toFixed(2)}Cr`;
        } else if (num >= 1e5) {
            return `₹${(num / 1e5).toFixed(2)}L`;
        }
        return `₹${num.toFixed(2)}`;
    }

    showLoading() {
        document.getElementById('loadingSpinner').classList.remove('d-none');
        document.getElementById('analysisResults').classList.add('d-none');
    }

    hideLoading() {
        document.getElementById('loadingSpinner').classList.add('d-none');
    }

    showError(message) {
        document.getElementById('errorText').textContent = message;
        document.getElementById('errorMessage').classList.remove('d-none');
        this.hideLoading();
    }

    hideError() {
        document.getElementById('errorMessage').classList.add('d-none');
    }

    scrollToAnalysis() {
        document.getElementById('analysis').scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new MoneySavyy();
});

// Add smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add loading animation to buttons
document.addEventListener('click', (e) => {
    if (e.target.matches('button') || e.target.closest('button')) {
        const btn = e.target.matches('button') ? e.target : e.target.closest('button');
        if (btn.id === 'searchBtn') {
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
            setTimeout(() => {
                btn.innerHTML = '<i class="fas fa-search"></i> Analyze';
            }, 3000);
        }
    }
});

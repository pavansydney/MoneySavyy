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

            this.currentStock = data;
            this.displayAnalysis(data);
            this.hideLoading();

        } catch (error) {
            this.showError('Failed to analyze stock. Please try again.');
            console.error('Analysis error:', error);
        }
    }

    displayAnalysis(data) {
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
        this.updateRecommendation(data.recommendation);

        // Update chart
        this.updateChart(data.chart);

        // Update prediction tab
        this.updatePrediction(data.prediction);

        // Update news tab
        this.updateNews(data.news);

        // Update fundamentals tab
        this.updateFundamentals(data.fundamentals);

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
    }

    updateRecommendation(rec) {
        const recDiv = document.getElementById('recommendation');
        const badgeClass = `badge bg-${rec.color}`;
        
        recDiv.innerHTML = `
            <span class="${badgeClass}">
                <i class="fas fa-chart-line me-1"></i>
                ${rec.recommendation}
            </span>
            <small class="d-block mt-1 text-muted">
                Confidence: ${rec.confidence} | Score: ${rec.score.toFixed(1)}
            </small>
        `;
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

    updatePrediction(prediction) {
        const container = document.getElementById('predictionContent');
        
        if (prediction.error) {
            container.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    ${prediction.error}
                </div>
            `;
            return;
        }

        const trendColor = prediction.predicted_change_percent >= 0 ? 'success' : 'danger';
        const trendIcon = prediction.predicted_change_percent >= 0 ? 'fa-arrow-up' : 'fa-arrow-down';

        container.innerHTML = `
            <div class="prediction-card">
                <div class="row text-center">
                    <div class="col-md-3">
                        <div class="prediction-metric">
                            <h4>${prediction.model_used}</h4>
                            <p class="mb-0">Model Used</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="prediction-metric">
                            <h4>${(prediction.accuracy * 100).toFixed(1)}%</h4>
                            <p class="mb-0">Accuracy</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="prediction-metric">
                            <h4>₹${prediction.predicted_30d_avg.toFixed(2)}</h4>
                            <p class="mb-0">30-Day Avg Prediction</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="prediction-metric">
                            <h4 class="text-${trendColor}">
                                <i class="fas ${trendIcon} me-1"></i>
                                ${prediction.predicted_change_percent >= 0 ? '+' : ''}${prediction.predicted_change_percent.toFixed(1)}%
                            </h4>
                            <p class="mb-0">Expected Change</p>
                        </div>
                    </div>
                </div>
            </div>
            <div class="mt-3">
                <h6><i class="fas fa-lightbulb text-warning me-2"></i>AI Insights:</h6>
                <ul class="list-unstyled">
                    <li><i class="fas fa-check text-success me-2"></i>Model trained on ${prediction.model_used.toLowerCase()} regression</li>
                    <li><i class="fas fa-check text-success me-2"></i>Analysis based on price history, volume, and volatility</li>
                    <li><i class="fas fa-check text-success me-2"></i>Prediction confidence: ${(prediction.accuracy * 100).toFixed(1)}%</li>
                </ul>
            </div>
        `;
    }

    updateNews(newsData) {
        const container = document.getElementById('newsContent');
        
        if (!newsData || newsData.length === 0) {
            container.innerHTML = '<p class="text-muted">No recent news available.</p>';
            return;
        }

        const newsHtml = newsData.map(news => {
            const sentimentClass = news.sentiment.toLowerCase();
            const sentimentColor = sentimentClass === 'positive' ? 'success' : sentimentClass === 'negative' ? 'danger' : 'warning';
            const sentimentIcon = sentimentClass === 'positive' ? 'fa-smile' : sentimentClass === 'negative' ? 'fa-frown' : 'fa-meh';

            return `
                <div class="news-item sentiment-${sentimentClass}">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h6 class="mb-0">${news.title}</h6>
                        <span class="sentiment-badge badge bg-${sentimentColor}">
                            <i class="fas ${sentimentIcon} me-1"></i>
                            ${news.sentiment}
                        </span>
                    </div>
                    <p class="text-muted mb-2">${news.summary}</p>
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">
                            <i class="fas fa-clock me-1"></i>
                            ${news.published} | ${news.source}
                        </small>
                        ${news.link !== '#' && news.link !== 'N/A' ? 
                            `<a href="${news.link}" target="_blank" class="btn btn-sm btn-outline-primary">
                                <i class="fas fa-external-link-alt me-1"></i>Read More
                            </a>` : ''
                        }
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = newsHtml;
    }

    updateFundamentals(fundamentals) {
        const container = document.getElementById('fundamentalsContent');
        
        const fundamentalItems = [
            { label: 'Market Cap', value: this.formatLargeNumber(fundamentals.market_cap), icon: 'fa-building' },
            { label: 'P/E Ratio', value: fundamentals.pe_ratio ? fundamentals.pe_ratio.toFixed(2) : 'N/A', icon: 'fa-calculator' },
            { label: 'Dividend Yield', value: fundamentals.dividend_yield ? (fundamentals.dividend_yield * 100).toFixed(2) + '%' : 'N/A', icon: 'fa-percent' },
            { label: '52W High', value: fundamentals.week_52_high ? `₹${fundamentals.week_52_high.toFixed(2)}` : 'N/A', icon: 'fa-arrow-up' },
            { label: '52W Low', value: fundamentals.week_52_low ? `₹${fundamentals.week_52_low.toFixed(2)}` : 'N/A', icon: 'fa-arrow-down' },
            { label: 'Sector', value: fundamentals.sector || 'N/A', icon: 'fa-industry' },
            { label: 'Industry', value: fundamentals.industry || 'N/A', icon: 'fa-cogs' }
        ];

        const fundamentalsHtml = `
            <div class="fundamentals-grid">
                ${fundamentalItems.map(item => `
                    <div class="fundamental-item">
                        <i class="fas ${item.icon} text-primary mb-2"></i>
                        <h5>${item.value}</h5>
                        <p class="mb-0 text-muted">${item.label}</p>
                    </div>
                `).join('')}
            </div>
        `;

        container.innerHTML = fundamentalsHtml;
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

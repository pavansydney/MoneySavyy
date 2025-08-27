# Complete test suite for Gemini AI News & Fundamentals integration
# PowerShell Version for Windows

Write-Host "🧪 Testing Gemini AI Enhanced Stock Analysis Features" -ForegroundColor Cyan
Write-Host "=================================================="

$BaseURL = "http://localhost:5000"

function Test-API {
    param($Url, $TestName)
    Write-Host ""
    Write-Host $TestName -ForegroundColor Yellow
    Write-Host ("-" * $TestName.Length)
    
    try {
        $response = Invoke-RestMethod -Uri $Url -Method GET -ContentType "application/json"
        Write-Host "✅ HTTP Status: 200" -ForegroundColor Green
        $response | ConvertTo-Json -Depth 10 | Write-Host
    }
    catch {
        Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Status Code: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    }
}

# Test 1: Complete Stock Analysis with Gemini AI
Test-API -Url "$BaseURL/api/analyze/TCS" -TestName "1. 📈 Testing Complete Stock Analysis with Gemini AI (TCS)"

# Test 2: News Sentiment Analysis
Test-API -Url "$BaseURL/api/news-sentiment/TCS" -TestName "2. 📰 Testing News Sentiment Analysis Endpoint"

# Test 3: Fundamentals Analysis
Test-API -Url "$BaseURL/api/fundamentals/TCS" -TestName "3. 📊 Testing Fundamentals Analysis Endpoint"

# Test 4: Different Stocks
Write-Host ""
Write-Host "4. 🔍 Testing with Different Stocks" -ForegroundColor Yellow
Write-Host "------------------------------------"

$stocks = @("RELIANCE", "INFY", "HDFCBANK", "ICICIBANK")

foreach ($stock in $stocks) {
    Write-Host "Testing $stock..." -ForegroundColor Cyan
    try {
        $response = Invoke-RestMethod -Uri "$BaseURL/api/analyze/$stock" -Method GET -ContentType "application/json"
        Write-Host "✅ $stock analysis completed" -ForegroundColor Green
        Write-Host "  Symbol: $($response.symbol)"
        Write-Host "  Company: $($response.company_name)"
        Write-Host "  Gemini Recommendation: $($response.gemini_analysis.recommendation)"
        Write-Host "  Sentiment: $($response.news_sentiment.sentiment_label)"
        Write-Host "  Fundamentals Rating: $($response.fundamentals_analysis.investment_recommendation.rating)"
    }
    catch {
        Write-Host "❌ Error testing $stock" -ForegroundColor Red
    }
    Write-Host ""
}

# Test 5: Gemini Models
Test-API -Url "$BaseURL/api/gemini-models" -TestName "5. 🤖 Testing Gemini Models Endpoint"

# Test 6: Gemini Health Check
Test-API -Url "$BaseURL/api/test-gemini" -TestName "6. ⚡ Testing Gemini Health Check"

Write-Host ""
Write-Host "✅ All tests completed!" -ForegroundColor Green
Write-Host "======================"
Write-Host "Check the responses above for:" -ForegroundColor Cyan
Write-Host "- HTTP Status 200 for successful requests"
Write-Host "- Proper JSON structure in responses"
Write-Host "- Gemini AI analysis data in all responses"
Write-Host "- News sentiment and fundamentals analysis"

#!/bin/bash
# Complete test suite for Gemini AI News & Fundamentals integration

echo "🧪 Testing Gemini AI Enhanced Stock Analysis Features"
echo "=================================================="

BASE_URL="http://localhost:5000"

echo ""
echo "1. 📈 Testing Complete Stock Analysis with Gemini AI (TCS)"
echo "-----------------------------------------------------------"
curl -X GET "$BASE_URL/api/analyze/TCS" \
  -H "Content-Type: application/json" \
  -w "\nHTTP Status: %{http_code}\n" \
  -s | jq '.' 2>/dev/null || echo "Response received (jq not available for formatting)"

echo ""
echo "2. 📰 Testing News Sentiment Analysis Endpoint"
echo "-----------------------------------------------"
curl -X GET "$BASE_URL/api/news-sentiment/TCS" \
  -H "Content-Type: application/json" \
  -w "\nHTTP Status: %{http_code}\n" \
  -s | jq '.' 2>/dev/null || echo "Response received (jq not available for formatting)"

echo ""
echo "3. 📊 Testing Fundamentals Analysis Endpoint"
echo "---------------------------------------------"
curl -X GET "$BASE_URL/api/fundamentals/TCS" \
  -H "Content-Type: application/json" \
  -w "\nHTTP Status: %{http_code}\n" \
  -s | jq '.' 2>/dev/null || echo "Response received (jq not available for formatting)"

echo ""
echo "4. 🔍 Testing with Different Stocks"
echo "------------------------------------"

stocks=("RELIANCE" "INFY" "HDFCBANK" "ICICIBANK")

for stock in "${stocks[@]}"; do
    echo "Testing $stock..."
    curl -X GET "$BASE_URL/api/analyze/$stock" \
      -H "Content-Type: application/json" \
      -w "\nHTTP Status: %{http_code}\n" \
      -s | jq -r '.symbol, .company_name, .gemini_analysis.recommendation, .news_sentiment.sentiment_label, .fundamentals_analysis.investment_recommendation.rating' 2>/dev/null || echo "✅ $stock analysis completed"
    echo ""
done

echo ""
echo "5. 🤖 Testing Gemini Models Endpoint"
echo "------------------------------------"
curl -X GET "$BASE_URL/api/gemini-models" \
  -H "Content-Type: application/json" \
  -w "\nHTTP Status: %{http_code}\n" \
  -s | jq '.' 2>/dev/null || echo "Response received (jq not available for formatting)"

echo ""
echo "6. ⚡ Testing Gemini Health Check"
echo "---------------------------------"
curl -X GET "$BASE_URL/api/test-gemini" \
  -H "Content-Type: application/json" \
  -w "\nHTTP Status: %{http_code}\n" \
  -s | jq '.' 2>/dev/null || echo "Response received (jq not available for formatting)"

echo ""
echo "✅ All tests completed!"
echo "======================"
echo "Check the responses above for:"
echo "- HTTP Status 200 for successful requests"
echo "- Proper JSON structure in responses"
echo "- Gemini AI analysis data in all responses"
echo "- News sentiment and fundamentals analysis"

#!/bin/bash
# Quick API tests using curl

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                     LIVE API TESTS - CURL COMMANDS                           ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

BASE_URL="http://localhost:7860"
EMAIL="23f2003858@ds.study.iitm.ac.in"
SECRET="12356789"

# Test 1: Health Check
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 1: Health Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" $BASE_URL/)
http_code=$(echo "$response" | grep "HTTP_STATUS" | cut -d: -f2)
body=$(echo "$response" | grep -v "HTTP_STATUS")

echo "Status Code: $http_code"
echo "Response: $body"
if [ "$http_code" = "200" ]; then
    echo "✅ PASS: Health check working"
else
    echo "❌ FAIL: Expected 200, got $http_code"
fi
echo ""

# Test 2: Invalid Secret
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 2: Invalid Secret Rejection"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST $BASE_URL/receive_request \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$EMAIL\",\"secret\":\"wrong_secret\",\"url\":\"https://example.com/test\"}")
http_code=$(echo "$response" | grep "HTTP_STATUS" | cut -d: -f2)
body=$(echo "$response" | grep -v "HTTP_STATUS")

echo "Status Code: $http_code"
echo "Response: $body"
if [ "$http_code" = "403" ]; then
    echo "✅ PASS: Invalid secret rejected"
else
    echo "❌ FAIL: Expected 403, got $http_code"
fi
echo ""

# Test 3: Missing Fields
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 3: Missing Required Fields"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST $BASE_URL/receive_request \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$EMAIL\",\"secret\":\"$SECRET\"}")
http_code=$(echo "$response" | grep "HTTP_STATUS" | cut -d: -f2)
body=$(echo "$response" | grep -v "HTTP_STATUS")

echo "Status Code: $http_code"
echo "Response: $body"
if [ "$http_code" = "400" ] || [ "$http_code" = "422" ]; then
    echo "✅ PASS: Missing fields detected"
else
    echo "❌ FAIL: Expected 400/422, got $http_code"
fi
echo ""

# Test 4: Valid Request
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 4: Valid Request Acceptance"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST $BASE_URL/receive_request \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$EMAIL\",\"secret\":\"$SECRET\",\"url\":\"https://example.com/test-quiz\"}")
http_code=$(echo "$response" | grep "HTTP_STATUS" | cut -d: -f2)
body=$(echo "$response" | grep -v "HTTP_STATUS")

echo "Status Code: $http_code"
echo "Response: $body"
if [ "$http_code" = "200" ]; then
    echo "✅ PASS: Valid request accepted"
    echo "⏳ Quiz solving started in background (check server logs)"
else
    echo "❌ FAIL: Expected 200, got $http_code"
fi
echo ""

# Test 5: Malformed JSON
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 5: Malformed JSON Handling"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST $BASE_URL/receive_request \
    -H "Content-Type: application/json" \
    -d "not valid json")
http_code=$(echo "$response" | grep "HTTP_STATUS" | cut -d: -f2)
body=$(echo "$response" | grep -v "HTTP_STATUS")

echo "Status Code: $http_code"
echo "Response: $body"
if [ "$http_code" = "400" ] || [ "$http_code" = "422" ]; then
    echo "✅ PASS: Malformed JSON rejected"
else
    echo "❌ FAIL: Expected 400/422, got $http_code"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎉 API Tests Complete!"
echo ""
echo "Check results above. All critical endpoints tested:"
echo "  ✓ Health check (GET /)"
echo "  ✓ Invalid secret handling (403)"
echo "  ✓ Missing fields validation (400/422)"
echo "  ✓ Valid request acceptance (200)"
echo "  ✓ Malformed JSON handling (400/422)"
echo ""
echo "Server logs show background quiz solving in progress."
echo ""

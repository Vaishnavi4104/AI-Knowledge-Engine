"""
Test script for API endpoints
Run this after starting the server: python test_endpoints.py
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n" + "="*50)
    print("1. Testing Health Endpoint")
    print("="*50)
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Server not running! Start the server first.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_analyze_ticket():
    """Test analyze ticket endpoint"""
    print("\n" + "="*50)
    print("2. Testing Analyze Ticket Endpoint")
    print("="*50)
    try:
        payload = {
            "text": "My payment failed and I need help urgently. The transaction was declined."
        }
        response = requests.post(
            f"{BASE_URL}/api/analyze_ticket",
            json=payload,
            timeout=30
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_recommend():
    """Test recommend endpoint"""
    print("\n" + "="*50)
    print("3. Testing Recommend Endpoint")
    print("="*50)
    try:
        payload = {
            "text": "Unable to login to my account after changing password"
        }
        response = requests.post(
            f"{BASE_URL}/api/recommend",
            json=payload,
            timeout=30
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_topics():
    """Test topics endpoint"""
    print("\n" + "="*50)
    print("4. Testing Topics Endpoint")
    print("="*50)
    try:
        response = requests.get(f"{BASE_URL}/api/topics", timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_usage():
    """Test usage endpoint"""
    print("\n" + "="*50)
    print("5. Testing Usage Endpoint")
    print("="*50)
    try:
        response = requests.get(f"{BASE_URL}/api/usage", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n🚀 Starting API Endpoint Tests")
    print("="*50)
    print("Make sure the server is running at http://localhost:8000")
    print("="*50)
    
    # Wait a bit for server to be ready
    print("\n⏳ Waiting 3 seconds for server to be ready...")
    time.sleep(3)
    
    # Test health first
    if not test_health():
        print("\n❌ Server is not running. Please start it first:")
        print("   uvicorn main:app --host 127.0.0.1 --port 8000 --reload")
        return
    
    # Run all tests
    results = []
    results.append(("Health", test_health()))
    results.append(("Analyze Ticket", test_analyze_ticket()))
    results.append(("Recommend", test_recommend()))
    results.append(("Topics", test_topics()))
    results.append(("Usage", test_usage()))
    
    # Summary
    print("\n" + "="*50)
    print("📊 Test Summary")
    print("="*50)
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")

if __name__ == "__main__":
    main()



#!/usr/bin/env python3
"""
Integration Test Suite
======================

This script tests the integration between all system components.
"""

import os
import sys
import requests
import time
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SERVICES = {
    'Lead Scoring': 'http://localhost:5001',
    'Property Search': 'http://localhost:5002',
    'Property Valuation': 'http://localhost:5003',
    'Email Marketing': 'http://localhost:5004',
    'Dashboard Analytics': 'http://localhost:5005',
    'Data Collection': 'http://localhost:5006',
    'Web Interface': 'http://localhost:3000'
}

def test_service_health(name, url):
    """Test if a service is healthy"""
    try:
        response = requests.get(f"{url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {name}: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ {name}: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {name}: Connection failed ({e})")
        return False

def test_lead_scoring_api():
    """Test lead scoring API"""
    print("\n🧪 Testing Lead Scoring API...")
    
    test_data = {
        "user_id": "test_user_123",
        "interactions": [
            {"type": "page_view", "page": "/properties", "duration": 120},
            {"type": "property_view", "property_id": "prop_123", "duration": 300}
        ]
    }
    
    try:
        # Test interaction tracking
        response = requests.post(
            "http://localhost:5001/api/track-interaction",
            json={
                "user_id": "test_user_123",
                "type": "page_view",
                "page_url": "/test",
                "duration": 60
            },
            timeout=10
        )
        
        if response.status_code in [200, 404]:  # 404 is ok for test user
            print("✅ Lead scoring API responding")
            return True
        else:
            print(f"❌ Lead scoring API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Lead scoring API test failed: {e}")
        return False

def test_property_search_api():
    """Test property search API"""
    print("\n🧪 Testing Property Search API...")
    
    test_filters = {
        "filters": {
            "property_type": "apartment",
            "min_price": 100000,
            "max_price": 500000,
            "city": "Milano"
        },
        "limit": 10
    }
    
    try:
        response = requests.post(
            "http://localhost:5002/api/search",
            json=test_filters,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Property search API responding - found {data.get('total_found', 0)} properties")
            return True
        else:
            print(f"❌ Property search API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Property search API test failed: {e}")
        return False

def test_valuation_api():
    """Test property valuation API"""
    print("\n🧪 Testing Property Valuation API...")
    
    test_property = {
        "property_data": {
            "square_meters": 80,
            "bedrooms": 2,
            "bathrooms": 1,
            "city": "Milano",
            "condition": "good",
            "building_year": 2010
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:5003/api/valuate",
            json=test_property,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            valuation = data.get('valuation', {})
            estimated_value = valuation.get('estimated_value', 0)
            print(f"✅ Property valuation API responding - estimated value: €{estimated_value:,.2f}")
            return True
        else:
            print(f"❌ Property valuation API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Property valuation API test failed: {e}")
        return False

def test_web_interface():
    """Test web interface"""
    print("\n🧪 Testing Web Interface...")
    
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        
        if response.status_code == 200:
            if "RealEstate AI" in response.text:
                print("✅ Web interface responding with correct content")
                return True
            else:
                print("⚠️  Web interface responding but content may be incorrect")
                return False
        else:
            print(f"❌ Web interface error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Web interface test failed: {e}")
        return False

def test_n8n_connection():
    """Test n8n connection"""
    print("\n🧪 Testing n8n Connection...")
    
    try:
        response = requests.get("http://localhost:5678/healthz", timeout=5)
        
        if response.status_code == 200:
            print("✅ n8n is accessible")
            return True
        else:
            print(f"❌ n8n connection error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ n8n connection test failed: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 INTEGRATION TEST SUITE")
    print("=" * 60)
    
    all_tests_passed = True
    
    # Test service health
    print("🔍 Testing Service Health...")
    for name, url in SERVICES.items():
        if not test_service_health(name, url):
            all_tests_passed = False
    
    # Wait a moment for services to be ready
    time.sleep(2)
    
    # Test APIs
    api_tests = [
        test_lead_scoring_api,
        test_property_search_api,
        test_valuation_api,
        test_web_interface,
        test_n8n_connection
    ]
    
    for test_func in api_tests:
        if not test_func():
            all_tests_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("✅ ALL INTEGRATION TESTS PASSED!")
        print("\n🎉 Your AI-powered real estate system is ready to use!")
        print("\nNext steps:")
        print("1. Open http://localhost:3000 to access the dashboard")
        print("2. Configure your Open WebUI at https://ai.intelligentb2b.com")
        print("3. Import n8n workflows at http://localhost:5678")
        print("4. Add real property data to your Baserow database")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease check:")
        print("1. All services are running")
        print("2. Environment variables are properly set")
        print("3. Baserow connection is working")
        print("4. No port conflicts exist")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

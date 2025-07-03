#!/usr/bin/env python3
"""
Test Baserow Connection
======================

This script tests the connection to your Baserow instance and verifies
that all required tables exist and are accessible.
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASEROW_API_URL = os.getenv("BASEROW_API_URL", "https://dayta.intelligentb2b.com/api")
BASEROW_TOKEN = os.getenv("BASEROW_TOKEN")

def test_baserow_connection():
    """Test connection to Baserow API"""
    print("🔍 Testing Baserow Connection...")
    print(f"API URL: {BASEROW_API_URL}")
    
    if not BASEROW_TOKEN:
        print("❌ BASEROW_TOKEN not found in environment variables")
        return False
    
    headers = {
        'Authorization': f'Token {BASEROW_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Test basic API access
        response = requests.get(f"{BASEROW_API_URL}/applications/", headers=headers)
        
        if response.status_code == 200:
            print("✅ Successfully connected to Baserow API")
            applications = response.json()
            print(f"📊 Found {len(applications)} applications")
            
            # List applications
            for app in applications:
                print(f"   - {app['name']} (ID: {app['id']})")
            
            return True
        else:
            print(f"❌ Failed to connect to Baserow API: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error connecting to Baserow: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_table_access():
    """Test access to required tables"""
    print("\n🔍 Testing Table Access...")
    
    table_ids = {
        'BASEROW_PROPERTIES_TABLE_ID': 'Properties',
        'BASEROW_USERS_TABLE_ID': 'Users',
        'BASEROW_LEADS_TABLE_ID': 'Leads',
        'BASEROW_INTERACTIONS_TABLE_ID': 'Interactions',
        'BASEROW_DEALS_TABLE_ID': 'Deals',
        'BASEROW_MARKET_DATA_TABLE_ID': 'Market Data',
        'BASEROW_EMAIL_CAMPAIGNS_TABLE_ID': 'Email Campaigns',
        'BASEROW_ANALYTICS_TABLE_ID': 'Analytics'
    }
    
    headers = {
        'Authorization': f'Token {BASEROW_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    all_accessible = True
    
    for env_var, table_name in table_ids.items():
        table_id = os.getenv(env_var)
        
        if not table_id:
            print(f"⚠️  {env_var} not set in environment variables")
            continue
        
        try:
            url = f"{BASEROW_API_URL}/database/rows/table/{table_id}/"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {table_name} table accessible (ID: {table_id}) - {data.get('count', 0)} rows")
            else:
                print(f"❌ {table_name} table not accessible: {response.status_code}")
                all_accessible = False
                
        except Exception as e:
            print(f"❌ Error accessing {table_name} table: {e}")
            all_accessible = False
    
    return all_accessible

def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 BASEROW CONNECTION TEST")
    print("=" * 60)
    
    # Test connection
    connection_ok = test_baserow_connection()
    
    if connection_ok:
        # Test table access
        tables_ok = test_table_access()
        
        if tables_ok:
            print("\n✅ All tests passed! Your Baserow setup is ready.")
            print("\n📝 Next steps:")
            print("1. Start your Python services")
            print("2. Configure n8n workflows")
            print("3. Test the web interface")
            return True
        else:
            print("\n⚠️  Some tables are not accessible.")
            print("Run 'python setup_baserow_tables.py' to create missing tables.")
            return False
    else:
        print("\n❌ Connection test failed.")
        print("Please check your BASEROW_TOKEN and BASEROW_API_URL settings.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

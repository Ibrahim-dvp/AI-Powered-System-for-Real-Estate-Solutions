# External Portal Integration and Data Collection

**Integration:** n8n Workflows + API Connectors + Data Processing + Baserow Storage  
**Date:** January 7, 2025

## Overview

This system integrates with major Italian real estate portals to collect property data, market insights, and lead information in real-time. It uses both official APIs and ethical web scraping to gather comprehensive market intelligence.

## Supported Portals

### 1. Official API Integrations

**Immobiliare.it (REST-XML API)**
- Property listings and details
- Market statistics and trends
- Search alerts and notifications
- Lead generation data

**Idealista.it (OAuth2 API, JSON)**
- Property database access
- Market analysis data
- Price history and trends
- Neighborhood statistics

**OpenAPI (Quotazioni Start)**
- Property valuations and pricing
- Registry data and transactions
- Market indices and benchmarks
- Investment analysis data

### 2. Web Scraping Integrations

**Supported Portals:**
- Tecnocasa.it
- Casa.it
- Subito.it
- Bakeca.it
- Trovacasa.net
- Ccasa.it
- Mitula.it
- Trovit.it

**Social Media Monitoring:**
- Facebook real estate groups
- LinkedIn property networks
- Instagram real estate accounts
- Twitter market discussions

## Part 1: API Integration Architecture

### 1.1 Immobiliare.it Integration

```python
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import os

class ImmobiliareAPI:
    def __init__(self):
        self.base_url = "https://api.immobiliare.it"
        self.api_key = os.getenv('IMMOBILIARE_API_KEY')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/xml',
            'Accept': 'application/xml'
        }
    
    def search_properties(self, filters):
        """Search properties with specific filters"""
        endpoint = f"{self.base_url}/search"
        
        # Build XML request
        search_xml = self.build_search_xml(filters)
        
        response = requests.post(endpoint, data=search_xml, headers=self.headers)
        
        if response.status_code == 200:
            return self.parse_property_xml(response.content)
        else:
            raise Exception(f"API Error: {response.status_code}")
    
    def build_search_xml(self, filters):
        """Build XML search request"""
        root = ET.Element("PropertySearch")
        
        # Location filters
        if filters.get('city'):
            location = ET.SubElement(root, "Location")
            ET.SubElement(location, "City").text = filters['city']
        
        if filters.get('province'):
            ET.SubElement(location, "Province").text = filters['province']
        
        # Property type
        if filters.get('property_type'):
            ET.SubElement(root, "PropertyType").text = filters['property_type']
        
        # Price range
        if filters.get('min_price') or filters.get('max_price'):
            price_range = ET.SubElement(root, "PriceRange")
            if filters.get('min_price'):
                ET.SubElement(price_range, "Min").text = str(filters['min_price'])
            if filters.get('max_price'):
                ET.SubElement(price_range, "Max").text = str(filters['max_price'])
        
        # Size range
        if filters.get('min_size') or filters.get('max_size'):
            size_range = ET.SubElement(root, "SizeRange")
            if filters.get('min_size'):
                ET.SubElement(size_range, "Min").text = str(filters['min_size'])
            if filters.get('max_size'):
                ET.SubElement(size_range, "Max").text = str(filters['max_size'])
        
        return ET.tostring(root, encoding='unicode')
    
    def parse_property_xml(self, xml_content):
        """Parse XML response to extract property data"""
        root = ET.fromstring(xml_content)
        properties = []
        
        for property_elem in root.findall('.//Property'):
            property_data = {
                'id': property_elem.find('ID').text if property_elem.find('ID') is not None else '',
                'title': property_elem.find('Title').text if property_elem.find('Title') is not None else '',
                'description': property_elem.find('Description').text if property_elem.find('Description') is not None else '',
                'price': int(property_elem.find('Price').text) if property_elem.find('Price') is not None else 0,
                'size': int(property_elem.find('Size').text) if property_elem.find('Size') is not None else 0,
                'rooms': int(property_elem.find('Rooms').text) if property_elem.find('Rooms') is not None else 0,
                'bathrooms': int(property_elem.find('Bathrooms').text) if property_elem.find('Bathrooms') is not None else 0,
                'location': {
                    'city': property_elem.find('.//City').text if property_elem.find('.//City') is not None else '',
                    'province': property_elem.find('.//Province').text if property_elem.find('.//Province') is not None else '',
                    'address': property_elem.find('.//Address').text if property_elem.find('.//Address') is not None else '',
                    'latitude': float(property_elem.find('.//Latitude').text) if property_elem.find('.//Latitude') is not None else 0,
                    'longitude': float(property_elem.find('.//Longitude').text) if property_elem.find('.//Longitude') is not None else 0
                },
                'features': self.parse_features(property_elem.find('Features')),
                'images': self.parse_images(property_elem.find('Images')),
                'contact': self.parse_contact(property_elem.find('Contact')),
                'published_date': property_elem.find('PublishedDate').text if property_elem.find('PublishedDate') is not None else '',
                'updated_date': property_elem.find('UpdatedDate').text if property_elem.find('UpdatedDate') is not None else ''
            }
            properties.append(property_data)
        
        return properties
    
    def parse_features(self, features_elem):
        """Parse property features"""
        if features_elem is None:
            return []
        
        features = []
        for feature in features_elem.findall('Feature'):
            features.append(feature.text)
        
        return features
    
    def parse_images(self, images_elem):
        """Parse property images"""
        if images_elem is None:
            return []
        
        images = []
        for image in images_elem.findall('Image'):
            images.append({
                'url': image.find('URL').text if image.find('URL') is not None else '',
                'caption': image.find('Caption').text if image.find('Caption') is not None else ''
            })
        
        return images
    
    def parse_contact(self, contact_elem):
        """Parse contact information"""
        if contact_elem is None:
            return {}
        
        return {
            'agency': contact_elem.find('Agency').text if contact_elem.find('Agency') is not None else '',
            'agent': contact_elem.find('Agent').text if contact_elem.find('Agent') is not None else '',
            'phone': contact_elem.find('Phone').text if contact_elem.find('Phone') is not None else '',
            'email': contact_elem.find('Email').text if contact_elem.find('Email') is not None else ''
        }
    
    def get_market_statistics(self, location, property_type=None):
        """Get market statistics for a location"""
        endpoint = f"{self.base_url}/market/statistics"
        
        params = {
            'location': location,
            'period': '12months'
        }
        
        if property_type:
            params['property_type'] = property_type
        
        response = requests.get(endpoint, params=params, headers=self.headers)
        
        if response.status_code == 200:
            return self.parse_market_xml(response.content)
        else:
            raise Exception(f"Market API Error: {response.status_code}")
    
    def parse_market_xml(self, xml_content):
        """Parse market statistics XML"""
        root = ET.fromstring(xml_content)
        
        return {
            'average_price': float(root.find('.//AveragePrice').text) if root.find('.//AveragePrice') is not None else 0,
            'price_per_sqm': float(root.find('.//PricePerSqm').text) if root.find('.//PricePerSqm') is not None else 0,
            'total_listings': int(root.find('.//TotalListings').text) if root.find('.//TotalListings') is not None else 0,
            'new_listings': int(root.find('.//NewListings').text) if root.find('.//NewListings') is not None else 0,
            'sold_properties': int(root.find('.//SoldProperties').text) if root.find('.//SoldProperties') is not None else 0,
            'days_on_market': int(root.find('.//DaysOnMarket').text) if root.find('.//DaysOnMarket') is not None else 0,
            'price_trend': root.find('.//PriceTrend').text if root.find('.//PriceTrend') is not None else 'stable'
        }
```

### 1.2 Idealista.it Integration

```python
import requests
import base64
from datetime import datetime, timedelta

class IdealistaAPI:
    def __init__(self):
        self.base_url = "https://api.idealista.com"
        self.client_id = os.getenv('IDEALISTA_CLIENT_ID')
        self.client_secret = os.getenv('IDEALISTA_CLIENT_SECRET')
        self.access_token = None
        self.token_expires = None
        
        self.authenticate()
    
    def authenticate(self):
        """OAuth2 authentication"""
        auth_url = f"{self.base_url}/oauth/token"
        
        # Encode credentials
        credentials = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        
        headers = {
            'Authorization': f'Basic {credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'client_credentials',
            'scope': 'read'
        }
        
        response = requests.post(auth_url, headers=headers, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data['access_token']
            self.token_expires = datetime.now() + timedelta(seconds=token_data['expires_in'])
        else:
            raise Exception(f"Authentication failed: {response.status_code}")
    
    def ensure_authenticated(self):
        """Ensure token is valid"""
        if not self.access_token or datetime.now() >= self.token_expires:
            self.authenticate()
    
    def search_properties(self, filters):
        """Search properties using Idealista API"""
        self.ensure_authenticated()
        
        endpoint = f"{self.base_url}/3.5/es/search"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        # Build search parameters
        params = self.build_search_params(filters)
        
        response = requests.post(endpoint, json=params, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Search API Error: {response.status_code}")
    
    def build_search_params(self, filters):
        """Build search parameters for Idealista API"""
        params = {
            'operation': filters.get('operation', 'sale'),  # sale or rent
            'propertyType': filters.get('property_type', 'homes'),
            'center': f"{filters.get('latitude', 41.9028)},{filters.get('longitude', 12.4964)}",
            'distance': filters.get('distance', 5000),  # meters
            'numPage': filters.get('page', 1),
            'maxItems': filters.get('max_items', 50)
        }
        
        # Price filters
        if filters.get('min_price'):
            params['minPrice'] = filters['min_price']
        if filters.get('max_price'):
            params['maxPrice'] = filters['max_price']
        
        # Size filters
        if filters.get('min_size'):
            params['minSize'] = filters['min_size']
        if filters.get('max_size'):
            params['maxSize'] = filters['max_size']
        
        # Room filters
        if filters.get('min_rooms'):
            params['minRooms'] = filters['min_rooms']
        if filters.get('max_rooms'):
            params['maxRooms'] = filters['max_rooms']
        
        return params
    
    def get_property_details(self, property_code):
        """Get detailed property information"""
        self.ensure_authenticated()
        
        endpoint = f"{self.base_url}/3.5/es/detail"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        
        params = {
            'country': 'it',
            'propertyCode': property_code
        }
        
        response = requests.post(endpoint, json=params, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Detail API Error: {response.status_code}")
    
    def get_market_data(self, location):
        """Get market data for specific location"""
        # This would use Idealista's market data endpoints
        # Implementation depends on available API endpoints
        pass
```

### 1.3 OpenAPI (Quotazioni Start) Integration

```python
class QuotazioniStartAPI:
    def __init__(self):
        self.base_url = "https://api.quotazionistart.it"
        self.api_key = os.getenv('QUOTAZIONI_API_KEY')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_property_valuation(self, property_data):
        """Get property valuation"""
        endpoint = f"{self.base_url}/valuation"
        
        payload = {
            'address': property_data['address'],
            'city': property_data['city'],
            'province': property_data['province'],
            'property_type': property_data['property_type'],
            'size': property_data['size'],
            'rooms': property_data.get('rooms', 0),
            'bathrooms': property_data.get('bathrooms', 0),
            'floor': property_data.get('floor', 0),
            'condition': property_data.get('condition', 'good'),
            'year_built': property_data.get('year_built', 2000)
        }
        
        response = requests.post(endpoint, json=payload, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Valuation API Error: {response.status_code}")
    
    def get_market_indices(self, location):
        """Get market indices for location"""
        endpoint = f"{self.base_url}/market/indices"
        
        params = {
            'location': location,
            'period': '12months'
        }
        
        response = requests.get(endpoint, params=params, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Market API Error: {response.status_code}")
    
    def get_transaction_data(self, filters):
        """Get historical transaction data"""
        endpoint = f"{self.base_url}/transactions"
        
        response = requests.get(endpoint, params=filters, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Transaction API Error: {response.status_code}")
```

## Part 2: Web Scraping Implementation

### 2.1 Ethical Web Scraping Framework

```python
import requests
from bs4 import BeautifulSoup
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

class EthicalScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Rate limiting
        self.min_delay = 2  # seconds
        self.max_delay = 5  # seconds
        self.last_request_time = 0
        
        # Selenium setup for dynamic content
        self.setup_selenium()
    
    def setup_selenium(self):
        """Setup Selenium WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        self.driver = webdriver.Chrome(options=chrome_options)
    
    def respect_rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_delay:
            sleep_time = random.uniform(self.min_delay, self.max_delay)
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def get_page(self, url, use_selenium=False):
        """Get page content with rate limiting"""
        self.respect_rate_limit()
        
        if use_selenium:
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            return self.driver.page_source
        else:
            response = self.session.get(url)
            response.raise_for_status()
            return response.text
    
    def parse_property_listing(self, html, portal_type):
        """Parse property listing based on portal type"""
        soup = BeautifulSoup(html, 'html.parser')
        
        if portal_type == 'tecnocasa':
            return self.parse_tecnocasa(soup)
        elif portal_type == 'casa':
            return self.parse_casa(soup)
        elif portal_type == 'subito':
            return self.parse_subito(soup)
        # Add more portal parsers as needed
        
        return None
    
    def parse_tecnocasa(self, soup):
        """Parse Tecnocasa property listing"""
        try:
            property_data = {
                'title': soup.find('h1', class_='property-title').get_text(strip=True) if soup.find('h1', class_='property-title') else '',
                'price': self.extract_price(soup.find('span', class_='price')),
                'location': soup.find('div', class_='location').get_text(strip=True) if soup.find('div', class_='location') else '',
                'size': self.extract_size(soup.find('span', class_='size')),
                'rooms': self.extract_rooms(soup.find('span', class_='rooms')),
                'description': soup.find('div', class_='description').get_text(strip=True) if soup.find('div', class_='description') else '',
                'features': self.extract_features(soup.find_all('li', class_='feature')),
                'images': self.extract_images(soup.find_all('img', class_='property-image')),
                'contact': self.extract_contact_info(soup),
                'portal': 'tecnocasa',
                'scraped_at': datetime.now().isoformat()
            }
            
            return property_data
            
        except Exception as e:
            print(f"Error parsing Tecnocasa listing: {e}")
            return None
    
    def parse_casa(self, soup):
        """Parse Casa.it property listing"""
        # Similar implementation for Casa.it
        pass
    
    def parse_subito(self, soup):
        """Parse Subito.it property listing"""
        # Similar implementation for Subito.it
        pass
    
    def extract_price(self, price_element):
        """Extract price from element"""
        if not price_element:
            return 0
        
        price_text = price_element.get_text(strip=True)
        # Remove currency symbols and extract number
        import re
        price_match = re.search(r'[\d.,]+', price_text.replace('.', '').replace(',', ''))
        
        return int(price_match.group()) if price_match else 0
    
    def extract_size(self, size_element):
        """Extract size from element"""
        if not size_element:
            return 0
        
        size_text = size_element.get_text(strip=True)
        import re
        size_match = re.search(r'(\d+)', size_text)
        
        return int(size_match.group(1)) if size_match else 0
    
    def extract_rooms(self, rooms_element):
        """Extract number of rooms"""
        if not rooms_element:
            return 0
        
        rooms_text = rooms_element.get_text(strip=True)
        import re
        rooms_match = re.search(r'(\d+)', rooms_text)
        
        return int(rooms_match.group(1)) if rooms_match else 0
    
    def extract_features(self, feature_elements):
        """Extract property features"""
        features = []
        for element in feature_elements:
            feature_text = element.get_text(strip=True)
            if feature_text:
                features.append(feature_text)
        
        return features
    
    def extract_images(self, image_elements):
        """Extract image URLs"""
        images = []
        for img in image_elements:
            src = img.get('src') or img.get('data-src')
            if src:
                images.append(src)
        
        return images
    
    def extract_contact_info(self, soup):
        """Extract contact information"""
        contact = {}
        
        # Try to find agency name
        agency_elem = soup.find('span', class_='agency-name') or soup.find('div', class_='agency')
        if agency_elem:
            contact['agency'] = agency_elem.get_text(strip=True)
        
        # Try to find phone number
        phone_elem = soup.find('a', href=lambda x: x and 'tel:' in x)
        if phone_elem:
            contact['phone'] = phone_elem.get('href').replace('tel:', '')
        
        return contact
```

## Part 3: Social Media Monitoring

### 3.1 Facebook Groups Monitoring

```python
import facebook
from datetime import datetime, timedelta

class FacebookMonitor:
    def __init__(self):
        self.access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.graph = facebook.GraphAPI(access_token=self.access_token)
        
        # Real estate groups to monitor
        self.target_groups = [
            'real-estate-rome',
            'immobiliare-milano',
            'case-firenze',
            # Add more group IDs
        ]
    
    def monitor_groups(self):
        """Monitor Facebook groups for real estate posts"""
        all_posts = []
        
        for group_id in self.target_groups:
            try:
                posts = self.get_group_posts(group_id)
                all_posts.extend(posts)
            except Exception as e:
                print(f"Error monitoring group {group_id}: {e}")
        
        return all_posts
    
    def get_group_posts(self, group_id, limit=50):
        """Get recent posts from a Facebook group"""
        try:
            posts = self.graph.get_object(
                f"{group_id}/feed",
                fields='id,message,created_time,from,link,picture,type',
                limit=limit
            )
            
            real_estate_posts = []
            
            for post in posts['data']:
                if self.is_real_estate_post(post):
                    processed_post = self.process_facebook_post(post)
                    real_estate_posts.append(processed_post)
            
            return real_estate_posts
            
        except Exception as e:
            print(f"Error getting group posts: {e}")
            return []
    
    def is_real_estate_post(self, post):
        """Check if post is related to real estate"""
        message = post.get('message', '').lower()
        
        real_estate_keywords = [
            'vendesi', 'affittasi', 'casa', 'appartamento', 'villa',
            'immobile', 'proprietà', 'affitto', 'vendita', 'locazione',
            'bilocale', 'trilocale', 'quadrilocale', 'monolocale',
            'euro', '€', 'mq', 'metri quadri'
        ]
        
        return any(keyword in message for keyword in real_estate_keywords)
    
    def process_facebook_post(self, post):
        """Process Facebook post to extract real estate information"""
        return {
            'id': post['id'],
            'message': post.get('message', ''),
            'created_time': post['created_time'],
            'author': post.get('from', {}).get('name', ''),
            'link': post.get('link', ''),
            'picture': post.get('picture', ''),
            'type': post.get('type', ''),
            'platform': 'facebook',
            'extracted_info': self.extract_property_info(post.get('message', '')),
            'processed_at': datetime.now().isoformat()
        }
    
    def extract_property_info(self, message):
        """Extract property information from message text"""
        import re
        
        info = {}
        
        # Extract price
        price_patterns = [
            r'€\s*(\d+(?:\.\d{3})*)',
            r'(\d+(?:\.\d{3})*)\s*euro',
            r'(\d+(?:\.\d{3})*)\s*€'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                info['price'] = int(match.group(1).replace('.', ''))
                break
        
        # Extract size
        size_patterns = [
            r'(\d+)\s*mq',
            r'(\d+)\s*metri\s*quadri',
            r'(\d+)\s*m²'
        ]
        
        for pattern in size_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                info['size'] = int(match.group(1))
                break
        
        # Extract rooms
        room_patterns = [
            r'(\d+)\s*locali',
            r'(\d+)\s*camere',
            r'(mono|bi|tri|quadri)locale'
        ]
        
        for pattern in room_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                if match.group(1) == 'mono':
                    info['rooms'] = 1
                elif match.group(1) == 'bi':
                    info['rooms'] = 2
                elif match.group(1) == 'tri':
                    info['rooms'] = 3
                elif match.group(1) == 'quadri':
                    info['rooms'] = 4
                else:
                    info['rooms'] = int(match.group(1))
                break
        
        # Extract location
        location_patterns = [
            r'(Roma|Milano|Firenze|Napoli|Torino|Bologna|Venezia|Genova)',
            r'zona\s+([A-Za-z\s]+)',
            r'quartiere\s+([A-Za-z\s]+)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                info['location'] = match.group(1).strip()
                break
        
        return info
```

## Part 4: n8n Integration Workflows

### 4.1 Data Collection Workflow

```json
{
  "name": "Real Estate Data Collection",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "hours",
              "hoursInterval": 6
            }
          ]
        }
      },
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1,
      "position": [240, 300]
    },
    {
      "parameters": {
        "functionCode": "// Immobiliare.it API Call\nconst filters = {\n  city: 'Rome',\n  property_type: 'apartment',\n  min_price: 100000,\n  max_price: 500000\n};\n\nreturn {\n  json: {\n    portal: 'immobiliare',\n    filters: filters,\n    timestamp: new Date().toISOString()\n  }\n};"
      },
      "name": "Prepare Immobiliare Request",
      "type": "n8n-nodes-base.function",
      "typeVersion": 1,
      "position": [460, 200]
    },
    {
      "parameters": {
        "url": "http://localhost:5005/api/collect/immobiliare",
        "options": {
          "headers": {
            "Content-Type": "application/json"
          }
        },
        "jsonParameters": true,
        "bodyParametersJson": "={{ JSON.stringify($json) }}"
      },
      "name": "Call Immobiliare API",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 1,
      "position": [680, 200]
    },
    {
      "parameters": {
        "functionCode": "// Idealista.it API Call\nconst filters = {\n  operation: 'sale',\n  property_type: 'homes',\n  latitude: 41.9028,\n  longitude: 12.4964,\n  distance: 10000\n};\n\nreturn {\n  json: {\n    portal: 'idealista',\n    filters: filters,\n    timestamp: new Date().toISOString()\n  }\n};"
      },
      "name": "Prepare Idealista Request",
      "type": "n8n-nodes-base.function",
      "typeVersion": 1,
      "position": [460, 400]
    },
    {
      "parameters": {
        "url": "http://localhost:5005/api/collect/idealista",
        "options": {
          "headers": {
            "Content-Type": "application/json"
          }
        },
        "jsonParameters": true,
        "bodyParametersJson": "={{ JSON.stringify($json) }}"
      },
      "name": "Call Idealista API",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 1,
      "position": [680, 400]
    },
    {
      "parameters": {
        "functionCode": "// Process and merge data from all sources\nconst allData = [];\n\n// Process Immobiliare data\nif ($('Call Immobiliare API').all()) {\n  const immobiliareData = $('Call Immobiliare API').all();\n  allData.push(...immobiliareData.map(item => ({\n    ...item.json,\n    source: 'immobiliare'\n  })));\n}\n\n// Process Idealista data\nif ($('Call Idealista API').all()) {\n  const idealistaData = $('Call Idealista API').all();\n  allData.push(...idealistaData.map(item => ({\n    ...item.json,\n    source: 'idealista'\n  })));\n}\n\nreturn allData.map(data => ({ json: data }));"
      },
      "name": "Merge Portal Data",
      "type": "n8n-nodes-base.function",
      "typeVersion": 1,
      "position": [900, 300]
    },
    {
      "parameters": {
        "url": "https://daytaa.intelligentb2b.com/api/database/rows/table/{{ $env.BASEROW_PROPERTIES_TABLE_ID }}/",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "options": {
          "headers": {
            "Content-Type": "application/json"
          }
        },
        "jsonParameters": true,
        "bodyParametersJson": "={{ JSON.stringify($json) }}"
      },
      "name": "Save to Baserow",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 1,
      "position": [1120, 300]
    }
  ],
  "connections": {
    "Schedule Trigger": {
      "main": [
        [
          {
            "node": "Prepare Immobiliare Request",
            "type": "main",
            "index": 0
          },
          {
            "node": "Prepare Idealista Request",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Prepare Immobiliare Request": {
      "main": [
        [
          {
            "node": "Call Immobiliare API",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Prepare Idealista Request": {
      "main": [
        [
          {
            "node": "Call Idealista API",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Call Immobiliare API": {
      "main": [
        [
          {
            "node": "Merge Portal Data",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Call Idealista API": {
      "main": [
        [
          {
            "node": "Merge Portal Data",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Merge Portal Data": {
      "main": [
        [
          {
            "node": "Save to Baserow",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

This comprehensive external portal integration system provides real-time data collection from major Italian real estate portals, social media monitoring, and automated data processing workflows that integrate seamlessly with your existing Baserow database and n8n automation platform.


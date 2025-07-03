from flask import Blueprint, request, jsonify
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime, timedelta
import os
import json
import re
from urllib.parse import urljoin, urlparse
import base64

data_collection_bp = Blueprint('data_collection', __name__)

class DataCollectionService:
    def __init__(self):
        # API configurations
        self.immobiliare_config = {
            'base_url': 'https://api.immobiliare.it',
            'api_key': os.getenv('IMMOBILIARE_API_KEY', 'demo_key'),
            'headers': {
                'Authorization': f'Bearer {os.getenv("IMMOBILIARE_API_KEY", "demo_key")}',
                'Content-Type': 'application/xml',
                'Accept': 'application/xml'
            }
        }
        
        self.idealista_config = {
            'base_url': 'https://api.idealista.com',
            'client_id': os.getenv('IDEALISTA_CLIENT_ID', 'demo_client'),
            'client_secret': os.getenv('IDEALISTA_CLIENT_SECRET', 'demo_secret'),
            'access_token': None,
            'token_expires': None
        }
        
        self.quotazioni_config = {
            'base_url': 'https://api.quotazionistart.it',
            'api_key': os.getenv('QUOTAZIONI_API_KEY', 'demo_key'),
            'headers': {
                'Authorization': f'Bearer {os.getenv("QUOTAZIONI_API_KEY", "demo_key")}',
                'Content-Type': 'application/json'
            }
        }
        
        # Baserow configuration
        self.baserow_config = {
            'api_url': os.getenv('BASEROW_API_URL', 'https://dayta.intelligentb2b.com/api'),
            'token': os.getenv('BASEROW_TOKEN', ''),
            'properties_table_id': os.getenv('BASEROW_PROPERTIES_TABLE_ID', ''),
            'market_data_table_id': os.getenv('BASEROW_MARKET_DATA_TABLE_ID', '')
        }
        
        # Rate limiting for scraping
        self.last_request_time = {}
        self.min_delay = 2  # seconds between requests
        
        # Mock data for demonstration
        self.generate_mock_data()
    
    def generate_mock_data(self):
        """Generate mock data for demonstration purposes"""
        self.mock_properties = [
            {
                'id': 'IMM001',
                'title': 'Elegant Apartment in Trastevere',
                'description': 'Beautiful 3-bedroom apartment in the heart of Rome',
                'price': 450000,
                'size': 120,
                'rooms': 3,
                'bathrooms': 2,
                'location': {
                    'city': 'Rome',
                    'province': 'RM',
                    'address': 'Via di Trastevere 45',
                    'latitude': 41.8902,
                    'longitude': 12.4696
                },
                'features': ['Balcony', 'Parking', 'Elevator', 'Air Conditioning'],
                'images': [
                    'https://example.com/image1.jpg',
                    'https://example.com/image2.jpg'
                ],
                'contact': {
                    'agency': 'Roma Properties',
                    'agent': 'Marco Rossi',
                    'phone': '+39 06 1234567',
                    'email': 'marco@romaproperties.it'
                },
                'published_date': '2025-01-01',
                'portal': 'immobiliare'
            },
            {
                'id': 'IDE002',
                'title': 'Modern Villa in Milan',
                'description': 'Luxury villa with garden in prestigious area',
                'price': 850000,
                'size': 250,
                'rooms': 5,
                'bathrooms': 3,
                'location': {
                    'city': 'Milan',
                    'province': 'MI',
                    'address': 'Via Brera 12',
                    'latitude': 45.4642,
                    'longitude': 9.1900
                },
                'features': ['Garden', 'Swimming Pool', 'Garage', 'Security System'],
                'images': [
                    'https://example.com/villa1.jpg',
                    'https://example.com/villa2.jpg'
                ],
                'contact': {
                    'agency': 'Milano Luxury',
                    'agent': 'Giulia Bianchi',
                    'phone': '+39 02 9876543',
                    'email': 'giulia@milanoluxury.it'
                },
                'published_date': '2025-01-02',
                'portal': 'idealista'
            }
        ]
        
        self.mock_market_data = {
            'Rome': {
                'average_price': 4500,
                'price_per_sqm': 4500,
                'total_listings': 1250,
                'new_listings': 85,
                'sold_properties': 42,
                'days_on_market': 65,
                'price_trend': 'increasing'
            },
            'Milan': {
                'average_price': 6200,
                'price_per_sqm': 6200,
                'total_listings': 980,
                'new_listings': 67,
                'sold_properties': 38,
                'days_on_market': 58,
                'price_trend': 'stable'
            }
        }
    
    def respect_rate_limit(self, portal):
        """Implement rate limiting for web scraping"""
        current_time = time.time()
        last_time = self.last_request_time.get(portal, 0)
        
        if current_time - last_time < self.min_delay:
            sleep_time = random.uniform(self.min_delay, self.min_delay + 2)
            time.sleep(sleep_time)
        
        self.last_request_time[portal] = time.time()
    
    def collect_immobiliare_data(self, filters):
        """Collect data from Immobiliare.it"""
        try:
            # In a real implementation, this would make actual API calls
            # For demo purposes, return mock data with applied filters
            
            filtered_properties = []
            for prop in self.mock_properties:
                if prop['portal'] == 'immobiliare':
                    # Apply filters
                    if filters.get('city') and prop['location']['city'].lower() != filters['city'].lower():
                        continue
                    if filters.get('min_price') and prop['price'] < filters['min_price']:
                        continue
                    if filters.get('max_price') and prop['price'] > filters['max_price']:
                        continue
                    if filters.get('min_size') and prop['size'] < filters['min_size']:
                        continue
                    if filters.get('max_size') and prop['size'] > filters['max_size']:
                        continue
                    
                    filtered_properties.append(prop)
            
            return {
                'success': True,
                'data': filtered_properties,
                'total_count': len(filtered_properties),
                'source': 'immobiliare',
                'collected_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'source': 'immobiliare'
            }
    
    def collect_idealista_data(self, filters):
        """Collect data from Idealista.it"""
        try:
            # Mock implementation - in reality would use OAuth2 and API calls
            filtered_properties = []
            for prop in self.mock_properties:
                if prop['portal'] == 'idealista':
                    # Apply location-based filtering
                    if filters.get('center'):
                        # In real implementation, would calculate distance
                        filtered_properties.append(prop)
            
            return {
                'success': True,
                'data': filtered_properties,
                'total_count': len(filtered_properties),
                'source': 'idealista',
                'collected_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'source': 'idealista'
            }
    
    def collect_quotazioni_data(self, location):
        """Collect market data from Quotazioni Start"""
        try:
            market_data = self.mock_market_data.get(location, {})
            
            if market_data:
                return {
                    'success': True,
                    'data': {
                        'location': location,
                        'market_statistics': market_data,
                        'valuation_data': {
                            'confidence_level': 85.6,
                            'data_points': 1250,
                            'last_updated': datetime.now().isoformat()
                        }
                    },
                    'source': 'quotazioni_start',
                    'collected_at': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': 'Location not found',
                    'source': 'quotazioni_start'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'source': 'quotazioni_start'
            }
    
    def scrape_portal_data(self, portal, search_params):
        """Scrape data from various real estate portals"""
        try:
            self.respect_rate_limit(portal)
            
            # Mock scraping results
            scraped_data = []
            
            if portal == 'tecnocasa':
                scraped_data = [
                    {
                        'title': 'Cozy Apartment - Tecnocasa',
                        'price': 320000,
                        'location': 'Florence',
                        'size': 85,
                        'rooms': 2,
                        'description': 'Beautiful apartment in historic center',
                        'features': ['Historic Building', 'City Center'],
                        'contact': {'agency': 'Tecnocasa Firenze'},
                        'portal': 'tecnocasa',
                        'scraped_at': datetime.now().isoformat()
                    }
                ]
            elif portal == 'casa':
                scraped_data = [
                    {
                        'title': 'Family Home - Casa.it',
                        'price': 280000,
                        'location': 'Naples',
                        'size': 110,
                        'rooms': 3,
                        'description': 'Perfect for families',
                        'features': ['Balcony', 'Near Schools'],
                        'contact': {'agency': 'Casa Napoli'},
                        'portal': 'casa',
                        'scraped_at': datetime.now().isoformat()
                    }
                ]
            elif portal == 'subito':
                scraped_data = [
                    {
                        'title': 'Investment Opportunity - Subito',
                        'price': 180000,
                        'location': 'Turin',
                        'size': 65,
                        'rooms': 2,
                        'description': 'Great investment property',
                        'features': ['Renovation Needed', 'Good Location'],
                        'contact': {'phone': '+39 011 123456'},
                        'portal': 'subito',
                        'scraped_at': datetime.now().isoformat()
                    }
                ]
            
            return {
                'success': True,
                'data': scraped_data,
                'total_count': len(scraped_data),
                'source': portal,
                'collected_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'source': portal
            }
    
    def monitor_social_media(self, platform, keywords):
        """Monitor social media for real estate posts"""
        try:
            # Mock social media monitoring results
            social_posts = []
            
            if platform == 'facebook':
                social_posts = [
                    {
                        'id': 'fb_001',
                        'message': 'Vendesi appartamento 3 locali Roma Trastevere €380.000 90mq',
                        'author': 'Mario Verdi',
                        'created_time': datetime.now().isoformat(),
                        'platform': 'facebook',
                        'group': 'Real Estate Rome',
                        'extracted_info': {
                            'price': 380000,
                            'size': 90,
                            'rooms': 3,
                            'location': 'Roma Trastevere'
                        },
                        'lead_potential': 'high'
                    }
                ]
            elif platform == 'instagram':
                social_posts = [
                    {
                        'id': 'ig_001',
                        'message': 'Beautiful villa for sale in Milan! 5 rooms, garden, €750k',
                        'author': '@milanproperties',
                        'created_time': datetime.now().isoformat(),
                        'platform': 'instagram',
                        'hashtags': ['#milanrealestate', '#villa', '#forsale'],
                        'extracted_info': {
                            'price': 750000,
                            'rooms': 5,
                            'location': 'Milan',
                            'features': ['garden']
                        },
                        'lead_potential': 'medium'
                    }
                ]
            
            return {
                'success': True,
                'data': social_posts,
                'total_count': len(social_posts),
                'platform': platform,
                'keywords': keywords,
                'monitored_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'platform': platform
            }
    
    def save_to_baserow(self, data, table_type='properties'):
        """Save collected data to Baserow"""
        try:
            if table_type == 'properties':
                table_id = self.baserow_config['properties_table_id']
            elif table_type == 'market_data':
                table_id = self.baserow_config['market_data_table_id']
            else:
                raise ValueError(f"Unknown table type: {table_type}")
            
            # Mock Baserow save operation
            saved_records = []
            
            for item in data:
                # Transform data for Baserow format
                baserow_record = self.transform_for_baserow(item, table_type)
                
                # In real implementation, would make actual API call to Baserow
                # response = requests.post(
                #     f"{self.baserow_config['api_url']}/database/rows/table/{table_id}/",
                #     headers={'Authorization': f'Token {self.baserow_config["token"]}'},
                #     json=baserow_record
                # )
                
                # Mock successful save
                saved_record = {
                    'id': len(saved_records) + 1,
                    **baserow_record,
                    'created_at': datetime.now().isoformat()
                }
                saved_records.append(saved_record)
            
            return {
                'success': True,
                'saved_count': len(saved_records),
                'records': saved_records
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def transform_for_baserow(self, data, table_type):
        """Transform data for Baserow table format"""
        if table_type == 'properties':
            return {
                'title': data.get('title', ''),
                'description': data.get('description', ''),
                'price': data.get('price', 0),
                'size': data.get('size', 0),
                'rooms': data.get('rooms', 0),
                'bathrooms': data.get('bathrooms', 0),
                'city': data.get('location', {}).get('city', ''),
                'province': data.get('location', {}).get('province', ''),
                'address': data.get('location', {}).get('address', ''),
                'latitude': data.get('location', {}).get('latitude', 0),
                'longitude': data.get('location', {}).get('longitude', 0),
                'features': ', '.join(data.get('features', [])),
                'portal_source': data.get('portal', ''),
                'portal_id': data.get('id', ''),
                'contact_agency': data.get('contact', {}).get('agency', ''),
                'contact_agent': data.get('contact', {}).get('agent', ''),
                'contact_phone': data.get('contact', {}).get('phone', ''),
                'contact_email': data.get('contact', {}).get('email', ''),
                'published_date': data.get('published_date', ''),
                'collected_at': datetime.now().isoformat()
            }
        elif table_type == 'market_data':
            return {
                'location': data.get('location', ''),
                'average_price': data.get('market_statistics', {}).get('average_price', 0),
                'price_per_sqm': data.get('market_statistics', {}).get('price_per_sqm', 0),
                'total_listings': data.get('market_statistics', {}).get('total_listings', 0),
                'new_listings': data.get('market_statistics', {}).get('new_listings', 0),
                'sold_properties': data.get('market_statistics', {}).get('sold_properties', 0),
                'days_on_market': data.get('market_statistics', {}).get('days_on_market', 0),
                'price_trend': data.get('market_statistics', {}).get('price_trend', ''),
                'data_source': data.get('source', ''),
                'collected_at': datetime.now().isoformat()
            }
        
        return data

# Initialize service
data_service = DataCollectionService()

@data_collection_bp.route('/collect/immobiliare', methods=['POST'])
def collect_immobiliare():
    """Collect data from Immobiliare.it"""
    try:
        filters = request.json.get('filters', {})
        result = data_service.collect_immobiliare_data(filters)
        
        if result['success'] and result['data']:
            # Save to Baserow
            save_result = data_service.save_to_baserow(result['data'], 'properties')
            result['baserow_save'] = save_result
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@data_collection_bp.route('/collect/idealista', methods=['POST'])
def collect_idealista():
    """Collect data from Idealista.it"""
    try:
        filters = request.json.get('filters', {})
        result = data_service.collect_idealista_data(filters)
        
        if result['success'] and result['data']:
            # Save to Baserow
            save_result = data_service.save_to_baserow(result['data'], 'properties')
            result['baserow_save'] = save_result
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@data_collection_bp.route('/collect/quotazioni', methods=['POST'])
def collect_quotazioni():
    """Collect market data from Quotazioni Start"""
    try:
        location = request.json.get('location', 'Rome')
        result = data_service.collect_quotazioni_data(location)
        
        if result['success'] and result['data']:
            # Save to Baserow
            save_result = data_service.save_to_baserow([result['data']], 'market_data')
            result['baserow_save'] = save_result
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@data_collection_bp.route('/scrape/<portal>', methods=['POST'])
def scrape_portal(portal):
    """Scrape data from various real estate portals"""
    try:
        search_params = request.json.get('search_params', {})
        result = data_service.scrape_portal_data(portal, search_params)
        
        if result['success'] and result['data']:
            # Save to Baserow
            save_result = data_service.save_to_baserow(result['data'], 'properties')
            result['baserow_save'] = save_result
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@data_collection_bp.route('/monitor/social/<platform>', methods=['POST'])
def monitor_social(platform):
    """Monitor social media for real estate posts"""
    try:
        keywords = request.json.get('keywords', [])
        result = data_service.monitor_social_media(platform, keywords)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@data_collection_bp.route('/collect/all', methods=['POST'])
def collect_all_sources():
    """Collect data from all configured sources"""
    try:
        filters = request.json.get('filters', {})
        results = {}
        
        # Collect from Immobiliare.it
        results['immobiliare'] = data_service.collect_immobiliare_data(filters)
        
        # Collect from Idealista.it
        results['idealista'] = data_service.collect_idealista_data(filters)
        
        # Collect market data
        location = filters.get('city', 'Rome')
        results['market_data'] = data_service.collect_quotazioni_data(location)
        
        # Scrape additional portals
        portals_to_scrape = ['tecnocasa', 'casa', 'subito']
        for portal in portals_to_scrape:
            results[f'scraped_{portal}'] = data_service.scrape_portal_data(portal, filters)
        
        # Monitor social media
        results['social_facebook'] = data_service.monitor_social_media('facebook', ['vendesi', 'affittasi'])
        results['social_instagram'] = data_service.monitor_social_media('instagram', ['forsale', 'realestate'])
        
        # Aggregate results
        total_properties = 0
        all_properties = []
        
        for source, result in results.items():
            if result.get('success') and result.get('data'):
                if isinstance(result['data'], list):
                    total_properties += len(result['data'])
                    all_properties.extend(result['data'])
        
        # Save all properties to Baserow
        if all_properties:
            save_result = data_service.save_to_baserow(all_properties, 'properties')
        else:
            save_result = {'success': True, 'saved_count': 0}
        
        return jsonify({
            'success': True,
            'total_properties_collected': total_properties,
            'sources': results,
            'baserow_save': save_result,
            'collected_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@data_collection_bp.route('/status', methods=['GET'])
def get_collection_status():
    """Get status of data collection services"""
    try:
        status = {
            'service': 'data-collection-service',
            'status': 'healthy',
            'apis': {
                'immobiliare': {
                    'configured': bool(os.getenv('IMMOBILIARE_API_KEY')),
                    'status': 'ready'
                },
                'idealista': {
                    'configured': bool(os.getenv('IDEALISTA_CLIENT_ID')),
                    'status': 'ready'
                },
                'quotazioni': {
                    'configured': bool(os.getenv('QUOTAZIONI_API_KEY')),
                    'status': 'ready'
                }
            },
            'baserow': {
                'configured': bool(os.getenv('BASEROW_TOKEN')),
                'url': os.getenv('BASEROW_API_URL', 'https://dayta.intelligentb2b.com/api')
            },
            'scraping': {
                'enabled': True,
                'supported_portals': ['tecnocasa', 'casa', 'subito', 'bakeca', 'trovacasa']
            },
            'social_monitoring': {
                'enabled': True,
                'supported_platforms': ['facebook', 'instagram', 'twitter']
            },
            'last_updated': datetime.now().isoformat()
        }
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


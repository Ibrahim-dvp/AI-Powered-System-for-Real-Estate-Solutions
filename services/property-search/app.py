"""
Property Search Service
======================

This service provides intelligent property search and recommendation capabilities.
It uses AI-powered matching algorithms to find properties that best match user
preferences and requirements.

Features:
- Intelligent property matching
- Personalized recommendations
- Advanced search filters
- Location-based search
- Price range optimization
"""

import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
BASEROW_API_URL = os.getenv("BASEROW_API_URL", "https://dayta.intelligentb2b.com/api")
BASEROW_TOKEN = os.getenv("BASEROW_TOKEN")
BASEROW_PROPERTIES_TABLE_ID = os.getenv("BASEROW_PROPERTIES_TABLE_ID")
BASEROW_USERS_TABLE_ID = os.getenv("BASEROW_USERS_TABLE_ID")

class PropertySearchEngine:
    """Main property search and recommendation engine"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.property_cache = {}
        self.last_cache_update = None
        self.cache_duration = 3600  # 1 hour in seconds
        
    def get_properties_from_baserow(self):
        """Fetch properties from Baserow"""
        try:
            headers = {
                'Authorization': f'Token {BASEROW_TOKEN}',
                'Content-Type': 'application/json'
            }
            
            url = f"{BASEROW_API_URL}/database/rows/table/{BASEROW_PROPERTIES_TABLE_ID}/"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            else:
                logger.error(f"Error fetching properties: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching properties: {str(e)}")
            return []
    
    def update_property_cache(self):
        """Update property cache if needed"""
        current_time = datetime.now().timestamp()
        
        if (self.last_cache_update is None or 
            current_time - self.last_cache_update > self.cache_duration):
            
            properties = self.get_properties_from_baserow()
            if properties:
                self.property_cache = {prop['id']: prop for prop in properties}
                self.last_cache_update = current_time
                logger.info(f"Property cache updated with {len(properties)} properties")
    
    def search_properties(self, filters):
        """Search properties based on filters"""
        self.update_property_cache()
        
        properties = list(self.property_cache.values())
        if not properties:
            return []
        
        # Apply filters
        filtered_properties = []
        
        for prop in properties:
            # Check if property matches filters
            if self.property_matches_filters(prop, filters):
                filtered_properties.append(prop)
        
        # Sort by relevance
        sorted_properties = self.sort_by_relevance(filtered_properties, filters)
        
        return sorted_properties
    
    def property_matches_filters(self, property_data, filters):
        """Check if property matches search filters"""
        try:
            # Property type filter
            if filters.get('property_type') and property_data.get('property_type') != filters['property_type']:
                return False
            
            # Listing type filter (sale/rent)
            if filters.get('listing_type') and property_data.get('listing_type') != filters['listing_type']:
                return False
            
            # Price range filter
            price = property_data.get('current_price', 0)
            if filters.get('min_price') and price < filters['min_price']:
                return False
            if filters.get('max_price') and price > filters['max_price']:
                return False
            
            # Location filter
            if filters.get('city') and property_data.get('city', '').lower() != filters['city'].lower():
                return False
            if filters.get('region') and property_data.get('region', '').lower() != filters['region'].lower():
                return False
            
            # Size filter
            size = property_data.get('square_meters', 0)
            if filters.get('min_size') and size < filters['min_size']:
                return False
            if filters.get('max_size') and size > filters['max_size']:
                return False
            
            # Bedrooms filter
            bedrooms = property_data.get('bedrooms', 0)
            if filters.get('min_bedrooms') and bedrooms < filters['min_bedrooms']:
                return False
            if filters.get('max_bedrooms') and bedrooms > filters['max_bedrooms']:
                return False
            
            # Bathrooms filter
            bathrooms = property_data.get('bathrooms', 0)
            if filters.get('min_bathrooms') and bathrooms < filters['min_bathrooms']:
                return False
            
            # Features filter
            features = filters.get('features', [])
            for feature in features:
                if not property_data.get(feature, False):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error matching property filters: {str(e)}")
            return False
    
    def sort_by_relevance(self, properties, filters):
        """Sort properties by relevance to search criteria"""
        if not properties:
            return []
        
        # Create scoring system
        scored_properties = []
        
        for prop in properties:
            score = self.calculate_relevance_score(prop, filters)
            scored_properties.append((prop, score))
        
        # Sort by score (descending)
        scored_properties.sort(key=lambda x: x[1], reverse=True)
        
        return [prop for prop, score in scored_properties]
    
    def calculate_relevance_score(self, property_data, filters):
        """Calculate relevance score for a property"""
        score = 0
        
        try:
            # Price score - closer to user's budget preference gets higher score
            target_price = filters.get('target_price')
            if target_price:
                price = property_data.get('current_price', 0)
                price_diff = abs(price - target_price) / target_price
                score += max(0, 100 - price_diff * 100)
            
            # Location score - exact matches get higher score
            if filters.get('preferred_cities'):
                city = property_data.get('city', '').lower()
                if city in [c.lower() for c in filters['preferred_cities']]:
                    score += 50
            
            # Size score
            target_size = filters.get('target_size')
            if target_size:
                size = property_data.get('square_meters', 0)
                if size > 0:
                    size_diff = abs(size - target_size) / target_size
                    score += max(0, 50 - size_diff * 50)
            
            # Features score
            desired_features = filters.get('features', [])
            for feature in desired_features:
                if property_data.get(feature, False):
                    score += 10
            
            # Freshness score - newer listings get higher score
            listing_date = property_data.get('listing_date')
            if listing_date:
                days_on_market = property_data.get('days_on_market', 0)
                if days_on_market < 30:
                    score += 20
                elif days_on_market < 60:
                    score += 10
            
            # Condition score
            condition = property_data.get('condition', '').lower()
            if condition in ['excellent', 'good']:
                score += 15
            elif condition == 'fair':
                score += 5
            
            return max(0, score)
            
        except Exception as e:
            logger.error(f"Error calculating relevance score: {str(e)}")
            return 0
    
    def get_similar_properties(self, property_id, limit=10):
        """Get properties similar to a given property"""
        self.update_property_cache()
        
        if property_id not in self.property_cache:
            return []
        
        target_property = self.property_cache[property_id]
        all_properties = list(self.property_cache.values())
        
        # Calculate similarity scores
        similarities = []
        for prop in all_properties:
            if prop['id'] != property_id:
                similarity = self.calculate_property_similarity(target_property, prop)
                similarities.append((prop, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return [prop for prop, sim in similarities[:limit]]
    
    def calculate_property_similarity(self, prop1, prop2):
        """Calculate similarity between two properties"""
        try:
            score = 0
            
            # Same property type
            if prop1.get('property_type') == prop2.get('property_type'):
                score += 30
            
            # Same listing type
            if prop1.get('listing_type') == prop2.get('listing_type'):
                score += 20
            
            # Price similarity
            price1 = prop1.get('current_price', 0)
            price2 = prop2.get('current_price', 0)
            if price1 > 0 and price2 > 0:
                price_diff = abs(price1 - price2) / max(price1, price2)
                score += max(0, 25 - price_diff * 25)
            
            # Size similarity
            size1 = prop1.get('square_meters', 0)
            size2 = prop2.get('square_meters', 0)
            if size1 > 0 and size2 > 0:
                size_diff = abs(size1 - size2) / max(size1, size2)
                score += max(0, 15 - size_diff * 15)
            
            # Same city
            if prop1.get('city') == prop2.get('city'):
                score += 10
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculating property similarity: {str(e)}")
            return 0
    
    def get_personalized_recommendations(self, user_id, limit=10):
        """Get personalized property recommendations for a user"""
        try:
            # Get user preferences from Baserow
            user_data = self.get_user_data(user_id)
            if not user_data:
                return []
            
            # Extract user preferences
            filters = self.extract_user_preferences(user_data)
            
            # Search properties based on preferences
            properties = self.search_properties(filters)
            
            return properties[:limit]
            
        except Exception as e:
            logger.error(f"Error getting personalized recommendations: {str(e)}")
            return []
    
    def get_user_data(self, user_id):
        """Get user data from Baserow"""
        try:
            headers = {
                'Authorization': f'Token {BASEROW_TOKEN}',
                'Content-Type': 'application/json'
            }
            
            url = f"{BASEROW_API_URL}/database/rows/table/{BASEROW_USERS_TABLE_ID}/{user_id}/"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            logger.error(f"Error fetching user data: {str(e)}")
            return None
    
    def extract_user_preferences(self, user_data):
        """Extract search filters from user data"""
        filters = {}
        
        # Extract basic preferences
        if user_data.get('property_type_preference'):
            filters['property_type'] = user_data['property_type_preference']
        
        if user_data.get('budget_min'):
            filters['min_price'] = user_data['budget_min']
        
        if user_data.get('budget_max'):
            filters['max_price'] = user_data['budget_max']
        
        if user_data.get('preferred_city'):
            filters['city'] = user_data['preferred_city']
        
        if user_data.get('min_bedrooms'):
            filters['min_bedrooms'] = user_data['min_bedrooms']
        
        if user_data.get('min_bathrooms'):
            filters['min_bathrooms'] = user_data['min_bathrooms']
        
        return filters

# Initialize search engine
search_engine = PropertySearchEngine()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'property-search-service',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/search', methods=['POST'])
def search_properties():
    """Search properties based on filters"""
    try:
        data = request.get_json()
        filters = data.get('filters', {})
        limit = data.get('limit', 50)
        
        # Perform search
        properties = search_engine.search_properties(filters)
        
        # Limit results
        results = properties[:limit]
        
        return jsonify({
            'success': True,
            'total_found': len(properties),
            'returned': len(results),
            'properties': results
        })
        
    except Exception as e:
        logger.error(f"Error in property search: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/recommendations/<user_id>', methods=['GET'])
def get_recommendations(user_id):
    """Get personalized property recommendations"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        # Get recommendations
        recommendations = search_engine.get_personalized_recommendations(user_id, limit)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'recommendations': recommendations
        })
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/similar/<property_id>', methods=['GET'])
def get_similar_properties(property_id):
    """Get properties similar to a given property"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        # Get similar properties
        similar_properties = search_engine.get_similar_properties(property_id, limit)
        
        return jsonify({
            'success': True,
            'property_id': property_id,
            'similar_properties': similar_properties
        })
        
    except Exception as e:
        logger.error(f"Error getting similar properties: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/property/<property_id>', methods=['GET'])
def get_property_details(property_id):
    """Get detailed information about a specific property"""
    try:
        search_engine.update_property_cache()
        
        if property_id not in search_engine.property_cache:
            return jsonify({'error': 'Property not found'}), 404
        
        property_data = search_engine.property_cache[property_id]
        
        return jsonify({
            'success': True,
            'property': property_data
        })
        
    except Exception as e:
        logger.error(f"Error getting property details: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/refresh-cache', methods=['POST'])
def refresh_cache():
    """Manually refresh property cache"""
    try:
        search_engine.property_cache = {}
        search_engine.last_cache_update = None
        search_engine.update_property_cache()
        
        return jsonify({
            'success': True,
            'message': 'Cache refreshed successfully',
            'properties_cached': len(search_engine.property_cache)
        })
        
    except Exception as e:
        logger.error(f"Error refreshing cache: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)

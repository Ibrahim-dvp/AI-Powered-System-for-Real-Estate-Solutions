from flask import Blueprint, request, jsonify
import requests
import os
from datetime import datetime

property_search_bp = Blueprint('property_search', __name__)

# Configuration
BASEROW_API_URL = "https://daytaa.intelligentb2b.com/api"
BASEROW_TOKEN = os.getenv('BASEROW_TOKEN', 'your_baserow_token_here')

@property_search_bp.route('/search-properties', methods=['POST'])
def search_properties():
    """Search properties based on chatbot criteria"""
    try:
        criteria = request.json
        
        # Build Baserow filter query
        filters = []
        
        # Budget filters
        if criteria.get('budget_min'):
            filters.append(f"filter__current_price__gte={criteria['budget_min']}")
        if criteria.get('budget_max'):
            filters.append(f"filter__current_price__lte={criteria['budget_max']}")
        
        # Property type filter
        if criteria.get('property_type'):
            filters.append(f"filter__property_type__equal={criteria['property_type']}")
        
        # Location filter
        if criteria.get('location'):
            filters.append(f"filter__city__contains={criteria['location']}")
        
        # Bedroom filter
        if criteria.get('bedrooms'):
            filters.append(f"filter__bedrooms__equal={criteria['bedrooms']}")
        
        # Bathroom filter
        if criteria.get('bathrooms'):
            filters.append(f"filter__bathrooms__equal={criteria['bathrooms']}")
        
        # Size filters
        if criteria.get('min_sqm'):
            filters.append(f"filter__square_meters__gte={criteria['min_sqm']}")
        if criteria.get('max_sqm'):
            filters.append(f"filter__square_meters__lte={criteria['max_sqm']}")
        
        # Only active listings
        filters.append("filter__status__equal=Active")
        
        # Query Baserow
        headers = {
            'Authorization': f'Token {BASEROW_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        query_params = '&'.join(filters) + '&size=10'  # Limit to 10 results
        
        # Mock response for demonstration (replace with actual Baserow call)
        properties = generate_mock_properties(criteria)
        
        # Format properties for chatbot response
        formatted_properties = []
        for prop in properties:
            formatted_properties.append({
                'id': prop['id'],
                'title': prop['title'],
                'price': prop['current_price'],
                'location': f"{prop['city']}, {prop['region']}",
                'type': prop['property_type'],
                'bedrooms': prop['bedrooms'],
                'bathrooms': prop['bathrooms'],
                'square_meters': prop['square_meters'],
                'description': prop['description'][:200] + '...' if len(prop['description']) > 200 else prop['description'],
                'url': f"https://your-website.com/property/{prop['id']}",
                'price_per_sqm': round(prop['current_price'] / prop['square_meters'], 2) if prop['square_meters'] > 0 else 0,
                'features': prop.get('features', [])
            })
        
        return jsonify({
            'success': True,
            'properties': formatted_properties,
            'total_found': len(formatted_properties),
            'search_criteria': criteria,
            'message': f"Found {len(formatted_properties)} properties matching your criteria."
        })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'properties': [],
            'message': 'Sorry, I encountered an error while searching for properties. Please try again.'
        }), 500

@property_search_bp.route('/get-property-details/<property_id>', methods=['GET'])
def get_property_details(property_id):
    """Get detailed information about a specific property"""
    try:
        headers = {
            'Authorization': f'Token {BASEROW_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        # Mock property details (replace with actual Baserow call)
        property_data = generate_mock_property_details(property_id)
        
        if property_data:
            return jsonify({
                'success': True,
                'property': property_data,
                'message': 'Property details retrieved successfully.'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Property not found',
                'message': 'Sorry, I could not find details for this property.'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Sorry, I encountered an error while retrieving property details.'
        }), 500

@property_search_bp.route('/get-similar-properties/<property_id>', methods=['GET'])
def get_similar_properties(property_id):
    """Get properties similar to the specified property"""
    try:
        # Get the reference property details
        reference_property = generate_mock_property_details(property_id)
        
        if not reference_property:
            return jsonify({
                'success': False,
                'error': 'Reference property not found'
            }), 404
        
        # Find similar properties based on type, location, and price range
        criteria = {
            'property_type': reference_property['property_type'],
            'location': reference_property['city'],
            'budget_min': reference_property['current_price'] * 0.8,  # 20% below
            'budget_max': reference_property['current_price'] * 1.2,  # 20% above
            'bedrooms': reference_property['bedrooms']
        }
        
        similar_properties = generate_mock_properties(criteria, exclude_id=property_id)
        
        formatted_properties = []
        for prop in similar_properties[:5]:  # Limit to 5 similar properties
            formatted_properties.append({
                'id': prop['id'],
                'title': prop['title'],
                'price': prop['current_price'],
                'location': f"{prop['city']}, {prop['region']}",
                'type': prop['property_type'],
                'bedrooms': prop['bedrooms'],
                'bathrooms': prop['bathrooms'],
                'square_meters': prop['square_meters'],
                'price_per_sqm': round(prop['current_price'] / prop['square_meters'], 2) if prop['square_meters'] > 0 else 0,
                'url': f"https://your-website.com/property/{prop['id']}"
            })
        
        return jsonify({
            'success': True,
            'similar_properties': formatted_properties,
            'reference_property_id': property_id,
            'message': f"Found {len(formatted_properties)} similar properties."
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Sorry, I encountered an error while finding similar properties.'
        }), 500

@property_search_bp.route('/get-market-insights', methods=['POST'])
def get_market_insights():
    """Get market insights for a specific area and property type"""
    try:
        criteria = request.json
        location = criteria.get('location', 'Rome')
        property_type = criteria.get('property_type', 'apartment')
        
        # Mock market insights (replace with actual market data analysis)
        insights = {
            'location': location,
            'property_type': property_type,
            'average_price': 450000,
            'average_price_per_sqm': 4500,
            'market_trend': 'increasing',
            'trend_percentage': 5.2,
            'days_on_market_avg': 45,
            'total_listings': 234,
            'new_listings_this_month': 28,
            'price_range': {
                'min': 200000,
                'max': 800000,
                'median': 420000
            },
            'neighborhood_highlights': [
                'Excellent public transportation',
                'Close to schools and parks',
                'Growing commercial district',
                'Historic architecture'
            ],
            'investment_potential': 'high',
            'recommendations': [
                'Properties in this area typically appreciate 3-5% annually',
                'Best time to buy is during winter months for better prices',
                'Consider properties near the new metro line for higher appreciation'
            ]
        }
        
        return jsonify({
            'success': True,
            'insights': insights,
            'message': f"Market insights for {property_type}s in {location} retrieved successfully."
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Sorry, I encountered an error while retrieving market insights.'
        }), 500

@property_search_bp.route('/schedule-viewing', methods=['POST'])
def schedule_viewing():
    """Schedule a property viewing"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['property_id', 'contact_name', 'contact_email', 'preferred_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}',
                    'message': f'Please provide your {field.replace("_", " ")}.'
                }), 400
        
        # Mock scheduling logic (replace with actual calendar integration)
        viewing_data = {
            'viewing_id': f"VIEW_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'property_id': data['property_id'],
            'contact_name': data['contact_name'],
            'contact_email': data['contact_email'],
            'contact_phone': data.get('contact_phone', ''),
            'preferred_date': data['preferred_date'],
            'preferred_time': data.get('preferred_time', '10:00'),
            'notes': data.get('notes', ''),
            'status': 'scheduled',
            'agent_assigned': 'Marco Rossi',
            'agent_phone': '+39 123 456 7890',
            'property_address': 'Via Roma 123, Rome, Italy'
        }
        
        # Here you would:
        # 1. Save to Baserow appointments table
        # 2. Send confirmation email
        # 3. Notify assigned agent
        # 4. Add to calendar system
        
        return jsonify({
            'success': True,
            'viewing': viewing_data,
            'message': f"Your viewing has been scheduled for {data['preferred_date']} at {data.get('preferred_time', '10:00')}. You'll receive a confirmation email shortly."
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Sorry, I encountered an error while scheduling your viewing. Please try again.'
        }), 500

@property_search_bp.route('/get-financing-options', methods=['POST'])
def get_financing_options():
    """Get financing options for a property"""
    try:
        data = request.json
        property_price = data.get('property_price', 0)
        down_payment = data.get('down_payment', 0)
        annual_income = data.get('annual_income', 0)
        
        if property_price <= 0:
            return jsonify({
                'success': False,
                'error': 'Invalid property price',
                'message': 'Please provide a valid property price.'
            }), 400
        
        # Calculate financing options
        loan_amount = property_price - down_payment
        
        financing_options = [
            {
                'type': 'Fixed Rate Mortgage',
                'interest_rate': 3.5,
                'term_years': 30,
                'monthly_payment': calculate_monthly_payment(loan_amount, 3.5, 30),
                'total_interest': calculate_total_interest(loan_amount, 3.5, 30),
                'requirements': ['Stable income', 'Good credit score', 'Down payment 20%']
            },
            {
                'type': 'Variable Rate Mortgage',
                'interest_rate': 2.8,
                'term_years': 30,
                'monthly_payment': calculate_monthly_payment(loan_amount, 2.8, 30),
                'total_interest': calculate_total_interest(loan_amount, 2.8, 30),
                'requirements': ['Stable income', 'Good credit score', 'Down payment 15%']
            },
            {
                'type': 'First-Time Buyer Program',
                'interest_rate': 3.2,
                'term_years': 25,
                'monthly_payment': calculate_monthly_payment(loan_amount, 3.2, 25),
                'total_interest': calculate_total_interest(loan_amount, 3.2, 25),
                'requirements': ['First-time buyer', 'Income limits apply', 'Down payment 10%']
            }
        ]
        
        # Calculate affordability
        max_monthly_payment = (annual_income / 12) * 0.28  # 28% rule
        affordable_options = [opt for opt in financing_options if opt['monthly_payment'] <= max_monthly_payment]
        
        return jsonify({
            'success': True,
            'financing_options': financing_options,
            'affordable_options': affordable_options,
            'loan_amount': loan_amount,
            'max_affordable_payment': round(max_monthly_payment, 2),
            'message': f"Found {len(affordable_options)} financing options within your budget."
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Sorry, I encountered an error while calculating financing options.'
        }), 500

def generate_mock_properties(criteria, exclude_id=None):
    """Generate mock properties for demonstration"""
    properties = [
        {
            'id': '1',
            'title': 'Modern Apartment in City Center',
            'property_type': 'apartment',
            'current_price': 450000,
            'city': 'Rome',
            'region': 'Lazio',
            'bedrooms': 2,
            'bathrooms': 2,
            'square_meters': 85,
            'description': 'Beautiful modern apartment in the heart of Rome with stunning city views.',
            'features': ['Balcony', 'Elevator', 'Parking', 'Air Conditioning']
        },
        {
            'id': '2',
            'title': 'Charming Villa with Garden',
            'property_type': 'villa',
            'current_price': 750000,
            'city': 'Florence',
            'region': 'Tuscany',
            'bedrooms': 4,
            'bathrooms': 3,
            'square_meters': 200,
            'description': 'Elegant villa with private garden and swimming pool in prestigious neighborhood.',
            'features': ['Garden', 'Swimming Pool', 'Garage', 'Fireplace']
        },
        {
            'id': '3',
            'title': 'Cozy House Near Metro',
            'property_type': 'house',
            'current_price': 380000,
            'city': 'Milan',
            'region': 'Lombardy',
            'bedrooms': 3,
            'bathrooms': 2,
            'square_meters': 120,
            'description': 'Perfect family home with easy access to public transportation.',
            'features': ['Terrace', 'Basement', 'Near Metro', 'Renovated']
        }
    ]
    
    # Filter based on criteria
    filtered_properties = []
    for prop in properties:
        if exclude_id and prop['id'] == exclude_id:
            continue
            
        matches = True
        
        if criteria.get('property_type') and prop['property_type'] != criteria['property_type']:
            matches = False
        
        if criteria.get('budget_min') and prop['current_price'] < criteria['budget_min']:
            matches = False
            
        if criteria.get('budget_max') and prop['current_price'] > criteria['budget_max']:
            matches = False
            
        if criteria.get('bedrooms') and prop['bedrooms'] != criteria['bedrooms']:
            matches = False
            
        if criteria.get('location') and criteria['location'].lower() not in prop['city'].lower():
            matches = False
        
        if matches:
            filtered_properties.append(prop)
    
    return filtered_properties

def generate_mock_property_details(property_id):
    """Generate mock property details"""
    properties = {
        '1': {
            'id': '1',
            'title': 'Modern Apartment in City Center',
            'property_type': 'apartment',
            'current_price': 450000,
            'city': 'Rome',
            'region': 'Lazio',
            'address': 'Via del Corso 123, Rome',
            'bedrooms': 2,
            'bathrooms': 2,
            'square_meters': 85,
            'floor_number': 3,
            'building_year': 2018,
            'energy_class': 'A2',
            'description': 'Beautiful modern apartment in the heart of Rome with stunning city views. Recently renovated with high-quality finishes.',
            'features': ['Balcony', 'Elevator', 'Parking', 'Air Conditioning', 'Double Glazing', 'Security System'],
            'monthly_expenses': 150,
            'property_taxes': 2500,
            'images': [
                'https://example.com/image1.jpg',
                'https://example.com/image2.jpg',
                'https://example.com/image3.jpg'
            ],
            'virtual_tour_url': 'https://example.com/virtual-tour/1',
            'agent': {
                'name': 'Marco Rossi',
                'phone': '+39 123 456 7890',
                'email': 'marco.rossi@realestate.com'
            }
        }
    }
    
    return properties.get(property_id)

def calculate_monthly_payment(loan_amount, annual_rate, years):
    """Calculate monthly mortgage payment"""
    monthly_rate = annual_rate / 100 / 12
    num_payments = years * 12
    
    if monthly_rate == 0:
        return loan_amount / num_payments
    
    monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
    return round(monthly_payment, 2)

def calculate_total_interest(loan_amount, annual_rate, years):
    """Calculate total interest paid over the life of the loan"""
    monthly_payment = calculate_monthly_payment(loan_amount, annual_rate, years)
    total_payments = monthly_payment * years * 12
    return round(total_payments - loan_amount, 2)


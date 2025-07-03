from flask import Blueprint, request, jsonify
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import requests
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import joblib

analytics_bp = Blueprint('analytics', __name__)

class DashboardAnalytics:
    def __init__(self):
        self.baserow_config = {
            'api_url': os.getenv('BASEROW_API_URL', 'https://daytaa.intelligentb2b.com/api'),
            'token': os.getenv('BASEROW_TOKEN', ''),
            'users_table_id': os.getenv('BASEROW_USERS_TABLE_ID', ''),
            'properties_table_id': os.getenv('BASEROW_PROPERTIES_TABLE_ID', ''),
            'deals_table_id': os.getenv('BASEROW_DEALS_TABLE_ID', ''),
            'interactions_table_id': os.getenv('BASEROW_INTERACTIONS_TABLE_ID', '')
        }
        
        # Initialize predictive models
        self.revenue_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.conversion_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        self.price_model = LinearRegression()
        
        # Mock data for demonstration
        self.mock_data = self.generate_mock_data()
    
    def generate_mock_data(self):
        """Generate realistic mock data for dashboard"""
        np.random.seed(42)
        
        # Generate date range for last 12 months
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Generate sales data
        sales_data = []
        base_revenue = 50000
        
        for i, date in enumerate(date_range):
            # Add seasonal patterns and trends
            seasonal_factor = 1 + 0.2 * np.sin(2 * np.pi * date.dayofyear / 365)
            trend_factor = 1 + (i / len(date_range)) * 0.3
            noise = np.random.normal(1, 0.1)
            
            daily_revenue = base_revenue * seasonal_factor * trend_factor * noise
            
            sales_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'revenue': max(0, daily_revenue),
                'deals_closed': np.random.poisson(2),
                'leads_generated': np.random.poisson(15),
                'property_views': np.random.poisson(50)
            })
        
        return {
            'sales_data': sales_data,
            'agents': self.generate_agent_data(),
            'properties': self.generate_property_data(),
            'market_data': self.generate_market_data()
        }
    
    def generate_agent_data(self):
        """Generate mock agent performance data"""
        agents = []
        agent_names = ['Marco Rossi', 'Giulia Bianchi', 'Alessandro Conti', 'Francesca Romano', 'Luca Ferrari']
        
        for i, name in enumerate(agent_names):
            agents.append({
                'id': i + 1,
                'name': name,
                'deals_closed': np.random.randint(5, 25),
                'revenue_generated': np.random.randint(200000, 800000),
                'leads_converted': np.random.randint(10, 50),
                'conversion_rate': np.random.uniform(15, 35),
                'avg_deal_size': np.random.randint(300000, 600000),
                'calls_made': np.random.randint(100, 300),
                'emails_sent': np.random.randint(200, 500),
                'meetings_held': np.random.randint(20, 80),
                'properties_shown': np.random.randint(30, 100),
                'rating': np.random.uniform(4.0, 5.0)
            })
        
        return agents
    
    def generate_property_data(self):
        """Generate mock property data"""
        properties = []
        cities = ['Rome', 'Milan', 'Florence', 'Naples', 'Turin']
        property_types = ['apartment', 'house', 'villa', 'commercial']
        
        for i in range(50):
            properties.append({
                'id': i + 1,
                'title': f'Property {i + 1}',
                'city': np.random.choice(cities),
                'property_type': np.random.choice(property_types),
                'price': np.random.randint(200000, 1000000),
                'square_meters': np.random.randint(50, 300),
                'bedrooms': np.random.randint(1, 5),
                'bathrooms': np.random.randint(1, 3),
                'days_on_market': np.random.randint(1, 180),
                'views': np.random.randint(10, 500),
                'inquiries': np.random.randint(0, 20),
                'status': np.random.choice(['available', 'under_contract', 'sold'])
            })
        
        return properties
    
    def generate_market_data(self):
        """Generate mock market data"""
        return {
            'average_price_sqm': 4500,
            'price_change_monthly': 2.3,
            'inventory_levels': 'moderate',
            'days_on_market_avg': 65,
            'market_velocity': 'normal',
            'price_trends': {
                'last_6_months': [4200, 4250, 4300, 4400, 4450, 4500],
                'forecast_6_months': [4550, 4600, 4650, 4700, 4750, 4800]
            },
            'volume_trends': {
                'last_6_months': [120, 135, 140, 155, 160, 165],
                'forecast_6_months': [170, 175, 180, 185, 190, 195]
            }
        }
    
    def get_dashboard_overview(self, date_range='30d'):
        """Get high-level dashboard overview"""
        # Calculate date range
        end_date = datetime.now()
        if date_range == '7d':
            start_date = end_date - timedelta(days=7)
        elif date_range == '30d':
            start_date = end_date - timedelta(days=30)
        elif date_range == '90d':
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=365)
        
        # Filter sales data
        sales_data = [
            item for item in self.mock_data['sales_data']
            if datetime.strptime(item['date'], '%Y-%m-%d') >= start_date
        ]
        
        # Calculate KPIs
        total_revenue = sum(item['revenue'] for item in sales_data)
        total_deals = sum(item['deals_closed'] for item in sales_data)
        total_leads = sum(item['leads_generated'] for item in sales_data)
        total_views = sum(item['property_views'] for item in sales_data)
        
        # Calculate previous period for comparison
        prev_start = start_date - (end_date - start_date)
        prev_sales_data = [
            item for item in self.mock_data['sales_data']
            if prev_start <= datetime.strptime(item['date'], '%Y-%m-%d') < start_date
        ]
        
        prev_revenue = sum(item['revenue'] for item in prev_sales_data) if prev_sales_data else 1
        prev_deals = sum(item['deals_closed'] for item in prev_sales_data) if prev_sales_data else 1
        prev_leads = sum(item['leads_generated'] for item in prev_sales_data) if prev_sales_data else 1
        
        # Calculate changes
        revenue_change = ((total_revenue - prev_revenue) / prev_revenue) * 100 if prev_revenue > 0 else 0
        deals_change = ((total_deals - prev_deals) / prev_deals) * 100 if prev_deals > 0 else 0
        leads_change = ((total_leads - prev_leads) / prev_leads) * 100 if prev_leads > 0 else 0
        
        return {
            'kpis': {
                'total_revenue': {
                    'value': total_revenue,
                    'change': revenue_change,
                    'trend': 'up' if revenue_change > 0 else 'down'
                },
                'deals_closed': {
                    'value': total_deals,
                    'change': deals_change,
                    'trend': 'up' if deals_change > 0 else 'down'
                },
                'leads_generated': {
                    'value': total_leads,
                    'change': leads_change,
                    'trend': 'up' if leads_change > 0 else 'down'
                },
                'conversion_rate': {
                    'value': (total_deals / total_leads * 100) if total_leads > 0 else 0,
                    'change': 2.3,
                    'trend': 'up'
                },
                'avg_deal_size': {
                    'value': total_revenue / total_deals if total_deals > 0 else 0,
                    'change': 5.7,
                    'trend': 'up'
                },
                'property_views': {
                    'value': total_views,
                    'change': 12.4,
                    'trend': 'up'
                }
            },
            'charts_data': {
                'revenue_trend': self.get_revenue_trend_data(sales_data),
                'deals_pipeline': self.get_pipeline_data(),
                'lead_sources': self.get_lead_sources_data(),
                'property_performance': self.get_property_performance_data()
            }
        }
    
    def get_revenue_trend_data(self, sales_data):
        """Get revenue trend data for charts"""
        # Group by week for better visualization
        df = pd.DataFrame(sales_data)
        df['date'] = pd.to_datetime(df['date'])
        df['week'] = df['date'].dt.to_period('W')
        
        weekly_data = df.groupby('week').agg({
            'revenue': 'sum',
            'deals_closed': 'sum',
            'leads_generated': 'sum'
        }).reset_index()
        
        weekly_data['week'] = weekly_data['week'].astype(str)
        
        return weekly_data.to_dict('records')
    
    def get_pipeline_data(self):
        """Get deal pipeline data"""
        return {
            'stages': [
                {'name': 'Lead', 'count': 45, 'value': 2250000},
                {'name': 'Qualified', 'count': 32, 'value': 1920000},
                {'name': 'Proposal', 'count': 18, 'value': 1440000},
                {'name': 'Negotiation', 'count': 12, 'value': 1080000},
                {'name': 'Closed Won', 'count': 8, 'value': 800000}
            ]
        }
    
    def get_lead_sources_data(self):
        """Get lead sources breakdown"""
        return [
            {'source': 'Website', 'count': 156, 'percentage': 35},
            {'source': 'Referrals', 'count': 89, 'percentage': 20},
            {'source': 'Social Media', 'count': 67, 'percentage': 15},
            {'source': 'Email Marketing', 'count': 56, 'percentage': 12},
            {'source': 'Direct', 'count': 45, 'percentage': 10},
            {'source': 'Other', 'count': 34, 'percentage': 8}
        ]
    
    def get_property_performance_data(self):
        """Get property performance metrics"""
        properties = self.mock_data['properties']
        
        # Calculate performance metrics
        avg_days_market = np.mean([p['days_on_market'] for p in properties])
        total_views = sum(p['views'] for p in properties)
        total_inquiries = sum(p['inquiries'] for p in properties)
        
        return {
            'avg_days_on_market': avg_days_market,
            'total_views': total_views,
            'total_inquiries': total_inquiries,
            'inquiry_rate': (total_inquiries / total_views * 100) if total_views > 0 else 0,
            'top_performing': sorted(properties, key=lambda x: x['views'], reverse=True)[:5]
        }
    
    def get_agent_performance(self, agent_id=None):
        """Get agent performance data"""
        agents = self.mock_data['agents']
        
        if agent_id:
            agent = next((a for a in agents if a['id'] == agent_id), None)
            if not agent:
                return None
            
            # Add detailed metrics for specific agent
            agent['performance_trend'] = [
                {'month': 'Jan', 'deals': 3, 'revenue': 180000},
                {'month': 'Feb', 'deals': 4, 'revenue': 240000},
                {'month': 'Mar', 'deals': 5, 'revenue': 300000},
                {'month': 'Apr', 'deals': 3, 'revenue': 210000},
                {'month': 'May', 'deals': 6, 'revenue': 360000},
                {'month': 'Jun', 'deals': 4, 'revenue': 280000}
            ]
            
            return agent
        else:
            # Return all agents with rankings
            sorted_agents = sorted(agents, key=lambda x: x['revenue_generated'], reverse=True)
            for i, agent in enumerate(sorted_agents):
                agent['rank'] = i + 1
            
            return sorted_agents
    
    def get_market_analysis(self, location=None):
        """Get market analysis data"""
        market_data = self.mock_data['market_data']
        
        if location:
            # Filter by location if specified
            market_data['location'] = location
        
        # Add trend analysis
        market_data['trend_analysis'] = {
            'price_momentum': 'positive',
            'volume_momentum': 'positive',
            'market_health_score': 78,
            'investment_rating': 'good',
            'recommendations': [
                'Good time for buyers - stable prices',
                'Sellers should price competitively',
                'Investment opportunities in emerging areas'
            ]
        }
        
        return market_data
    
    def get_forecasting_data(self, metric='revenue', periods=6):
        """Get forecasting predictions"""
        if metric == 'revenue':
            # Generate revenue forecast
            historical = [450000, 520000, 480000, 590000, 610000, 580000]
            forecast = [620000, 650000, 680000, 710000, 740000, 770000]
        elif metric == 'deals':
            historical = [12, 15, 13, 18, 19, 17]
            forecast = [20, 22, 24, 26, 28, 30]
        else:
            historical = [150, 180, 165, 200, 210, 195]
            forecast = [220, 240, 260, 280, 300, 320]
        
        return {
            'historical': historical,
            'forecast': forecast,
            'confidence_intervals': {
                'upper': [f * 1.1 for f in forecast],
                'lower': [f * 0.9 for f in forecast]
            },
            'accuracy': 85.6,
            'model_type': 'Random Forest Regression'
        }

# Initialize analytics service
analytics_service = DashboardAnalytics()

@analytics_bp.route('/dashboard/overview', methods=['GET'])
def get_dashboard_overview():
    """Get dashboard overview with KPIs and charts"""
    try:
        date_range = request.args.get('range', '30d')
        overview = analytics_service.get_dashboard_overview(date_range)
        
        return jsonify({
            'success': True,
            'data': overview,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/analytics/sales', methods=['GET'])
def get_sales_analytics():
    """Get detailed sales analytics"""
    try:
        date_range = request.args.get('range', '30d')
        overview = analytics_service.get_dashboard_overview(date_range)
        
        sales_analytics = {
            'revenue_metrics': overview['kpis'],
            'trends': overview['charts_data']['revenue_trend'],
            'pipeline': overview['charts_data']['deals_pipeline'],
            'forecasting': analytics_service.get_forecasting_data('revenue')
        }
        
        return jsonify({
            'success': True,
            'data': sales_analytics
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/analytics/agents', methods=['GET'])
def get_agent_analytics():
    """Get agent performance analytics"""
    try:
        agent_id = request.args.get('agent_id', type=int)
        agents_data = analytics_service.get_agent_performance(agent_id)
        
        return jsonify({
            'success': True,
            'data': agents_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/analytics/market', methods=['GET'])
def get_market_analytics():
    """Get market analysis data"""
    try:
        location = request.args.get('location')
        market_data = analytics_service.get_market_analysis(location)
        
        return jsonify({
            'success': True,
            'data': market_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/analytics/properties', methods=['GET'])
def get_property_analytics():
    """Get property performance analytics"""
    try:
        overview = analytics_service.get_dashboard_overview()
        property_data = overview['charts_data']['property_performance']
        
        return jsonify({
            'success': True,
            'data': property_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/forecasting/<metric>', methods=['GET'])
def get_forecasting(metric):
    """Get forecasting data for specific metric"""
    try:
        periods = request.args.get('periods', 6, type=int)
        forecast_data = analytics_service.get_forecasting_data(metric, periods)
        
        return jsonify({
            'success': True,
            'data': forecast_data,
            'metric': metric
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/crm/pipeline', methods=['GET'])
def get_crm_pipeline():
    """Get CRM pipeline data"""
    try:
        overview = analytics_service.get_dashboard_overview()
        pipeline_data = overview['charts_data']['deals_pipeline']
        
        # Add detailed deal information
        pipeline_data['deals'] = [
            {
                'id': 1,
                'client_name': 'Marco Rossi',
                'property': 'Luxury Apartment - Rome',
                'value': 450000,
                'stage': 'Negotiation',
                'probability': 75,
                'agent': 'Giulia Bianchi',
                'last_activity': '2025-01-06',
                'next_action': 'Follow up on financing'
            },
            {
                'id': 2,
                'client_name': 'Anna Verdi',
                'property': 'Villa - Florence',
                'value': 680000,
                'stage': 'Proposal',
                'probability': 60,
                'agent': 'Alessandro Conti',
                'last_activity': '2025-01-05',
                'next_action': 'Schedule property viewing'
            }
        ]
        
        return jsonify({
            'success': True,
            'data': pipeline_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


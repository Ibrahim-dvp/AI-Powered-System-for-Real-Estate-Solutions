from flask import Blueprint, request, jsonify
import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
import requests
from jinja2 import Template
import uuid

email_campaigns_bp = Blueprint('email_campaigns', __name__)

class EmailMarketingService:
    def __init__(self):
        self.smtp_config = {
            'host': os.getenv('SMTP_HOST', 'smtp.gmail.com'),
            'port': int(os.getenv('SMTP_PORT', 587)),
            'username': os.getenv('SMTP_USERNAME', ''),
            'password': os.getenv('SMTP_PASSWORD', ''),
            'use_tls': True
        }
        
        self.baserow_config = {
            'api_url': os.getenv('BASEROW_API_URL', 'https://daytaa.intelligentb2b.com/api'),
            'token': os.getenv('BASEROW_TOKEN', ''),
            'users_table_id': os.getenv('BASEROW_USERS_TABLE_ID', ''),
            'campaigns_table_id': os.getenv('BASEROW_CAMPAIGNS_TABLE_ID', '')
        }
        
        self.email_templates = self.load_email_templates()
    
    def load_email_templates(self):
        """Load email templates"""
        return {
            'welcome': {
                'subject': 'Welcome {{first_name}} - Your Real Estate Journey Begins!',
                'template': '''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center;">
                        <h1>Welcome {{first_name}}!</h1>
                        <p>Your Real Estate Journey Starts Here</p>
                    </div>
                    
                    <div style="padding: 30px;">
                        <h2>Thank you for joining our community!</h2>
                        <p>Hi {{first_name}},</p>
                        <p>We're excited to help you find your perfect property. Based on your preferences, we've curated some amazing options for you.</p>
                        
                        {% if featured_properties %}
                        <h3>🏠 Properties You Might Love:</h3>
                        {% for property in featured_properties %}
                        <div style="border: 1px solid #ddd; margin: 20px 0; padding: 15px; border-radius: 8px;">
                            <h4>{{property.title}}</h4>
                            <p><strong>Price:</strong> €{{property.price}}</p>
                            <p><strong>Location:</strong> {{property.location}}</p>
                            <p><strong>Details:</strong> {{property.bedrooms}} bed, {{property.bathrooms}} bath, {{property.square_meters}}m²</p>
                            <a href="{{property.url}}" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Property</a>
                        </div>
                        {% endfor %}
                        {% endif %}
                        
                        <div style="background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 8px;">
                            <h3>🎯 What's Next?</h3>
                            <ul>
                                <li>Browse our latest listings</li>
                                <li>Set up property alerts</li>
                                <li>Schedule viewings</li>
                                <li>Get market insights</li>
                            </ul>
                        </div>
                        
                        <p>Questions? Reply to this email or call us at +39 123 456 7890</p>
                        <p>Best regards,<br>Your Real Estate Team</p>
                    </div>
                </div>
                '''
            },
            'property_alert': {
                'subject': '🏠 New Property Alert: {{property_title}} in {{property_location}}',
                'template': '''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: #007bff; color: white; padding: 20px; text-align: center;">
                        <h1>🏠 New Property Alert!</h1>
                        <p>A property matching your criteria is now available</p>
                    </div>
                    
                    <div style="padding: 30px;">
                        <h2>Hi {{first_name}},</h2>
                        <p>Great news! A new property that matches your search criteria has just been listed:</p>
                        
                        <div style="border: 2px solid #007bff; margin: 20px 0; padding: 20px; border-radius: 10px; background: #f8f9fa;">
                            <h3>{{property_title}}</h3>
                            <p><strong>💰 Price:</strong> €{{property_price}}</p>
                            <p><strong>📍 Location:</strong> {{property_location}}</p>
                            <p><strong>🏠 Type:</strong> {{property_type}}</p>
                            <p><strong>🛏️ Bedrooms:</strong> {{property_bedrooms}}</p>
                            <p><strong>🚿 Bathrooms:</strong> {{property_bathrooms}}</p>
                            <p><strong>📐 Size:</strong> {{property_size}}m²</p>
                            
                            <p>{{property_description}}</p>
                            
                            <div style="margin: 20px 0;">
                                <a href="{{property_url}}" style="background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin-right: 10px;">View Details</a>
                                <a href="{{viewing_url}}" style="background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">Schedule Viewing</a>
                            </div>
                        </div>
                        
                        <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <h4>⚡ Act Fast!</h4>
                            <p>Properties like this don't last long. Similar properties in this area typically receive offers within 5-7 days.</p>
                        </div>
                        
                        <p>Questions about this property? Reply to this email or call us at +39 123 456 7890</p>
                    </div>
                </div>
                '''
            },
            'market_insights': {
                'subject': '📊 {{month}} Market Update: Key Insights for {{first_name}}',
                'template': '''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center;">
                        <h1>📊 Market Insights</h1>
                        <p>Your Weekly Real Estate Update</p>
                    </div>
                    
                    <div style="padding: 30px;">
                        <h2>Hi {{first_name}},</h2>
                        <p>Here's your weekly dose of real estate market insights to keep you informed about the latest trends and opportunities.</p>
                        
                        <div style="background: #e7f3ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <h3>🏠 Market Snapshot</h3>
                            <p><strong>Average Price/m²:</strong> €{{avg_price_sqm}}</p>
                            <p><strong>Market Trend:</strong> {{trend_direction}} {{trend_percentage}}%</p>
                            <p><strong>Days on Market:</strong> {{avg_days_market}} days</p>
                        </div>
                        
                        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <h3>🎯 Key Trends</h3>
                            <ul>
                                <li>Inventory levels are {{inventory_level}}</li>
                                <li>{{trend_insight}}</li>
                                <li>Best opportunities in {{opportunity_areas}}</li>
                            </ul>
                        </div>
                        
                        <div style="background: #d4edda; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <h3>💡 What This Means for You</h3>
                            <p>{{personalized_advice}}</p>
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{{market_report_url}}" style="background: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-size: 18px;">View Full Report</a>
                        </div>
                        
                        <p>Want personalized insights? <a href="{{consultation_url}}">Book a free consultation</a> with our experts!</p>
                    </div>
                </div>
                '''
            },
            'reengagement': {
                'subject': '{{first_name}}, we miss you! {{incentive_text}}',
                'template': '''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: #28a745; color: white; padding: 20px; text-align: center;">
                        <h1>We Miss You, {{first_name}}! 👋</h1>
                        <p>Come back and discover what's new</p>
                    </div>
                    
                    <div style="padding: 30px;">
                        <h2>It's been a while!</h2>
                        <p>Hi {{first_name}},</p>
                        <p>We noticed you haven't visited us recently. We've been working hard to improve our platform and add amazing new features!</p>
                        
                        {% if incentive_offer %}
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin: 20px 0;">
                            <h3>🎁 Special Welcome Back Offer</h3>
                            <p>{{incentive_offer}}</p>
                            <a href="{{incentive_url}}" style="background: white; color: #667eea; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">Claim Your Offer</a>
                        </div>
                        {% endif %}
                        
                        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <h3>🚀 What's New</h3>
                            <ul>
                                <li>AI-powered property recommendations</li>
                                <li>Virtual reality property tours</li>
                                <li>Instant mortgage pre-approval</li>
                                <li>Market trend predictions</li>
                            </ul>
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{{search_url}}" style="background: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-size: 18px; margin: 10px;">Start Searching</a>
                            <a href="{{consultation_url}}" style="background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-size: 18px; margin: 10px;">Book Consultation</a>
                        </div>
                        
                        <p>Questions? Our team is here to help! Reply to this email or call us at +39 123 456 7890</p>
                    </div>
                </div>
                '''
            }
        }
    
    def send_email(self, to_email, subject, html_content, from_email=None):
        """Send email using SMTP"""
        try:
            if not from_email:
                from_email = self.smtp_config['username']
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_email
            msg['To'] = to_email
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            server = smtplib.SMTP(self.smtp_config['host'], self.smtp_config['port'])
            if self.smtp_config['use_tls']:
                server.starttls()
            
            server.login(self.smtp_config['username'], self.smtp_config['password'])
            server.send_message(msg)
            server.quit()
            
            return {'success': True, 'message': 'Email sent successfully'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def render_template(self, template_name, data):
        """Render email template with data"""
        if template_name not in self.email_templates:
            return None
        
        template_data = self.email_templates[template_name]
        
        # Render subject
        subject_template = Template(template_data['subject'])
        subject = subject_template.render(**data)
        
        # Render content
        content_template = Template(template_data['template'])
        content = content_template.render(**data)
        
        return {
            'subject': subject,
            'content': content
        }
    
    def get_user_from_baserow(self, user_id):
        """Get user data from Baserow"""
        try:
            headers = {
                'Authorization': f'Token {self.baserow_config["token"]}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.baserow_config['api_url']}/database/rows/table/{self.baserow_config['users_table_id']}/{user_id}/"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            print(f"Error fetching user from Baserow: {e}")
            return None
    
    def log_campaign_to_baserow(self, campaign_data):
        """Log email campaign to Baserow"""
        try:
            headers = {
                'Authorization': f'Token {self.baserow_config["token"]}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.baserow_config['api_url']}/database/rows/table/{self.baserow_config['campaigns_table_id']}/"
            response = requests.post(url, headers=headers, json=campaign_data)
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Error logging campaign to Baserow: {e}")
            return False
    
    def create_campaign(self, campaign_type, recipients, template_data):
        """Create and send email campaign"""
        results = []
        
        for recipient in recipients:
            try:
                # Merge recipient data with template data
                email_data = {**template_data, **recipient}
                
                # Render email template
                rendered = self.render_template(campaign_type, email_data)
                if not rendered:
                    results.append({
                        'email': recipient.get('email', 'unknown'),
                        'success': False,
                        'error': 'Template not found'
                    })
                    continue
                
                # Send email
                send_result = self.send_email(
                    recipient['email'],
                    rendered['subject'],
                    rendered['content']
                )
                
                # Log campaign
                campaign_log = {
                    'campaign_name': f"{campaign_type.title()} Campaign",
                    'campaign_type': campaign_type,
                    'recipient_email': recipient['email'],
                    'subject_line': rendered['subject'],
                    'sent_date': datetime.now().isoformat(),
                    'campaign_status': 'Sent' if send_result['success'] else 'Failed',
                    'user_id': recipient.get('id', ''),
                    'campaign_id': str(uuid.uuid4())
                }
                
                self.log_campaign_to_baserow(campaign_log)
                
                results.append({
                    'email': recipient['email'],
                    'success': send_result['success'],
                    'error': send_result.get('error', '')
                })
                
            except Exception as e:
                results.append({
                    'email': recipient.get('email', 'unknown'),
                    'success': False,
                    'error': str(e)
                })
        
        return results

# Initialize email service
email_service = EmailMarketingService()

@email_campaigns_bp.route('/send-welcome-email', methods=['POST'])
def send_welcome_email():
    """Send welcome email to new user"""
    try:
        data = request.json
        user_data = data.get('user_data', {})
        
        # Get property recommendations if provided
        featured_properties = data.get('featured_properties', [])
        
        template_data = {
            'first_name': user_data.get('first_name', 'Friend'),
            'featured_properties': featured_properties
        }
        
        recipients = [user_data]
        results = email_service.create_campaign('welcome', recipients, template_data)
        
        return jsonify({
            'success': True,
            'results': results,
            'campaign_type': 'welcome'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@email_campaigns_bp.route('/send-property-alert', methods=['POST'])
def send_property_alert():
    """Send property alert email"""
    try:
        data = request.json
        property_data = data.get('property_data', {})
        recipients = data.get('recipients', [])
        
        template_data = {
            'property_title': property_data.get('title', ''),
            'property_price': property_data.get('price', 0),
            'property_location': property_data.get('location', ''),
            'property_type': property_data.get('property_type', ''),
            'property_bedrooms': property_data.get('bedrooms', 0),
            'property_bathrooms': property_data.get('bathrooms', 0),
            'property_size': property_data.get('square_meters', 0),
            'property_description': property_data.get('description', ''),
            'property_url': f"https://your-website.com/property/{property_data.get('id', '')}",
            'viewing_url': f"https://your-website.com/schedule-viewing/{property_data.get('id', '')}"
        }
        
        results = email_service.create_campaign('property_alert', recipients, template_data)
        
        return jsonify({
            'success': True,
            'results': results,
            'campaign_type': 'property_alert'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@email_campaigns_bp.route('/send-market-insights', methods=['POST'])
def send_market_insights():
    """Send market insights email"""
    try:
        data = request.json
        market_data = data.get('market_data', {})
        recipients = data.get('recipients', [])
        
        current_date = datetime.now()
        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        current_month = month_names[current_date.month - 1]
        
        template_data = {
            'month': current_month,
            'avg_price_sqm': market_data.get('average_price_sqm', 4500),
            'trend_direction': '📈' if market_data.get('trend_percentage', 0) > 0 else '📉',
            'trend_percentage': abs(market_data.get('trend_percentage', 3.2)),
            'avg_days_market': market_data.get('average_days_on_market', 65),
            'inventory_level': market_data.get('inventory_levels', 'moderate'),
            'trend_insight': 'Strong buyer demand continues in prime locations',
            'opportunity_areas': 'emerging neighborhoods with growth potential',
            'personalized_advice': 'Based on current trends, this is a good time for both buyers and sellers to act.',
            'market_report_url': 'https://your-website.com/market-report',
            'consultation_url': 'https://your-website.com/consultation'
        }
        
        results = email_service.create_campaign('market_insights', recipients, template_data)
        
        return jsonify({
            'success': True,
            'results': results,
            'campaign_type': 'market_insights'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@email_campaigns_bp.route('/send-reengagement', methods=['POST'])
def send_reengagement():
    """Send re-engagement email"""
    try:
        data = request.json
        recipients = data.get('recipients', [])
        incentive_data = data.get('incentive_data', {})
        
        template_data = {
            'incentive_text': incentive_data.get('text', 'Special offer inside!'),
            'incentive_offer': incentive_data.get('offer', 'Free property valuation worth €200'),
            'incentive_url': incentive_data.get('url', 'https://your-website.com/special-offer'),
            'search_url': 'https://your-website.com/search',
            'consultation_url': 'https://your-website.com/consultation'
        }
        
        results = email_service.create_campaign('reengagement', recipients, template_data)
        
        return jsonify({
            'success': True,
            'results': results,
            'campaign_type': 'reengagement'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@email_campaigns_bp.route('/campaign-analytics', methods=['GET'])
def get_campaign_analytics():
    """Get email campaign analytics"""
    try:
        # Get date range from query parameters
        days = int(request.args.get('days', 30))
        start_date = datetime.now() - timedelta(days=days)
        
        # Mock analytics data (in real implementation, fetch from Baserow)
        analytics = {
            'total_campaigns': 156,
            'total_emails_sent': 2847,
            'total_delivered': 2789,
            'total_opened': 892,
            'total_clicked': 234,
            'delivery_rate': 97.96,
            'open_rate': 31.99,
            'click_rate': 26.23,
            'unsubscribe_rate': 1.2,
            'campaign_breakdown': {
                'welcome': {
                    'sent': 45,
                    'delivered': 44,
                    'opened': 18,
                    'clicked': 8,
                    'open_rate': 40.91,
                    'click_rate': 44.44
                },
                'property_alert': {
                    'sent': 78,
                    'delivered': 76,
                    'opened': 31,
                    'clicked': 12,
                    'open_rate': 40.79,
                    'click_rate': 38.71
                },
                'market_insights': {
                    'sent': 23,
                    'delivered': 23,
                    'opened': 8,
                    'clicked': 3,
                    'open_rate': 34.78,
                    'click_rate': 37.5
                },
                'reengagement': {
                    'sent': 10,
                    'delivered': 10,
                    'opened': 4,
                    'clicked': 2,
                    'open_rate': 40.0,
                    'click_rate': 50.0
                }
            },
            'top_performing_subjects': [
                {'subject': 'New luxury villa in Florence - Perfect match!', 'open_rate': 52.3},
                {'subject': 'Welcome Maria - Your dream home awaits!', 'open_rate': 48.7},
                {'subject': 'Market Update: Prices rising in Rome', 'open_rate': 45.2}
            ],
            'recent_campaigns': [
                {
                    'id': 'camp_001',
                    'name': 'Weekly Market Insights',
                    'type': 'market_insights',
                    'sent_date': '2025-01-06T10:00:00Z',
                    'recipients': 234,
                    'open_rate': 34.2,
                    'click_rate': 8.1
                },
                {
                    'id': 'camp_002',
                    'name': 'New Property Alert - Milan',
                    'type': 'property_alert',
                    'sent_date': '2025-01-05T14:30:00Z',
                    'recipients': 67,
                    'open_rate': 41.8,
                    'click_rate': 12.3
                }
            ]
        }
        
        return jsonify({
            'success': True,
            'analytics': analytics,
            'date_range': {
                'start_date': start_date.isoformat(),
                'end_date': datetime.now().isoformat(),
                'days': days
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@email_campaigns_bp.route('/test-email', methods=['POST'])
def test_email():
    """Send test email"""
    try:
        data = request.json
        template_name = data.get('template', 'welcome')
        test_email = data.get('email', '')
        test_data = data.get('test_data', {})
        
        if not test_email:
            return jsonify({
                'success': False,
                'error': 'Test email address required'
            }), 400
        
        # Default test data
        default_test_data = {
            'first_name': 'Test User',
            'property_title': 'Beautiful Apartment in Rome',
            'property_price': '450000',
            'property_location': 'Rome, Italy',
            'month': 'January'
        }
        
        template_data = {**default_test_data, **test_data}
        recipients = [{'email': test_email, 'first_name': template_data['first_name']}]
        
        results = email_service.create_campaign(template_name, recipients, template_data)
        
        return jsonify({
            'success': True,
            'results': results,
            'message': f'Test email sent to {test_email}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


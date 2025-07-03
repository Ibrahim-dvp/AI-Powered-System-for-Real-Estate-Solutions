# Email Marketing Automation with n8n

**Integration:** n8n + Baserow + Email Services + AI Personalization  
**Date:** January 7, 2025

## Overview

This email marketing automation system uses n8n workflows to deliver personalized property recommendations, nurture leads through automated sequences, and manage targeted campaigns based on user behavior, preferences, and lead scoring data from your Baserow database.

## Architecture

```
User Behavior → Baserow → n8n Triggers → Email Templates → Personalization → Delivery
     ↓              ↓           ↓              ↓               ↓            ↓
Lead Scoring → Segmentation → Campaign Logic → Content AI → Email Service → Analytics
```

## Part 1: Email Campaign Types

### 1.1 Automated Campaign Types

**Welcome Series:**
- New user registration welcome
- Platform introduction and features
- First property recommendations

**Property Alerts:**
- New listings matching criteria
- Price changes on saved properties
- Similar properties to viewed ones

**Nurture Campaigns:**
- Market insights and trends
- Neighborhood spotlights
- Investment tips and guides

**Re-engagement:**
- Inactive user reactivation
- Updated search suggestions
- Special offers and incentives

**Transactional:**
- Viewing confirmations
- Document requests
- Agent introductions

### 1.2 Segmentation Strategy

**Behavioral Segments:**
- Active browsers (high engagement)
- Property savers (bookmark behavior)
- Search refiners (multiple searches)
- Inquiry makers (contact forms)

**Demographic Segments:**
- First-time buyers
- Investors
- Luxury market
- Budget-conscious

**Geographic Segments:**
- City-specific campaigns
- Neighborhood focus
- Regional market updates

**Lifecycle Segments:**
- New leads (0-7 days)
- Warm prospects (8-30 days)
- Long-term nurture (30+ days)
- Past clients

## Part 2: n8n Email Workflows

### 2.1 Welcome Series Workflow

```json
{
  "name": "Welcome Email Series",
  "nodes": [
    {
      "parameters": {
        "triggerOn": "specificTable",
        "tableId": "USERS_TABLE_ID",
        "event": "created"
      },
      "name": "New User Trigger",
      "type": "n8n-nodes-base.baserowTrigger",
      "typeVersion": 1,
      "position": [240, 300]
    },
    {
      "parameters": {
        "functionCode": "// Process new user data\nconst user = $input.first().json;\n\n// Determine user type and preferences\nlet userType = 'general';\nif (user.annual_income && user.annual_income > 100000) {\n  userType = 'luxury';\n} else if (user.investment_purpose) {\n  userType = 'investor';\n} else if (user.first_time_buyer) {\n  userType = 'first_time';\n}\n\n// Prepare welcome email data\nconst emailData = {\n  user_id: user.id,\n  email: user.email,\n  first_name: user.first_name,\n  user_type: userType,\n  preferences: {\n    budget_min: user.budget_min || 0,\n    budget_max: user.budget_max || 1000000,\n    property_type: user.property_type_interest || 'apartment',\n    location: user.location_preferences || 'Rome'\n  },\n  welcome_sequence: 1\n};\n\nreturn [{ json: emailData }];"
      },
      "name": "Process User Data",
      "type": "n8n-nodes-base.function",
      "typeVersion": 1,
      "position": [460, 300]
    },
    {
      "parameters": {
        "url": "http://localhost:5001/api/search-properties",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "httpMethod": "POST",
        "jsonParameters": true,
        "parametersJson": "={{ JSON.stringify({\n  budget_min: $json.preferences.budget_min,\n  budget_max: $json.preferences.budget_max,\n  property_type: $json.preferences.property_type,\n  location: $json.preferences.location\n}) }}",
        "options": {}
      },
      "name": "Get Property Recommendations",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 1,
      "position": [680, 300]
    },
    {
      "parameters": {
        "functionCode": "// Generate personalized welcome email content\nconst userData = $('Process User Data').first().json;\nconst properties = $input.first().json.properties || [];\n\n// Select top 3 properties for email\nconst featuredProperties = properties.slice(0, 3);\n\n// Generate email content based on user type\nlet emailContent = '';\nlet subject = '';\n\nswitch(userData.user_type) {\n  case 'luxury':\n    subject = `Welcome ${userData.first_name} - Exclusive Luxury Properties Await`;\n    emailContent = `\n      <h1>Welcome to Premium Real Estate, ${userData.first_name}!</h1>\n      <p>We're delighted to have you join our exclusive community of luxury property enthusiasts.</p>\n      <p>Based on your preferences, we've curated some exceptional properties that match your sophisticated taste:</p>\n    `;\n    break;\n    \n  case 'investor':\n    subject = `Welcome ${userData.first_name} - Investment Opportunities Inside`;\n    emailContent = `\n      <h1>Welcome to Smart Investing, ${userData.first_name}!</h1>\n      <p>Ready to build your real estate portfolio? We've identified some promising investment opportunities:</p>\n    `;\n    break;\n    \n  case 'first_time':\n    subject = `Welcome ${userData.first_name} - Your Home Journey Starts Here`;\n    emailContent = `\n      <h1>Welcome Home, ${userData.first_name}!</h1>\n      <p>Congratulations on taking the first step toward homeownership! We're here to guide you every step of the way.</p>\n      <p>Here are some perfect starter homes in your area:</p>\n    `;\n    break;\n    \n  default:\n    subject = `Welcome ${userData.first_name} - Your Perfect Property Awaits`;\n    emailContent = `\n      <h1>Welcome ${userData.first_name}!</h1>\n      <p>Thank you for joining our real estate community. We're excited to help you find your perfect property.</p>\n      <p>Based on your search preferences, here are some properties you might love:</p>\n    `;\n}\n\n// Add property listings to email\nfeaturedProperties.forEach(property => {\n  emailContent += `\n    <div style=\"border: 1px solid #ddd; margin: 20px 0; padding: 15px; border-radius: 8px;\">\n      <h3>${property.title}</h3>\n      <p><strong>Price:</strong> €${property.price.toLocaleString()}</p>\n      <p><strong>Location:</strong> ${property.location}</p>\n      <p><strong>Details:</strong> ${property.bedrooms} bed, ${property.bathrooms} bath, ${property.square_meters}m²</p>\n      <p>${property.description}</p>\n      <a href=\"${property.url}\" style=\"background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;\">View Property</a>\n    </div>\n  `;\n});\n\n// Add footer\nemailContent += `\n  <div style=\"margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;\">\n    <p>This is just the beginning! We'll continue to send you personalized property recommendations based on your preferences.</p>\n    <p>Questions? Reply to this email or call us at +39 123 456 7890</p>\n    <p>Best regards,<br>Your Real Estate Team</p>\n  </div>\n`;\n\nreturn [{\n  json: {\n    ...userData,\n    email_subject: subject,\n    email_content: emailContent,\n    featured_properties: featuredProperties\n  }\n}];"
      },
      "name": "Generate Email Content",
      "type": "n8n-nodes-base.function",
      "typeVersion": 1,
      "position": [900, 300]
    },
    {
      "parameters": {
        "fromEmail": "noreply@intelligentb2b.com",
        "toEmail": "={{ $json.email }}",
        "subject": "={{ $json.email_subject }}",
        "emailFormat": "html",
        "message": "={{ $json.email_content }}",
        "options": {}
      },
      "name": "Send Welcome Email",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 1,
      "position": [1120, 300]
    },
    {
      "parameters": {
        "authentication": "headerAuth",
        "resource": "row",
        "operation": "create",
        "tableId": "EMAIL_CAMPAIGNS_TABLE_ID",
        "fieldsUi": {
          "fieldValues": [
            {
              "fieldName": "campaign_name",
              "fieldValue": "Welcome Series - Email 1"
            },
            {
              "fieldName": "campaign_type",
              "fieldValue": "Welcome"
            },
            {
              "fieldName": "recipient_email",
              "fieldValue": "={{ $json.email }}"
            },
            {
              "fieldName": "subject_line",
              "fieldValue": "={{ $json.email_subject }}"
            },
            {
              "fieldName": "sent_date",
              "fieldValue": "={{ new Date().toISOString() }}"
            },
            {
              "fieldName": "campaign_status",
              "fieldValue": "Sent"
            },
            {
              "fieldName": "user_id",
              "fieldValue": "={{ $json.user_id }}"
            }
          ]
        }
      },
      "name": "Log Email Campaign",
      "type": "n8n-nodes-base.baserow",
      "typeVersion": 1,
      "position": [1340, 300]
    },
    {
      "parameters": {
        "amount": 24,
        "unit": "hours"
      },
      "name": "Wait 24 Hours",
      "type": "n8n-nodes-base.wait",
      "typeVersion": 1,
      "position": [1560, 300]
    },
    {
      "parameters": {
        "functionCode": "// Prepare second welcome email\nconst userData = $('Generate Email Content').first().json;\n\nlet emailContent = `\n  <h1>Getting Started with Your Property Search</h1>\n  <p>Hi ${userData.first_name},</p>\n  <p>Yesterday we welcomed you to our platform. Today, let's help you make the most of your property search!</p>\n  \n  <h2>🔍 Search Tips for Better Results:</h2>\n  <ul>\n    <li><strong>Use Filters:</strong> Narrow down by price, location, and property type</li>\n    <li><strong>Save Favorites:</strong> Bookmark properties you like for easy access</li>\n    <li><strong>Set Alerts:</strong> Get notified when new properties match your criteria</li>\n    <li><strong>Virtual Tours:</strong> Take 360° tours from the comfort of your home</li>\n  </ul>\n  \n  <h2>📍 Popular Neighborhoods in ${userData.preferences.location}:</h2>\n  <p>Based on your interest in ${userData.preferences.location}, here are some trending areas:</p>\n  <ul>\n    <li><strong>City Center:</strong> Historic charm with modern amenities</li>\n    <li><strong>Business District:</strong> Perfect for professionals and investors</li>\n    <li><strong>Residential Areas:</strong> Family-friendly with great schools</li>\n    <li><strong>Emerging Zones:</strong> Up-and-coming areas with growth potential</li>\n  </ul>\n  \n  <div style=\"background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 8px;\">\n    <h3>💡 Pro Tip:</h3>\n    <p>Schedule a consultation with one of our expert agents to get personalized advice and access to exclusive listings!</p>\n    <a href=\"https://your-website.com/book-consultation\" style=\"background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px;\">Book Free Consultation</a>\n  </div>\n  \n  <p>Questions about any of this? Just reply to this email - we're here to help!</p>\n  <p>Happy house hunting!<br>Your Real Estate Team</p>\n`;\n\nreturn [{\n  json: {\n    ...userData,\n    email_subject: `${userData.first_name}, here's how to find your perfect property`,\n    email_content: emailContent,\n    welcome_sequence: 2\n  }\n}];"
      },
      "name": "Generate Email 2 Content",
      "type": "n8n-nodes-base.function",
      "typeVersion": 1,
      "position": [1780, 300]
    },
    {
      "parameters": {
        "fromEmail": "noreply@intelligentb2b.com",
        "toEmail": "={{ $json.email }}",
        "subject": "={{ $json.email_subject }}",
        "emailFormat": "html",
        "message": "={{ $json.email_content }}",
        "options": {}
      },
      "name": "Send Email 2",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 1,
      "position": [2000, 300]
    }
  ],
  "connections": {
    "New User Trigger": {
      "main": [
        [
          {
            "node": "Process User Data",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Process User Data": {
      "main": [
        [
          {
            "node": "Get Property Recommendations",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Get Property Recommendations": {
      "main": [
        [
          {
            "node": "Generate Email Content",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Generate Email Content": {
      "main": [
        [
          {
            "node": "Send Welcome Email",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Send Welcome Email": {
      "main": [
        [
          {
            "node": "Log Email Campaign",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Log Email Campaign": {
      "main": [
        [
          {
            "node": "Wait 24 Hours",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Wait 24 Hours": {
      "main": [
        [
          {
            "node": "Generate Email 2 Content",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Generate Email 2 Content": {
      "main": [
        [
          {
            "node": "Send Email 2",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

### 2.2 Property Alert Workflow

```json
{
  "name": "New Property Alert System",
  "nodes": [
    {
      "parameters": {
        "triggerOn": "specificTable",
        "tableId": "PROPERTIES_TABLE_ID",
        "event": "created"
      },
      "name": "New Property Trigger",
      "type": "n8n-nodes-base.baserowTrigger",
      "typeVersion": 1,
      "position": [240, 300]
    },
    {
      "parameters": {
        "authentication": "headerAuth",
        "resource": "row",
        "operation": "getAll",
        "tableId": "USERS_TABLE_ID",
        "filters": {
          "filter": [
            {
              "field": "marketing_consent",
              "type": "equal",
              "value": true
            }
          ]
        }
      },
      "name": "Get Subscribed Users",
      "type": "n8n-nodes-base.baserow",
      "typeVersion": 1,
      "position": [460, 300]
    },
    {
      "parameters": {
        "functionCode": "// Match property with user preferences\nconst property = $('New Property Trigger').first().json;\nconst users = $input.all().map(item => item.json);\n\nconst matchedUsers = [];\n\nusers.forEach(user => {\n  let matchScore = 0;\n  let matchReasons = [];\n  \n  // Budget match\n  if (user.budget_min && user.budget_max) {\n    if (property.current_price >= user.budget_min && property.current_price <= user.budget_max) {\n      matchScore += 40;\n      matchReasons.push('Within your budget');\n    }\n  }\n  \n  // Property type match\n  if (user.property_type_interest && user.property_type_interest.includes(property.property_type)) {\n    matchScore += 30;\n    matchReasons.push('Matches your preferred property type');\n  }\n  \n  // Location match\n  if (user.location_preferences && user.location_preferences.toLowerCase().includes(property.city.toLowerCase())) {\n    matchScore += 20;\n    matchReasons.push('In your preferred location');\n  }\n  \n  // Bedroom match\n  if (user.bedrooms_needed && property.bedrooms >= user.bedrooms_needed) {\n    matchScore += 10;\n    matchReasons.push('Has enough bedrooms');\n  }\n  \n  // Only send to users with good match (score >= 50)\n  if (matchScore >= 50) {\n    matchedUsers.push({\n      ...user,\n      match_score: matchScore,\n      match_reasons: matchReasons,\n      property: property\n    });\n  }\n});\n\nreturn matchedUsers.map(user => ({ json: user }));"
      },
      "name": "Match Users to Property",
      "type": "n8n-nodes-base.function",
      "typeVersion": 1,
      "position": [680, 300]
    },
    {
      "parameters": {
        "functionCode": "// Generate personalized property alert email\nconst user = $input.first().json;\nconst property = user.property;\n\nconst emailContent = `\n  <h1>🏠 New Property Alert for ${user.first_name}!</h1>\n  \n  <p>Great news! A new property that matches your criteria has just been listed:</p>\n  \n  <div style=\"border: 2px solid #007bff; margin: 20px 0; padding: 20px; border-radius: 10px; background: #f8f9fa;\">\n    <h2>${property.title}</h2>\n    \n    <div style=\"display: flex; justify-content: space-between; margin: 15px 0;\">\n      <div>\n        <p><strong>💰 Price:</strong> €${property.current_price.toLocaleString()}</p>\n        <p><strong>📍 Location:</strong> ${property.city}, ${property.region}</p>\n        <p><strong>🏠 Type:</strong> ${property.property_type}</p>\n      </div>\n      <div>\n        <p><strong>🛏️ Bedrooms:</strong> ${property.bedrooms}</p>\n        <p><strong>🚿 Bathrooms:</strong> ${property.bathrooms}</p>\n        <p><strong>📐 Size:</strong> ${property.square_meters}m²</p>\n      </div>\n    </div>\n    \n    <p><strong>Description:</strong> ${property.description}</p>\n    \n    <div style=\"margin: 20px 0;\">\n      <a href=\"https://your-website.com/property/${property.id}\" style=\"background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin-right: 10px;\">View Full Details</a>\n      <a href=\"https://your-website.com/schedule-viewing/${property.id}\" style=\"background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;\">Schedule Viewing</a>\n    </div>\n  </div>\n  \n  <div style=\"background: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0;\">\n    <h3>🎯 Why this property matches you:</h3>\n    <ul>\n      ${user.match_reasons.map(reason => `<li>${reason}</li>`).join('')}\n    </ul>\n    <p><strong>Match Score:</strong> ${user.match_score}% compatibility</p>\n  </div>\n  \n  <div style=\"background: #e7f3ff; padding: 15px; border-radius: 8px; margin: 20px 0;\">\n    <h3>⚡ Act Fast!</h3>\n    <p>Properties like this don't last long. In this area, similar properties typically receive offers within <strong>5-7 days</strong>.</p>\n    <p>Want to be the first to see it? <a href=\"https://your-website.com/schedule-viewing/${property.id}\">Schedule a viewing today</a>!</p>\n  </div>\n  \n  <hr style=\"margin: 30px 0;\">\n  \n  <p>Questions about this property? Reply to this email or call us at +39 123 456 7890</p>\n  \n  <p style=\"font-size: 12px; color: #666;\">\n    You're receiving this because you subscribed to property alerts matching your criteria. \n    <a href=\"https://your-website.com/unsubscribe?email=${user.email}\">Unsubscribe</a> | \n    <a href=\"https://your-website.com/preferences?email=${user.email}\">Update Preferences</a>\n  </p>\n`;\n\nreturn [{\n  json: {\n    user_id: user.id,\n    email: user.email,\n    first_name: user.first_name,\n    email_subject: `🏠 New ${property.property_type} in ${property.city} - Perfect Match!`,\n    email_content: emailContent,\n    property_id: property.id,\n    match_score: user.match_score\n  }\n}];"
      },
      "name": "Generate Alert Email",
      "type": "n8n-nodes-base.function",
      "typeVersion": 1,
      "position": [900, 300]
    },
    {
      "parameters": {
        "fromEmail": "alerts@intelligentb2b.com",
        "toEmail": "={{ $json.email }}",
        "subject": "={{ $json.email_subject }}",
        "emailFormat": "html",
        "message": "={{ $json.email_content }}",
        "options": {}
      },
      "name": "Send Property Alert",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 1,
      "position": [1120, 300]
    },
    {
      "parameters": {
        "authentication": "headerAuth",
        "resource": "row",
        "operation": "create",
        "tableId": "EMAIL_CAMPAIGNS_TABLE_ID",
        "fieldsUi": {
          "fieldValues": [
            {
              "fieldName": "campaign_name",
              "fieldValue": "Property Alert"
            },
            {
              "fieldName": "campaign_type",
              "fieldValue": "Property Alert"
            },
            {
              "fieldName": "recipient_email",
              "fieldValue": "={{ $json.email }}"
            },
            {
              "fieldName": "subject_line",
              "fieldValue": "={{ $json.email_subject }}"
            },
            {
              "fieldName": "sent_date",
              "fieldValue": "={{ new Date().toISOString() }}"
            },
            {
              "fieldName": "campaign_status",
              "fieldValue": "Sent"
            },
            {
              "fieldName": "user_id",
              "fieldValue": "={{ $json.user_id }}"
            },
            {
              "fieldName": "property_id",
              "fieldValue": "={{ $json.property_id }}"
            }
          ]
        }
      },
      "name": "Log Alert Campaign",
      "type": "n8n-nodes-base.baserow",
      "typeVersion": 1,
      "position": [1340, 300]
    }
  ],
  "connections": {
    "New Property Trigger": {
      "main": [
        [
          {
            "node": "Get Subscribed Users",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Get Subscribed Users": {
      "main": [
        [
          {
            "node": "Match Users to Property",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Match Users to Property": {
      "main": [
        [
          {
            "node": "Generate Alert Email",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Generate Alert Email": {
      "main": [
        [
          {
            "node": "Send Property Alert",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Send Property Alert": {
      "main": [
        [
          {
            "node": "Log Alert Campaign",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

### 2.3 Lead Nurture Workflow

```json
{
  "name": "Weekly Market Insights Nurture Campaign",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "cronExpression",
              "expression": "0 0 10 * * 3"
            }
          ]
        }
      },
      "name": "Weekly Wednesday Trigger",
      "type": "n8n-nodes-base.cron",
      "typeVersion": 1,
      "position": [240, 300]
    },
    {
      "parameters": {
        "authentication": "headerAuth",
        "resource": "row",
        "operation": "getAll",
        "tableId": "USERS_TABLE_ID",
        "filters": {
          "filter": [
            {
              "field": "marketing_consent",
              "type": "equal",
              "value": true
            },
            {
              "field": "lead_status",
              "type": "not_equal",
              "value": "Closed Won"
            }
          ]
        }
      },
      "name": "Get Active Leads",
      "type": "n8n-nodes-base.baserow",
      "typeVersion": 1,
      "position": [460, 300]
    },
    {
      "parameters": {
        "url": "http://localhost:5002/api/market-analysis",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "httpMethod": "POST",
        "jsonParameters": true,
        "parametersJson": "={{ JSON.stringify({\n  location: 'Rome',\n  property_type: 'apartment'\n}) }}",
        "options": {}
      },
      "name": "Get Market Data",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 1,
      "position": [680, 300]
    },
    {
      "parameters": {
        "functionCode": "// Generate market insights email content\nconst users = $('Get Active Leads').all().map(item => item.json);\nconst marketData = $input.first().json.market_analysis;\n\nconst currentDate = new Date();\nconst monthNames = ['January', 'February', 'March', 'April', 'May', 'June',\n  'July', 'August', 'September', 'October', 'November', 'December'];\nconst currentMonth = monthNames[currentDate.getMonth()];\n\n// Generate insights content\nconst insightsContent = `\n  <h1>📊 ${currentMonth} Real Estate Market Insights</h1>\n  \n  <div style=\"background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin: 20px 0;\">\n    <h2>🏠 Market Snapshot</h2>\n    <div style=\"display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-top: 15px;\">\n      <div>\n        <h3>Average Price/m²</h3>\n        <p style=\"font-size: 24px; font-weight: bold;\">€${marketData.market_metrics.average_price_sqm.toLocaleString()}</p>\n      </div>\n      <div>\n        <h3>Market Trend</h3>\n        <p style=\"font-size: 24px; font-weight: bold;\">${marketData.market_metrics.trend_percentage > 0 ? '📈' : '📉'} ${marketData.market_metrics.trend_percentage}%</p>\n      </div>\n    </div>\n  </div>\n  \n  <div style=\"background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;\">\n    <h2>🎯 Key Market Trends</h2>\n    <ul>\n      <li><strong>Inventory Levels:</strong> ${marketData.market_metrics.inventory_levels} - ${marketData.market_metrics.inventory_levels === 'low' ? 'Great time for sellers!' : 'More options for buyers!'}</li>\n      <li><strong>Days on Market:</strong> Properties are selling in an average of ${marketData.market_metrics.average_days_on_market} days</li>\n      <li><strong>Price Range:</strong> €${marketData.market_metrics.price_range.min.toLocaleString()} - €${marketData.market_metrics.price_range.max.toLocaleString()}</li>\n    </ul>\n  </div>\n  \n  <div style=\"background: #e7f3ff; padding: 20px; border-radius: 8px; margin: 20px 0;\">\n    <h2>🏘️ Neighborhood Spotlight</h2>\n    <p><strong>Transportation Score:</strong> ${marketData.neighborhood_insights.transportation_score}/10 - Excellent connectivity</p>\n    <p><strong>School Rating:</strong> ${marketData.neighborhood_insights.school_rating}/10 - Great for families</p>\n    <p><strong>Safety Score:</strong> ${marketData.neighborhood_insights.safety_score}/10 - Secure environment</p>\n    <p><strong>Future Development:</strong> ${marketData.neighborhood_insights.future_development}</p>\n  </div>\n  \n  <div style=\"background: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0;\">\n    <h2>💡 Investment Outlook</h2>\n    <ul>\n      <li><strong>Appreciation Forecast:</strong> ${marketData.investment_outlook.appreciation_forecast}</li>\n      <li><strong>Rental Yield:</strong> ${marketData.investment_outlook.rental_yield}</li>\n      <li><strong>Market Liquidity:</strong> ${marketData.investment_outlook.liquidity}</li>\n      <li><strong>Risk Level:</strong> ${marketData.investment_outlook.risk_level}</li>\n    </ul>\n  </div>\n  \n  <div style=\"background: #d4edda; padding: 20px; border-radius: 8px; margin: 20px 0;\">\n    <h2>📈 What This Means for You</h2>\n    <p>Based on current market conditions:</p>\n    <ul>\n      <li><strong>For Buyers:</strong> ${marketData.market_metrics.trend_percentage > 0 ? 'Consider acting soon as prices are rising' : 'Good opportunity to negotiate as market is cooling'}</li>\n      <li><strong>For Sellers:</strong> ${marketData.market_metrics.average_days_on_market < 60 ? 'Excellent time to list with fast sales' : 'Price competitively for quicker sales'}</li>\n      <li><strong>For Investors:</strong> Focus on areas with strong rental demand and growth potential</li>\n    </ul>\n  </div>\n  \n  <div style=\"text-align: center; margin: 30px 0;\">\n    <a href=\"https://your-website.com/market-report\" style=\"background: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-size: 18px;\">View Full Market Report</a>\n  </div>\n  \n  <hr style=\"margin: 30px 0;\">\n  \n  <p>Want personalized market insights for your specific area? <a href=\"https://your-website.com/consultation\">Book a free consultation</a> with one of our market experts!</p>\n`;\n\n// Return array of users with email content\nreturn users.map(user => ({\n  json: {\n    user_id: user.id,\n    email: user.email,\n    first_name: user.first_name,\n    email_subject: `📊 ${currentMonth} Market Update: Key Insights for ${user.first_name}`,\n    email_content: `\n      <p>Hi ${user.first_name},</p>\n      <p>Hope you're having a great week! Here's your weekly dose of real estate market insights to keep you informed about the latest trends and opportunities.</p>\n      ${insightsContent}\n      <p>As always, if you have any questions or want to discuss how these trends affect your property goals, just reply to this email!</p>\n      <p>Best regards,<br>Your Real Estate Team</p>\n      \n      <p style=\"font-size: 12px; color: #666; margin-top: 30px;\">\n        You're receiving this weekly market update because you're subscribed to our insights. \n        <a href=\"https://your-website.com/unsubscribe?email=${user.email}\">Unsubscribe</a> | \n        <a href=\"https://your-website.com/preferences?email=${user.email}\">Update Preferences</a>\n      </p>\n    `\n  }\n}));"
      },
      "name": "Generate Market Insights Email",
      "type": "n8n-nodes-base.function",
      "typeVersion": 1,
      "position": [900, 300]
    },
    {
      "parameters": {
        "fromEmail": "insights@intelligentb2b.com",
        "toEmail": "={{ $json.email }}",
        "subject": "={{ $json.email_subject }}",
        "emailFormat": "html",
        "message": "={{ $json.email_content }}",
        "options": {}
      },
      "name": "Send Market Insights",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 1,
      "position": [1120, 300]
    },
    {
      "parameters": {
        "authentication": "headerAuth",
        "resource": "row",
        "operation": "create",
        "tableId": "EMAIL_CAMPAIGNS_TABLE_ID",
        "fieldsUi": {
          "fieldValues": [
            {
              "fieldName": "campaign_name",
              "fieldValue": "Weekly Market Insights"
            },
            {
              "fieldName": "campaign_type",
              "fieldValue": "Nurture"
            },
            {
              "fieldName": "recipient_email",
              "fieldValue": "={{ $json.email }}"
            },
            {
              "fieldName": "subject_line",
              "fieldValue": "={{ $json.email_subject }}"
            },
            {
              "fieldName": "sent_date",
              "fieldValue": "={{ new Date().toISOString() }}"
            },
            {
              "fieldName": "campaign_status",
              "fieldValue": "Sent"
            },
            {
              "fieldName": "user_id",
              "fieldValue": "={{ $json.user_id }}"
            }
          ]
        }
      },
      "name": "Log Insights Campaign",
      "type": "n8n-nodes-base.baserow",
      "typeVersion": 1,
      "position": [1340, 300]
    }
  ],
  "connections": {
    "Weekly Wednesday Trigger": {
      "main": [
        [
          {
            "node": "Get Active Leads",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Get Active Leads": {
      "main": [
        [
          {
            "node": "Get Market Data",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Get Market Data": {
      "main": [
        [
          {
            "node": "Generate Market Insights Email",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Generate Market Insights Email": {
      "main": [
        [
          {
            "node": "Send Market Insights",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Send Market Insights": {
      "main": [
        [
          {
            "node": "Log Insights Campaign",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

### 2.4 Re-engagement Workflow

```json
{
  "name": "Re-engagement Campaign for Inactive Users",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "cronExpression",
              "expression": "0 0 14 * * 1"
            }
          ]
        }
      },
      "name": "Weekly Monday Check",
      "type": "n8n-nodes-base.cron",
      "typeVersion": 1,
      "position": [240, 300]
    },
    {
      "parameters": {
        "authentication": "headerAuth",
        "resource": "row",
        "operation": "getAll",
        "tableId": "USER_INTERACTIONS_TABLE_ID",
        "filters": {
          "filter": [
            {
              "field": "created_at",
              "type": "date_before",
              "value": "{{ new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString().split('T')[0] }}"
            }
          ]
        }
      },
      "name": "Get Recent Interactions",
      "type": "n8n-nodes-base.baserow",
      "typeVersion": 1,
      "position": [460, 300]
    },
    {
      "parameters": {
        "authentication": "headerAuth",
        "resource": "row",
        "operation": "getAll",
        "tableId": "USERS_TABLE_ID",
        "filters": {
          "filter": [
            {
              "field": "marketing_consent",
              "type": "equal",
              "value": true
            }
          ]
        }
      },
      "name": "Get All Users",
      "type": "n8n-nodes-base.baserow",
      "typeVersion": 1,
      "position": [680, 300]
    },
    {
      "parameters": {
        "functionCode": "// Find inactive users (no interactions in last 14 days)\nconst recentInteractions = $('Get Recent Interactions').all().map(item => item.json);\nconst allUsers = $input.all().map(item => item.json);\n\n// Get user IDs with recent activity\nconst activeUserIds = new Set(recentInteractions.map(interaction => interaction.user_id));\n\n// Find inactive users\nconst inactiveUsers = allUsers.filter(user => {\n  // User is inactive if:\n  // 1. No recent interactions\n  // 2. Registered more than 14 days ago\n  // 3. Has marketing consent\n  \n  const registrationDate = new Date(user.registration_date);\n  const fourteenDaysAgo = new Date(Date.now() - 14 * 24 * 60 * 60 * 1000);\n  \n  return !activeUserIds.has(user.id) && \n         registrationDate < fourteenDaysAgo && \n         user.marketing_consent;\n});\n\n// Categorize inactive users by inactivity period\nconst categorizedUsers = inactiveUsers.map(user => {\n  const registrationDate = new Date(user.registration_date);\n  const daysSinceRegistration = Math.floor((Date.now() - registrationDate.getTime()) / (24 * 60 * 60 * 1000));\n  \n  let category = 'recent';\n  if (daysSinceRegistration > 90) {\n    category = 'long_term';\n  } else if (daysSinceRegistration > 30) {\n    category = 'medium_term';\n  }\n  \n  return {\n    ...user,\n    inactivity_category: category,\n    days_since_registration: daysSinceRegistration\n  };\n});\n\nreturn categorizedUsers.map(user => ({ json: user }));"
      },
      "name": "Identify Inactive Users",
      "type": "n8n-nodes-base.function",
      "typeVersion": 1,
      "position": [900, 300]
    },
    {
      "parameters": {
        "functionCode": "// Generate personalized re-engagement email\nconst user = $input.first().json;\n\nlet emailContent = '';\nlet subject = '';\nlet incentive = '';\n\n// Customize content based on inactivity period\nswitch(user.inactivity_category) {\n  case 'recent':\n    subject = `${user.first_name}, we miss you! New properties await 🏠`;\n    incentive = 'Free property valuation for your current home';\n    emailContent = `\n      <h1>We Miss You, ${user.first_name}! 👋</h1>\n      <p>It's been a while since we've seen you on our platform. We wanted to reach out and see if we can help you find what you're looking for!</p>\n      \n      <div style=\"background: #e7f3ff; padding: 20px; border-radius: 8px; margin: 20px 0;\">\n        <h2>🎁 Welcome Back Gift</h2>\n        <p>As a thank you for being part of our community, we're offering you a <strong>free professional property valuation</strong> (worth €200)!</p>\n        <a href=\"https://your-website.com/free-valuation?user=${user.id}\" style=\"background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;\">Claim Your Free Valuation</a>\n      </div>\n    `;\n    break;\n    \n  case 'medium_term':\n    subject = `${user.first_name}, exclusive properties + special offer inside! 🌟`;\n    incentive = '€500 cashback on your first property purchase';\n    emailContent = `\n      <h1>Exclusive Comeback Offer for ${user.first_name}! ⭐</h1>\n      <p>We've been working hard to improve our platform and add amazing new features. Here's what you've been missing:</p>\n      \n      <div style=\"background: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0;\">\n        <h2>🚀 New Features Just for You</h2>\n        <ul>\n          <li>AI-powered property recommendations</li>\n          <li>Virtual reality property tours</li>\n          <li>Instant mortgage pre-approval</li>\n          <li>Market trend predictions</li>\n        </ul>\n      </div>\n      \n      <div style=\"background: #d4edda; padding: 20px; border-radius: 8px; margin: 20px 0;\">\n        <h2>💰 Special Comeback Offer</h2>\n        <p>Purchase a property through us in the next 30 days and receive <strong>€500 cashback</strong> at closing!</p>\n        <a href=\"https://your-website.com/comeback-offer?user=${user.id}\" style=\"background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;\">Claim Your €500 Cashback</a>\n      </div>\n    `;\n    break;\n    \n  case 'long_term':\n    subject = `${user.first_name}, major updates + VIP treatment await! 👑`;\n    incentive = 'VIP service with dedicated agent + €1000 closing credit';\n    emailContent = `\n      <h1>Welcome Back, VIP Member ${user.first_name}! 👑</h1>\n      <p>Wow, it's been quite a while! The real estate market has evolved significantly, and so have we. Let us show you what you've been missing:</p>\n      \n      <div style=\"background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin: 20px 0;\">\n        <h2>🏆 VIP Welcome Back Package</h2>\n        <ul>\n          <li>Dedicated personal agent</li>\n          <li>Priority access to new listings</li>\n          <li>Free market analysis report</li>\n          <li>Complimentary legal consultation</li>\n          <li><strong>€1,000 closing credit</strong></li>\n        </ul>\n        <a href=\"https://your-website.com/vip-package?user=${user.id}\" style=\"background: white; color: #667eea; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;\">Activate VIP Status</a>\n      </div>\n    `;\n    break;\n}\n\n// Add common content\nemailContent += `\n  <div style=\"background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;\">\n    <h2>🏠 What's New in Real Estate</h2>\n    <ul>\n      <li>Market prices have ${Math.random() > 0.5 ? 'increased' : 'stabilized'} by 3.2% this quarter</li>\n      <li>New government incentives for first-time buyers</li>\n      <li>Record-low interest rates for qualified buyers</li>\n      <li>Emerging neighborhoods with high growth potential</li>\n    </ul>\n  </div>\n  \n  <div style=\"text-align: center; margin: 30px 0;\">\n    <h3>Ready to Find Your Perfect Property?</h3>\n    <a href=\"https://your-website.com/search?user=${user.id}\" style=\"background: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-size: 18px; margin: 10px;\">Start Searching</a>\n    <a href=\"https://your-website.com/consultation?user=${user.id}\" style=\"background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-size: 18px; margin: 10px;\">Book Consultation</a>\n  </div>\n  \n  <hr style=\"margin: 30px 0;\">\n  \n  <p>Questions? Our team is here to help! Reply to this email or call us at +39 123 456 7890</p>\n  \n  <p style=\"font-size: 12px; color: #666;\">\n    Missing our emails? <a href=\"https://your-website.com/preferences?email=${user.email}\">Update your preferences</a> or \n    <a href=\"https://your-website.com/unsubscribe?email=${user.email}\">unsubscribe</a>\n  </p>\n`;\n\nreturn [{\n  json: {\n    user_id: user.id,\n    email: user.email,\n    first_name: user.first_name,\n    email_subject: subject,\n    email_content: emailContent,\n    inactivity_category: user.inactivity_category,\n    incentive: incentive\n  }\n}];"
      },
      "name": "Generate Re-engagement Email",
      "type": "n8n-nodes-base.function",
      "typeVersion": 1,
      "position": [1120, 300]
    },
    {
      "parameters": {
        "fromEmail": "comeback@intelligentb2b.com",\n        "toEmail": "={{ $json.email }}",\n        "subject": "={{ $json.email_subject }}",\n        "emailFormat": "html",\n        "message": "={{ $json.email_content }}",\n        "options": {}\n      },\n      "name": "Send Re-engagement Email",\n      "type": "n8n-nodes-base.emailSend",\n      "typeVersion": 1,\n      "position": [1340, 300]\n    }\n  ],\n  "connections": {\n    "Weekly Monday Check": {\n      "main": [\n        [\n          {\n            "node": "Get Recent Interactions",\n            "type": "main",\n            "index": 0\n          }\n        ]\n      ]\n    },\n    "Get Recent Interactions": {\n      "main": [\n        [\n          {\n            "node": "Get All Users",\n            "type": "main",\n            "index": 0\n          }\n        ]\n      ]\n    },\n    "Get All Users": {\n      "main": [\n        [\n          {\n            "node": "Identify Inactive Users",\n            "type": "main",\n            "index": 0\n          }\n        ]\n      ]\n    },\n    "Identify Inactive Users": {\n      "main": [\n        [\n          {\n            "node": "Generate Re-engagement Email",\n            "type": "main",\n            "index": 0\n          }\n        ]\n      ]\n    },\n    "Generate Re-engagement Email": {\n      "main": [\n        [\n          {\n            "node": "Send Re-engagement Email",\n            "type": "main",\n            "index": 0\n          }\n        ]\n      ]\n    }\n  }\n}\n```\n\n## Part 3: Email Template System\n\n### 3.1 Responsive Email Templates\n\nCreate reusable email templates for consistent branding:\n\n```html\n<!-- Base Email Template -->\n<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>{{email_title}}</title>\n    <style>\n        /* Reset styles */\n        * {\n            margin: 0;\n            padding: 0;\n            box-sizing: border-box;\n        }\n        \n        body {\n            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;\n            line-height: 1.6;\n            color: #333;\n            background-color: #f4f4f4;\n        }\n        \n        .email-container {\n            max-width: 600px;\n            margin: 0 auto;\n            background-color: #ffffff;\n            box-shadow: 0 0 10px rgba(0,0,0,0.1);\n        }\n        \n        .header {\n            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);\n            color: white;\n            padding: 20px;\n            text-align: center;\n        }\n        \n        .header h1 {\n            font-size: 24px;\n            margin-bottom: 10px;\n        }\n        \n        .content {\n            padding: 30px;\n        }\n        \n        .property-card {\n            border: 1px solid #ddd;\n            border-radius: 8px;\n            margin: 20px 0;\n            overflow: hidden;\n            box-shadow: 0 2px 4px rgba(0,0,0,0.1);\n        }\n        \n        .property-image {\n            width: 100%;\n            height: 200px;\n            object-fit: cover;\n        }\n        \n        .property-details {\n            padding: 15px;\n        }\n        \n        .property-price {\n            font-size: 24px;\n            font-weight: bold;\n            color: #007bff;\n            margin-bottom: 10px;\n        }\n        \n        .property-location {\n            color: #666;\n            margin-bottom: 10px;\n        }\n        \n        .property-features {\n            display: flex;\n            justify-content: space-between;\n            margin: 10px 0;\n            font-size: 14px;\n        }\n        \n        .btn {\n            display: inline-block;\n            padding: 12px 24px;\n            background-color: #007bff;\n            color: white;\n            text-decoration: none;\n            border-radius: 5px;\n            font-weight: bold;\n            margin: 10px 5px;\n        }\n        \n        .btn-secondary {\n            background-color: #28a745;\n        }\n        \n        .btn-warning {\n            background-color: #ffc107;\n            color: #333;\n        }\n        \n        .highlight-box {\n            background-color: #e7f3ff;\n            border-left: 4px solid #007bff;\n            padding: 15px;\n            margin: 20px 0;\n        }\n        \n        .warning-box {\n            background-color: #fff3cd;\n            border-left: 4px solid #ffc107;\n            padding: 15px;\n            margin: 20px 0;\n        }\n        \n        .success-box {\n            background-color: #d4edda;\n            border-left: 4px solid #28a745;\n            padding: 15px;\n            margin: 20px 0;\n        }\n        \n        .footer {\n            background-color: #f8f9fa;\n            padding: 20px;\n            text-align: center;\n            font-size: 12px;\n            color: #666;\n        }\n        \n        .social-links {\n            margin: 15px 0;\n        }\n        \n        .social-links a {\n            display: inline-block;\n            margin: 0 10px;\n            color: #007bff;\n            text-decoration: none;\n        }\n        \n        /* Mobile responsiveness */\n        @media only screen and (max-width: 600px) {\n            .email-container {\n                width: 100% !important;\n            }\n            \n            .content {\n                padding: 20px !important;\n            }\n            \n            .property-features {\n                flex-direction: column;\n            }\n            \n            .btn {\n                display: block;\n                text-align: center;\n                margin: 10px 0;\n            }\n        }\n    </style>\n</head>\n<body>\n    <div class="email-container">\n        <!-- Header -->\n        <div class="header">\n            <h1>{{company_name}}</h1>\n            <p>{{header_subtitle}}</p>\n        </div>\n        \n        <!-- Main Content -->\n        <div class="content">\n            {{email_content}}\n        </div>\n        \n        <!-- Footer -->\n        <div class="footer">\n            <div class="social-links">\n                <a href="{{facebook_url}}">Facebook</a>\n                <a href="{{instagram_url}}">Instagram</a>\n                <a href="{{linkedin_url}}">LinkedIn</a>\n            </div>\n            \n            <p>{{company_name}} | {{company_address}}</p>\n            <p>Phone: {{company_phone}} | Email: {{company_email}}</p>\n            \n            <p style="margin-top: 15px;">\n                <a href="{{unsubscribe_url}}">Unsubscribe</a> | \n                <a href="{{preferences_url}}">Update Preferences</a> | \n                <a href="{{privacy_url}}">Privacy Policy</a>\n            </p>\n        </div>\n    </div>\n</body>\n</html>\n```\n\n### 3.2 Property Listing Template Component\n\n```html\n<!-- Property Listing Component -->\n<div class="property-card">\n    <img src="{{property_image_url}}" alt="{{property_title}}" class="property-image">\n    <div class="property-details">\n        <div class="property-price">€{{property_price}}</div>\n        <div class="property-location">📍 {{property_location}}</div>\n        <h3>{{property_title}}</h3>\n        \n        <div class="property-features">\n            <span>🛏️ {{bedrooms}} bed</span>\n            <span>🚿 {{bathrooms}} bath</span>\n            <span>📐 {{square_meters}}m²</span>\n        </div>\n        \n        <p>{{property_description}}</p>\n        \n        <div style="margin-top: 15px;">\n            <a href="{{property_url}}" class="btn">View Details</a>\n            <a href="{{schedule_viewing_url}}" class="btn btn-secondary">Schedule Viewing</a>\n        </div>\n    </div>\n</div>\n```\n\n## Part 4: Email Analytics and Optimization\n\n### 4.1 Email Performance Tracking\n\nCreate an analytics workflow to track email performance:\n\n```json\n{\n  "name": "Email Analytics Tracking",\n  "nodes": [\n    {\n      "parameters": {\n        "rule": {\n          "interval": [\n            {\n              "field": "cronExpression",\n              "expression": "0 0 9 * * *"\n            }\n          ]\n        }\n      },\n      "name": "Daily Analytics Check",\n      "type": "n8n-nodes-base.cron",\n      "typeVersion": 1,\n      "position": [240, 300]\n    },\n    {\n      "parameters": {\n        "authentication": "headerAuth",\n        "resource": "row",\n        "operation": "getAll",\n        "tableId": "EMAIL_CAMPAIGNS_TABLE_ID",\n        "filters": {\n          "filter": [\n            {\n              "field": "sent_date",\n              "type": "date_after",\n              "value": "{{ new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString().split('T')[0] }}"\n            }\n          ]\n        }\n      },\n      "name": "Get Yesterday's Campaigns",\n      "type": "n8n-nodes-base.baserow",\n      "typeVersion": 1,\n      "position": [460, 300]\n    },\n    {\n      "parameters": {\n        "functionCode": "// Calculate email performance metrics\nconst campaigns = $input.all().map(item => item.json);\n\n// Group by campaign type\nconst campaignStats = {};\n\ncampaigns.forEach(campaign => {\n  const type = campaign.campaign_type;\n  \n  if (!campaignStats[type]) {\n    campaignStats[type] = {\n      campaign_type: type,\n      total_sent: 0,\n      total_delivered: 0,\n      total_opened: 0,\n      total_clicked: 0,\n      open_rate: 0,\n      click_rate: 0,\n      delivery_rate: 0\n    };\n  }\n  \n  campaignStats[type].total_sent += 1;\n  campaignStats[type].total_delivered += campaign.emails_delivered || 1;\n  campaignStats[type].total_opened += campaign.emails_opened || 0;\n  campaignStats[type].total_clicked += campaign.emails_clicked || 0;\n});\n\n// Calculate rates\nObject.keys(campaignStats).forEach(type => {\n  const stats = campaignStats[type];\n  stats.delivery_rate = (stats.total_delivered / stats.total_sent * 100).toFixed(2);\n  stats.open_rate = (stats.total_opened / stats.total_delivered * 100).toFixed(2);\n  stats.click_rate = (stats.total_clicked / stats.total_opened * 100).toFixed(2);\n});\n\nreturn Object.values(campaignStats).map(stats => ({ json: stats }));"
      },\n      "name": "Calculate Performance Metrics",\n      "type": "n8n-nodes-base.function",\n      "typeVersion": 1,\n      "position": [680, 300]\n    }\n  ]\n}\n```\n\n### 4.2 A/B Testing Framework\n\nImplement A/B testing for email optimization:\n\n```javascript\n// A/B Testing Function for Email Campaigns\nfunction createABTestCampaign(campaignData) {\n  const variants = [\n    {\n      name: 'Variant A',\n      subject_line: campaignData.subject_a,\n      email_content: campaignData.content_a,\n      send_percentage: 50\n    },\n    {\n      name: 'Variant B',\n      subject_line: campaignData.subject_b,\n      email_content: campaignData.content_b,\n      send_percentage: 50\n    }\n  ];\n  \n  // Split audience randomly\n  const audience = campaignData.recipients;\n  const shuffled = audience.sort(() => 0.5 - Math.random());\n  \n  const splitPoint = Math.floor(shuffled.length / 2);\n  \n  return {\n    variant_a: {\n      ...variants[0],\n      recipients: shuffled.slice(0, splitPoint)\n    },\n    variant_b: {\n      ...variants[1],\n      recipients: shuffled.slice(splitPoint)\n    }\n  };\n}\n```\n\n## Part 5: Integration and Deployment\n\n### 5.1 Email Service Configuration\n\nConfigure email service providers in n8n:\n\n**SMTP Configuration:**\n```json\n{\n  "smtp_host": "smtp.gmail.com",\n  "smtp_port": 587,\n  "smtp_secure": false,\n  "smtp_auth": {\n    "user": "your-email@gmail.com",\n    "pass": "your-app-password"\n  }\n}\n```\n\n**SendGrid Configuration:**\n```json\n{\n  "api_key": "your-sendgrid-api-key",\n  "from_email": "noreply@intelligentb2b.com",\n  "from_name": "Real Estate Team"\n}\n```\n\n### 5.2 GDPR Compliance\n\nImplement GDPR-compliant email practices:\n\n```javascript\n// GDPR Compliance Functions\nfunction checkMarketingConsent(userId) {\n  // Check user's marketing consent status\n  return baserowAPI.getUser(userId).marketing_consent;\n}\n\nfunction handleUnsubscribe(email, campaignType = 'all') {\n  // Update user preferences\n  return baserowAPI.updateUser({\n    email: email,\n    marketing_consent: false,\n    unsubscribe_date: new Date().toISOString(),\n    unsubscribe_reason: campaignType\n  });\n}\n\nfunction generateUnsubscribeLink(email, campaignId) {\n  const token = generateSecureToken(email, campaignId);\n  return `https://your-website.com/unsubscribe?token=${token}`;\n}\n```\n\n### 5.3 Performance Monitoring\n\nSet up monitoring for email deliverability:\n\n```javascript\n// Email Performance Monitoring\nconst emailMetrics = {\n  deliveryRate: {\n    target: 95,\n    current: 0,\n    status: 'unknown'\n  },\n  openRate: {\n    target: 25,\n    current: 0,\n    status: 'unknown'\n  },\n  clickRate: {\n    target: 3,\n    current: 0,\n    status: 'unknown'\n  },\n  unsubscribeRate: {\n    target: 2,\n    current: 0,\n    status: 'unknown'\n  }\n};\n\nfunction checkEmailHealth() {\n  // Calculate current metrics\n  // Compare against targets\n  // Send alerts if thresholds exceeded\n  \n  Object.keys(emailMetrics).forEach(metric => {\n    const data = emailMetrics[metric];\n    if (data.current < data.target * 0.8) {\n      sendAlert(`Email ${metric} below threshold: ${data.current}%`);\n    }\n  });\n}\n```\n\nThis comprehensive email marketing automation system provides personalized, behavior-driven email campaigns that nurture leads, engage prospects, and drive conversions while maintaining GDPR compliance and optimizing performance through analytics and A/B testing.


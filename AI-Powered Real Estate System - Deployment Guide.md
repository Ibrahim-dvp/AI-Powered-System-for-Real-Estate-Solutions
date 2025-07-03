# AI-Powered Real Estate System - Deployment Guide

## Quick Start Deployment

### Prerequisites Checklist
- [ ] Access to Baserow instance at dayta.intelligentb2b.com
- [ ] Access to Open WebUI instance at ai.intelligentb2b.com  
- [ ] Docker and Docker Compose installed
- [ ] Python 3.11+ installed
- [ ] Node.js 20+ installed
- [ ] Git repository access

### 1. Environment Setup

```bash
# Clone the system components
git clone <repository-url> ai-real-estate-system
cd ai-real-estate-system

# Create environment configuration
cp .env.example .env
# Edit .env with your specific configuration
```

### 2. Baserow Configuration

#### Required Environment Variables
```bash
BASEROW_API_URL=https://dayta.intelligentb2b.com/api
BASEROW_TOKEN=your_baserow_token_here
BASEROW_PROPERTIES_TABLE_ID=your_properties_table_id
BASEROW_USERS_TABLE_ID=your_users_table_id
BASEROW_LEADS_TABLE_ID=your_leads_table_id
BASEROW_INTERACTIONS_TABLE_ID=your_interactions_table_id
BASEROW_DEALS_TABLE_ID=your_deals_table_id
BASEROW_MARKET_DATA_TABLE_ID=your_market_data_table_id
BASEROW_EMAIL_CAMPAIGNS_TABLE_ID=your_email_campaigns_table_id
BASEROW_ANALYTICS_TABLE_ID=your_analytics_table_id
```

#### Table Creation Script
```bash
# Run the Baserow setup script
python scripts/setup_baserow_tables.py
```

### 3. Service Deployment

#### Deploy All Services with Docker Compose
```bash
# Build and start all services
docker-compose up -d

# Verify all services are running
docker-compose ps
```

#### Individual Service Deployment
```bash
# Lead Scoring Service (Port 5001)
cd lead-scoring-service
source venv/bin/activate
python src/main.py

# Property Search Service (Port 5002)  
cd property-search-service
source venv/bin/activate
python src/main.py

# Property Valuation Service (Port 5003)
cd property-valuation-service
source venv/bin/activate
python src/main.py

# Email Marketing Service (Port 5004)
cd email-marketing-service
source venv/bin/activate
python src/main.py

# Dashboard Analytics Service (Port 5005)
cd dashboard-analytics-service
source venv/bin/activate
python src/main.py

# Data Collection Service (Port 5006)
cd data-collection-service
source venv/bin/activate
python src/main.py
```

### 4. Open WebUI Configuration

#### Model Setup
1. Access your Open WebUI at ai.intelligentb2b.com
2. Navigate to Admin Panel > Models
3. Create new model with these settings:
   - Name: `real-estate-assistant`
   - Base Model: `gpt-4o-mini`
   - System Prompt: Use the provided real estate assistant prompt
   - Functions: Import the provided function definitions

#### Function Definitions Import
```json
{
  "property_search": {
    "name": "property_search",
    "description": "Search for properties based on user criteria",
    "parameters": {
      "type": "object",
      "properties": {
        "location": {"type": "string"},
        "property_type": {"type": "string"},
        "min_price": {"type": "number"},
        "max_price": {"type": "number"},
        "min_size": {"type": "number"},
        "max_size": {"type": "number"},
        "rooms": {"type": "number"}
      }
    }
  },
  "schedule_appointment": {
    "name": "schedule_appointment",
    "description": "Schedule a property viewing appointment",
    "parameters": {
      "type": "object",
      "properties": {
        "property_id": {"type": "string"},
        "user_name": {"type": "string"},
        "user_email": {"type": "string"},
        "user_phone": {"type": "string"},
        "preferred_date": {"type": "string"},
        "preferred_time": {"type": "string"}
      }
    }
  }
}
```

### 5. n8n Workflow Setup

#### Import Workflows
1. Access your n8n instance
2. Import the provided workflow JSON files:
   - `lead-scoring-workflow.json`
   - `email-marketing-workflow.json`
   - `data-collection-workflow.json`
   - `property-alerts-workflow.json`

#### Configure Webhook URLs
Update webhook URLs in workflows to point to your deployed services:
```
Lead Scoring: http://your-domain:5001/api/leads/score
Email Marketing: http://your-domain:5004/api/campaigns/trigger
Data Collection: http://your-domain:5006/api/collect/all
```

### 6. External API Configuration

#### Immobiliare.it API
```bash
IMMOBILIARE_API_KEY=your_api_key_here
IMMOBILIARE_BASE_URL=https://api.immobiliare.it
```

#### Idealista.it API
```bash
IDEALISTA_CLIENT_ID=your_client_id_here
IDEALISTA_CLIENT_SECRET=your_client_secret_here
IDEALISTA_BASE_URL=https://api.idealista.com
```

#### OpenAI API
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 7. Testing Deployment

#### Health Check Script
```bash
#!/bin/bash
echo "Checking service health..."

services=(
  "http://localhost:5001/health"
  "http://localhost:5002/health" 
  "http://localhost:5003/health"
  "http://localhost:5004/health"
  "http://localhost:5005/health"
  "http://localhost:5006/health"
)

for service in "${services[@]}"; do
  if curl -f "$service" > /dev/null 2>&1; then
    echo "✓ $service is healthy"
  else
    echo "✗ $service is not responding"
  fi
done
```

#### Integration Test
```bash
# Test lead scoring
curl -X POST http://localhost:5001/api/leads/score \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user", "interactions": []}'

# Test property search
curl -X POST http://localhost:5002/api/properties/search \
  -H "Content-Type: application/json" \
  -d '{"location": "Rome", "max_price": 500000}'

# Test property valuation
curl -X POST http://localhost:5003/api/valuations/estimate \
  -H "Content-Type: application/json" \
  -d '{"address": "Via del Corso 1, Rome", "size": 100}'
```

## Production Deployment

### Docker Compose Production Configuration

```yaml
version: '3.8'
services:
  lead-scoring:
    build: ./lead-scoring-service
    ports:
      - "5001:5000"
    environment:
      - FLASK_ENV=production
      - BASEROW_API_URL=${BASEROW_API_URL}
      - BASEROW_TOKEN=${BASEROW_TOKEN}
    restart: unless-stopped
    
  property-search:
    build: ./property-search-service
    ports:
      - "5002:5000"
    environment:
      - FLASK_ENV=production
      - BASEROW_API_URL=${BASEROW_API_URL}
      - BASEROW_TOKEN=${BASEROW_TOKEN}
    restart: unless-stopped
    
  property-valuation:
    build: ./property-valuation-service
    ports:
      - "5003:5000"
    environment:
      - FLASK_ENV=production
      - BASEROW_API_URL=${BASEROW_API_URL}
      - BASEROW_TOKEN=${BASEROW_TOKEN}
    restart: unless-stopped
    
  email-marketing:
    build: ./email-marketing-service
    ports:
      - "5004:5000"
    environment:
      - FLASK_ENV=production
      - BASEROW_API_URL=${BASEROW_API_URL}
      - BASEROW_TOKEN=${BASEROW_TOKEN}
    restart: unless-stopped
    
  dashboard-analytics:
    build: ./dashboard-analytics-service
    ports:
      - "5005:5000"
    environment:
      - FLASK_ENV=production
      - BASEROW_API_URL=${BASEROW_API_URL}
      - BASEROW_TOKEN=${BASEROW_TOKEN}
    restart: unless-stopped
    
  data-collection:
    build: ./data-collection-service
    ports:
      - "5006:5000"
    environment:
      - FLASK_ENV=production
      - BASEROW_API_URL=${BASEROW_API_URL}
      - BASEROW_TOKEN=${BASEROW_TOKEN}
      - IMMOBILIARE_API_KEY=${IMMOBILIARE_API_KEY}
      - IDEALISTA_CLIENT_ID=${IDEALISTA_CLIENT_ID}
      - IDEALISTA_CLIENT_SECRET=${IDEALISTA_CLIENT_SECRET}
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - lead-scoring
      - property-search
      - property-valuation
      - email-marketing
      - dashboard-analytics
      - data-collection
    restart: unless-stopped
```

### Nginx Configuration

```nginx
upstream lead_scoring {
    server lead-scoring:5000;
}

upstream property_search {
    server property-search:5000;
}

upstream property_valuation {
    server property-valuation:5000;
}

upstream email_marketing {
    server email-marketing:5000;
}

upstream dashboard_analytics {
    server dashboard-analytics:5000;
}

upstream data_collection {
    server data-collection:5000;
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    location /api/leads/ {
        proxy_pass http://lead_scoring/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/properties/ {
        proxy_pass http://property_search/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/valuations/ {
        proxy_pass http://property_valuation/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/campaigns/ {
        proxy_pass http://email_marketing/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/dashboard/ {
        proxy_pass http://dashboard_analytics/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/collect/ {
        proxy_pass http://data_collection/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /dashboard/ {
        proxy_pass http://dashboard_analytics/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Monitoring Setup

#### Prometheus Configuration
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'real-estate-services'
    static_configs:
      - targets: 
        - 'lead-scoring:5000'
        - 'property-search:5000'
        - 'property-valuation:5000'
        - 'email-marketing:5000'
        - 'dashboard-analytics:5000'
        - 'data-collection:5000'
```

#### Grafana Dashboard Import
Import the provided Grafana dashboard JSON for comprehensive system monitoring.

### Security Configuration

#### SSL/TLS Setup
```bash
# Generate SSL certificates with Let's Encrypt
certbot certonly --webroot -w /var/www/html -d your-domain.com
```

#### Firewall Configuration
```bash
# Allow only necessary ports
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw enable
```

#### Environment Security
```bash
# Secure environment variables
chmod 600 .env
chown root:root .env
```

## Troubleshooting

### Common Issues

#### Service Not Starting
```bash
# Check logs
docker-compose logs service-name

# Check port conflicts
netstat -tulpn | grep :5001
```

#### Database Connection Issues
```bash
# Test Baserow connection
curl -H "Authorization: Token your_token" \
  https://daytaa.intelligentb2b.com/api/database/tables/
```

#### API Integration Issues
```bash
# Test external APIs
curl -H "Authorization: Bearer your_api_key" \
  https://api.immobiliare.it/test
```

### Performance Issues

#### High Memory Usage
```bash
# Monitor memory usage
docker stats

# Optimize Python memory
export PYTHONOPTIMIZE=1
```

#### Slow Database Queries
```bash
# Check Baserow performance
# Add indexes to frequently queried fields
# Optimize query patterns
```

### Maintenance Tasks

#### Daily Tasks
- Check service health
- Monitor error logs  
- Verify backup completion

#### Weekly Tasks
- Update dependencies
- Review performance metrics
- Clean up old logs

#### Monthly Tasks
- Security updates
- Capacity planning review
- Business metrics analysis

This deployment guide provides comprehensive instructions for setting up and maintaining the AI-powered real estate system in both development and production environments.


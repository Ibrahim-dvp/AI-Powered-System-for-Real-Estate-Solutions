# AI-Powered Real Estate System: Database Schema Design

**Author:** Manus AI  
**Date:** January 7, 2025  
**Version:** 1.0

## Overview

This document provides comprehensive database schema design for the AI-powered real estate system using Baserow as the primary database platform. The schema is designed to support all seven core modules while maintaining data integrity, performance, and scalability. The design follows relational database principles while leveraging Baserow's flexibility for rapid development and easy maintenance.

## Core Entity Models

### Users Table

The Users table serves as the central repository for all user information, supporting both registered users and anonymous visitors with mechanisms for profile merging and comprehensive behavioral tracking.

| Field Name | Type | Required | Description | Constraints |
|------------|------|----------|-------------|-------------|
| user_id | Auto Number | Yes | Primary key, unique identifier | Auto-increment |
| email | Email | No | User email address | Unique when not null |
| phone | Phone Number | No | User phone number | Format validation |
| first_name | Text | No | User first name | Max 50 characters |
| last_name | Text | Text | User last name | Max 50 characters |
| date_of_birth | Date | No | User date of birth | Privacy protected |
| gender | Single Select | No | User gender | Options: Male, Female, Other, Prefer not to say |
| marital_status | Single Select | No | Marital status | Options: Single, Married, Divorced, Widowed |
| household_size | Number | No | Number of people in household | Min 1, Max 20 |
| annual_income | Number | No | Annual household income | Privacy protected |
| employment_status | Single Select | No | Current employment status | Options: Employed, Self-employed, Unemployed, Retired, Student |
| preferred_language | Single Select | No | Preferred communication language | Default: Italian |
| communication_preferences | Multiple Select | No | Preferred communication channels | Options: Email, Phone, SMS, WhatsApp |
| registration_date | Date | Yes | Account creation date | Auto-populated |
| last_login | Date and Time | No | Last login timestamp | Auto-updated |
| user_status | Single Select | Yes | Account status | Options: Active, Inactive, Suspended, Deleted |
| lead_score | Number | No | Current lead score | Range 0-100, auto-calculated |
| lead_grade | Single Select | No | Lead quality grade | Options: A, B, C, D, Unqualified |
| source | Single Select | No | How user found the service | Options: Website, Social Media, Referral, Advertisement |
| utm_source | Text | No | Marketing campaign source | Max 100 characters |
| utm_medium | Text | No | Marketing campaign medium | Max 100 characters |
| utm_campaign | Text | No | Marketing campaign name | Max 100 characters |
| privacy_consent | Checkbox | Yes | GDPR consent status | Required for EU users |
| marketing_consent | Checkbox | No | Marketing communication consent | Default false |
| created_at | Date and Time | Yes | Record creation timestamp | Auto-populated |
| updated_at | Date and Time | Yes | Last update timestamp | Auto-updated |

### Properties Table

The Properties table maintains comprehensive information about real estate listings including physical characteristics, location data, pricing history, and market metrics.

| Field Name | Type | Required | Description | Constraints |
|------------|------|----------|-------------|-------------|
| property_id | Auto Number | Yes | Primary key, unique identifier | Auto-increment |
| external_id | Text | No | External portal property ID | Max 100 characters |
| property_type | Single Select | Yes | Type of property | Options: Apartment, House, Villa, Commercial, Land |
| listing_type | Single Select | Yes | Listing type | Options: Sale, Rent, Both |
| title | Text | Yes | Property listing title | Max 200 characters |
| description | Long Text | No | Detailed property description | Rich text supported |
| address | Text | Yes | Full property address | Max 300 characters |
| city | Text | Yes | City name | Max 100 characters |
| region | Text | Yes | Region/Province | Max 100 characters |
| postal_code | Text | Yes | Postal code | Format validation |
| country | Text | Yes | Country | Default: Italy |
| latitude | Number | No | GPS latitude coordinate | Decimal degrees |
| longitude | Number | No | GPS longitude coordinate | Decimal degrees |
| neighborhood | Text | No | Neighborhood name | Max 100 characters |
| square_meters | Number | No | Total floor area in square meters | Min 1 |
| lot_size | Number | No | Lot size in square meters | Min 1 |
| bedrooms | Number | No | Number of bedrooms | Min 0, Max 20 |
| bathrooms | Number | No | Number of bathrooms | Min 0, Max 20 |
| floors | Number | No | Number of floors | Min 1, Max 50 |
| floor_number | Number | No | Floor number if apartment | Min -5, Max 50 |
| building_year | Number | No | Year of construction | Min 1800, Max current year |
| renovation_year | Number | No | Year of last major renovation | Min building_year |
| condition | Single Select | No | Property condition | Options: Excellent, Good, Fair, Poor, Needs Renovation |
| heating_type | Single Select | No | Heating system type | Options: Central, Autonomous, Heat Pump, None |
| energy_class | Single Select | No | Energy efficiency class | Options: A4, A3, A2, A1, B, C, D, E, F, G |
| parking_spaces | Number | No | Number of parking spaces | Min 0, Max 20 |
| garage | Checkbox | No | Has garage | Default false |
| garden | Checkbox | No | Has garden | Default false |
| balcony | Checkbox | No | Has balcony | Default false |
| terrace | Checkbox | No | Has terrace | Default false |
| elevator | Checkbox | No | Has elevator | Default false |
| furnished | Single Select | No | Furnishing status | Options: Furnished, Semi-furnished, Unfurnished |
| pet_friendly | Checkbox | No | Pets allowed | Default false |
| current_price | Number | Yes | Current listing price in EUR | Min 1 |
| original_price | Number | No | Original listing price | Min 1 |
| price_per_sqm | Number | No | Price per square meter | Auto-calculated |
| monthly_expenses | Number | No | Monthly expenses (HOA, etc.) | Min 0 |
| property_taxes | Number | No | Annual property taxes | Min 0 |
| listing_date | Date | Yes | Date property was listed | Auto-populated |
| last_price_change | Date | No | Date of last price change | Auto-updated |
| status | Single Select | Yes | Property status | Options: Active, Pending, Sold, Rented, Withdrawn |
| days_on_market | Number | No | Days since listing | Auto-calculated |
| view_count | Number | No | Number of times viewed | Auto-updated |
| inquiry_count | Number | No | Number of inquiries received | Auto-updated |
| agent_id | Link to Users | No | Assigned agent | Link to Users table |
| owner_id | Link to Users | No | Property owner | Link to Users table |
| source_portal | Single Select | No | Source real estate portal | Options: Internal, Immobiliare.it, Idealista.it, etc. |
| virtual_tour_url | URL | No | Virtual tour link | URL validation |
| video_url | URL | No | Property video link | URL validation |
| created_at | Date and Time | Yes | Record creation timestamp | Auto-populated |
| updated_at | Date and Time | Yes | Last update timestamp | Auto-updated |

### Property_Images Table

The Property_Images table manages all images associated with properties, supporting multiple images per property with ordering and categorization.

| Field Name | Type | Required | Description | Constraints |
|------------|------|----------|-------------|-------------|
| image_id | Auto Number | Yes | Primary key, unique identifier | Auto-increment |
| property_id | Link to Properties | Yes | Associated property | Link to Properties table |
| image_url | URL | Yes | Image URL or file path | URL validation |
| image_type | Single Select | Yes | Type of image | Options: Exterior, Interior, Floor Plan, Aerial, Other |
| room_type | Single Select | No | Room type for interior images | Options: Living Room, Kitchen, Bedroom, Bathroom, Other |
| display_order | Number | Yes | Display order | Min 1 |
| is_primary | Checkbox | No | Primary listing image | Default false |
| alt_text | Text | No | Image alt text for accessibility | Max 200 characters |
| caption | Text | No | Image caption | Max 300 characters |
| created_at | Date and Time | Yes | Record creation timestamp | Auto-populated |

### Leads Table

The Leads table tracks potential customers through the sales funnel, maintaining scoring information, interaction history, and conversion tracking.

| Field Name | Type | Required | Description | Constraints |
|------------|------|----------|-------------|-------------|
| lead_id | Auto Number | Yes | Primary key, unique identifier | Auto-increment |
| user_id | Link to Users | No | Associated user account | Link to Users table |
| email | Email | No | Lead email address | Required if no user_id |
| phone | Phone Number | No | Lead phone number | Format validation |
| first_name | Text | No | Lead first name | Max 50 characters |
| last_name | Text | No | Lead last name | Max 50 characters |
| lead_source | Single Select | Yes | How lead was generated | Options: Website, Social Media, Referral, Advertisement, Cold Call |
| lead_status | Single Select | Yes | Current lead status | Options: New, Contacted, Qualified, Proposal, Negotiation, Closed Won, Closed Lost |
| lead_score | Number | No | Current lead score | Range 0-100, auto-calculated |
| lead_grade | Single Select | No | Lead quality grade | Options: Hot, Warm, Cold, Unqualified |
| budget_min | Number | No | Minimum budget | Min 0 |
| budget_max | Number | No | Maximum budget | Min budget_min |
| property_type_interest | Multiple Select | No | Interested property types | Options: Apartment, House, Villa, Commercial, Land |
| location_preferences | Long Text | No | Preferred locations | JSON format |
| timeline | Single Select | No | Purchase/rental timeline | Options: Immediate, 1-3 months, 3-6 months, 6-12 months, 1+ years |
| financing_needed | Checkbox | No | Requires financing | Default false |
| first_time_buyer | Checkbox | No | First-time buyer | Default false |
| investment_purpose | Checkbox | No | Investment property | Default false |
| assigned_agent_id | Link to Users | No | Assigned sales agent | Link to Users table |
| last_contact_date | Date | No | Last contact attempt | Auto-updated |
| next_follow_up | Date | No | Scheduled follow-up date | Future date |
| conversion_date | Date | No | Date lead converted to customer | Auto-populated |
| conversion_value | Number | No | Value of conversion | Min 0 |
| notes | Long Text | No | Agent notes about lead | Rich text supported |
| created_at | Date and Time | Yes | Record creation timestamp | Auto-populated |
| updated_at | Date and Time | Yes | Last update timestamp | Auto-updated |

### User_Interactions Table

The User_Interactions table captures comprehensive user behavior data across all digital touchpoints for behavioral analysis and lead scoring.

| Field Name | Type | Required | Description | Constraints |
|------------|------|----------|-------------|-------------|
| interaction_id | Auto Number | Yes | Primary key, unique identifier | Auto-increment |
| user_id | Link to Users | No | Associated user | Link to Users table |
| session_id | Text | Yes | Browser session identifier | Max 100 characters |
| interaction_type | Single Select | Yes | Type of interaction | Options: Page View, Property View, Search, Click, Download, Form Submit |
| page_url | URL | No | Page URL | URL validation |
| property_id | Link to Properties | No | Associated property | Link to Properties table |
| search_query | Text | No | Search terms used | Max 500 characters |
| search_filters | Long Text | No | Applied search filters | JSON format |
| time_spent | Number | No | Time spent in seconds | Min 0 |
| scroll_depth | Number | No | Page scroll percentage | Range 0-100 |
| click_coordinates | Text | No | Click coordinates | JSON format |
| device_type | Single Select | No | Device type | Options: Desktop, Mobile, Tablet |
| browser | Text | No | Browser name and version | Max 100 characters |
| operating_system | Text | No | Operating system | Max 100 characters |
| ip_address | Text | No | User IP address | Privacy protected |
| referrer_url | URL | No | Referring page URL | URL validation |
| utm_source | Text | No | Campaign source | Max 100 characters |
| utm_medium | Text | No | Campaign medium | Max 100 characters |
| utm_campaign | Text | No | Campaign name | Max 100 characters |
| created_at | Date and Time | Yes | Interaction timestamp | Auto-populated |

### Property_Valuations Table

The Property_Valuations table stores automated valuation results and historical valuation data for trend analysis and accuracy tracking.

| Field Name | Type | Required | Description | Constraints |
|------------|------|----------|-------------|-------------|
| valuation_id | Auto Number | Yes | Primary key, unique identifier | Auto-increment |
| property_id | Link to Properties | Yes | Associated property | Link to Properties table |
| valuation_type | Single Select | Yes | Type of valuation | Options: Automated, Manual, Comparative, Investment |
| estimated_value | Number | Yes | Estimated property value | Min 1 |
| confidence_score | Number | No | Confidence in valuation | Range 0-100 |
| value_per_sqm | Number | No | Value per square meter | Auto-calculated |
| comparable_properties | Long Text | No | Comparable property data | JSON format |
| market_factors | Long Text | No | Market factors considered | JSON format |
| valuation_method | Single Select | Yes | Valuation methodology | Options: Hedonic, Comparative, Income, Cost |
| data_sources | Multiple Select | No | Data sources used | Options: Land Registry, Market Data, Portal Data |
| valuation_date | Date | Yes | Date of valuation | Auto-populated |
| valid_until | Date | No | Valuation expiry date | Future date |
| created_by | Single Select | Yes | Valuation creator | Options: System, Agent, External |
| notes | Long Text | No | Valuation notes | Rich text supported |
| created_at | Date and Time | Yes | Record creation timestamp | Auto-populated |

### Email_Campaigns Table

The Email_Campaigns table manages email marketing campaigns with comprehensive tracking and performance metrics.

| Field Name | Type | Required | Description | Constraints |
|------------|------|----------|-------------|-------------|
| campaign_id | Auto Number | Yes | Primary key, unique identifier | Auto-increment |
| campaign_name | Text | Yes | Campaign name | Max 200 characters |
| campaign_type | Single Select | Yes | Type of campaign | Options: Newsletter, Property Alert, Nurture, Promotional, Transactional |
| subject_line | Text | Yes | Email subject line | Max 200 characters |
| email_content | Long Text | Yes | Email HTML content | Rich text supported |
| target_segment | Single Select | No | Target user segment | Options: All Users, New Leads, Active Buyers, Past Clients |
| segment_criteria | Long Text | No | Segmentation criteria | JSON format |
| sender_name | Text | Yes | Sender name | Max 100 characters |
| sender_email | Email | Yes | Sender email address | Email validation |
| scheduled_date | Date and Time | No | Scheduled send date | Future date |
| sent_date | Date and Time | No | Actual send date | Auto-populated |
| campaign_status | Single Select | Yes | Campaign status | Options: Draft, Scheduled, Sending, Sent, Cancelled |
| total_recipients | Number | No | Total recipients | Auto-calculated |
| emails_sent | Number | No | Emails successfully sent | Auto-updated |
| emails_delivered | Number | No | Emails delivered | Auto-updated |
| emails_opened | Number | No | Emails opened | Auto-updated |
| emails_clicked | Number | No | Emails clicked | Auto-updated |
| emails_bounced | Number | No | Emails bounced | Auto-updated |
| emails_unsubscribed | Number | No | Unsubscribe requests | Auto-updated |
| open_rate | Number | No | Open rate percentage | Auto-calculated |
| click_rate | Number | No | Click rate percentage | Auto-calculated |
| bounce_rate | Number | No | Bounce rate percentage | Auto-calculated |
| unsubscribe_rate | Number | No | Unsubscribe rate percentage | Auto-calculated |
| created_at | Date and Time | Yes | Record creation timestamp | Auto-populated |
| updated_at | Date and Time | Yes | Last update timestamp | Auto-updated |

### Chatbot_Conversations Table

The Chatbot_Conversations table tracks all chatbot interactions across multiple platforms for analysis and improvement.

| Field Name | Type | Required | Description | Constraints |
|------------|------|----------|-------------|-------------|
| conversation_id | Auto Number | Yes | Primary key, unique identifier | Auto-increment |
| user_id | Link to Users | No | Associated user | Link to Users table |
| platform | Single Select | Yes | Communication platform | Options: Website, WhatsApp, Facebook, Instagram, Telegram |
| platform_user_id | Text | No | Platform-specific user ID | Max 100 characters |
| conversation_status | Single Select | Yes | Conversation status | Options: Active, Completed, Abandoned, Escalated |
| lead_qualified | Checkbox | No | Lead qualification result | Default false |
| appointment_scheduled | Checkbox | No | Appointment scheduled | Default false |
| satisfaction_rating | Number | No | User satisfaction rating | Range 1-5 |
| conversation_summary | Long Text | No | AI-generated summary | Auto-populated |
| extracted_preferences | Long Text | No | User preferences extracted | JSON format |
| started_at | Date and Time | Yes | Conversation start time | Auto-populated |
| ended_at | Date and Time | No | Conversation end time | Auto-updated |
| total_messages | Number | No | Total message count | Auto-calculated |
| response_time_avg | Number | No | Average response time in seconds | Auto-calculated |
| created_at | Date and Time | Yes | Record creation timestamp | Auto-populated |

### Chatbot_Messages Table

The Chatbot_Messages table stores individual messages within conversations for detailed analysis and training data.

| Field Name | Type | Required | Description | Constraints |
|------------|------|----------|-------------|-------------|
| message_id | Auto Number | Yes | Primary key, unique identifier | Auto-increment |
| conversation_id | Link to Chatbot_Conversations | Yes | Associated conversation | Link to Chatbot_Conversations table |
| sender_type | Single Select | Yes | Message sender | Options: User, Bot, Agent |
| message_content | Long Text | Yes | Message text content | Max 4000 characters |
| message_type | Single Select | Yes | Type of message | Options: Text, Image, File, Quick Reply, Button |
| intent_detected | Text | No | Detected user intent | Max 100 characters |
| entities_extracted | Long Text | No | Extracted entities | JSON format |
| confidence_score | Number | No | Intent confidence score | Range 0-100 |
| response_time | Number | No | Response time in seconds | Min 0 |
| timestamp | Date and Time | Yes | Message timestamp | Auto-populated |

## Relationship Definitions

### Primary Relationships

**Users to Leads (One-to-Many):** A user can have multiple lead records over time, supporting lead lifecycle management and historical tracking. This relationship enables analysis of user progression through multiple sales cycles.

**Properties to Property_Images (One-to-Many):** Each property can have multiple images with different types and display orders. This relationship supports comprehensive property visualization and marketing materials.

**Users to User_Interactions (One-to-Many):** Users generate multiple interactions across their engagement with the platform. This relationship enables comprehensive behavioral analysis and lead scoring.

**Properties to Property_Valuations (One-to-Many):** Properties can have multiple valuations over time, supporting trend analysis and valuation accuracy tracking. This relationship enables historical valuation comparison and market trend analysis.

**Users to Email_Campaigns (Many-to-Many through Email_Recipients):** Users can receive multiple campaigns, and campaigns can target multiple users. This relationship requires a junction table for tracking individual email delivery and engagement metrics.

**Users to Chatbot_Conversations (One-to-Many):** Users can have multiple conversations across different platforms and time periods. This relationship enables conversation history tracking and user preference learning.

**Chatbot_Conversations to Chatbot_Messages (One-to-Many):** Each conversation contains multiple messages from users and bots. This relationship enables detailed conversation analysis and chatbot training data collection.

### Secondary Relationships

**Leads to Properties (Many-to-Many through Lead_Property_Interest):** Leads can be interested in multiple properties, and properties can attract multiple leads. This relationship tracks specific property interest and enables targeted marketing.

**Users to Properties (Many-to-Many through Property_Views):** Users can view multiple properties, and properties can be viewed by multiple users. This relationship tracks viewing behavior and supports recommendation algorithms.

**Properties to Market_Data (One-to-Many):** Properties are associated with market data points over time, enabling trend analysis and valuation accuracy. This relationship supports comparative market analysis and pricing optimization.

## Data Integrity and Constraints

### Referential Integrity

All foreign key relationships maintain referential integrity through Baserow's built-in constraint mechanisms. Cascade delete operations are carefully configured to prevent data loss while maintaining consistency.

**User Deletion:** When users are deleted, their interaction data is anonymized rather than deleted to preserve analytical value while protecting privacy. Lead records are maintained with anonymized user references.

**Property Deletion:** Property deletion cascades to related images and valuations but preserves interaction data with anonymized property references for historical analysis.

**Campaign Deletion:** Email campaign deletion preserves recipient data for compliance and analysis purposes while removing campaign content and configuration.

### Data Validation

**Email Validation:** All email fields use Baserow's built-in email validation with additional custom validation for business rules such as domain restrictions and disposable email detection.

**Phone Number Validation:** Phone numbers are validated for format and country codes, with support for international formats and mobile/landline distinction.

**Geographic Validation:** Address and coordinate data is validated against geographic databases to ensure accuracy and consistency. Postal codes are validated against official postal code databases.

**Financial Validation:** Price and financial data includes range validation, currency formatting, and business rule validation such as minimum property values and reasonable price ranges.

### Performance Optimization

**Indexing Strategy:** Primary indexes are created on frequently queried fields including user_id, property_id, email addresses, and timestamp fields. Composite indexes support complex queries across multiple fields.

**Partitioning:** Large tables such as User_Interactions and Chatbot_Messages are partitioned by date to improve query performance and enable efficient data archival.

**Archival Policies:** Historical data is archived to separate tables after defined retention periods while maintaining accessibility for analytical purposes. Archived data uses compressed storage to optimize costs.

## Security and Privacy Considerations

### Data Encryption

**Field-Level Encryption:** Sensitive fields including personal information, financial data, and contact details are encrypted at the field level using AES-256 encryption with proper key management.

**Encryption Key Management:** Encryption keys are managed through secure key management systems with regular rotation and access controls. Keys are never stored with encrypted data.

### Access Controls

**Role-Based Access:** Database access is controlled through role-based permissions with granular field-level access controls. Different user roles have access to different data subsets based on business requirements.

**Audit Logging:** All database access and modifications are logged with user identification, timestamp, and operation details. Audit logs are stored securely and monitored for unusual access patterns.

### Privacy Protection

**Data Anonymization:** Personal data can be anonymized for analytical purposes while preserving data utility. Anonymization processes are reversible only by authorized personnel with proper justification.

**Right to be Forgotten:** GDPR compliance includes mechanisms for complete data deletion upon user request, with verification processes to ensure complete removal across all related tables.

**Consent Management:** User consent preferences are tracked and enforced at the database level, preventing unauthorized use of personal data for marketing or other purposes.

## Migration and Deployment Strategy

### Initial Data Migration

**Legacy System Integration:** Migration scripts handle data import from existing CRM systems, real estate portals, and other data sources. Data mapping ensures that legacy data is properly transformed to match the new schema.

**Data Quality Assurance:** Migration processes include comprehensive data quality checks, duplicate detection, and data cleansing procedures. Migration reports provide visibility into data quality issues and resolution status.

### Deployment Phases

**Phased Rollout:** Database deployment follows a phased approach with initial deployment of core tables followed by gradual addition of advanced features. Each phase includes testing and validation procedures.

**Rollback Procedures:** Comprehensive rollback procedures enable quick recovery from deployment issues. Database snapshots and transaction logs support point-in-time recovery capabilities.

### Ongoing Maintenance

**Schema Evolution:** Database schema changes are managed through version-controlled migration scripts with testing procedures and rollback capabilities. Schema changes are coordinated with application deployments.

**Performance Monitoring:** Continuous monitoring of database performance includes query analysis, index optimization, and capacity planning. Performance metrics are tracked and analyzed for optimization opportunities.

**Backup and Recovery:** Automated backup procedures ensure data protection with multiple backup copies stored in geographically distributed locations. Recovery procedures are tested regularly to ensure reliability.

---

**Document Status:** Complete  
**Last Updated:** January 7, 2025  
**Next Review:** February 7, 2025  
**Approval:** Pending Database Review


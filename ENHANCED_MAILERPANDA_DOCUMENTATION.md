# Enhanced MailerPanda Agent - Complete HushMCP Integration

## Overview

The MailerPanda agent has been completely rewritten to implement the full HushMCP (Hushh Model Context Protocol) framework, providing privacy-first, consent-driven email campaign management with advanced AI capabilities.

## Key Features

### 🔐 HushMCP Framework Integration

#### Consent Management
- **Multi-scope validation**: Validates consent tokens for different operations
- **Dynamic consent checking**: Real-time validation before each sensitive operation
- **Granular permissions**: Separate scopes for reading, writing, and temporary operations

#### Vault Integration
- **Secure data storage**: All campaign data encrypted in user's personal vault
- **Encrypted email content**: Campaign templates and content securely stored
- **Audit trail**: Complete history of campaign operations

#### Trust Links
- **Cross-agent delegation**: Seamless integration with other HushMCP agents
- **Secure handoffs**: Encrypted trust links for AddToCalendar and other agents
- **User-controlled sharing**: Users maintain full control over data sharing

### 🤖 AI-Powered Content Generation

#### Gemini AI Integration
- **Professional email composition**: AI-generated content with customizable tone
- **Dynamic personalization**: Content adapted based on recipient context
- **Multi-format support**: Plain text, HTML, and structured content

#### Smart Campaign Management
- **Intelligent batching**: Automatic email batching for delivery optimization
- **Response tracking**: Campaign performance monitoring and analytics
- **Follow-up automation**: Intelligent follow-up scheduling

### 📧 Advanced Email Operations

#### Mailjet Integration
- **Professional delivery**: Enterprise-grade email sending service
- **Delivery tracking**: Real-time delivery status and analytics
- **Template management**: Reusable email templates with AI enhancement

#### Contact Management
- **Secure contact storage**: Encrypted contact lists in user vault
- **Email validation**: Advanced email validation using operons
- **List segmentation**: Smart contact categorization and targeting

## HushMCP Consent Scopes

### Required Scopes

| Operation | Required Scopes | Purpose |
|-----------|----------------|---------|
| Content Generation | `VAULT_READ_EMAIL`, `CUSTOM_TEMPORARY` | Read existing campaigns, temporary AI processing |
| Email Sending | `VAULT_READ_EMAIL`, `VAULT_WRITE_EMAIL`, `CUSTOM_TEMPORARY` | Read contacts, store results, temporary operations |
| Contact Management | `VAULT_READ_FILE`, `VAULT_WRITE_FILE` | Access and update contact lists |
| Campaign Storage | `VAULT_WRITE_EMAIL`, `VAULT_WRITE_FILE` | Store campaign data and results |

### Consent Token Structure

```python
{
    'email_token': 'HCT:...',      # VAULT_READ_EMAIL
    'file_token': 'HCT:...',       # VAULT_READ_FILE  
    'write_token': 'HCT:...',      # VAULT_WRITE_EMAIL
    'temp_token': 'HCT:...'        # CUSTOM_TEMPORARY
}
```

## API Usage

### Basic Email Campaign

```python
POST /agents/mailerpanda

{
    "user_id": "user_001",
    "consent_tokens": {
        "email_token": "HCT:vault_read_email_token...",
        "write_token": "HCT:vault_write_email_token...",
        "temp_token": "HCT:custom_temporary_token..."
    },
    "parameters": {
        "user_input": "Send welcome email to new@customer.com about our product launch",
        "mode": "interactive"
    }
}
```

### Advanced Campaign with Cross-Agent Integration

```python
POST /agents/mailerpanda

{
    "user_id": "user_001",
    "consent_tokens": {
        "email_token": "HCT:...",
        "write_token": "HCT:...",
        "temp_token": "HCT:...",
        "file_token": "HCT:..."
    },
    "parameters": {
        "user_input": "Create product launch campaign with follow-up calendar reminders",
        "mode": "interactive",
        "delegate_to_calendar": true
    }
}
```

## Enhanced Workflow

### 1. Consent Validation
- Validates all required consent tokens
- Checks token expiry and scope permissions
- Ensures user authorization for each operation

### 2. Content Generation
- AI-powered email content creation
- Professional tone and formatting
- Personalization based on recipient context

### 3. Secure Processing
- All data encrypted in transit and at rest
- Vault storage for campaign data
- Trust links for cross-agent operations

### 4. Email Delivery
- Professional email sending via Mailjet
- Delivery tracking and analytics
- Error handling and retry logic

### 5. Follow-up Integration
- Automatic calendar reminder creation
- Cross-agent trust link generation
- Seamless handoff to AddToCalendar agent

## Security Features

### Privacy-First Design
- **Zero-knowledge architecture**: Agent cannot access data without explicit consent
- **Encrypted storage**: All data encrypted with user-specific keys
- **Audit logging**: Complete audit trail of all operations
- **Consent expiry**: Automatic token expiration for enhanced security

### Trust Links
- **Secure delegation**: Encrypted trust links for cross-agent communication
- **User-controlled**: Users can revoke trust links at any time
- **Scope-limited**: Trust links limited to specific operations and time windows

## Operons Integration

### Email Validation Operon
- **Advanced validation**: Multi-layered email address validation
- **Bulk processing**: Efficient validation of large contact lists
- **Detailed reporting**: Comprehensive validation results with error details

### Email Analysis Operon
- **Content analysis**: AI-powered email content analysis
- **Sentiment detection**: Automatic tone and sentiment analysis
- **Optimization suggestions**: Recommendations for improving email effectiveness

## Error Handling

### Consent Errors
- **Missing tokens**: Clear error messages for missing consent tokens
- **Expired tokens**: Automatic detection of expired consent
- **Insufficient scope**: Detailed scope requirement explanations

### Operational Errors
- **Network failures**: Robust retry logic for network issues
- **API errors**: Comprehensive error handling for external APIs
- **Validation errors**: Detailed validation error reporting

## Performance Optimizations

### Efficient Processing
- **Batch operations**: Intelligent batching for large email lists
- **Parallel processing**: Concurrent operations where safe
- **Caching**: Smart caching of frequently accessed data

### Resource Management
- **Memory optimization**: Efficient memory usage for large campaigns
- **Rate limiting**: Respect for external API rate limits
- **Cleanup**: Automatic cleanup of temporary data

## Integration Examples

### With AddToCalendar Agent
```python
# MailerPanda creates trust link for calendar integration
trust_link = agent._create_trust_link_for_delegation(
    user_id="user_001",
    target_agent="addtocalendar",
    delegation_context={"calendar_access": "write"},
    consent_token=temp_token
)

# Calendar reminders automatically created after email campaign
```

### With Finance Assistant
```python
# Email campaign for financial product
campaign_result = agent.handle(
    user_input="Send investment newsletter to premium clients",
    consent_tokens=all_tokens,
    mode="interactive"
)

# Automatic trust link creation for financial analysis
```

## Testing and Validation

### Unit Tests
- **Consent validation tests**: Comprehensive consent token testing
- **Vault operation tests**: Encryption and storage validation
- **Trust link tests**: Cross-agent delegation testing

### Integration Tests
- **End-to-end workflow tests**: Complete campaign lifecycle testing
- **Cross-agent tests**: Multi-agent interaction validation
- **Performance tests**: Load and stress testing

## Migration Notes

### From Previous Version
- **Enhanced consent model**: New multi-scope consent validation
- **Vault integration**: All data now stored in encrypted vault
- **Trust links**: New cross-agent delegation capabilities
- **API changes**: Updated API endpoints and parameters

### Backward Compatibility
- **Legacy support**: Graceful handling of old consent tokens
- **Migration tools**: Utilities for migrating existing campaigns
- **Documentation**: Comprehensive migration guides

## Future Enhancements

### Planned Features
- **Advanced analytics**: Enhanced campaign performance analytics
- **AI optimization**: Machine learning for campaign optimization
- **Multi-channel support**: SMS and social media integration
- **Advanced personalization**: Dynamic content based on user behavior

### HushMCP Roadmap
- **Enhanced operons**: Additional reusable email operations
- **Cross-agent workflows**: More sophisticated multi-agent workflows
- **Advanced consent**: Fine-grained consent management
- **Performance improvements**: Continued optimization and enhancement

---

## Quick Start

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Set environment variables**: Copy `.env.example` to `.env` and configure
3. **Create consent tokens**: Use the HushMCP token system
4. **Start the API**: `python api.py`
5. **Send test campaign**: Use the provided examples

The enhanced MailerPanda agent represents a complete implementation of the HushMCP framework, providing enterprise-grade email campaign management with privacy-first, consent-driven architecture.

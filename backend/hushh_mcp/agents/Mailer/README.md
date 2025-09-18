# Mailer Agent - Basic Email Sending Service

## Agent Architecture Flow

```mermaid
flowchart TD
    A[Email Request] --> B[Consent Token Validation]
    B --> C{Valid Token?}
    C -->|No| D[Error: Invalid Token]
    C -->|Yes| E[Email Data Processing]
    
    E --> F[Excel/CSV Input]
    F --> G[Contact List Parsing]
    G --> H[Email Validation]
    
    H --> I[Template Processing]
    I --> J[Basic Personalization]
    J --> K[Subject Line Generation]
    
    K --> L[Email Queue]
    L --> M[Batch Processing]
    M --> N[Rate Limiting]
    
    N --> O[Email Service Provider]
    O --> P[SMTP/API Integration]
    P --> Q[Email Delivery]
    
    Q --> R[Delivery Status]
    R --> S[Success/Failure Tracking]
    S --> T[Status Reports]
    
    U[Vault Storage] --> V[Encrypted Email Data]
    G --> U
    T --> U
    
    W[Error Handling] --> X[Retry Logic]
    R --> W
    X --> Y[Exponential Backoff]
    Y --> O
    
    style A fill:#e1f5fe
    style I fill:#fff3e0
    style L fill:#e8f5e8
    style O fill:#f3e5f5
    style U fill:#ffebee
    style W fill:#fff9c4
```

## Workflow Description

### 1. Input Processing
- **Email Request**: Basic email sending requests
- **Consent Validation**: HushhMCP token verification for email permissions
- **Data Processing**: Parse contact lists and email content

### 2. Contact Management
- **Excel/CSV Support**: Import contact lists from spreadsheet files
- **Email Validation**: Verify email address formats and deliverability
- **List Segmentation**: Organize contacts for targeted campaigns

### 3. Email Preparation
- **Template Processing**: Apply email templates and formatting
- **Basic Personalization**: Simple mail merge functionality
- **Subject Line Generation**: Create appropriate subject lines

### 4. Delivery Management
- **Queue System**: Organize emails for optimal delivery timing
- **Batch Processing**: Send emails in manageable batches
- **Rate Limiting**: Respect email service provider limits

### 5. Email Sending
- **Service Integration**: Connect with SMTP servers or email APIs
- **Delivery Tracking**: Monitor email sending status
- **Error Handling**: Automatic retry with exponential backoff

### 6. Reporting & Storage
- **Status Tracking**: Monitor delivery success and failures
- **Performance Reports**: Generate sending statistics
- **Encrypted Storage**: Secure storage of email data and results

## Key Features
- 📧 **Basic Email Sending**: Reliable email delivery service
- 📊 **Excel/CSV Support**: Import contacts from spreadsheet files
- 🔄 **Batch Processing**: Efficient bulk email handling
- 📈 **Delivery Tracking**: Monitor email sending status
- 🔒 **Secure Storage**: Encrypted data management
- ⚙️ **Error Handling**: Robust retry and error recovery

## API Endpoints
- `POST /agents/mailer/execute` - Send email campaigns
- `GET /agents/mailer/status` - Check sending status
- `POST /agents/mailer/upload` - Upload contact lists
- `GET /agents/mailer/reports` - Delivery reports

## Supported Features
- **Contact Import**: Excel, CSV file support
- **Template System**: Basic email templates
- **Personalization**: Simple mail merge capabilities
- **Delivery Tracking**: Real-time status monitoring
- **Bulk Sending**: Efficient batch processing

## Differences from MailerPanda
- **Simpler Interface**: Basic email sending without AI
- **No AI Generation**: Manual template creation
- **Basic Personalization**: Simple variable substitution
- **Direct Sending**: No human approval workflow
- **Lightweight**: Minimal dependencies and features
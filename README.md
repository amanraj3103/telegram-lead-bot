# WhatsApp Lead Collection Backend

A production-ready WhatsApp chatbot backend for Dream Axis Travel Solutions that collects job applications for truck and trailer drivers in Europe. Built with FastAPI, featuring GDPR compliance, multi-language support, and AI-powered conversations.

## 🚀 Features

- **GDPR Compliant**: Explicit consent collection with data deletion capabilities
- **Multi-Language Support**: 7 languages (English, Polish, German, Spanish, Ukrainian, Hindi, Malayalam)
- **AI-Powered Conversations**: Uses OpenAI for natural lead collection
- **WhatsApp Integration**: Official Meta WhatsApp Cloud API
- **Google Sheets Storage**: Secure lead data storage
- **Email Notifications**: Instant admin notifications for new leads
- **Data Validation**: Comprehensive validation for all collected data

## 🧱 Tech Stack

- **Python 3.11+**
- **FastAPI** - Web framework
- **Meta WhatsApp Cloud API** - Messaging
- **OpenAI API** - AI conversations
- **Google Sheets API** - Data storage
- **SMTP** - Email notifications
- **langdetect** - Language detection

## 📁 Project Structure

```
lead_bot/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── routes/
│   │   └── whatsapp_webhook.py # WhatsApp webhook handler
│   └── services/
│       ├── whatsapp_service.py # WhatsApp API integration
│       ├── openai_service.py   # AI conversation service
│       ├── sheets_service.py   # Google Sheets integration
│       ├── email_service.py    # Email notification service
│       └── language_service.py # Language detection
│   └── utils/
│       ├── consent_texts.py    # GDPR consent texts
│       └── validators.py       # Data validation utilities
├── requirements.txt
├── env.example
└── README.md
```

## 🛠 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd lead_bot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your credentials
   ```

## ⚙️ Configuration

### Required Environment Variables

```bash
# WhatsApp Cloud API
WHATSAPP_API_TOKEN=your_whatsapp_api_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_VERIFY_TOKEN=your_verify_token

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Google Sheets
GOOGLE_SHEET_NAME=Dream Axis Leads
GOOGLE_CREDENTIALS_PATH=/path/to/service-account.json

# Email (SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
ADMIN_EMAILS=admin1@company.com,admin2@company.com
```

### Google Sheets Setup

1. Create a Google Cloud Project
2. Enable Google Sheets API
3. Create a Service Account
4. Download the JSON credentials file
5. Share your Google Sheet with the service account email

### WhatsApp Business API Setup

1. Set up a Meta Business account
2. Create a WhatsApp Business app
3. Configure webhooks pointing to your `/api/webhook` endpoint
4. Get your API token and phone number ID

## 🚀 Running the Application

### Development
```bash
uvicorn app.main:app --reload
```

### Production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📡 API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /api/webhook` - WhatsApp webhook verification
- `POST /api/webhook` - WhatsApp message handler

## 🗣 Chat Flow

1. **Language Detection**: Automatically detects user language from first message
2. **GDPR Consent**: Presents consent text in detected language
3. **AI Collection**: Uses OpenAI to ask questions naturally in user's language
4. **Validation**: Validates email, phone, and required fields
5. **Storage**: Saves to Google Sheets with consent tracking
6. **Notification**: Sends email to admins
7. **Confirmation**: Confirms successful collection to user

## 🗑 GDPR Compliance

### Data Deletion
Users can delete their data by sending language-specific keywords:
- English: `DELETE`
- Polish: `USUŃ`
- German: `LÖSCHEN`
- Spanish: `ELIMINAR`
- Ukrainian: `ВИДАЛИТИ`
- Hindi: `हटाएँ`
- Malayalam: `ഇല്ലാതാക്കുക`

### Data Storage
- Personal data is anonymized (not deleted) for audit compliance
- Consent status and timestamps are tracked
- All operations are logged

## 🔒 Security

- Webhook signature verification
- Environment variable configuration
- No personal data logging
- Secure credential management

## 📧 Email Notifications

Admin emails include:
- Complete lead details
- Consent status and timestamp
- Language code
- Source information

## 🧪 Testing

Test the webhook endpoint with sample WhatsApp payloads:

```bash
curl -X POST http://localhost:8000/api/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "object": "whatsapp_business_account",
    "entry": [{
      "changes": [{
        "value": {
          "messages": [{
            "from": "1234567890",
            "text": {"body": "Hello"},
            "timestamp": "1234567890"
          }]
        }
      }]
    }]
  }'
```

## 📈 Monitoring

- Health check endpoint: `GET /health`
- Error notifications sent to admin emails
- Conversation states tracked in memory (use Redis for production)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is proprietary software for Dream Axis Travel Solutions.

## 🆘 Support

For support, contact the development team or check the error logs in your email notifications.


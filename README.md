# Telegram Lead Bot

A WhatsApp and Telegram chatbot backend for automated lead collection, built for Dream Axis Travel Solutions. Collects job applications for truck and trailer drivers in Europe through AI-powered conversations.

Built with Python, FastAPI, and the Meta WhatsApp Cloud API.

## What it does

- Collects lead data through structured, AI-powered conversations using OpenAI
- Supports 7 languages: English, Polish, German, Spanish, Ukrainian, Hindi, Malayalam
- Stores lead data securely in Google Sheets with instant admin email notifications
- GDPR compliant with explicit consent collection and data deletion capabilities
- Validates all collected data (phone numbers, emails, names) before storage
- Automatically detects user language and responds accordingly

## Tech stack

Python 3.11, FastAPI, Meta WhatsApp Cloud API, OpenAI API, Google Sheets API, SMTP, langdetect

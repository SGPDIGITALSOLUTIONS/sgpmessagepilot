# MessagePilot

A powerful bulk WhatsApp messaging solution by SGP Digital Solutions.

## Overview

MessagePilot is a professional tool designed to streamline WhatsApp communication with multiple contacts. It allows you to easily generate personalized WhatsApp messages for multiple recipients while maintaining privacy and compliance with WhatsApp's terms of service.

## Features

- Upload contact spreadsheets (Excel/CSV)
- Personalize messages with contact information
- Smart phone number formatting (UK format support)
- Secure local data processing
- No data storage - immediate file deletion
- Compliant with WhatsApp's terms of service
- User-friendly interface
- Azure cloud deployment

## Security Features

- Local data processing only
- No data storage
- PII (Personally Identifiable Information) protection
- Secure URL handling
- Comprehensive security headers
- Input validation and sanitization
- Azure App Service security

## Requirements

- Python 3.7+
- Flask
- Pandas
- Other dependencies listed in requirements.txt

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run the application:
```bash
cd app
python -m flask run
```

## Usage

1. Access the tool via web browser at `http://localhost:5000`
2. Upload your contact spreadsheet (Excel/CSV)
3. Customize your message template
4. Generate WhatsApp message links
5. Send messages manually through WhatsApp

## Compliance

MessagePilot is designed to be compliant with WhatsApp's terms of service:
- No automation of message sending
- Uses official WhatsApp click-to-chat links
- Requires manual message sending
- Respects WhatsApp's messaging limits

## Created By

SGP Digital Solutions - Professional Digital Solutions Provider

## License

All rights reserved. This software is proprietary to SGP Digital Solutions.

## SMS Setup with Twilio

To enable SMS functionality, you'll need to set up a Twilio account and configure the following:

1. Sign up for a [Twilio account](https://www.twilio.com/try-twilio)
2. Get your Twilio credentials from the [Twilio Console](https://console.twilio.com/):
   - Account SID
   - Auth Token
   - Twilio Phone Number

3. Create a `.env` file in the root directory with your Twilio credentials:
   ```
   TWILIO_ACCOUNT_SID=your_account_sid_here
   TWILIO_AUTH_TOKEN=your_auth_token_here
   TWILIO_PHONE_NUMBER=your_twilio_phone_number_here
   ```

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

The SMS functionality includes:
- Rate limiting (1 message per second by default)
- Batch processing (50 messages per batch)
- Message length validation (max 1600 characters)
- Phone number formatting for UK numbers
- Error handling and logging
- Message status tracking

### SMS Usage Example

```python
from SMS.utils.sms_handler import SMSHandler

# Initialize the SMS handler
sms = SMSHandler()

# Send a single message
result = sms.send_single_sms(
    to_number="447123456789",
    message="Hello from MessagePilot!"
)

# Send batch messages with templates
recipients = [
    {"phone": "447123456789", "name": "John"},
    {"phone": "447987654321", "name": "Jane"}
]
message_template = "Hello {name}, welcome to MessagePilot!"

results = sms.send_batch_sms(recipients, message_template)

# Check message status
status = sms.get_message_status(message_id="message_sid_here")
```

### Important Notes

- Ensure your Twilio account has sufficient credits
- Test with a small batch of numbers first
- Monitor your Twilio console for delivery status
- Keep your `.env` file secure and never commit it to version control
- Follow SMS regulations and obtain proper consent before sending messages 
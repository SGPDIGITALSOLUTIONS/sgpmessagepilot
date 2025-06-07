from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import time
import logging
from typing import List, Dict, Optional, Union
from app.config import Config

logger = logging.getLogger(__name__)

class SMSHandler:
    """Handles SMS operations including sending and status checking"""
    
    def __init__(self):
        """Initialize the SMS handler with Twilio credentials"""
        self.account_sid = Config.TWILIO_ACCOUNT_SID
        self.auth_token = Config.TWILIO_AUTH_TOKEN
        self.phone_number = Config.TWILIO_PHONE_NUMBER
        
        if not all([self.account_sid, self.auth_token, self.phone_number]):
            logger.error("Missing Twilio credentials. Please check your .env file.")
            raise ValueError("Missing Twilio credentials")
        
        self.client = Client(self.account_sid, self.auth_token)
        self.rate_limit = Config.SMS_RATE_LIMIT
        self.max_length = Config.SMS_MAX_LENGTH
        self.batch_size = Config.SMS_BATCH_SIZE

    def validate_message(self, message: str) -> bool:
        """
        Validate message length and content
        
        Args:
            message (str): The message to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not message or not isinstance(message, str):
            logger.error("Invalid message: Message must be a non-empty string")
            return False
            
        if len(message) > self.max_length:
            logger.error(f"Message exceeds maximum length of {self.max_length} characters")
            return False
            
        return True

    def format_phone_number(self, phone: str) -> Optional[str]:
        """
        Format phone number to E.164 format
        
        Args:
            phone (str): The phone number to format
            
        Returns:
            Optional[str]: Formatted phone number or None if invalid
        """
        # Remove any non-digit characters
        cleaned = ''.join(filter(str.isdigit, str(phone)))
        
        if not cleaned:
            return None
            
        # Handle UK numbers
        if cleaned.startswith('0'):
            cleaned = '44' + cleaned[1:]
        elif not cleaned.startswith('44'):
            cleaned = '44' + cleaned
            
        return '+' + cleaned

    def send_single_sms(self, to_number: str, message: str) -> Dict[str, Union[bool, str]]:
        """
        Send a single SMS message
        
        Args:
            to_number (str): The recipient's phone number
            message (str): The message to send
            
        Returns:
            dict: Result of the operation with status and message
        """
        if not self.validate_message(message):
            return {'success': False, 'error': 'Invalid message'}
            
        formatted_number = self.format_phone_number(to_number)
        if not formatted_number:
            return {'success': False, 'error': 'Invalid phone number'}
            
        try:
            message = self.client.messages.create(
                body=message,
                from_=self.phone_number,
                to=formatted_number
            )
            logger.info(f"SMS sent successfully to {formatted_number}. Message SID: {message.sid}")
            return {'success': True, 'message_id': message.sid}
            
        except TwilioRestException as e:
            logger.error(f"Failed to send SMS to {formatted_number}: {str(e)}")
            return {'success': False, 'error': str(e)}

    def send_batch_sms(self, recipients: List[Dict[str, str]], message_template: str) -> List[Dict[str, Union[bool, str]]]:
        """
        Send SMS messages to multiple recipients with rate limiting
        
        Args:
            recipients (List[Dict]): List of recipient dictionaries with phone numbers and template variables
            message_template (str): Message template with placeholders
            
        Returns:
            List[Dict]: List of results for each message
        """
        results = []
        
        for i, recipient in enumerate(recipients):
            # Apply rate limiting
            if i > 0 and i % self.rate_limit == 0:
                time.sleep(1)  # Sleep for 1 second after every rate_limit messages
                
            # Format message for this recipient
            try:
                personalized_message = message_template.format(**recipient)
            except KeyError as e:
                logger.error(f"Missing template variable for recipient: {str(e)}")
                results.append({
                    'success': False,
                    'error': f"Missing template variable: {str(e)}",
                    'recipient': recipient
                })
                continue
                
            # Send message
            result = self.send_single_sms(recipient.get('phone'), personalized_message)
            result['recipient'] = recipient
            results.append(result)
            
            # Process in batches
            if (i + 1) % self.batch_size == 0:
                logger.info(f"Processed {i + 1} messages")
                
        return results

    def get_message_status(self, message_id: str) -> Dict[str, str]:
        """
        Get the status of a sent message
        
        Args:
            message_id (str): The Twilio message SID
            
        Returns:
            dict: Message status information
        """
        try:
            message = self.client.messages(message_id).fetch()
            return {
                'status': message.status,
                'error_code': message.error_code,
                'error_message': message.error_message
            }
        except TwilioRestException as e:
            logger.error(f"Failed to get message status for {message_id}: {str(e)}")
            return {
                'status': 'error',
                'error_code': str(e.code),
                'error_message': str(e)
            }
    
    def get_remaining_quota(self) -> Dict[str, Any]:
        """Get remaining SMS quota information"""
        # TODO: Implement actual quota checking logic
        return {
            'daily_limit': 1000,
            'used_today': 0,
            'remaining': 1000,
            'reset_time': '00:00 UTC'
        } 
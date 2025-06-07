import re
from typing import Tuple, List

def validate_phone_numbers(numbers: List[str]) -> Tuple[List[str], List[str]]:
    """
    Validate a list of phone numbers and separate them into valid and invalid numbers
    
    Args:
        numbers (List[str]): List of phone numbers to validate
        
    Returns:
        Tuple[List[str], List[str]]: (valid_numbers, invalid_numbers)
    """
    valid_numbers = []
    invalid_numbers = []
    
    # Basic UK phone number pattern
    # Accepts formats:
    # - +44 7XXX XXXXXX
    # - 07XXX XXXXXX
    # - 447XXX XXXXXX
    uk_pattern = re.compile(r'^(?:(?:\+44)|(?:44)|(?:0))(?:7\d{9})$')
    
    for number in numbers:
        # Clean the number
        cleaned = clean_phone_number(number)
        
        # Validate
        if uk_pattern.match(cleaned):
            # Standardize to international format
            if cleaned.startswith('0'):
                cleaned = '44' + cleaned[1:]
            elif not cleaned.startswith('44'):
                cleaned = '44' + cleaned
                
            valid_numbers.append(cleaned)
        else:
            invalid_numbers.append(number)
    
    return valid_numbers, invalid_numbers

def clean_phone_number(number: str) -> str:
    """
    Clean a phone number by removing all non-digit characters
    
    Args:
        number (str): Phone number to clean
        
    Returns:
        str: Cleaned phone number
    """
    # Remove all non-digit characters except '+'
    cleaned = re.sub(r'[^\d+]', '', str(number))
    
    # Remove '+' if it exists
    if cleaned.startswith('+'):
        cleaned = cleaned[1:]
    
    return cleaned 
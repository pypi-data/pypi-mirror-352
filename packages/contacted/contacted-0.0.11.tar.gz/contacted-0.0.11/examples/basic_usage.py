"""
Contacted Python SDK - Basic Usage Examples
"""

import os
from contacted import ContactedAI


def basic_example():
    """Basic usage example"""
    # Initialize the client
    contacted = ContactedAI(
        api_key=os.getenv('CONTACTED_API_KEY', 'your-api-key-here')
    )

    try:
        # Send a message (your exact API!)
        result = contacted.send(
            from_email='sender@example.com',
            to_email='receiver@example.com',
            subject='Welcome to our platform!',
            prompt='Generate a personalized welcome email for the user',  # 10+ chars
            data={
                'name': 'John Doe',
                'plan': 'premium',
                'link': 'https://dashboard.example.com'
            }
        )

        print('Message sent successfully:', result)

    except ValueError as error:
        print('Error:', error)


def validation_examples():
    """Examples showing validation errors"""
    contacted = ContactedAI(api_key="test-key")

    # These will throw validation errors BEFORE hitting your API:

    print("Testing validation errors...")

    try:
        contacted.send(
            from_email='invalid-email',
            to_email='user@example.com',
            subject='Test Subject',
            prompt='Generate email'
        )
    except ValueError as error:
        print('❌ Email validation:', error)
        # "Invalid 'from' email address format"

    try:
        contacted.send(
            from_email='sender@example.com',
            to_email='receiver@example.com',
            subject='Test Subject',
            prompt='short'  # Less than 10 characters
        )
    except ValueError as error:
        print('❌ Prompt validation:', error)
        # "Prompt must be at least 10 characters long"

    try:
        contacted.send(
            from_email='sender@example.com',
            to_email='receiver@example.com',
            subject='Test Subject',
            prompt='This is a valid prompt with enough characters',
            data={
                'key with space': 'invalid key'  # Keys can't have spaces
            }
        )
    except ValueError as error:
        print('❌ Data validation:', error)
        # "Data keys cannot contain spaces"

    print('✅ All validation examples completed')


def advanced_example():
    """Advanced usage with error handling"""
    contacted = ContactedAI(
        api_key=os.getenv('CONTACTED_API_KEY'),
        timeout=60  # Custom timeout
    )

    # Example with comprehensive error handling
    try:
        result = contacted.send(
            from_email='automated@mycompany.com',
            to_email='customer@example.com',
            subject='Welcome to your business account',
            prompt='Create a personalized onboarding email with account details',
            data={
                'firstName': 'Sarah',
                'lastName': 'Johnson',
                'accountType': 'business',
                'trialDays': 14,
                'loginUrl': 'https://app.mycompany.com/login'
            }
        )

        print(f"✅ Email queued successfully!")
        print(f"   ID: {result.get('id')}")
        print(f"   Status: {result.get('status')}")

    except ValueError as e:
        error_msg = str(e)
        if 'Invalid' in error_msg:
            print(f"❌ Validation Error: {error_msg}")
        elif 'API Error' in error_msg:
            print(f"❌ API Error: {error_msg}")
        else:
            print(f"❌ Network Error: {error_msg}")


def sending_profile_example():
    """Example using sending profiles"""
    contacted = ContactedAI(api_key=os.getenv('CONTACTED_API_KEY'))

    try:
        result = contacted.send(
            from_email='marketing@mycompany.com',
            to_email='customer@example.com',
            subject='New Product Launch Announcement',
            prompt='Create an exciting product launch email with key features',
            sending_profile='marketing-profile-id',  # Optional sending profile
            data={
                'customerName': 'Alex Chen',
                'productName': 'Pro Dashboard',
                'launchDate': 'June 15th',
                'earlyBirdDiscount': '20%'
            }
        )

        print(f"✅ Marketing email sent with profile!")
        print(f"   ID: {result.get('id')}")

    except ValueError as error:
        print(f"❌ Error: {error}")


def message_tracking_example():
    """Example showing message status tracking"""
    contacted = ContactedAI(api_key=os.getenv('CONTACTED_API_KEY'))

    try:
        # Send a message
        result = contacted.send(
            from_email='orders@mystore.com',
            to_email='customer@example.com',
            subject='Order Confirmation #12345',
            prompt='Generate order confirmation with shipping details',
            data={
                'orderNumber': '12345',
                'total': '$99.99',
                'shippingDate': '2024-06-10',
                'trackingUrl': 'https://shipping.com/track/12345'
            }
        )

        message_id = result['id']
        print(f"✅ Order confirmation sent: {message_id}")

        # Check message status
        status = contacted.get_message_status(message_id)
        print(f"📧 Message Status: {status['status']}")
        print(f"   Created: {status['created_at']}")

        if status['status'] == 'sent':
            print(f"   Delivered: {status['sent_at']}")
        elif status['status'] == 'failed':
            print(f"   Error: {status.get('error_reason', 'Unknown error')}")

    except ValueError as error:
        print(f"❌ Error: {error}")


if __name__ == '__main__':
    print("=== ContactedAI Python SDK Examples ===\n")

    print("1. Basic Example:")
    basic_example()

    print("\n2. Validation Examples:")
    validation_examples()

    print("\n3. Advanced Example:")
    advanced_example()

    print("\n4. Sending Profile Example:")
    sending_profile_example()

    print("\n5. Message Tracking Example:")
    message_tracking_example()
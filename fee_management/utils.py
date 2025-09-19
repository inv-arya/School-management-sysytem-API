from django.conf import settings
import razorpay
import logging

logger = logging.getLogger('fee_management')

def get_razorpay_client():
    
    try:
        # Check if keys are configured
        if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
            raise ValueError("Razorpay API keys not configured in settings.py")
        
        # Create client with your keys
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        
        # Log successful initialization
        logger.debug(f"Razorpay client initialized with Key ID: {settings.RAZORPAY_KEY_ID[:8]}...")
        
        return client
        
    except Exception as e:
        logger.error(f"Razorpay client initialization failed: {str(e)}")
        raise ValueError(f"Payment service unavailable: {str(e)}")

def generate_receipt_filename(transaction_id):
    
    short_id = str(transaction_id).replace('-', '').upper()[:8]
    return f"receipt_{short_id}.pdf"
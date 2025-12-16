import requests
from django.conf import settings
import logging
import json

logger = logging.getLogger(__name__)

class ChapaService:
    @staticmethod
    def initialize_payment(amount, currency, email, first_name, last_name, tx_ref, callback_url, return_url, phone_number=None, customization=None):
        url = f"{settings.CHAPA_API_URL}/transaction/initialize"
        headers = {
            'Authorization': f'Bearer {settings.CHAPA_SECRET_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Chapa requires phone_number field
        if not phone_number:
            phone_number = '0900000000'  # Default placeholder
            
        data = {
            'amount': str(amount),
            'currency': currency,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'phone_number': phone_number,
            'tx_ref': tx_ref,
            'callback_url': callback_url,
            'return_url': return_url,
            'customization': customization or {}
        }
        
        try:
            # Validate API key is configured
            if not settings.CHAPA_SECRET_KEY or settings.CHAPA_SECRET_KEY.strip() == '':
                raise Exception("Chapa API Key is not configured. Please set CHAPA_SECRET_KEY environment variable.")
            
            logger.info(f"Sending to Chapa: {data}")
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            # Check response status
            if response.status_code == 401:
                error_body = response.json() if response.content else {}
                error_msg = error_body.get('message', 'Invalid API Key')
                logger.error(f"Chapa authentication error: {error_msg}")
                raise Exception(f"Chapa API Error: {json.dumps(error_body) if error_body else error_msg}")
            
            response.raise_for_status()
            result = response.json()
            
            # Check if Chapa returned an error in the response body
            if result.get('status') == 'failed' or result.get('status') == 'error':
                error_msg = result.get('message', 'Payment initialization failed')
                logger.error(f"Chapa returned error status: {error_msg}")
                raise Exception(f"Chapa API Error: {json.dumps(result)}")
            
            return result
        except requests.exceptions.Timeout:
            logger.error("Chapa API request timeout")
            raise Exception("Payment service timeout. Please try again.") from None
        except requests.exceptions.ConnectionError:
            logger.error("Chapa API connection error")
            raise Exception("Unable to connect to payment service. Please check your internet connection and try again.") from None
        except requests.exceptions.HTTPError as e:
            logger.error(f"Chapa HTTP error: {e.response.status_code if hasattr(e, 'response') else 'unknown'}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_body = e.response.json()
                    logger.error(f"Chapa error response: {error_body}")
                    error_msg = error_body.get('message', str(e))
                    raise Exception(f"Chapa API Error: {json.dumps(error_body)}") from e
                except (ValueError, AttributeError):
                    logger.error(f"Chapa response text: {e.response.text}")
                    raise Exception(f"Chapa API Error: {json.dumps({'message': e.response.text, 'status': 'failed', 'data': None})}") from e
            raise Exception(f"Payment service error: {str(e)}") from e
        except Exception as e:
            # Re-raise if it's already formatted
            if 'Chapa API Error' in str(e) or 'Payment service' in str(e):
                raise
            logger.error(f"Unexpected Chapa service error: {str(e)}")
            raise Exception(f"Payment initialization error: {str(e)}") from e

    @staticmethod
    def verify_payment(tx_ref):
        url = f"{settings.CHAPA_API_URL}/transaction/verify/{tx_ref}"
        headers = {
            'Authorization': f'Bearer {settings.CHAPA_SECRET_KEY}',
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Chapa verification error: {str(e)}")
            return None

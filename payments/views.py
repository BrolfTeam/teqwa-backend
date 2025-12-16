from rest_framework import views, status, permissions
from rest_framework.response import Response
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from .models import Transaction
from .serializers import InitializePaymentSerializer
from .chapa import ChapaService
import hmac
import hashlib
import json
import logging

logger = logging.getLogger(__name__)

class InitializePaymentView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logger.info(f"Payment Initialization Request Data: {request.data}")
        
        # Check if Chapa is configured
        if not settings.CHAPA_SECRET_KEY or settings.CHAPA_SECRET_KEY.strip() == '':
            logger.error("CHAPA_SECRET_KEY is not configured")
            return Response({
                'error': 'Payment service is not configured. Please contact the administrator.',
                'message': 'CHAPA_SECRET_KEY environment variable is missing or empty.'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        serializer = InitializePaymentSerializer(data=request.data)
        if serializer.is_valid():
            # Extract data
            data = serializer.validated_data
            
            # Get content type
            try:
                content_type = ContentType.objects.get(model=data['content_type_model'])
            except ContentType.DoesNotExist:
                logger.error(f"Invalid content type: {data['content_type_model']}")
                return Response({'error': 'Invalid content type'}, status=status.HTTP_400_BAD_REQUEST)

            # Create Transaction
            transaction = Transaction.objects.create(
                amount=data['amount'],
                currency=data['currency'],
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                content_type=content_type,
                object_id=data['object_id'],
                status='pending'
            )
            
            # Prepare callback URLs
            return_url = f"{settings.FRONTEND_URL}/payment/success/{transaction.tx_ref}" 
            
            if settings.WEBHOOK_URL:
                 webhook_url = f"{settings.WEBHOOK_URL}/api/v1/payments/webhook/"
            else:
                 webhook_url = f"{settings.FRONTEND_URL.replace('5173', '8000')}/api/v1/payments/webhook/" 
            
            # Get phone number if provided, otherwise use default
            phone_number = data.get('phone_number', '0900000000')
            
            # Initialize with Chapa
            try:
                response = ChapaService.initialize_payment(
                    amount=data['amount'],
                    currency=data['currency'],
                    email=data['email'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    tx_ref=str(transaction.tx_ref),
                    callback_url=webhook_url,
                    return_url=return_url,
                    phone_number=phone_number
                )
                logger.info(f"Chapa Response: {response}")
                
                if response and response.get('status') == 'success' and response.get('data'):
                    checkout_url = response['data'].get('checkout_url') if isinstance(response.get('data'), dict) else None
                    if checkout_url:
                        return Response({
                            'checkout_url': checkout_url,
                            'tx_ref': transaction.tx_ref
                        })
                    else:
                        logger.error(f"Chapa response missing checkout_url: {response}")
                        transaction.status = 'failed'
                        transaction.save()
                        return Response({
                            'error': 'Payment gateway response is invalid. Please try again or contact support.',
                            'message': 'Checkout URL not found in payment response'
                        }, status=status.HTTP_502_BAD_GATEWAY)
                else:
                    transaction.status = 'failed'
                    transaction.save()
                    error_msg = response.get('message', 'Failed to initialize payment') if response else 'No response from payment provider'
                    
                    # Handle specific Chapa error messages
                    if error_msg and 'Invalid API Key' in error_msg:
                        error_msg = 'Payment service configuration error. Please contact the administrator.'
                        logger.error("Chapa API Key is invalid or account is inactive")
                    elif error_msg and ("can't accept payments" in error_msg.lower() or "account is active" in error_msg.lower()):
                        error_msg = 'Payment service is currently unavailable. Please try again later or contact support.'
                        logger.error(f"Chapa account issue: {error_msg}")
                    
                    return Response({
                        'error': error_msg,
                        'message': 'Unable to process payment at this time. Please try again later or contact support if the issue persists.'
                    }, status=status.HTTP_502_BAD_GATEWAY)

            except Exception as e:
                logger.error(f"Chapa service error: {str(e)}", exc_info=True)
                transaction.status = 'failed'
                transaction.save()
                
                error_message = str(e)
                # Clean up error messages for user-facing responses
                if 'Chapa API Error' in error_message:
                    # Extract the actual error message from the exception
                    if 'Invalid API Key' in error_message or "can't accept payments" in error_message:
                        error_message = 'Payment service configuration error. Please contact the administrator.'
                    else:
                        # Extract the message part after "Chapa API Error: "
                        if 'Chapa API Error:' in error_message:
                            parts = error_message.split('Chapa API Error:', 1)
                            if len(parts) > 1:
                                try:
                                    import json
                                    error_data = json.loads(parts[1].strip())
                                    error_message = error_data.get('message', 'Payment initialization failed')
                                except:
                                    error_message = parts[1].strip()
                
                return Response({
                    'error': error_message,
                    'message': 'Unable to process payment at this time. Please try again later or contact support.'
                }, status=status.HTTP_502_BAD_GATEWAY)
        
        logger.error(f"Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChapaWebhookView(views.APIView):
    permission_classes = [permissions.AllowAny] # Webhook comes from external service

    def post(self, request):
        # Verify signature
        chapa_signature = request.headers.get('Chapa-Signature') or request.headers.get('x-chapa-signature')
        if not chapa_signature:
             return Response({'error': 'No signature provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        payload = request.body
        secret = settings.CHAPA_WEBHOOK_SECRET.encode('utf-8')
        expected_signature = hmac.new(secret, payload, hashlib.sha256).hexdigest()
        
        if chapa_signature != expected_signature:
            # In some cases, Chapa might use a different hashing or payload structure verify.
            # If standard HMAC SHA256 matches, good. If not, log warning but if strictly required, fail.
            # For now we enforce it.
            logger.warning(f"Invalid webhook signature. Received: {chapa_signature}")
            return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            event = json.loads(payload)
            # Depending on Chapa's webhook payload structure.
            # Usually generic structure: { "tx_ref": "...", "status": "success", ... }
            # Or wrapped in "data".
            # Let's assume standard payload.
            
            tx_ref = event.get('tx_ref')
            # If nested
            if not tx_ref and 'data' in event:
                tx_ref = event['data'].get('tx_ref')
            
            if not tx_ref:
                return Response({'error': 'No content'}, status=status.HTTP_200_OK) 

            transaction = Transaction.objects.get(tx_ref=tx_ref)
            
            # Check success status
            # It might be event['status'] or event['event'] == 'charge.success'
            # We will rely on verifying it again to be safe or just trusting the webhook 'status' field if present.
            # Best practice: Verify against API to be sure.
            
            verification = ChapaService.verify_payment(tx_ref)
            if verification and verification.get('status') == 'success' and verification['data']['status'] == 'success':
                transaction.status = 'success'
                transaction.chapa_reference = verification['data'].get('reference', '')
                transaction.save()
                
                # Update related object
                related_obj = transaction.content_object
                if related_obj:
                    # Generic handling based on known models
                    model_name = related_obj._meta.model_name
                    if model_name == 'donation':
                        related_obj.status = 'completed'
                        related_obj.save()
                        # Send donation confirmation email
                        try:
                            from authentication.utils import (
                                send_donation_confirmation_email,
                                send_new_donation_alert,
                                send_large_donation_alert
                            )
                            user = related_obj.user if hasattr(related_obj, 'user') and related_obj.user else None
                            if user:
                                send_donation_confirmation_email(related_obj, user)
                                send_new_donation_alert(related_obj, user)
                                send_large_donation_alert(related_obj, user, threshold=10000)
                        except Exception as e:
                            print(f"Error sending donation email notifications: {e}")
                    elif model_name == 'futsalbooking':
                        related_obj.status = 'confirmed' # or completed
                        related_obj.save()
                    elif model_name == 'serviceenrollment':
                        related_obj.status = 'confirmed'
                        related_obj.payment_status = 'paid'
                        related_obj.save()
            
            return Response(status=status.HTTP_200_OK)

        except Transaction.DoesNotExist:
            logger.error(f"Transaction not found for webhook: {tx_ref}")
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Webhook error: {str(e)}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyPaymentView(views.APIView):
    permission_classes = [permissions.AllowAny] # Allow frontend to verify without auth if just checking by ref (or make precise)

    def get(self, request, tx_ref):
        try:
            transaction = Transaction.objects.get(tx_ref=tx_ref)
            
            # If already success, return
            if transaction.status == 'success':
                return Response({'status': 'success', 'data': {'status': 'success'}})
            
            # Otherwise, verify with Chapa
            verification = ChapaService.verify_payment(tx_ref)
            if verification and verification.get('status') == 'success' and verification['data']['status'] == 'success':
                transaction.status = 'success'
                transaction.chapa_reference = verification['data'].get('reference', '')
                transaction.save()
                
                # Update related object
                related_obj = transaction.content_object
                if related_obj:
                    # Generic handling 
                    model_name = related_obj._meta.model_name
                    if model_name == 'donation':
                        related_obj.status = 'completed'
                        related_obj.save()
                        # Send donation confirmation email
                        try:
                            from authentication.utils import (
                                send_donation_confirmation_email,
                                send_new_donation_alert,
                                send_large_donation_alert
                            )
                            user = related_obj.user if hasattr(related_obj, 'user') and related_obj.user else None
                            if user:
                                send_donation_confirmation_email(related_obj, user)
                                send_new_donation_alert(related_obj, user)
                                send_large_donation_alert(related_obj, user, threshold=10000)
                        except Exception as e:
                            print(f"Error sending donation email notifications: {e}")
                    elif model_name == 'futsalbooking':
                        related_obj.status = 'confirmed'
                        related_obj.save()
                    elif model_name == 'serviceenrollment':
                        related_obj.status = 'confirmed'
                        related_obj.payment_status = 'paid'
                        related_obj.save()
                
                return Response({'status': 'success', 'data': verification['data']})
            else:
                return Response({'status': 'failed', 'message': 'Payment not verified'}, status=status.HTTP_400_BAD_REQUEST)

        except Transaction.DoesNotExist:
            return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)

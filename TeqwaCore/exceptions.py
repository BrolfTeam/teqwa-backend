from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError, DatabaseError
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Custom exception handler that intercepts standard Python exceptions
    and returns them as structured JSON responses.
    """
    # Call REST framework's default exception handler first to handle explicit APIExceptions
    response = exception_handler(exc, context)

    # If response is None, then there's an unhandled exception (like a standard Python error)
    if response is None:
        if isinstance(exc, IntegrityError):
            data = {
                'error': 'Database integrity error',
                'detail': str(exc)
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        
        if isinstance(exc, DatabaseError):
            data = {
                'error': 'Database error', 
                'detail': 'A database error occurred.'
            }
            # Log the actual error for admins to see
            logger.error(f"Database Error: {exc}", exc_info=True)
            return Response(data, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Catch-all for other unhandled exceptions (KeyError, ValueError, etc.)
        logger.error(f"Unhandled Exception: {exc}", exc_info=True)
        data = {
            'error': 'Internal Server Error',
            'detail': 'An unexpected error occurred. Please contact support.'
        }
        return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response

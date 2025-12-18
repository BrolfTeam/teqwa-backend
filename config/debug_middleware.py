"""
Debug middleware to log request details for troubleshooting ALLOWED_HOSTS issues.
"""
import json
import os
import time
from django.conf import settings

log_path = '/tmp/debug.log'  # Use /tmp for easier access in container

# #region agent log
try:
    with open(log_path, 'a') as f:
        f.write(json.dumps({
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'A',
            'location': 'debug_middleware.py:init',
            'message': 'Debug middleware loaded',
            'data': {'ALLOWED_HOSTS': getattr(settings, 'ALLOWED_HOSTS', [])},
            'timestamp': int(time.time() * 1000)
        }) + '\n')
except Exception:
    pass
# #endregion

class DebugMiddleware:
    """Middleware to log request details for debugging."""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # #region agent log
        try:
            # Get host from raw headers before get_host() which may raise DisallowedHost
            host_header = request.META.get('HTTP_HOST', '')
            host_from_meta = request.META.get('SERVER_NAME', '')
            # Also check X-Forwarded-Host
            forwarded_host = request.META.get('HTTP_X_FORWARDED_HOST', '')
            path = request.path
            allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
            
            # Extract host without port for comparison
            host_header_no_port = host_header.split(':')[0] if host_header else ''
            
            # Try to get host normally, but catch DisallowedHost
            try:
                host = request.get_host()
                host_no_port = host.split(':')[0] if ':' in host else host
            except Exception as e:
                host = f"ERROR: {type(e).__name__}: {str(e)}"
                host_no_port = host_header_no_port
            
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'post-fix',
                    'hypothesisId': 'A',
                    'location': 'debug_middleware.py:__call__:before',
                    'message': 'Request received',
                    'data': {
                        'HTTP_HOST_header': host_header,
                        'HTTP_HOST_no_port': host_header_no_port,
                        'SERVER_NAME': host_from_meta,
                        'X_FORWARDED_HOST': forwarded_host,
                        'get_host_result': host,
                        'get_host_no_port': host_no_port,
                        'path': path,
                        'method': request.method,
                        'ALLOWED_HOSTS': allowed_hosts,
                        'host_header_in_allowed': host_header in allowed_hosts,
                        'host_header_no_port_in_allowed': host_header_no_port in allowed_hosts,
                        'host_from_meta_in_allowed': host_from_meta in allowed_hosts,
                        'all_meta_headers': {k: v for k, v in request.META.items() if 'HOST' in k.upper()}
                    },
                    'timestamp': int(time.time() * 1000)
                }) + '\n')
        except Exception as e:
            try:
                with open(log_path, 'a') as f:
                    f.write(json.dumps({
                        'sessionId': 'debug-session',
                        'runId': 'post-fix',
                        'hypothesisId': 'A',
                        'location': 'debug_middleware.py:__call__:log_error',
                        'message': 'Error logging request',
                        'data': {'error': str(e)},
                        'timestamp': int(time.time() * 1000)
                    }) + '\n')
            except Exception:
                pass
        # #endregion
        
        try:
            response = self.get_response(request)
            # #region agent log
            try:
                with open(log_path, 'a') as f:
                    f.write(json.dumps({
                        'sessionId': 'debug-session',
                        'runId': 'post-fix',
                        'hypothesisId': 'A',
                        'location': 'debug_middleware.py:__call__:after',
                        'message': 'Response generated',
                        'data': {
                            'status_code': response.status_code,
                            'path': request.path
                        },
                        'timestamp': int(time.time() * 1000)
                    }) + '\n')
            except Exception:
                pass
            # #endregion
            return response
        except Exception as e:
            # #region agent log
            try:
                with open(log_path, 'a') as f:
                    f.write(json.dumps({
                        'sessionId': 'debug-session',
                        'runId': 'post-fix',
                        'hypothesisId': 'A',
                        'location': 'debug_middleware.py:__call__:exception',
                        'message': 'Exception raised',
                        'data': {
                            'exception_type': type(e).__name__,
                            'exception_message': str(e),
                            'path': request.path,
                            'host': request.get_host()
                        },
                        'timestamp': int(time.time() * 1000)
                    }) + '\n')
            except Exception:
                pass
            # #endregion
            raise

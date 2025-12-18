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
            host = request.get_host()
            path = request.path
            allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'A',
                    'location': 'debug_middleware.py:__call__:before',
                    'message': 'Request received',
                    'data': {
                        'host': host,
                        'path': path,
                        'method': request.method,
                        'ALLOWED_HOSTS': allowed_hosts,
                        'host_in_allowed': host in allowed_hosts or '*' in allowed_hosts
                    },
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
                        'runId': 'run1',
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
                        'runId': 'run1',
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

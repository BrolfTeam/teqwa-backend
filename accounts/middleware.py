from django.utils.deprecation import MiddlewareMixin
from django.contrib.sessions.models import Session
from django.utils import timezone
from .models import UserSession, UserActivity


class UserSessionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated and hasattr(request, 'session'):
            session_key = request.session.session_key
            if session_key:
                try:
                    session = Session.objects.get(session_key=session_key)
                    user_session, created = UserSession.objects.get_or_create(
                        session=session,
                        defaults={
                            'user': request.user,
                            'ip_address': self.get_client_ip(request),
                            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                            'device_info': self.get_device_info(request),
                        }
                    )
                    if not created:
                        user_session.last_activity = timezone.now()
                        user_session.save()
                except Session.DoesNotExist:
                    pass
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_device_info(self, request):
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        return {
            'user_agent': user_agent,
            'is_mobile': 'Mobile' in user_agent,
            'is_tablet': 'Tablet' in user_agent,
        }
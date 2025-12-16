from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """API root endpoint with available endpoints"""
    return Response({
        'message': 'Welcome to Teqwa Project API',
        'version': '1.0.0',
        'endpoints': {
            'authentication': {
                'login': '/api/v1/auth/login/',
                'register': '/api/v1/auth/register/',
                'logout': '/api/v1/auth/logout/',
                'profile': '/api/v1/auth/profile/',
                'update_profile': '/api/v1/auth/profile/update/',
                'refresh': '/api/v1/auth/refresh/',
                'password_reset_request': '/api/v1/auth/password-reset/request/',
                'password_reset_confirm': '/api/v1/auth/password-reset/confirm/',
                'verify_email': '/api/v1/auth/verify-email/',
                'resend_verification': '/api/v1/auth/resend-verification/',
                'change_password': '/api/v1/auth/change-password/'
            },
            'accounts': {
                'profile': '/api/v1/accounts/profile/',
                'update_profile': '/api/v1/accounts/profile/update/',
                'sessions': '/api/v1/accounts/sessions/',
                'activities': '/api/v1/accounts/activities/',
                'change_password': '/api/v1/accounts/change-password/'
            },
            'announcements': {
                'list': '/api/v1/announcements/',
                'create': '/api/v1/announcements/create/',
                'detail': '/api/v1/announcements/{id}/'
            },
            'events': {
                'list': '/api/v1/events/',
                'create': '/api/v1/events/create/',
                'upcoming': '/api/v1/events/?upcoming=true',
                'detail': '/api/v1/events/{id}/',
                'register': '/api/v1/events/{id}/register/',
                'unregister': '/api/v1/events/{id}/unregister/',
                'attendees': '/api/v1/events/{id}/attendees/'
            },
            'education': {
                'list': '/api/v1/education/',
                'create': '/api/v1/education/create/',
                'detail': '/api/v1/education/{id}/',
                'enroll': '/api/v1/education/{id}/book/',
                'my_enrollments': '/api/v1/education/my-bookings/',
                'all_enrollments': '/api/v1/education/bookings/',
                'update_enrollment_status': '/api/v1/education/bookings/{enrollment_id}/status/',
                'lectures': '/api/v1/education/lectures/',
                'lecture_detail': '/api/v1/education/lectures/{id}/',
                'types': '/api/v1/education/?type=daily_qirat'
            },
            'futsal': {
                'slots': '/api/v1/futsal/slots/',
                'book': '/api/v1/futsal/slots/{id}/book/',
                'my_bookings': '/api/v1/futsal/my-bookings/',
                'all_bookings': '/api/v1/futsal/bookings/'
            },
            'donations': {
                'list': '/api/v1/donations/',
                'create': '/api/v1/donations/create/',
                'causes': '/api/v1/donations/causes/',
                'cause_detail': '/api/v1/donations/causes/{id}/',
                'create_cause': '/api/v1/donations/causes/create/',
                'stats': '/api/v1/donations/stats/'
            },
            'staff': {
                'list': '/api/v1/staff/',
                'detail': '/api/v1/staff/{id}/',
                'attendance': '/api/v1/staff/attendance/',
                'toggle_attendance': '/api/v1/staff/attendance/toggle/',
                'working_hours': '/api/v1/staff/working-hours/',
                'tasks': '/api/v1/staff/tasks/',
                'reports': '/api/v1/staff/reports/'
            },
            'prayer_times': {
                'current': '/api/v1/prayer-times/current/',
                'monthly': '/api/v1/prayer-times/monthly/{year}/{month}/',
                'qibla': '/api/v1/prayer-times/qibla/'
            },
            'itikaf': {
                'list': '/api/v1/itikaf/',
                'create': '/api/v1/itikaf/create/',
                'detail': '/api/v1/itikaf/{id}/',
                'register': '/api/v1/itikaf/{id}/register/',
                'unregister': '/api/v1/itikaf/{id}/unregister/',
                'my_registrations': '/api/v1/itikaf/my-registrations/',
                'participants': '/api/v1/itikaf/{id}/participants/',
                'schedules': '/api/v1/itikaf/{id}/schedules/',
                'create_schedule': '/api/v1/itikaf/{id}/schedules/create/',
                'update_registration_status': '/api/v1/itikaf/registrations/{registration_id}/status/'
            }
        },
        'documentation': '/api/docs/',
        'admin': '/admin/'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint"""
    return Response({
        'status': 'healthy',
        'message': 'Teqwa Project API is running'
    })
"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.http import JsonResponse

# Simple health check view
def health_check(request):
    return JsonResponse({'status': 'healthy', 'service': 'teqwa-backend'})

# Root view redirecting to API docs
def root_view(request):
    return JsonResponse({
        'message': 'Welcome to Teqwa Project API',
        'documentation': '/api/docs/',
        'api': '/api/v1/',
        'health': '/health/',
        'admin': '/admin/'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Root and health endpoints
    path('', root_view, name='index'),
    path('health/', health_check, name='health'),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # API root
    path('api/v1/', include('TeqwaCore.urls')),
    
    # API endpoints
    path('api/v1/auth/', include('authentication.urls')),
    path('api/v1/accounts/', include('accounts.urls')),
    path('api/v1/announcements/', include('announcements.urls')),
    path('api/v1/events/', include('events.urls')),
    path('api/v1/education/', include('education.urls')),
    path('api/v1/futsal/', include('futsal_booking.urls')),
    path('api/v1/payments/', include('payments.urls')),
    path('api/v1/donations/', include('donations.urls')),
    path('api/v1/staff/', include('staff.urls')),
    path('api/v1/itikaf/', include('itikaf.urls')),
    path('api/v1/contact/', include('contact.urls')),
    path('api/v1/memberships/', include('memberships.urls')),
    path('api/v1/students/', include('students.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

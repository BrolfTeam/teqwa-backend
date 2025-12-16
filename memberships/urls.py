from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MembershipTierViewSet, UserMembershipViewSet

router = DefaultRouter()
router.register(r'tiers', MembershipTierViewSet)
router.register(r'my-membership', UserMembershipViewSet, basename='my-membership')

urlpatterns = [
    path('', include(router.urls)),
]

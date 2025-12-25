from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import MembershipTier, UserMembership
from .serializers import MembershipTierSerializer, UserMembershipSerializer

class MembershipTierViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List and retrieve membership tiers.
    """
    queryset = MembershipTier.objects.filter(is_active=True)
    serializer_class = MembershipTierSerializer
    permission_classes = [permissions.AllowAny]


class UserMembershipViewSet(viewsets.ModelViewSet):
    """
    Manage user memberships.
    """
    serializer_class = UserMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        return UserMembership.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        # Check if user already has a membership record
        try:
            membership = UserMembership.objects.get(user=request.user)
            # If exists, we update it instead of creating new
            serializer = self.get_serializer(membership, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            
            # Reset status to pending for new subscription attempt
            serializer.save(status='pending')
            
            return Response(serializer.data)
        except UserMembership.DoesNotExist:
            return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, status='pending')

    @action(detail=False, methods=['get'])
    def current(self, request):
        """
        Get the current active membership for the user.
        """
        membership = self.get_queryset().filter(status='active').first()
        if membership:
            serializer = self.get_serializer(membership)
            return Response(serializer.data)
        # Return 200 with null instead of 404 to avoid console errors
        return Response(None)

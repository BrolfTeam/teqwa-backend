from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Sum
from .models import Donation, DonationCause
from .serializers import DonationSerializer, DonationCauseSerializer
from authentication.utils import (
    send_donation_confirmation_email,
    send_new_donation_alert,
    send_large_donation_alert
)


@api_view(['GET'])
@permission_classes([AllowAny])
def donation_list(request):
    """List donations (Admin only for full list, public for stats)"""
    if request.user.is_authenticated and request.user.role == 'admin':
        donations = Donation.objects.all()
        serializer = DonationSerializer(donations, many=True)
        return Response({
            'message': 'Donations retrieved successfully',
            'data': serializer.data,
            'count': donations.count()
        })
    else:
        # Public stats only
        completed_donations = Donation.objects.filter(status='completed')
        total_amount = completed_donations.aggregate(Sum('amount'))['amount__sum'] or 0
        
        return Response({
            'message': 'Donation statistics retrieved successfully',
            'data': {
                'total_amount': float(total_amount),
                'total_donations': completed_donations.count(),
                'currency': 'USD'
            }
        })


@api_view(['POST'])
@permission_classes([AllowAny])
def create_donation(request):
    """Create a new donation"""
    serializer = DonationSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        donation = serializer.save()
        
        # Send email notifications (for completed donations or if user exists)
        user = donation.user if hasattr(donation, 'user') and donation.user else None
        
        if donation.status == 'completed':
            # Send confirmation email to donor (user or anonymous)
            try:
                send_donation_confirmation_email(donation, user)
            except Exception as e:
                print(f"Error sending donation confirmation email: {e}")
            
            # Send admin alert for completed donations
            try:
                send_new_donation_alert(donation, user)
                send_large_donation_alert(donation, user, threshold=10000)
            except Exception as e:
                print(f"Error sending admin donation alert: {e}")
        else:
            # Send admin alert for pending donations
            try:
                send_new_donation_alert(donation, user)
            except Exception as e:
                print(f"Error sending admin donation alert: {e}")
        
        return Response({
            'message': 'Donation created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def donation_causes(request):
    """List donation causes"""
    active_only = request.GET.get('active', '').lower() == 'true'

    causes = DonationCause.objects.all()
    if active_only:
        causes = causes.filter(status='active')

    serializer = DonationCauseSerializer(causes, many=True, context={'request': request})
    return Response({
        'message': 'Donation causes retrieved successfully',
        'data': serializer.data,
        'count': causes.count()
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def cause_detail(request, cause_id):
    """Get specific donation cause"""
    try:
        cause = DonationCause.objects.get(pk=cause_id)
    except DonationCause.DoesNotExist:
        return Response({
            'error': 'Donation cause not found'
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = DonationCauseSerializer(cause, context={'request': request})
    data = serializer.data
    
    # Add recent donations for this cause
    recent_donations = Donation.objects.filter(
        cause=cause, 
        status='completed'
    ).order_by('-created_at')[:5]
    
    data['recent_donations'] = DonationSerializer(recent_donations, many=True).data
    
    return Response({
        'message': 'Donation cause retrieved successfully',
        'data': data
    })


from accounts.models import UserActivity

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_cause(request):
    """Create new donation cause (Admin only)"""
    if request.user.role != 'admin':
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = DonationCauseSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        cause = serializer.save()
        
        # Log activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='admin_action',
            description=f'Created new donation cause: {cause.title}',
            metadata={'source': 'donations', 'id': cause.id}
        )
        
        return Response({
            'message': 'Donation cause created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def donation_stats(request):
    """Get donation statistics (Admin/Staff only)"""
    if request.user.role not in ['admin', 'staff']:
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    completed_donations = Donation.objects.filter(status='completed')
    pending_donations = Donation.objects.filter(status='pending')
    
    total_completed = completed_donations.aggregate(Sum('amount'))['amount__sum'] or 0
    total_pending = pending_donations.aggregate(Sum('amount'))['amount__sum'] or 0
    
    stats = {
        'total_completed': completed_donations.count(),
        'total_pending': pending_donations.count(),
        'total_amount_completed': float(total_completed),
        'total_amount_pending': float(total_pending),
        'average_donation': float(total_completed) / completed_donations.count() if completed_donations.count() > 0 else 0,
        'currency': 'USD'
    }
    
    return Response({
        'message': 'Donation statistics retrieved successfully',
        'data': stats
    })
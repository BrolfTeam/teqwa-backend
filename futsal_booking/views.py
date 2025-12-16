from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils import timezone
from .models import FutsalSlot, FutsalBooking
from .serializers import FutsalSlotSerializer, FutsalBookingSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def slot_list(request):
    """List futsal slots for a specific date"""
    date = request.GET.get('date', timezone.now().date())
    available_only = request.GET.get('available', '').lower() == 'true'
    
    slots = FutsalSlot.objects.filter(date=date)
    
    if available_only:
        slots = slots.filter(available=True)
    
    serializer = FutsalSlotSerializer(slots, many=True)
    return Response({
        'message': 'Futsal slots retrieved successfully',
        'data': serializer.data,
        'count': slots.count()
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def slot_detail(request, pk):
    """Get specific futsal slot"""
    try:
        slot = FutsalSlot.objects.get(pk=pk)
    except FutsalSlot.DoesNotExist:
        return Response({
            'error': 'Futsal slot not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = FutsalSlotSerializer(slot)
    return Response({
        'message': 'Futsal slot retrieved successfully',
        'data': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def book_slot(request, pk):
    """Book a futsal slot"""
    try:
        slot = FutsalSlot.objects.get(pk=pk)
    except FutsalSlot.DoesNotExist:
        return Response({
            'error': 'Futsal slot not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if not slot.available:
        return Response({
            'error': 'Slot is not available'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if FutsalBooking.objects.filter(slot=slot, user=request.user, status__in=['pending', 'confirmed']).exists():
        return Response({
            'error': 'You already have a booking for this slot'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    booking_data = request.data.copy()
    booking_data['slot'] = pk
    
    serializer = FutsalBookingSerializer(data=booking_data, context={'request': request})
    
    if serializer.is_valid():
        booking = serializer.save()
        # Mark slot as unavailable
        slot.available = False
        slot.save()
        
        return Response({
            'message': 'Futsal slot booked successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_bookings(request):
    """Get user's futsal bookings"""
    bookings = FutsalBooking.objects.filter(user=request.user).select_related('slot')
    serializer = FutsalBookingSerializer(bookings, many=True)
    
    return Response({
        'message': 'Your bookings retrieved successfully',
        'data': serializer.data,
        'count': bookings.count()
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_bookings(request):
    """Get all futsal bookings (Admin/Staff only)"""
    if request.user.role not in ['admin', 'staff']:
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    date = request.GET.get('date', '')
    status_filter = request.GET.get('status', '')
    
    bookings = FutsalBooking.objects.select_related('slot', 'user').all()
    
    if date:
        bookings = bookings.filter(slot__date=date)
    
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    serializer = FutsalBookingSerializer(bookings, many=True)
    
    return Response({
        'message': 'All bookings retrieved successfully',
        'data': serializer.data,
        'count': bookings.count()
    })


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_booking_status(request, booking_id):
    """Update booking status (Admin/Staff only)"""
    if request.user.role not in ['admin', 'staff']:
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        booking = FutsalBooking.objects.get(pk=booking_id)
    except FutsalBooking.DoesNotExist:
        return Response({
            'error': 'Booking not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = FutsalBookingSerializer(booking, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        
        # Update slot availability based on booking status
        if booking.status == 'cancelled':
            booking.slot.available = True
            booking.slot.save()
        elif booking.status in ['confirmed', 'pending']:
            booking.slot.available = False
            booking.slot.save()
        
        return Response({
            'message': 'Booking status updated successfully',
            'data': serializer.data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from accounts.models import UserActivity

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_slot(request):
    """Create new futsal slot (Admin/Staff only)"""
    if request.user.role not in ['admin', 'staff']:
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = FutsalSlotSerializer(data=request.data)
    if serializer.is_valid():
        slot = serializer.save()
        
        # Log activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='admin_action',
            description=f'Created futsal slot for {slot.date} at {slot.start_time}',
            metadata={'source': 'futsal', 'id': slot.id}
        )
        
        return Response({
            'message': 'Futsal slot created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
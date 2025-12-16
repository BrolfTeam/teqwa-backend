from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import Event, EventRegistration
from .serializers import EventSerializer, EventRegistrationSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def event_list(request):
    """List all events"""
    status_filter = request.GET.get('status', '')
    upcoming_only = request.GET.get('upcoming', '').lower() == 'true'
    
    events = Event.objects.all()
    
    if status_filter:
        events = events.filter(status=status_filter)
    
    if upcoming_only:
        events = events.filter(status='upcoming')
    
    serializer = EventSerializer(events, many=True, context={'request': request})
    return Response({
        'message': 'Events retrieved successfully',
        'data': serializer.data,
        'count': events.count()
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def event_detail(request, pk):
    """Get specific event"""
    try:
        event = Event.objects.get(pk=pk)
    except Event.DoesNotExist:
        return Response({
            'error': 'Event not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = EventSerializer(event, context={'request': request})
    return Response({
        'message': 'Event retrieved successfully',
        'data': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def create_event(request):
    """Create new event (Admin/Staff only)"""
    if request.user.role not in ['admin', 'staff']:
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = EventSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Event created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_for_event(request, pk):
    """Register user for event"""
    try:
        event = Event.objects.get(pk=pk)
    except Event.DoesNotExist:
        return Response({
            'error': 'Event not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Check if user already registered
    if EventRegistration.objects.filter(event=event, user=request.user).exists():
        return Response({
            'error': 'Already registered for this event'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check capacity
    if event.attendee_count >= event.capacity:
        return Response({
            'error': 'Event is full'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    registration = EventRegistration.objects.create(
        event=event,
        user=request.user,
        status='confirmed'
    )
    
    # Send registration confirmation email
    try:
        send_event_registration_email(event, request.user, registration)
    except Exception as e:
        print(f"Error sending event registration email: {e}")
    
    serializer = EventRegistrationSerializer(registration)
    return Response({
        'message': 'Successfully registered for event',
        'data': serializer.data
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unregister_from_event(request, pk):
    """Unregister user from event"""
    try:
        event = Event.objects.get(pk=pk)
        registration = EventRegistration.objects.get(event=event, user=request.user)
        registration.delete()
        return Response({
            'message': 'Successfully unregistered from event'
        })
    except (Event.DoesNotExist, EventRegistration.DoesNotExist):
        return Response({
            'error': 'Registration not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def event_attendees(request, pk):
    """Get event attendees (Staff/Admin only)"""
    if request.user.role not in ['admin', 'staff']:
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        event = Event.objects.get(pk=pk)
    except Event.DoesNotExist:
        return Response({
            'error': 'Event not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    registrations = EventRegistration.objects.filter(event=event)
    serializer = EventRegistrationSerializer(registrations, many=True)
    
    return Response({
        'message': 'Event attendees retrieved successfully',
        'data': serializer.data,
        'count': registrations.count()
    })
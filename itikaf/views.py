from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.utils import timezone
from .models import ItikafProgram, ItikafSchedule, ItikafRegistration
from .serializers import (
    ItikafProgramSerializer, 
    ItikafScheduleSerializer,
    ItikafRegistrationSerializer,
    ItikafRegistrationCreateSerializer
)
from authentication.utils import send_itikaf_approval_email


@api_view(['GET'])
@permission_classes([AllowAny])
def program_list(request):
    """List all Iʿtikāf programs"""
    status_filter = request.GET.get('status', '')
    upcoming_only = request.GET.get('upcoming', '').lower() == 'true'
    
    programs = ItikafProgram.objects.all()
    
    if status_filter:
        programs = programs.filter(status=status_filter)
    
    if upcoming_only:
        programs = programs.filter(status='upcoming', start_date__gte=timezone.now())
    
    serializer = ItikafProgramSerializer(programs, many=True, context={'request': request})
    return Response({
        'message': 'Iʿtikāf programs retrieved successfully',
        'data': serializer.data,
        'count': programs.count()
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def program_detail(request, pk):
    """Get specific Iʿtikāf program"""
    try:
        program = ItikafProgram.objects.get(pk=pk)
    except ItikafProgram.DoesNotExist:
        return Response({
            'error': 'Iʿtikāf program not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ItikafProgramSerializer(program, context={'request': request})
    return Response({
        'message': 'Iʿtikāf program retrieved successfully',
        'data': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def create_program(request):
    """Create new Iʿtikāf program (Admin/Staff only)"""
    if request.user.role not in ['admin', 'staff']:
        return Response({
            'error': 'Permission denied. Only admin and staff can create programs.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = ItikafProgramSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Iʿtikāf program created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def program_schedules(request, pk):
    """Get schedules for a specific Iʿtikāf program"""
    try:
        program = ItikafProgram.objects.get(pk=pk)
    except ItikafProgram.DoesNotExist:
        return Response({
            'error': 'Iʿtikāf program not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    schedules = program.schedules.all()
    serializer = ItikafScheduleSerializer(schedules, many=True)
    
    return Response({
        'message': 'Schedules retrieved successfully',
        'data': serializer.data,
        'count': schedules.count()
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_for_program(request, pk):
    """Register user for Iʿtikāf program"""
    try:
        program = ItikafProgram.objects.get(pk=pk)
    except ItikafProgram.DoesNotExist:
        return Response({
            'error': 'Iʿtikāf program not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Check if registration is open
    if not program.is_registration_open:
        return Response({
            'error': 'Registration is closed for this program'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if user already registered
    if ItikafRegistration.objects.filter(program=program, user=request.user).exists():
        return Response({
            'error': 'You are already registered for this program'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check capacity
    if program.is_full:
        # Add to waitlist
        registration = ItikafRegistration.objects.create(
            program=program,
            user=request.user,
            status='waitlisted',
            emergency_contact=request.data.get('emergency_contact', ''),
            emergency_phone=request.data.get('emergency_phone', ''),
            special_requirements=request.data.get('special_requirements', ''),
            notes=request.data.get('notes', ''),
            payment_amount=program.fee
        )
        
        # Send waitlist notification email
        try:
            send_itikaf_approval_email(registration, program, request.user, status='waitlisted')
        except Exception as e:
            print(f"Error sending iʿtikāf waitlist email: {e}")
        
        serializer = ItikafRegistrationSerializer(registration)
        return Response({
            'message': 'Program is full. You have been added to the waitlist.',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    # Create registration
    registration_data = {
        'program': program.id,
        'emergency_contact': request.data.get('emergency_contact', ''),
        'emergency_phone': request.data.get('emergency_phone', ''),
        'special_requirements': request.data.get('special_requirements', ''),
        'notes': request.data.get('notes', ''),
    }
    
    serializer = ItikafRegistrationCreateSerializer(data=registration_data)
    if serializer.is_valid():
        registration = serializer.save(
            user=request.user,
            status='confirmed',
            payment_amount=program.fee
        )
        registration.confirmed_at = timezone.now()
        registration.save()
        
        result_serializer = ItikafRegistrationSerializer(registration)
        
        # Send registration confirmation email (status will be 'confirmed' or 'waitlisted')
        try:
            send_itikaf_approval_email(registration, program, request.user, status=registration.status)
        except Exception as e:
            print(f"Error sending iʿtikāf registration email: {e}")
        
        return Response({
            'message': 'Successfully registered for Iʿtikāf program',
            'data': result_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_registration_status(request, registration_id):
    """Update registration status (Admin/Staff only)"""
    if request.user.role not in ['admin', 'staff']:
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        registration = ItikafRegistration.objects.get(pk=registration_id)
    except ItikafRegistration.DoesNotExist:
        return Response({
            'error': 'Registration not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    old_status = registration.status
    new_status = request.data.get('status', old_status)
    
    if new_status not in ['pending', 'confirmed', 'waitlisted', 'cancelled']:
        return Response({
            'error': 'Invalid status'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    registration.status = new_status
    if new_status == 'confirmed' and not registration.confirmed_at:
        registration.confirmed_at = timezone.now()
    elif new_status == 'cancelled' and not registration.cancelled_at:
        registration.cancelled_at = timezone.now()
    registration.save()
    
    # Send email notification if status changed
    if old_status != new_status:
        try:
            send_itikaf_approval_email(registration, registration.program, registration.user, status=new_status)
        except Exception as e:
            print(f"Error sending iʿtikāf status change email: {e}")
    
    serializer = ItikafRegistrationSerializer(registration)
    return Response({
        'message': f'Registration status updated to {new_status}',
        'data': serializer.data
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unregister_from_program(request, pk):
    """Unregister user from Iʿtikāf program"""
    try:
        program = ItikafProgram.objects.get(pk=pk)
        registration = ItikafRegistration.objects.get(program=program, user=request.user)
        
        # Update status to cancelled
        registration.status = 'cancelled'
        registration.cancelled_at = timezone.now()
        registration.save()
        
        return Response({
            'message': 'Successfully unregistered from Iʿtikāf program'
        })
    except (ItikafProgram.DoesNotExist, ItikafRegistration.DoesNotExist):
        return Response({
            'error': 'Registration not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_registrations(request):
    """Get current user's Iʿtikāf registrations"""
    registrations = ItikafRegistration.objects.filter(user=request.user)
    serializer = ItikafRegistrationSerializer(registrations, many=True)
    
    return Response({
        'message': 'Your registrations retrieved successfully',
        'data': serializer.data,
        'count': registrations.count()
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def program_participants(request, pk):
    """Get program participants (Staff/Admin only)"""
    if request.user.role not in ['admin', 'staff']:
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        program = ItikafProgram.objects.get(pk=pk)
    except ItikafProgram.DoesNotExist:
        return Response({
            'error': 'Iʿtikāf program not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    registrations = ItikafRegistration.objects.filter(program=program)
    serializer = ItikafRegistrationSerializer(registrations, many=True)
    
    return Response({
        'message': 'Program participants retrieved successfully',
        'data': serializer.data,
        'count': registrations.count()
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_schedule(request, pk):
    """Create schedule for Iʿtikāf program (Admin/Staff only)"""
    if request.user.role not in ['admin', 'staff']:
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        program = ItikafProgram.objects.get(pk=pk)
    except ItikafProgram.DoesNotExist:
        return Response({
            'error': 'Iʿtikāf program not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    schedule_data = request.data.copy()
    schedule_data['program'] = program.id
    
    serializer = ItikafScheduleSerializer(data=schedule_data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Schedule created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

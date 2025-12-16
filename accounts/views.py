from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.db.models import Sum
from .models import UserProfile, UserSession, UserActivity
from .serializers import (
    UserDetailSerializer, UserProfileSerializer, UpdateProfileSerializer,
    UserSessionSerializer, UserActivitySerializer
)
from donations.models import Donation
from events.models import Event
from events.serializers import EventSerializer
from donations.serializers import DonationSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_list(request):
    """List all users (Admin only)"""
    if request.user.role != 'admin':
        return Response(
            {'error': 'Permission denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    users = User.objects.all().order_by('-date_joined')
    serializer = UserDetailSerializer(users, many=True)
    
    return Response({
        'message': 'Users retrieved successfully',
        'data': serializer.data,
        'count': users.count()
    })


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def user_detail(request, pk):
    """Get, update, or delete a user (Admin only)"""
    if request.user.role != 'admin':
        return Response(
            {'error': 'Permission denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = UserDetailSerializer(user)
        return Response({
            'message': 'User retrieved successfully',
            'data': serializer.data
        })
    
    elif request.method in ['PUT', 'PATCH']:
        serializer = UserDetailSerializer(user, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'User updated successfully',
                'data': serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        # Prevent deleting yourself
        if user.id == request.user.id:
            return Response(
                {'error': 'Cannot delete your own account'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.delete()
        return Response(
            {'message': 'User deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get user profile with detailed information"""
    serializer = UserDetailSerializer(request.user)
    return Response({
        'message': 'User profile retrieved successfully',
        'data': serializer.data
    })


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update user profile"""
    serializer = UpdateProfileSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        
        # Log activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='profile_update',
            description='User updated their profile',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            metadata={'updated_fields': list(request.data.keys())}
        )
        
        return Response({
            'message': 'Profile updated successfully',
            'data': UserDetailSerializer(request.user).data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_sessions(request):
    """Get user's active sessions"""
    sessions = UserSession.objects.filter(user=request.user, is_active=True)
    serializer = UserSessionSerializer(sessions, many=True)
    
    return Response({
        'message': 'User sessions retrieved successfully',
        'data': serializer.data,
        'count': sessions.count()
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def terminate_session(request, session_id):
    """Terminate a specific session"""
    try:
        user_session = UserSession.objects.get(id=session_id, user=request.user)
        user_session.is_active = False
        user_session.save()
        
        # Also delete the Django session
        try:
            user_session.session.delete()
        except:
            pass
        
        return Response({
            'message': 'Session terminated successfully'
        })
    except UserSession.DoesNotExist:
        return Response({
            'error': 'Session not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def terminate_all_sessions(request):
    """Terminate all user sessions except current"""
    current_session_key = request.session.session_key
    
    user_sessions = UserSession.objects.filter(user=request.user, is_active=True)
    terminated_count = 0
    
    for user_session in user_sessions:
        if user_session.session.session_key != current_session_key:
            user_session.is_active = False
            user_session.save()
            try:
                user_session.session.delete()
            except:
                pass
            terminated_count += 1
    
    return Response({
        'message': f'Terminated {terminated_count} sessions successfully'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_activities(request):
    """Get user's activity history"""
    activities = UserActivity.objects.filter(user=request.user)[:50]  # Last 50 activities
    serializer = UserActivitySerializer(activities, many=True)
    
    return Response({
        'message': 'User activities retrieved successfully',
        'data': serializer.data,
        'count': activities.count()
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change user password"""
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')
    
    if not current_password or not new_password:
        return Response({
            'error': 'Both current and new passwords are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not request.user.check_password(current_password):
        return Response({
            'error': 'Current password is incorrect'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if len(new_password) < 8:
        return Response({
            'error': 'New password must be at least 8 characters long'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    request.user.set_password(new_password)
    request.user.save()
    
    # Log activity
    UserActivity.objects.create(
        user=request.user,
        activity_type='profile_update',
        description='User changed their password',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    return Response({
        'message': 'Password changed successfully'
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    """Delete user account (soft delete by deactivating)"""
    password = request.data.get('password')
    
    if not password:
        return Response({
            'error': 'Password confirmation required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not request.user.check_password(password):
        return Response({
            'error': 'Password is incorrect'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Soft delete by deactivating account
    request.user.is_active = False
    request.user.save()
    
    # Log activity
    UserActivity.objects.create(
        user=request.user,
        activity_type='profile_update',
        description='User deactivated their account',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    return Response({
        'message': 'Account deactivated successfully'
    })


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_dashboard_stats(request):
    """Get dashboard statistics based on user role"""
    try:
        user = request.user
        role = user.role or 'visitor'  # Default to visitor if role is None
        
        data = {'role': role}

        # ---------------------------------------------------------
        # ADMIN VIEW: System-wide stats
        # ---------------------------------------------------------
        if role == 'admin':
            try:
                from staff.models import StaffMember
                
                # System Counts
                total_users = User.objects.count()
                total_staff = StaffMember.objects.count()
                
                # System Donations
                total_donations = Donation.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0

                data.update({
                    'counts': {
                        'users': total_users,
                        'staff': total_staff
                    },
                    'reports': {
                        'total_staff': total_staff
                    },
                    'donation_stats': {
                        'total_amount': float(total_donations),
                        'currency': 'ETB'
                    }
                })
            except Exception as e:
                print(f"Error in admin stats: {str(e)}")
                data.update({
                    'counts': {'users': 0, 'staff': 0},
                    'reports': {'total_staff': 0},
                    'donation_stats': {'total_amount': 0, 'currency': 'ETB'}
                })

        # ---------------------------------------------------------
        # STAFF VIEW: Work & Tasks
        # ---------------------------------------------------------
        elif role == 'staff':
            from staff.models import StaffMember, StaffTask, StaffAttendance
            
            try:
                staff_profile = StaffMember.objects.get(user=user)
                
                # Pending Tasks
                pending_tasks = StaffTask.objects.filter(
                    assigned_to=staff_profile, 
                    status__in=['pending', 'in_progress']
                ).count()
                
                # Attendance (This month or week)
                # For simplicity, let's just get total hours tracked ever, or simpler: presence today
                today_attendance = StaffAttendance.objects.filter(
                    staff=staff_profile, 
                    date=timezone.now().date()
                ).first()
                
                status_today = today_attendance.status if today_attendance else 'Absent'
                check_in_time = today_attendance.check_in if today_attendance else None
                
                data.update({
                    'tasks': {
                        'pending': pending_tasks
                    },
                    'attendance': {
                        'status': status_today,
                        'check_in': check_in_time
                    },
                    'counts': {
                         # Reuse structure for generic widgets if needed
                    }
                })
                
            except StaffMember.DoesNotExist:
                 data['error'] = 'Staff profile not found'

        # ---------------------------------------------------------
        # USER VIEW: Personal stats (Default)
        # ---------------------------------------------------------
        else:
            try:
                # 1. Community Points
                points = 0
                if hasattr(user, 'profile'):
                    points = user.profile.community_points
                    
                # 2. Donation Stats
                total_donations = Donation.objects.filter(user=user, status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
                # Show all recent donations so user sees pending ones too
                recent_donations = Donation.objects.filter(user=user).order_by('-created_at')[:5]
                
                # 3. Upcoming Events & Futsal Bookings
                from futsal_booking.models import FutsalBooking
                
                # Fetch Events
                upcoming_events_qs = Event.objects.filter(
                    registrations__user=user,
                    registrations__status__in=['confirmed', 'pending'],
                    status='upcoming', 
                    date__gte=timezone.now()
                )
                
                # Fetch Futsal
                upcoming_futsal_qs = FutsalBooking.objects.filter(
                    user=user,
                    status__in=['confirmed', 'pending', 'paid'], # assuming 'paid' is valid or equivalent to confirmed
                    slot__date__gte=timezone.now().date()
                ).select_related('slot')
                
                # Combine and ensure unique list
                combined_events = []
                
                # Process Events
                for event in upcoming_events_qs:
                    combined_events.append({
                        'id': f"event-{event.id}",
                        'title': event.title,
                        'date': event.date.isoformat(),
                        'location': event.location,
                        'type': 'event'
                    })
                    
                # Process Futsal (manually format since there's no serializer here yet)
                for booking in upcoming_futsal_qs:
                    # Combine date and time for sorting
                    import datetime
                    dt = datetime.datetime.combine(booking.slot.date, booking.slot.start_time)
                    combined_events.append({
                        'id': f"futsal-{booking.id}",
                        'title': f"Futsal: {booking.slot.start_time.strftime('%I:%M %p')}",
                        'date': dt.isoformat(),
                        'location': booking.slot.location,
                        'type': 'futsal'
                    })
                
                # Sort by date
                combined_events.sort(key=lambda x: x['date'])
                
                # Slice logic
                final_upcoming = combined_events[:5]
                upcoming_count = upcoming_events_qs.count() + upcoming_futsal_qs.count()

                data.update({
                    'points': points,
                    'donation_stats': {
                        'total_amount': float(total_donations),
                        'currency': 'ETB'
                    },
                    'counts': {
                         'upcoming_events': upcoming_count
                    },
                    'recent_donations': DonationSerializer(recent_donations, many=True).data,
                    'upcoming_events': final_upcoming
                })
            except Exception as e:
                import traceback
                print(f"Error in user stats: {str(e)}")
                print(traceback.format_exc())
                data.update({
                    'points': 0,
                    'donation_stats': {'total_amount': 0, 'currency': 'ETB'},
                    'counts': {'upcoming_events': 0},
                    'recent_donations': [],
                    'upcoming_events': []
                })
        
        # ---------------------------------------------------------
        # COMMON: Recent Activity (All Roles)
        # ---------------------------------------------------------
        try:
            # We can also merge Futsal/Donations into Activity if not already tracked by signals
            # But let's stick to existing UserActivity model
            recent_activities = UserActivity.objects.filter(user=user).order_by('-timestamp')[:10]
            data['recent_activities'] = UserActivitySerializer(recent_activities, many=True).data
        except Exception as e:
            # If UserActivity doesn't exist or has issues, return empty list
            data['recent_activities'] = []

        # Return appropriate message based on role
        if role == 'admin':
            return Response({'message': 'Admin stats retrieved', 'data': data})
        elif role == 'staff':
            return Response({'message': 'Staff stats retrieved', 'data': data})
        else:
            return Response({'message': 'Dashboard stats retrieved', 'data': data})
    
    except Exception as e:
        import traceback
        print(f"Error in dashboard stats: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': 'Failed to retrieve dashboard stats', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
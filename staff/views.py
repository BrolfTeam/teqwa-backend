from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import StaffMember, StaffAttendance, StaffTask
from .serializers import StaffMemberSerializer, StaffAttendanceSerializer, StaffTaskSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def staff_list(request):
    """List all active staff members"""
    active_only = request.GET.get('active', '').lower() == 'true'
    role_filter = request.GET.get('role', '')
    
    staff = StaffMember.objects.select_related('user').all()
    
    if active_only:
        staff = staff.filter(active=True)
    
    if role_filter:
        staff = staff.filter(role__iexact=role_filter)
    
    serializer = StaffMemberSerializer(staff, many=True)
    data = serializer.data
    
    # Remove sensitive info for public access
    if not (request.user.is_authenticated and request.user.role in ['admin', 'staff']):
        for member in data:
            member.pop('email', None)
            member.pop('phone', None)
    
    return Response({
        'message': 'Staff members retrieved successfully',
        'data': data,
        'count': staff.count()
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def staff_detail(request, pk):
    """Get specific staff member"""
    try:
        staff_member = StaffMember.objects.select_related('user').get(pk=pk)
    except StaffMember.DoesNotExist:
        return Response({
            'error': 'Staff member not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = StaffMemberSerializer(staff_member)
    data = serializer.data
    
    # Remove sensitive info for public access
    if not (request.user.is_authenticated and request.user.role in ['admin', 'staff']):
        data.pop('email', None)
        data.pop('phone', None)
    
    return Response({
        'message': 'Staff member retrieved successfully',
        'data': data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_staff(request):
    """Create new staff member (Admin only)"""
    if request.user.role != 'admin':
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = StaffMemberSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Staff member created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_staff(request, pk):
    """Update staff member (Admin only)"""
    if request.user.role != 'admin':
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        staff_member = StaffMember.objects.get(pk=pk)
    except StaffMember.DoesNotExist:
        return Response({
            'error': 'Staff member not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = StaffMemberSerializer(staff_member, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Staff member updated successfully',
            'data': serializer.data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def staff_attendance(request):
    """Get staff attendance records for a specific date"""
    if request.user.role not in ['admin', 'staff']:
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    from datetime import date
    date_param = request.GET.get('date', date.today())
    
    attendance = StaffAttendance.objects.filter(date=date_param).select_related('staff__user')
    serializer = StaffAttendanceSerializer(attendance, many=True)
    
    return Response({
        'message': 'Attendance records retrieved successfully',
        'data': serializer.data,
        'count': attendance.count()
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_attendance(request):
    """Toggle staff attendance status"""
    if request.user.role not in ['admin', 'staff']:
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    from datetime import date
    staff_id = request.data.get('staff_id')
    date_param = request.data.get('date', date.today())
    
    try:
        if staff_id:
            # Validate staff_id is integer
            try:
                staff_id = int(str(staff_id).strip())
                staff_member = StaffMember.objects.get(id=staff_id)
            except (ValueError, TypeError):
                 return Response({'error': 'Invalid staff ID format'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            staff_member = StaffMember.objects.get(user=request.user)
            
        attendance, created = StaffAttendance.objects.get_or_create(
            staff=staff_member,
            date=date_param,
            defaults={'status': 'present'}
        )
        
        if not created:
            attendance.status = 'absent' if attendance.status == 'present' else 'present'
            attendance.save()
        
        serializer = StaffAttendanceSerializer(attendance)
        return Response({
            'message': 'Attendance updated successfully',
            'data': serializer.data
        })
    except StaffMember.DoesNotExist:
        return Response({
            'error': 'Staff member not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error toggling attendance: {str(e)}")
        return Response({'error': f'Server Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clock_in(request):
    """Clock in staff member"""
    if request.user.role not in ['admin', 'staff']:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    from datetime import date, datetime
    staff_id = request.data.get('staff_id')
    
    try:
        if staff_id:
            staff_member = StaffMember.objects.get(id=staff_id)
        else:
            staff_member = StaffMember.objects.get(user=request.user)

        attendance, created = StaffAttendance.objects.get_or_create(
            staff=staff_member,
            date=date.today(),
            defaults={'status': 'present', 'check_in': datetime.now().time()}
        )
        
        if not created and not attendance.check_in:
            attendance.check_in = datetime.now().time()
            attendance.status = 'present'
            attendance.save()
        
        return Response({
            'message': 'Clocked in successfully',
            'data': StaffAttendanceSerializer(attendance).data
        })
    except StaffMember.DoesNotExist:
        return Response({'error': 'Staff profile not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clock_out(request):
    """Clock out staff member"""
    if request.user.role not in ['admin', 'staff']:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    from datetime import date, datetime, timedelta
    staff_id = request.data.get('staff_id')
    
    try:
        if staff_id:
            staff_member = StaffMember.objects.get(id=staff_id)
        else:
            staff_member = StaffMember.objects.get(user=request.user)

        attendance = StaffAttendance.objects.get(
            staff=staff_member,
            date=date.today()
        )
        
        attendance.check_out = datetime.now().time()
        attendance.status = 'present' # ensure it stays present or completed? Usually present with check_out time implies done.
        
        # Calculate total hours
        if attendance.check_in:
            today_date = date.today()
            # Handle check-in time (TimeField)
            check_in_dt = datetime.combine(today_date, attendance.check_in)
            check_out_dt = datetime.combine(today_date, attendance.check_out)
            
            # Simple diff
            total_seconds = (check_out_dt - check_in_dt).total_seconds()
            if total_seconds > 0:
                 attendance.total_hours = round(total_seconds / 3600, 2)
        
        attendance.save()
        
        return Response({
            'message': 'Clocked out successfully',
            'data': StaffAttendanceSerializer(attendance).data
        })
    except StaffMember.DoesNotExist:
        return Response({'error': 'Staff profile not found'}, status=status.HTTP_404_NOT_FOUND)
    except StaffAttendance.DoesNotExist:
        return Response({'error': 'No clock-in record found for today'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def working_hours(request):
    """Get working hours logs"""
    if request.user.role not in ['admin', 'staff']:
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    staff_id = request.GET.get('staff_id', '')
    attendance = StaffAttendance.objects.select_related('staff__user').filter(
        check_in__isnull=False
    ).order_by('-date')[:20]
    
    if staff_id:
        attendance = attendance.filter(staff_id=staff_id)
    
    serializer = StaffAttendanceSerializer(attendance, many=True)
    
    return Response({
        'message': 'Working hours retrieved successfully',
        'data': serializer.data,
        'count': attendance.count()
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def staff_tasks(request):
    """Get staff tasks"""
    if request.user.role not in ['admin', 'staff']:
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    staff_id = request.GET.get('staff_id', '')
    status_filter = request.GET.get('status', '')
    
    tasks = StaffTask.objects.select_related('assigned_to__user', 'assigned_by').all()
    
    # Staff can only see their own tasks (unless admin)
    if request.user.role == 'staff':
        try:
            staff_member = StaffMember.objects.get(user=request.user)
            tasks = tasks.filter(assigned_to=staff_member)
        except StaffMember.DoesNotExist:
            tasks = tasks.none()
    elif staff_id:
        tasks = tasks.filter(assigned_to_id=staff_id)
    
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    serializer = StaffTaskSerializer(tasks, many=True)
    
    return Response({
        'message': 'Tasks retrieved successfully',
        'data': serializer.data,
        'count': tasks.count()
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task(request):
    """Create new task (Admin only)"""
    if request.user.role != 'admin':
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = StaffTaskSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Task created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_task_status(request, task_id):
    """
    Update task status with state machine logic.
    Actions: accept, start, submit, approve, reject, cancel.
    """
    if request.user.role not in ['admin', 'staff']:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    from django.utils import timezone
    action = request.data.get('action')
    
    try:
        task = StaffTask.objects.select_related('assigned_to__user').get(pk=task_id)
        
        # Permission checks
        is_owner = (request.user.role == 'staff' and task.assigned_to.user == request.user)
        is_admin = (request.user.role == 'admin')
        
        if not (is_owner or is_admin):
            return Response({'error': 'Not authorized for this task'}, status=status.HTTP_403_FORBIDDEN)

        # State Transitions
        if action == 'accept':
            if task.status != 'pending':
                 return Response({'error': 'Task must be pending to accept'}, status=status.HTTP_400_BAD_REQUEST)
            task.status = 'accepted'
            
        elif action == 'start':
            if task.status not in ['accepted', 'rejected']: # Can restart if rejected
                return Response({'error': 'Task must be accepted to start'}, status=status.HTTP_400_BAD_REQUEST)
            
            # CONSTRAINT: Check if staff is checked in
            today_attendance = StaffAttendance.objects.filter(
                staff=task.assigned_to, 
                date=timezone.now().date(), 
                status='present'
            ).first()
            
            # We check if they are currently checked in (present and NO check_out)
            # Adapt logic based on how check-in is stored. 
            # If status='present' implies checked in, we are good.
            if not today_attendance or (today_attendance.check_out is not None):
                 return Response({
                     'error': 'You must be checked in to start a task. Please mark attendance first.'
                 }, status=status.HTTP_400_BAD_REQUEST)

            task.status = 'in_progress'
            task.started_at = timezone.now()
            
        elif action == 'submit':
            if task.status != 'in_progress':
                return Response({'error': 'Task must be in progress to submit'}, status=status.HTTP_400_BAD_REQUEST)
            task.status = 'submitted'
            task.submitted_at = timezone.now()
            
        elif action == 'approve':
            if not is_admin:
                return Response({'error': 'Only admin can approve tasks'}, status=status.HTTP_403_FORBIDDEN)
            if task.status != 'submitted':
                return Response({'error': 'Task must be submitted to approve'}, status=status.HTTP_400_BAD_REQUEST)
            task.status = 'completed'
            task.completed_at = timezone.now()
            
        elif action == 'reject':
            if not is_admin:
                return Response({'error': 'Only admin can reject tasks'}, status=status.HTTP_403_FORBIDDEN)
            if task.status != 'submitted':
                return Response({'error': 'Task must be submitted to reject'}, status=status.HTTP_400_BAD_REQUEST)
            task.status = 'rejected' 
            # Sent back to staff, they can 'start' again or we move to in_progress directly?
            # Let's move to in_progress or Keep as rejected and allow 'start' transition.
            
        elif action == 'cancel':
            if not is_admin:
                 return Response({'error': 'Only admin can cancel tasks'}, status=status.HTTP_403_FORBIDDEN)
            task.status = 'cancelled'

        else:
            return Response({'error': f'Invalid action: {action}'}, status=status.HTTP_400_BAD_REQUEST)

        task.save()
        return Response({
            'message': f'Task status updated to {task.status}',
            'data': StaffTaskSerializer(task).data
        })

    except StaffTask.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def staff_reports(request):
    """Get staff reports and statistics with filtering"""
    if request.user.role not in ['admin', 'staff']:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    from datetime import date, timedelta
    from django.db.models import Sum, Count, Q
    
    period = request.GET.get('period', 'daily') # daily, weekly, monthly
    target_staff_id = request.GET.get('staff_id')
    
    # Determine Date Range
    today = date.today()
    start_date = today
    
    if period == 'weekly':
        start_date = today - timedelta(days=7)
    elif period == 'monthly':
        start_date = today - timedelta(days=30)
    
    # Base Queries
    attendance_qs = StaffAttendance.objects.filter(date__gte=start_date)
    tasks_qs = StaffTask.objects.all() # We might want date filter on updated_at
    
    # Filter by Staff if requested or if Staff role
    if request.user.role == 'staff':
         try:
            staff_member = StaffMember.objects.get(user=request.user)
            attendance_qs = attendance_qs.filter(staff=staff_member)
            tasks_qs = tasks_qs.filter(assigned_to=staff_member)
         except StaffMember.DoesNotExist:
             return Response({'data': {}}) # Return empty if no profile
    elif target_staff_id:
        attendance_qs = attendance_qs.filter(staff_id=target_staff_id)
        tasks_qs = tasks_qs.filter(assigned_to_id=target_staff_id)

    # Aggregations
    total_hours = attendance_qs.aggregate(total=Sum('total_hours'))['total'] or 0
    
    # Task Stats
    task_stats = tasks_qs.aggregate(
        total=Count('id'),
        completed=Count('id', filter=Q(status='completed')),
        pending=Count('id', filter=Q(status='pending')),
        overdue=Count('id', filter=Q(due_date__lt=today, status__in=['pending', 'accepted', 'in_progress']))
    )
    
    # Dashboard Specifics (Today)
    today_stats = {}
    if period == 'daily':
        if request.user.role == 'staff' or target_staff_id:
            # Single Staff Context
            today_attendance = attendance_qs.filter(date=today).first()
            today_stats['attendance_status'] = today_attendance.status if today_attendance else 'absent'
            today_stats['check_in'] = today_attendance.check_in if today_attendance else None
            today_stats['check_out'] = today_attendance.check_out if today_attendance else None
        else:
            # Global Admin Context
            present_count = attendance_qs.filter(date=today, status='present').count()
            late_count = attendance_qs.filter(date=today, status='late').count()
            # Active staff count to calculate absent?
            active_staff_count = StaffMember.objects.filter(active=True).count()
            
            today_stats['present_count'] = present_count
            today_stats['late_count'] = late_count
            today_stats['total_staff'] = active_staff_count
            today_stats['absent_count'] = active_staff_count - present_count # Simple approximation
    
    return Response({
        'message': 'Staff reports retrieved successfully',
        'data': {
            'period': period,
            'hours_worked': float(total_hours),
            'tasks': task_stats,
            'today': today_stats
        }
    })
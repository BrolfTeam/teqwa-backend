from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import EducationalService, Course, ServiceEnrollment, Lecture, TimetableEntry
from .serializers import EducationalServiceSerializer, CourseSerializer, ServiceEnrollmentSerializer, LectureSerializer, TimetableEntrySerializer
from authentication.utils import send_admin_alert_email


@api_view(['GET'])
@permission_classes([AllowAny])
def service_list(request):
    """List all educational services"""
    service_type = request.GET.get('type', '')
    level = request.GET.get('level', '')
    age_group = request.GET.get('age_group', '')
    active_only = request.GET.get('active', '').lower() == 'true'
    
    services = EducationalService.objects.select_related('instructor').all()
    
    if service_type:
        services = services.filter(service_type=service_type)
    
    if level:
        services = services.filter(level=level)
    
    if age_group:
        services = services.filter(age_group=age_group)
    
    if active_only:
        services = services.filter(status='active')
    
    serializer = EducationalServiceSerializer(services, many=True)
    return Response({
        'message': 'Educational services retrieved successfully',
        'data': serializer.data,
        'count': services.count()
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def service_detail(request, pk):
    """Get specific educational service"""
    try:
        service = EducationalService.objects.select_related('instructor').get(pk=pk)
    except EducationalService.DoesNotExist:
        return Response({
            'error': 'Educational service not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = EducationalServiceSerializer(service)
    return Response({
        'message': 'Educational service retrieved successfully',
        'data': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def enroll_service(request, pk):
    """Book an educational service or course"""
    # Check if it's a course or service
    course = None
    service = None
    
    try:
        course = Course.objects.get(pk=pk)
        service = course.service
    except Course.DoesNotExist:
        try:
            service = EducationalService.objects.get(pk=pk)
        except EducationalService.DoesNotExist:
            return Response({
                'error': 'Service or course not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    # Check capacity
    if course:
        if course.enrolled_count >= course.capacity:
            return Response({
                'error': 'Course is full'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if ServiceEnrollment.objects.filter(course=course, user=request.user).exists():
            return Response({
                'error': 'Already enrolled in this course'
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        if service.enrolled_count >= service.capacity:
            return Response({
                'error': 'Service is full'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if ServiceEnrollment.objects.filter(service=service, user=request.user).exists():
            return Response({
                'error': 'Already booked this service'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # Copy to mutable dict to handle both JSON and MultiPart
    enrollment_data = request.data.copy()
    if course:
        enrollment_data['course'] = pk
    else:
        enrollment_data['service'] = pk

    # Ensure payment method fields are included (already in request.data but explicit check doesn't hurt)
    # enrollment_data['payment_method'] = request.data.get('payment_method', 'card')
    
    serializer = ServiceEnrollmentSerializer(data=enrollment_data, context={'request': request})
    
    if serializer.is_valid():
        # Force status to pending and assign user
        serializer.save(user=request.user, status='pending')
        
        return Response({
            'message': 'Successfully enrolled',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_enrollments(request):
    """Get user's service bookings"""
    enrollments = ServiceEnrollment.objects.filter(user=request.user).select_related(
        'service', 
        'course', 
        'course__service'
    )
    serializer = ServiceEnrollmentSerializer(enrollments, many=True)
    
    return Response({
        'message': 'Bookings retrieved successfully',
        'data': serializer.data,
        'count': enrollments.count()
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_enrollments(request):
    """Get all enrollments (Staff/Admin only)"""
    if request.user.role not in ['admin', 'staff']:
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    service_id = request.GET.get('service_id', '')
    enrollments = ServiceEnrollment.objects.select_related('user', 'service').all()
    
    if service_id:
        enrollments = enrollments.filter(service_id=service_id)
    
    serializer = ServiceEnrollmentSerializer(enrollments, many=True)
    
    return Response({
        'message': 'All enrollments retrieved successfully',
        'data': serializer.data,
        'count': enrollments.count()
    })


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_enrollment_status(request, enrollment_id):
    """Update enrollment status (Staff only)"""
    if request.user.role not in ['admin', 'staff']:
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        enrollment = ServiceEnrollment.objects.get(pk=enrollment_id)
    except ServiceEnrollment.DoesNotExist:
        return Response({
            'error': 'Enrollment not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ServiceEnrollmentSerializer(enrollment, data=request.data, partial=True)
    if serializer.is_valid():
        old_status = enrollment.status
        enrollment = serializer.save()
        new_status = enrollment.status
        
        # Send admin alert if status changed to approved (informational only)
        # Note: Admin is the one updating, so no need for alert
        # This is just for logging purposes
        
        return Response({
            'message': 'Enrollment status updated successfully',
            'data': serializer.data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_service(request):
    """Create new educational service (Admin/Staff only)"""
    if request.user.role not in ['admin', 'staff']:
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = EducationalServiceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Educational service created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def course_list(request):
    """List all courses"""
    service_id = request.GET.get('service_id', '')
    service_type = request.GET.get('type', '')
    level = request.GET.get('level', '')
    age_group = request.GET.get('age_group', '')
    active_only = request.GET.get('active', '').lower() == 'true'
    
    courses = Course.objects.select_related('service', 'instructor').all()
    
    if service_id:
        courses = courses.filter(service_id=service_id)
    
    if service_type:
        courses = courses.filter(service__service_type=service_type)
    
    if level:
        courses = courses.filter(level=level)
    
    if age_group:
        courses = courses.filter(age_group=age_group)
    
    if active_only:
        courses = courses.filter(status='active')
    
    serializer = CourseSerializer(courses, many=True)
    return Response({
        'message': 'Courses retrieved successfully',
        'data': serializer.data,
        'count': courses.count()
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def course_detail(request, pk):
    """Get specific course"""
    try:
        course = Course.objects.select_related('service', 'instructor').get(pk=pk)
    except Course.DoesNotExist:
        return Response({
            'error': 'Course not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = CourseSerializer(course)
    return Response({
        'message': 'Course retrieved successfully',
        'data': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_course(request):
    """Create new course (Admin/Staff only)"""
    if request.user.role not in ['admin', 'staff']:
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = CourseSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Course created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def lecture_list(request):
    """List all lectures"""
    subject = request.GET.get('subject', '')
    instructor_id = request.GET.get('instructor', '')
    search = request.GET.get('search', '')
    
    lectures = Lecture.objects.select_related('instructor').all()
    
    if subject:
        lectures = lectures.filter(subject=subject)
    
    if instructor_id:
        lectures = lectures.filter(instructor_id=instructor_id)
        
    if search:
        lectures = lectures.filter(title__icontains=search) | lectures.filter(description__icontains=search)
    
    serializer = LectureSerializer(lectures, many=True, context={'request': request})
    return Response({
        'message': 'Lectures retrieved successfully',
        'data': serializer.data,
        'count': lectures.count()
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def lecture_detail(request, pk):
    """Get specific lecture details"""
    try:
        lecture = Lecture.objects.select_related('instructor').get(pk=pk)
    except Lecture.DoesNotExist:
        return Response({
            'error': 'Lecture not found'
        }, status=status.HTTP_404_NOT_FOUND)
        
    serializer = LectureSerializer(lecture, context={'request': request})
    return Response({
        'message': 'Lecture retrieved successfully',
        'data': serializer.data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def timetable_list(request):
    """List all timetable entries for weekly schedule"""
    day = request.GET.get('day', '')
    active_only = request.GET.get('active', '').lower() != 'false'
    
    entries = TimetableEntry.objects.all()
    
    if active_only:
        entries = entries.filter(is_active=True)
        
    if day:
        entries = entries.filter(day_of_week=day)
        
    serializer = TimetableEntrySerializer(entries, many=True)
    return Response({
        'message': 'Timetable entries retrieved successfully',
        'data': serializer.data,
        'count': entries.count()
    })
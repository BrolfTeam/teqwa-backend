from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.contrib.auth import get_user_model

from .models import (
    Student, Parent, Course, Timetable, Assignment, Exam,
    Submission, Grade, StudentMessage, Announcement
)
from .serializers import (
    StudentSerializer, ParentSerializer, CourseSerializer, TimetableSerializer,
    AssignmentSerializer, ExamSerializer, SubmissionSerializer, GradeSerializer,
    StudentMessageSerializer, AnnouncementSerializer
)

User = get_user_model()


def is_student(user):
    """Check if user is a student"""
    return user.role == 'student' or hasattr(user, 'student_profile')


def is_teacher(user):
    """Check if user is a teacher"""
    return user.role == 'teacher' or (user.role == 'staff' and hasattr(user, 'staff_profile'))


def is_parent(user):
    """Check if user is a parent"""
    return user.role == 'parent' or hasattr(user, 'parent_profile')


def get_student(user):
    """Get student profile for user"""
    try:
        return user.student_profile
    except Student.DoesNotExist:
        return None


def get_parent(user):
    """Get parent profile for user"""
    try:
        return user.parent_profile
    except Parent.DoesNotExist:
        return None


# Student Dashboard Stats
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_dashboard_stats(request):
    """Get dashboard statistics for student"""
    if not is_student(request.user):
        return Response({'error': 'Access denied. Student access required.'}, status=status.HTTP_403_FORBIDDEN)

    student = get_student(request.user)
    if not student:
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)

    # Get enrolled courses
    enrollments = student.user.serviceenrollment_set.filter(status='confirmed')
    courses = []
    for e in enrollments:
        try:
            if hasattr(e.service, 'course') and e.service.course:
                courses.append(e.service.course)
        except Exception:
            continue

    # Get assignments
    assignments = Assignment.objects.filter(course__in=courses, is_published=True)
    pending_assignments = assignments.filter(due_date__gte=timezone.now()).count()
    overdue_assignments = assignments.filter(due_date__lt=timezone.now()).exclude(
        submissions__student=student, submissions__status='submitted'
    ).count()

    # Get submissions
    submissions = Submission.objects.filter(student=student)
    submitted_count = submissions.filter(status='submitted').count()
    graded_count = Grade.objects.filter(student=student).count()

    # Get upcoming exams
    upcoming_exams = Exam.objects.filter(course__in=courses, is_published=True, exam_date__gte=timezone.now()).count()

    # Get unread messages
    unread_messages = StudentMessage.objects.filter(recipient=request.user, is_read=False).count()

    # Get announcements
    announcements_count = Announcement.objects.filter(
        is_published=True,
        course__in=courses
    ).count()

    return Response({
        'message': 'Dashboard stats retrieved successfully',
        'data': {
            'courses_count': len(courses),
            'pending_assignments': pending_assignments,
            'overdue_assignments': overdue_assignments,
            'submitted_count': submitted_count,
            'graded_count': graded_count,
            'upcoming_exams': upcoming_exams,
            'unread_messages': unread_messages,
            'announcements_count': announcements_count,
        }
    })


# Timetable
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_timetable(request):
    """Get timetable for student"""
    if not is_student(request.user):
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

    student = get_student(request.user)
    if not student:
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)

    enrollments = student.user.serviceenrollment_set.filter(status='confirmed')
    courses = []
    for e in enrollments:
        try:
            if hasattr(e.service, 'course') and e.service.course:
                courses.append(e.service.course)
        except Exception:
            continue

    timetable = Timetable.objects.filter(course__in=courses).order_by('day', 'start_time') if courses else Timetable.objects.none()
    serializer = TimetableSerializer(timetable, many=True)

    return Response({
        'message': 'Timetable retrieved successfully',
        'data': serializer.data,
        'count': timetable.count()
    })


# Assignments
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_assignments(request):
    """Get assignments for student"""
    if not is_student(request.user):
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

    student = get_student(request.user)
    if not student:
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)

    enrollments = student.user.serviceenrollment_set.filter(status='confirmed')
    courses = []
    for e in enrollments:
        try:
            if hasattr(e.service, 'course') and e.service.course:
                courses.append(e.service.course)
        except Exception:
            continue

    assignments = Assignment.objects.filter(course__in=courses, is_published=True).order_by('-due_date') if courses else Assignment.objects.none()
    serializer = AssignmentSerializer(assignments, many=True)

    return Response({
        'message': 'Assignments retrieved successfully',
        'data': serializer.data,
        'count': assignments.count()
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def assignment_detail(request, assignment_id):
    """Get assignment detail"""
    if not is_student(request.user):
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

    try:
        assignment = Assignment.objects.get(id=assignment_id, is_published=True)
        serializer = AssignmentSerializer(assignment)
        return Response({
            'message': 'Assignment retrieved successfully',
            'data': serializer.data
        })
    except Assignment.DoesNotExist:
        return Response({'error': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)


# Exams
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_exams(request):
    """Get exams for student"""
    if not is_student(request.user):
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

    student = get_student(request.user)
    if not student:
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)

    enrollments = student.user.serviceenrollment_set.filter(status='confirmed')
    courses = []
    for e in enrollments:
        try:
            if hasattr(e.service, 'course') and e.service.course:
                courses.append(e.service.course)
        except Exception:
            continue

    exams = Exam.objects.filter(course__in=courses, is_published=True).order_by('-exam_date') if courses else Exam.objects.none()
    serializer = ExamSerializer(exams, many=True)

    return Response({
        'message': 'Exams retrieved successfully',
        'data': serializer.data,
        'count': exams.count()
    })


# Submissions
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def student_submissions(request, assignment_id=None):
    """Get or create submission"""
    if not is_student(request.user):
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

    student = get_student(request.user)
    if not student:
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        if assignment_id:
            try:
                submission = Submission.objects.get(assignment_id=assignment_id, student=student)
                serializer = SubmissionSerializer(submission)
                return Response({
                    'message': 'Submission retrieved successfully',
                    'data': serializer.data
                })
            except Submission.DoesNotExist:
                return Response({'error': 'Submission not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            submissions = Submission.objects.filter(student=student).order_by('-submitted_at', '-created_at')
            serializer = SubmissionSerializer(submissions, many=True)
            return Response({
                'message': 'Submissions retrieved successfully',
                'data': serializer.data,
                'count': submissions.count()
            })

    elif request.method == 'POST':
        try:
            assignment = Assignment.objects.get(id=assignment_id, is_published=True)
        except Assignment.DoesNotExist:
            return Response({'error': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)

        submission, created = Submission.objects.get_or_create(
            assignment=assignment,
            student=student,
            defaults={
                'content': request.data.get('content', ''),
                'files': request.data.get('files', []),
                'status': 'submitted',
                'submitted_at': timezone.now()
            }
        )

        if not created:
            submission.content = request.data.get('content', submission.content)
            submission.files = request.data.get('files', submission.files)
            submission.status = 'submitted'
            submission.submitted_at = timezone.now()
            submission.save()

        serializer = SubmissionSerializer(submission)
        return Response({
            'message': 'Submission created successfully' if created else 'Submission updated successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


# Grades
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_grades(request):
    """Get grades for student"""
    if not is_student(request.user):
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

    student = get_student(request.user)
    if not student:
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)

    grades = Grade.objects.filter(student=student).order_by('-graded_at')
    serializer = GradeSerializer(grades, many=True)

    # Calculate average percentage from score and max_score
    # percentage is a property, not a field, so we calculate it manually
    total_score = 0
    total_max = 0
    for grade in grades:
        total_score += float(grade.score)
        total_max += grade.max_score
    
    avg_percentage = 0
    if total_max > 0:
        avg_percentage = round((total_score / total_max) * 100, 2)

    return Response({
        'message': 'Grades retrieved successfully',
        'data': serializer.data,
        'count': grades.count(),
        'average_percentage': avg_percentage
    })


# Messages
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def student_messages(request):
    """Get or send messages"""
    if not is_student(request.user) and not is_teacher(request.user):
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        messages = StudentMessage.objects.filter(
            Q(sender=request.user) | Q(recipient=request.user)
        ).order_by('-created_at')
        serializer = StudentMessageSerializer(messages, many=True)
        return Response({
            'message': 'Messages retrieved successfully',
            'data': serializer.data,
            'count': messages.count()
        })

    elif request.method == 'POST':
        # Students can only message teachers
        if is_student(request.user):
            recipient_id = request.data.get('recipient_id')
            try:
                recipient = User.objects.get(id=recipient_id)
                if not is_teacher(recipient):
                    return Response({'error': 'Students can only message teachers'}, status=status.HTTP_403_FORBIDDEN)
            except User.DoesNotExist:
                return Response({'error': 'Recipient not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentMessageSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save(sender=request.user)
            return Response({
                'message': 'Message sent successfully',
                'data': StudentMessageSerializer(message).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_message_read(request, message_id):
    """Mark message as read"""
    try:
        message = StudentMessage.objects.get(id=message_id, recipient=request.user)
        message.is_read = True
        message.read_at = timezone.now()
        message.save()
        return Response({
            'message': 'Message marked as read',
            'data': StudentMessageSerializer(message).data
        })
    except StudentMessage.DoesNotExist:
        return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)


# Announcements
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_announcements(request):
    """Get announcements for student"""
    if not is_student(request.user):
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

    student = get_student(request.user)
    if not student:
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)

    enrollments = student.user.serviceenrollment_set.filter(status='confirmed')
    courses = []
    for e in enrollments:
        try:
            if hasattr(e.service, 'course') and e.service.course:
                courses.append(e.service.course)
        except Exception:
            continue

    # Get announcements for student's courses or general announcements
    if courses:
        announcements = Announcement.objects.filter(
            Q(course__in=courses) | Q(course__isnull=True),
            is_published=True
        ).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gte=timezone.now())
        ).order_by('-priority', '-published_at', '-created_at')
    else:
        # If no courses, only show general announcements
        announcements = Announcement.objects.filter(
            course__isnull=True,
            is_published=True
        ).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gte=timezone.now())
        ).order_by('-priority', '-published_at', '-created_at')

    serializer = AnnouncementSerializer(announcements, many=True)
    return Response({
        'message': 'Announcements retrieved successfully',
        'data': serializer.data,
        'count': announcements.count()
    })


# Parent Access
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def parent_dashboard(request):
    """Get dashboard for parent"""
    if not is_parent(request.user):
        return Response({'error': 'Access denied. Parent access required.'}, status=status.HTTP_403_FORBIDDEN)

    parent = get_parent(request.user)
    if not parent:
        return Response({'error': 'Parent profile not found'}, status=status.HTTP_404_NOT_FOUND)

    children = Student.objects.filter(parent=request.user)
    children_data = StudentSerializer(children, many=True).data

    # Get children's grades
    children_grades = Grade.objects.filter(student__in=children).order_by('-graded_at')
    grades_data = GradeSerializer(children_grades, many=True).data

    return Response({
        'message': 'Parent dashboard retrieved successfully',
        'data': {
            'children': children_data,
            'grades': grades_data,
            'children_count': children.count()
        }
    })


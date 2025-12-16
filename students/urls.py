from django.urls import path
from . import views

urlpatterns = [
    # Student Dashboard
    path('dashboard/stats/', views.student_dashboard_stats, name='student_dashboard_stats'),
    
    # Timetable
    path('timetable/', views.student_timetable, name='student_timetable'),
    
    # Assignments
    path('assignments/', views.student_assignments, name='student_assignments'),
    path('assignments/<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    
    # Exams
    path('exams/', views.student_exams, name='student_exams'),
    
    # Submissions
    path('submissions/', views.student_submissions, name='student_submissions'),
    path('submissions/<int:assignment_id>/', views.student_submissions, name='submission_detail'),
    
    # Grades
    path('grades/', views.student_grades, name='student_grades'),
    
    # Messages
    path('messages/', views.student_messages, name='student_messages'),
    path('messages/<int:message_id>/read/', views.mark_message_read, name='mark_message_read'),
    
    # Announcements
    path('announcements/', views.student_announcements, name='student_announcements'),
    
    # Parent Dashboard
    path('parent/dashboard/', views.parent_dashboard, name='parent_dashboard'),
]


from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Announcement
from .serializers import AnnouncementSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def announcement_list(request):
    """List all published announcements"""
    featured_only = request.GET.get('featured', '').lower() == 'true'
    
    announcements = Announcement.objects.filter(published=True)
    if featured_only:
        announcements = announcements.filter(featured=True)
    
    serializer = AnnouncementSerializer(announcements, many=True)
    return Response({
        'message': 'Announcements retrieved successfully',
        'data': serializer.data,
        'count': announcements.count()
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def announcement_detail(request, pk):
    """Get specific announcement"""
    try:
        announcement = Announcement.objects.get(pk=pk, published=True)
    except Announcement.DoesNotExist:
        return Response({
            'error': 'Announcement not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = AnnouncementSerializer(announcement)
    return Response({
        'message': 'Announcement retrieved successfully',
        'data': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_announcement(request):
    """Create new announcement (Admin/Staff only)"""
    if request.user.role not in ['admin', 'staff']:
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = AnnouncementSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Announcement created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_announcement(request, pk):
    """Update announcement (Admin/Staff only)"""
    if request.user.role not in ['admin', 'staff']:
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        announcement = Announcement.objects.get(pk=pk)
    except Announcement.DoesNotExist:
        return Response({
            'error': 'Announcement not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = AnnouncementSerializer(announcement, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Announcement updated successfully',
            'data': serializer.data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_announcement(request, pk):
    """Delete announcement (Admin only)"""
    if request.user.role != 'admin':
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        announcement = Announcement.objects.get(pk=pk)
        announcement.delete()
        return Response({
            'message': 'Announcement deleted successfully'
        })
    except Announcement.DoesNotExist:
        return Response({
            'error': 'Announcement not found'
        }, status=status.HTTP_404_NOT_FOUND)
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_logged_out
from .models import UserProfile, UserActivity
from donations.models import Donation
from events.models import EventRegistration

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create user profile when user is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log user login activity"""
    UserActivity.objects.create(
        user=user,
        activity_type='login',
        description=f'User logged in from {get_client_ip(request)}',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        metadata={
            'login_method': 'web',
            'session_key': request.session.session_key
        }
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout activity"""
    if user:
        UserActivity.objects.create(
            user=user,
            activity_type='logout',
            description=f'User logged out from {get_client_ip(request)}',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            metadata={
                'logout_method': 'web'
            }
        )


@receiver(post_save, sender=Donation)
def award_points_for_donation(sender, instance, created, **kwargs):
    """Award points when a donation is completed"""
    if instance.status == 'completed' and instance.user:
        # Check if points were already awarded for this donation
        # This prevents double counting if the save method is called multiple times
        already_awarded = UserActivity.objects.filter(
            user=instance.user,
            metadata__source='donation',
            metadata__id=instance.id
        ).exists()
        
        if not already_awarded:
            # Calculate points: 10 points per 1 unit of currency (e.g. $1)
            points_to_award = int(instance.amount * 10)
            
            # Update user profile
            profile, _ = UserProfile.objects.get_or_create(user=instance.user)
            profile.community_points += points_to_award
            profile.save()
            
            # Log activity
            UserActivity.objects.create(
                user=instance.user,
                activity_type='donation',
                description=f'Earned {points_to_award} points for donation of {instance.currency} {instance.amount}',
                metadata={
                    'source': 'donation',
                    'id': instance.id,
                    'points_awarded': points_to_award
                }
            )


@receiver(post_save, sender=EventRegistration)
def award_points_for_event(sender, instance, created, **kwargs):
    """Award points when an event registration is confirmed"""
    if instance.status == 'confirmed':
        # Check if points were already awarded for this registration
        already_awarded = UserActivity.objects.filter(
            user=instance.user,
            metadata__source='event_registration',
            metadata__id=instance.id
        ).exists()
        
        if not already_awarded:
            # Award fixed 50 points for attending an event
            points_to_award = 50
            
            # Update user profile
            profile, _ = UserProfile.objects.get_or_create(user=instance.user)
            profile.community_points += points_to_award
            profile.save()
            
            # Log activity
            UserActivity.objects.create(
                user=instance.user,
                activity_type='event_registration',
                description=f'Earned {points_to_award} points for registering for event: {instance.event.title}',
                metadata={
                    'source': 'event_registration',
                    'id': instance.id,
                    'points_awarded': points_to_award
                }
            )


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# --- Futsal Signals ---
from futsal_booking.models import FutsalBooking

@receiver(post_save, sender=FutsalBooking)
def log_futsal_booking(sender, instance, created, **kwargs):
    """Log futsal booking activity"""
    if created:
        UserActivity.objects.create(
            user=instance.user,
            activity_type='futsal_booking',
            description=f'Booked futsal slot for {instance.slot.date} at {instance.slot.start_time}',
            metadata={
                'source': 'futsal',
                'id': instance.id,
                'status': 'created'
            }
        )
    elif instance.status == 'cancelled':
         UserActivity.objects.create(
            user=instance.user,
            activity_type='futsal_booking',
            description=f'Cancelled futsal booking for {instance.slot.date}',
            metadata={
                'source': 'futsal',
                'id': instance.id,
                'status': 'cancelled'
            }
        )

# --- Staff Signals ---
from staff.models import StaffTask, StaffAttendance

@receiver(post_save, sender=StaffTask)
def log_staff_task(sender, instance, created, **kwargs):
    """Log staff task completion"""
    if instance.status == 'completed':
        # Check double logging
        already_logged = UserActivity.objects.filter(
            user=instance.assigned_to.user,
            metadata__source='staff_task',
            metadata__id=instance.id,
            metadata__status='completed'
        ).exists()

        if not already_logged:
             UserActivity.objects.create(
                user=instance.assigned_to.user,
                activity_type='task_update',
                description=f'Completed task: {instance.title}',
                metadata={
                    'source': 'staff_task',
                    'id': instance.id,
                    'status': 'completed'
                }
            )

@receiver(post_save, sender=StaffAttendance)
def log_staff_attendance(sender, instance, created, **kwargs):
    """Log staff attendance check-in/out"""
    if created: # Check-in
         UserActivity.objects.create(
            user=instance.staff.user,
            activity_type='attendance',
            description=f'Checked in for work at {instance.check_in.strftime("%H:%M")}' if instance.check_in else 'Marked present',
            metadata={
                'source': 'staff_attendance',
                'id': instance.id,
                'type': 'check_in'
            }
        )
    elif instance.check_out and instance.status == 'present': # Check-out (update)
         # Check if already logged check-out to avoid noise on every save
         already_logged = UserActivity.objects.filter(
            user=instance.staff.user,
            metadata__source='staff_attendance',
            metadata__id=instance.id,
            metadata__type='check_out'
        ).exists()
         
         if not already_logged:
            UserActivity.objects.create(
                user=instance.staff.user,
                activity_type='attendance',
                description=f'Checked out from work at {instance.check_out.strftime("%H:%M")}',
                metadata={
                    'source': 'staff_attendance',
                    'id': instance.id,
                    'type': 'check_out'
                }
            )

# --- Admin/Management Signals ---
from donations.models import DonationCause
from futsal_booking.models import FutsalSlot

# Note: DonationCause and FutsalSlot creation logging is best handled in views 
# if the models don't track the creator. 
# However, if we assume they might, we could try. 
# But to be safe and consistent with the user verification request, 
# I will stick to the View-based logging for these specific Admin actions 
# if the models lack user fields.

# I will instead rely on the fact that I already enabled 'UserActivity' fetching. 
# I will NOT add signals for these if I can't identify the user.
# I'll update the plan to check models first.
from django.core.mail import send_mail, send_mass_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model
import secrets

User = get_user_model()


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """Custom token generator for email verification"""
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.is_verified}"


email_verification_token = EmailVerificationTokenGenerator()
password_reset_token = PasswordResetTokenGenerator()


def generate_verification_token():
    """Generate a secure random token for email verification"""
    return secrets.token_urlsafe(32)


def send_verification_email(user, token):
    """Send email verification link to user"""
    # Get frontend URL from settings (must be configured via environment variable)
    frontend_url = getattr(settings, 'FRONTEND_URL', None)
    if not frontend_url:
        raise ValueError("FRONTEND_URL must be configured in Django settings")
    verification_link = f"{frontend_url}/verify-email/{token}"
    
    subject = 'Verify Your Email - Teqwa'
    message = f"""
    Hello {user.first_name or user.username},
    
    Thank you for registering with Teqwa!
    
    Please verify your email address by clicking the link below:
    {verification_link}
    
    This link will expire in 24 hours.
    
    If you didn't create an account, please ignore this email.
    
    Best regards,
    Teqwa Team
    """
    
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c5282;">Welcome to Teqwa!</h2>
                <p>Hello {user.first_name or user.username},</p>
                <p>Thank you for registering with Teqwa!</p>
                <p>Please verify your email address by clicking the button below:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_link}" 
                       style="background-color: #2c5282; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Verify Email Address
                    </a>
                </div>
                <p style="color: #666; font-size: 14px;">
                    This link will expire in 24 hours.
                </p>
                <p style="color: #666; font-size: 14px;">
                    If you didn't create an account, please ignore this email.
                </p>
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                <p style="color: #999; font-size: 12px;">
                    Best regards,<br>
                    Teqwa Team
                </p>
            </div>
        </body>
    </html>
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_password_reset_email(user, token):
    """Send password reset link to user"""
    # Get frontend URL from settings (must be configured via environment variable)
    frontend_url = getattr(settings, 'FRONTEND_URL', None)
    if not frontend_url:
        raise ValueError("FRONTEND_URL must be configured in Django settings")
    reset_link = f"{frontend_url}/reset-password/{token}"
    
    subject = 'Reset Your Password - Teqwa'
    message = f"""
    Hello {user.first_name or user.username},
    
    We received a request to reset your password for your Teqwa account.
    
    Please click the link below to reset your password:
    {reset_link}
    
    This link will expire in 24 hours.
    
    If you didn't request a password reset, please ignore this email or contact support if you have concerns.
    
    Best regards,
    Teqwa Team
    """
    
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c5282;">Password Reset Request</h2>
                <p>Hello {user.first_name or user.username},</p>
                <p>We received a request to reset your password for your Teqwa account.</p>
                <p>Please click the button below to reset your password:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_link}" 
                       style="background-color: #2c5282; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Reset Password
                    </a>
                </div>
                <p style="color: #666; font-size: 14px;">
                    This link will expire in 24 hours.
                </p>
                <p style="color: #666; font-size: 14px;">
                    If you didn't request a password reset, please ignore this email or contact support if you have concerns.
                </p>
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                <p style="color: #999; font-size: 12px;">
                    Best regards,<br>
                    Teqwa Team
                </p>
            </div>
        </body>
    </html>
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_donation_confirmation_email(donation, user=None):
    """Send donation confirmation email to donor"""
    # Get frontend URL from settings (must be configured via environment variable)
    frontend_url = getattr(settings, 'FRONTEND_URL', None)
    if not frontend_url:
        raise ValueError("FRONTEND_URL must be configured in Django settings")
    
    # Get user or use donation email
    recipient_email = user.email if user else donation.email
    recipient_name = user.first_name if user else donation.donor_name
    
    subject = f'Donation Confirmation - {donation.cause.title if donation.cause else "General Donation"}'
    
    message = f"""
    Hello {recipient_name},
    
    Thank you for your generous donation!
    
    Donation Details:
    - Amount: {donation.amount} {donation.currency or 'ETB'}
    - Cause: {donation.cause.title if donation.cause else 'General Donation'}
    - Status: {donation.status}
    - Transaction ID: {getattr(donation, 'transaction_id', 'N/A') or 'N/A'}
    - Date: {donation.created_at.strftime('%B %d, %Y at %I:%M %p')}
    
    Your contribution helps support our community and Islamic activities.
    
    May Allah (SWT) accept your donation and reward you abundantly.
    
    Best regards,
    Teqwa Team
    """
    
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c5282;">Thank You for Your Donation!</h2>
                <p>Hello {recipient_name},</p>
                <p>We have received your generous donation. May Allah (SWT) accept it and reward you abundantly.</p>
                
                <div style="background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #2c5282;">Donation Details</h3>
                    <p><strong>Amount:</strong> {donation.amount} {donation.currency or 'ETB'}</p>
                    <p><strong>Cause:</strong> {donation.cause.title if donation.cause else 'General Donation'}</p>
                    <p><strong>Status:</strong> <span style="color: {'green' if donation.status == 'completed' else 'orange'}">{donation.status.title()}</span></p>
                    {f'<p><strong>Transaction ID:</strong> {getattr(donation, "transaction_id", "")}</p>' if getattr(donation, 'transaction_id', None) else ''}
                    <p><strong>Date:</strong> {donation.created_at.strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>
                
                <p>Your contribution helps support our community and Islamic activities.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{frontend_url}/donations" 
                       style="background-color: #2c5282; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        View Donation History
                    </a>
                </div>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                <p style="color: #999; font-size: 12px;">
                    Best regards,<br>
                    Teqwa Team
                </p>
            </div>
        </body>
    </html>
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending donation confirmation email: {e}")


def send_event_registration_email(event, user, registration):
    """Send event registration confirmation email"""
    # Get frontend URL from settings (must be configured via environment variable)
    frontend_url = getattr(settings, 'FRONTEND_URL', None)
    if not frontend_url:
        raise ValueError("FRONTEND_URL must be configured in Django settings")
    
    subject = f'Event Registration Confirmed - {event.title}'
    
    message = f"""
    Hello {user.first_name or user.username},
    
    Your registration for the event "{event.title}" has been confirmed!
    
    Event Details:
    - Event: {event.title}
    - Date: {event.date.strftime('%B %d, %Y') if event.date else 'TBA'}
    - Time: {event.start_time.strftime('%I:%M %p') if event.start_time else 'TBA'}
    - Location: {event.location or 'TBA'}
    - Status: {registration.status}
    
    We look forward to seeing you there!
    
    Best regards,
    Teqwa Team
    """
    
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c5282;">Event Registration Confirmed!</h2>
                <p>Hello {user.first_name or user.username},</p>
                <p>Your registration for the event has been confirmed. We look forward to seeing you there!</p>
                
                <div style="background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #2c5282;">Event Details</h3>
                    <p><strong>Event:</strong> {event.title}</p>
                    {f"<p><strong>Date:</strong> {event.date.strftime('%B %d, %Y')}</p>" if event.date else ''}
                    {f"<p><strong>Time:</strong> {event.start_time.strftime('%I:%M %p')}</p>" if event.start_time else ''}
                    {f"<p><strong>Location:</strong> {event.location}</p>" if event.location else ''}
                    <p><strong>Status:</strong> <span style="color: green;">{registration.status.title()}</span></p>
                </div>
                
                {f'<p style="color: #666; font-size: 14px;">{event.description[:200]}...</p>' if event.description else ''}
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{frontend_url}/events/{event.id}" 
                       style="background-color: #2c5282; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        View Event Details
                    </a>
                </div>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                <p style="color: #999; font-size: 12px;">
                    Best regards,<br>
                    Teqwa Team
                </p>
            </div>
        </body>
    </html>
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending event registration email: {e}")


def send_itikaf_approval_email(registration, program, user, status='approved'):
    """Send iʿtikāf registration approval/rejection email"""
    # Get frontend URL from settings (must be configured via environment variable)
    frontend_url = getattr(settings, 'FRONTEND_URL', None)
    if not frontend_url:
        raise ValueError("FRONTEND_URL must be configured in Django settings")
    
    is_approved = status == 'approved'
    subject = f'Iʿtikāf Registration {"Approved" if is_approved else "Update"} - {program.title}'
    
    status_message = "approved and confirmed" if is_approved else f"updated to {status}"
    status_color = "green" if is_approved else "orange"
    
    message = f"""
    Hello {user.first_name or user.username},
    
    Your Iʿtikāf registration has been {status_message}.
    
    Program Details:
    - Program: {program.title}
    - Start Date: {program.start_date.strftime('%B %d, %Y') if program.start_date else 'TBA'}
    - End Date: {program.end_date.strftime('%B %d, %Y') if program.end_date else 'TBA'}
    - Location: {program.location or 'Main Mosque'}
    - Status: {registration.status.title()}
    - Fee: {registration.payment_amount or program.fee} ETB
    """
    
    if not is_approved and status == 'rejected':
        message += "\n\nYour registration was not approved. Please contact us if you have any questions."
    elif status == 'waitlisted':
        message += "\n\nThe program is currently full, and you have been added to the waitlist. We will notify you if a spot becomes available."
    
    message += """
    
    Best regards,
    Teqwa Team
    """
    
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c5282;">Iʿtikāf Registration {status.title()}</h2>
                <p>Hello {user.first_name or user.username},</p>
                <p>Your Iʿtikāf registration has been <strong>{status_message}</strong>.</p>
                
                <div style="background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #2c5282;">Program Details</h3>
                    <p><strong>Program:</strong> {program.title}</p>
                    {f"<p><strong>Start Date:</strong> {program.start_date.strftime('%B %d, %Y')}</p>" if program.start_date else ''}
                    {f"<p><strong>End Date:</strong> {program.end_date.strftime('%B %d, %Y')}</p>" if program.end_date else ''}
                    {f"<p><strong>Location:</strong> {program.location}</p>" if program.location else ''}
                    <p><strong>Status:</strong> <span style="color: {status_color};">{registration.status.title()}</span></p>
                    <p><strong>Fee:</strong> {registration.payment_amount or program.fee} ETB</p>
                </div>
                
                {f'<p style="color: #666; font-size: 14px;">{program.description[:200]}...</p>' if program.description else ''}
                
                {'<p style="color: #d32f2f; font-weight: bold;">Note: Your registration was not approved. Please contact us if you have any questions.</p>' if status == 'rejected' else ''}
                {'<p style="color: #f57c00; font-weight: bold;">Note: The program is currently full. You have been added to the waitlist. We will notify you if a spot becomes available.</p>' if status == 'waitlisted' else ''}
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{frontend_url}/itikaf/{program.id}" 
                       style="background-color: #2c5282; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        View Program Details
                    </a>
                </div>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                <p style="color: #999; font-size: 12px;">
                    Best regards,<br>
                    Teqwa Team
                </p>
            </div>
        </body>
    </html>
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending iʿtikāf approval email: {e}")


def send_admin_alert_email(subject_text, message_text, event_type='general', details=None):
    """Send alert email to all admin users"""
    try:
        admin_users = User.objects.filter(role='admin', is_active=True)
        admin_emails = [admin.email for admin in admin_users if admin.email]
        
        if not admin_emails:
            print("No admin email addresses found for alert")
            return
        
        subject = f'[ADMIN ALERT] {subject_text} - Teqwa'
        
        message = f"""
        Admin Alert: {subject_text}
        
        {message_text}
        """
        
        if details:
            message += "\n\nDetails:\n"
            for key, value in details.items():
                message += f"- {key}: {value}\n"
        
        message += """
        
        This is an automated alert from the Teqwa system.
        """
        
        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background-color: #d32f2f; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                        <h2 style="margin: 0;">ADMIN ALERT</h2>
                    </div>
                    <h3 style="color: #2c5282;">{subject_text}</h3>
                    <p>{message_text}</p>
                    
                    {f'''
                    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h4 style="margin-top: 0; color: #2c5282;">Details:</h4>
                        {''.join([f'<p><strong>{key}:</strong> {value}</p>' for key, value in details.items()])}
                    </div>
                    ''' if details else ''}
                    
                    <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 10px; margin: 20px 0;">
                        <p style="margin: 0; font-size: 12px; color: #856404;">
                            <strong>Event Type:</strong> {event_type}<br>
                            This is an automated alert from the Teqwa system.
                        </p>
                    </div>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    <p style="color: #999; font-size: 12px;">
                        Teqwa Management System
                    </p>
                </div>
            </body>
        </html>
        """
        
        # Send to all admins
        for email in admin_emails:
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    html_message=html_message,
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error sending admin alert to {email}: {e}")
                
    except Exception as e:
        print(f"Error in send_admin_alert_email: {e}")


def send_new_user_registration_alert(user):
    """Send alert to admins when a new user registers"""
    send_admin_alert_email(
        subject_text="New User Registration",
        message_text=f"A new user has registered: {user.get_full_name()} ({user.email})",
        event_type="user_registration",
        details={
            "Name": user.get_full_name(),
            "Email": user.email,
            "Role": user.role,
            "Registration Date": user.date_joined.strftime('%B %d, %Y at %I:%M %p') if user.date_joined else 'N/A'
        }
    )


def send_new_donation_alert(donation, user=None):
    """Send alert to admins when a new donation is made"""
    donor_name = user.get_full_name() if user else donation.donor_name
    donor_email = user.email if user else donation.email
    
    send_admin_alert_email(
        subject_text="New Donation Received",
        message_text=f"A new donation has been received: {donation.amount} {donation.currency or 'ETB'}",
        event_type="donation",
        details={
            "Amount": f"{donation.amount} {donation.currency or 'ETB'}",
            "Cause": donation.cause.title if donation.cause else "General Donation",
            "Donor": donor_name,
            "Donor Email": donor_email,
            "Status": donation.status,
            "Date": donation.created_at.strftime('%B %d, %Y at %I:%M %p') if donation.created_at else 'N/A'
        }
    )


def send_large_donation_alert(donation, user=None, threshold=10000):
    """Send special alert for large donations"""
    if float(donation.amount) >= threshold:
        donor_name = user.get_full_name() if user else donation.donor_name
        donor_email = user.email if user else donation.email
        # Transaction ID might be in related Transaction model or donation model
        transaction_id = getattr(donation, 'transaction_id', None) or "N/A"
        # Try to get from related transaction if it exists
        if transaction_id == "N/A" and hasattr(donation, 'transaction_set'):
            transaction = donation.transaction_set.first()
            if transaction:
                transaction_id = getattr(transaction, 'tx_ref', transaction_id)
        
        send_admin_alert_email(
            subject_text=f"LARGE DONATION ALERT - {donation.amount} {donation.currency or 'ETB'}",
            message_text=f"A large donation has been received that exceeds the threshold of {threshold} {donation.currency or 'ETB'}",
            event_type="large_donation",
            details={
                "Amount": f"{donation.amount} {donation.currency or 'ETB'}",
                "Threshold": f"{threshold} {donation.currency or 'ETB'}",
                "Cause": donation.cause.title if donation.cause else "General Donation",
                "Donor": donor_name,
                "Donor Email": donor_email,
                "Transaction ID": transaction_id,
                "Date": donation.created_at.strftime('%B %d, %Y at %I:%M %p') if donation.created_at else 'N/A'
            }
        )

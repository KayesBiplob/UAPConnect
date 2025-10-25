from .models import JobApplication, JobAdvert
from .enums import ApplicationStatus


def application_notifications(request):
    """
    Context processor to add application notification counts to all templates
    """
    notifications = {
        'new_decisions_count': 0,
        'unseen_applications': [],
        'pending_decisions_count': 0,
    }
    
    if request.user.is_authenticated:
        # Get applications with unseen decisions (not APPLIED status and not seen)
        # For applicants
        unseen_applications = JobApplication.objects.filter(
            email=request.user.email,
            decision_seen=False
        ).exclude(
            status=ApplicationStatus.APPLIED
        ).select_related('job_advert')
        
        notifications['new_decisions_count'] = unseen_applications.count()
        notifications['unseen_applications'] = unseen_applications
        
        # Get pending applications count for employer's jobs
        # For employers
        pending_applications = JobApplication.objects.filter(
            job_advert__created_by=request.user,
            status=ApplicationStatus.APPLIED
        ).count()
        
        notifications['pending_decisions_count'] = pending_applications
    
    return notifications

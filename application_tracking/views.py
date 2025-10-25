from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.db.models import Q

from accounts.models import User
from application_tracking.enums import ApplicationStatus
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .forms import JobAdvertForm, JobApplicationForm
from .models import JobAdvert, JobApplication

def home(request):
    # Calculate real statistics for achievements section
    total_users = User.objects.count()
    total_employers = User.objects.filter(is_staff=True).count()
    total_job_adverts = JobAdvert.objects.count()
    total_applications = JobApplication.objects.count()
    
    # Calculate success rate (applications that reached INTERVIEW stage)
    interview_applications = JobApplication.objects.filter(status=ApplicationStatus.INTERVIEW).count()
    success_rate = round((interview_applications / total_applications * 100)) if total_applications > 0 else 0
    
    context = {
        'total_users': total_users,
        'total_employers': total_employers,
        'total_job_adverts': total_job_adverts,
        'total_applications': total_applications,
        'success_rate': success_rate,
    }
    
    return render(request, "home.html", context)

@login_required
def create_advert(request: HttpRequest):
    form = JobAdvertForm(request.POST or None)

    if form.is_valid():
        instance: JobAdvert = form.save(commit=False)
        if request.user.is_authenticated:
            instance.created_by = request.user
        instance.save()

        messages.success(request, "Advert created. You can now receive applications.")
        return redirect(instance.get_absolute_url())

    context = {
        "job_advert_form":form,
        "title": "Create a new advert",
        "btn_text": "Create advert"
    }

    return render(request, "create_advert.html", context)
  

def list_adverts(request):
    job_list = JobAdvert.objects.all().order_by('-created_at')
    paginator = Paginator(job_list, 10)
    page_number = request.GET.get('page')
    job_adverts = paginator.get_page(page_number)

    return render(request, 'jobs_list.html', {'job_adverts': job_adverts})



def get_advert(request: HttpRequest, advert_id):
    form = JobApplicationForm()

    job_advert = get_object_or_404(JobAdvert, pk=advert_id)
    context = {
        "job_advert": job_advert,
        "application_form": form,
    }
    return render(request, "advert.html", context)
    
@login_required
def update_advert(request: HttpRequest, advert_id):
    advert: JobAdvert = get_object_or_404(JobAdvert, pk=advert_id)
    if request.user != advert.created_by:
        return HttpResponseForbidden("You can only update an advert created by you.")
    
    form = JobAdvertForm(request.POST or None, instance=advert)
    if form.is_valid():
        instance: JobAdvert = form.save(commit=False)
        instance.save()
        messages.success(request, "Advert updated successfully.")
        return redirect(instance.get_absolute_url())
    
    context = {
        "job_advert_form": form,
        "btn_text": "Update advert"
    }
    return render(request, "create_advert.html", context)
    

@login_required
def delete_advert(request: HttpRequest, advert_id):
    advert: JobAdvert = get_object_or_404(JobAdvert, pk=advert_id)
    if request.user != advert.created_by:
        return HttpResponseForbidden("You can only update an advert created by you.")
    
    advert.delete()
    messages.success(request, "Advert deleted successfully.")
    return redirect("my_jobs")
 


def apply(request: HttpRequest, advert_id):
    advert = get_object_or_404(JobAdvert, pk=advert_id)
    if request.method == "POST":
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            # Prevent duplicate applications for the same email
            email = form.cleaned_data["email"]
            if advert.applications.filter(email__iexact=email).exists():
                messages.error(request, "You have already applied for this position")
                return redirect("job_advert", advert_id=advert_id)
            
            # Save the new application
            application: JobApplication = form.save(commit=False)
            application.job_advert = advert
            application.save()
            messages.success(request, "Application submitted successfully.")
            return redirect("job_advert", advert_id=advert_id)

    else:
        form = JobApplicationForm()
    
    context = {
        "job_advert": advert,
        "application_form": form
    }
    return render(request, "advert.html", context)


@login_required
def my_applications(request: HttpRequest):
    user: User = request.user
    applications = JobApplication.objects.filter(email=user.email)
    
    # Mark all unseen decisions as seen
    JobApplication.objects.filter(
        email=user.email,
        decision_seen=False
    ).exclude(
        status=ApplicationStatus.APPLIED
    ).update(decision_seen=True)
    
    paginator = Paginator(applications, 10)

    requested_page = request.GET.get("page")
    paginated_applications = paginator.get_page(requested_page)

    context = {
        "my_applications": paginated_applications
    }

    return render(request, "my_applications.html", context)


@login_required
def my_jobs(request: HttpRequest):
    user: User = request.user
    jobs = JobAdvert.objects.filter(created_by=user)
    paginator = Paginator(jobs, 10)
    requested_page = request.GET.get("page")
    paginated_jobs = paginator.get_page(requested_page)

    context = {
        "my_jobs": paginated_jobs,
        "current_date": timezone.now().date()
    }

    return render(request, "my_jobs.html",  context)


@login_required
def advert_applications(request: HttpRequest, advert_id):
    advert: JobAdvert = get_object_or_404(JobAdvert, pk=advert_id)
    if request.user != advert.created_by:
        return HttpResponseForbidden("You can only see applications for an advert created by you.")
    
    applications = advert.applications.all()
    #applications = JobApplication.objects.filter(job_advert=advert.id)
    paginator = Paginator(applications, 10)
    requested_page = request.GET.get("page")
    paginated_applications = paginator.get_page(requested_page)

    context = {
        "applications": paginated_applications,
        "advert":advert
    }
    return render(request, "advert_applications.html", context)
    
@login_required
def decide(request: HttpRequest, job_application_id):
    job_application: JobApplication = get_object_or_404(JobApplication, pk=job_application_id)

    if request.user != job_application.job_advert.created_by:
        return HttpResponseForbidden("You can only decide on an advert created by you.")
    
    if request.method == "POST":
        status = request.POST.get("status")
        job_application.status = status
        # Mark as unseen when decision changes (except when changing to APPLIED)
        if status != ApplicationStatus.APPLIED:
            job_application.decision_seen = False
        job_application.save(update_fields=["status", "decision_seen"])
        messages.success(request, f"Application status updated to {status}")

        if status == ApplicationStatus.REJECTED:
            context = {
                "applicant_name":job_application.name,
                "job_title":job_application.job_advert.title,
                "company_name":job_application.job_advert.company_name,
            }
            message = render_to_string("emails/job_application_update.html", context)
            send_mail(
                subject=f"Application Outcome for {job_application.job_advert.title}",
                message=message,
                from_email="noreply@example.com",
                recipient_list=[job_application.email],
            )
        
        return redirect("advert_applications", advert_id=job_application.job_advert.id)


def search(request: HttpRequest):
    keyword = request.GET.get("keyword")
    location = request.GET.get("location")
    result = JobAdvert.objects.search(keyword, location)
    paginator = Paginator(result, 10)
    requested_page = request.GET.get("page")
    paginated_adverts = paginator.get_page(requested_page)

    context = {
        "job_adverts": paginated_adverts
    }
    return render(request, "jobs_list.html", context)



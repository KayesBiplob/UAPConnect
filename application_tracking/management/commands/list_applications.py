from django.core.management.base import BaseCommand
from application_tracking.models import JobApplication


class Command(BaseCommand):
    help = 'List all job applications'

    def handle(self, *args, **options):
        applications = JobApplication.objects.all()
        
        if applications.exists():
            self.stdout.write(self.style.SUCCESS(f'Found {applications.count()} application(s):\n'))
            for app in applications:
                self.stdout.write(
                    f'ID: {app.id} | Name: {app.name} | Email: {app.email} | '
                    f'Job: {app.job_advert.title} | Status: {app.status}'
                )
        else:
            self.stdout.write(self.style.WARNING('No applications found'))

from django.core.management.base import BaseCommand
from application_tracking.models import JobApplication


class Command(BaseCommand):
    help = 'Delete job application by email'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email of the applicant')

    def handle(self, *args, **options):
        email = options['email']
        
        # Find and delete applications with the given email
        applications = JobApplication.objects.filter(email__iexact=email)
        count = applications.count()
        
        if count > 0:
            applications.delete()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted {count} application(s) for email: {email}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'No applications found for email: {email}')
            )

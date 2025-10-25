from django.core.management.base import BaseCommand
from application_tracking.models import JobAdvert


class Command(BaseCommand):
    help = 'Delete test job advert with title "a"'

    def handle(self, *args, **options):
        # Find and delete job adverts with title "a"
        test_jobs = JobAdvert.objects.filter(title__iexact='a')
        count = test_jobs.count()
        
        if count > 0:
            test_jobs.delete()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted {count} test job(s) with title "a"')
            )
        else:
            self.stdout.write(
                self.style.WARNING('No test jobs found with title "a"')
            )

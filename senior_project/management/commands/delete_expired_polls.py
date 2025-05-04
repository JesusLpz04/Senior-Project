from django.core.management.base import BaseCommand
from django.utils import timezone
from FundFlow.models import Poll  

class Command(BaseCommand):
    help = 'Deletes all expired polls from the database'

    def handle(self, *args, **options):
        expired_polls = Poll.objects.filter(expiration_date__lt=timezone.now())
        count = expired_polls.count()
        expired_polls.delete()
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {count} expired polls')
        )
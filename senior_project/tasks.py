from celery import shared_task
from django.utils import timezone
from ..FundFlow.models import Poll

@shared_task
def delete_expired_polls():
    """Task to delete expired polls from the database"""
    expired_polls = Poll.objects.filter(expiration_date__lt=timezone.now())
    count = expired_polls.count()
    expired_polls.delete()
    return f'Successfully deleted {count} expired polls'
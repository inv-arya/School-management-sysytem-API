from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from chats.models import ChatRequest


class Command(BaseCommand):
    help = "Delete chat requests that were cancelled more than 2 days ago"

    def handle(self, *args, **kwargs):
        two_days_ago = timezone.now() - timedelta(days=2)

        expired_chats = ChatRequest.objects.filter(
            status=ChatRequest.STATUS_CANCELLED,
            cancelled_at__lte=two_days_ago
        )

        count = expired_chats.count()
        expired_chats.delete()

        self.stdout.write(self.style.SUCCESS(f"Deleted {count} cancelled chats older than 2 days"))

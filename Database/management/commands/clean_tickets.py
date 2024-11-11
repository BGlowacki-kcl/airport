from django.core.management.base import BaseCommand
from Database.models import Ticket, Flight

class Command(BaseCommand):
    help = 'Clean up tickets with no associated flight'

    def handle(self, *args, **kwargs):
        tickets_deleted = Ticket.objects.filter(flight__isnull=True).delete()
        tickets_deleted = Ticket.objects.filter(passenger__isnull=True).delete()
        self.stdout.write(self.style.SUCCESS(f'{tickets_deleted[0]} tickets deleted with no associated flight.'))
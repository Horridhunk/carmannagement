from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from clients.models import Client, Vehicle, WashOrder
from washers.models import Washer


class Command(BaseCommand):
    help = 'Reset the database by deleting all data (use with caution!)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to delete all data',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This command will delete ALL data from the database!\n'
                    'Use --confirm flag to proceed: python manage.py reset_db --confirm'
                )
            )
            return

        self.stdout.write('Deleting all data...')

        try:
            # Delete in order to avoid foreign key constraints
            deleted_counts = {}
            
            # Delete orders first
            count = WashOrder.objects.count()
            WashOrder.objects.all().delete()
            deleted_counts['Orders'] = count

            # Delete vehicles
            count = Vehicle.objects.count()
            Vehicle.objects.all().delete()
            deleted_counts['Vehicles'] = count

            # Delete clients
            count = Client.objects.count()
            Client.objects.all().delete()
            deleted_counts['Clients'] = count

            # Delete washers
            count = Washer.objects.count()
            Washer.objects.all().delete()
            deleted_counts['Washers'] = count

            # Delete non-superuser users (keep admin users)
            count = User.objects.filter(is_superuser=False).count()
            User.objects.filter(is_superuser=False).delete()
            deleted_counts['Users (non-admin)'] = count

            # Summary
            self.stdout.write(
                self.style.SUCCESS('Successfully deleted all data:')
            )
            for model, count in deleted_counts.items():
                self.stdout.write(f'  - {count} {model}')

            self.stdout.write(
                self.style.WARNING('Admin users (superusers) were preserved.')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error resetting database: {e}')
            )
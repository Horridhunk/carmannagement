from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta, time
from clients.models import TimeSlot

class Command(BaseCommand):
    help = 'Create time slots for car wash appointments'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to create time slots for (default: 30)'
        )

    def handle(self, *args, **options):
        days = options['days']
        
        # Define time slots for each day
        time_slots = [
            (time(8, 0), time(9, 0)),    # 8:00 AM - 9:00 AM
            (time(9, 0), time(10, 0)),   # 9:00 AM - 10:00 AM
            (time(10, 0), time(11, 0)),  # 10:00 AM - 11:00 AM
            (time(11, 0), time(12, 0)),  # 11:00 AM - 12:00 PM
            (time(13, 0), time(14, 0)),  # 1:00 PM - 2:00 PM
            (time(14, 0), time(15, 0)),  # 2:00 PM - 3:00 PM
            (time(15, 0), time(16, 0)),  # 3:00 PM - 4:00 PM
            (time(16, 0), time(17, 0)),  # 4:00 PM - 5:00 PM
        ]
        
        start_date = timezone.now().date()
        created_count = 0
        
        for day in range(days):
            current_date = start_date + timedelta(days=day)
            
            # Skip Sundays (weekday 6)
            if current_date.weekday() == 6:
                continue
            
            for start_time, end_time in time_slots:
                # Check if time slot already exists
                if not TimeSlot.objects.filter(
                    date=current_date,
                    start_time=start_time
                ).exists():
                    TimeSlot.objects.create(
                        date=current_date,
                        start_time=start_time,
                        end_time=end_time,
                        max_capacity=3,  # 3 appointments per slot
                        is_active=True
                    )
                    created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} time slots for the next {days} days'
            )
        )
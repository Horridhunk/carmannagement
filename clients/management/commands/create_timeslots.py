from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta, time
from clients.models import TimeSlot

class Command(BaseCommand):
    help = 'Create time slots from 8:00 AM to 6:00 PM for specified days'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to create time slots for (default: 30)'
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=60,
            help='Time slot duration in minutes (default: 60)'
        )

    def handle(self, *args, **options):
        days = options['days']
        interval = options['interval']
        
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=days)
        
        current_date = start_date
        created_count = 0
        skipped_count = 0
        
        while current_date < end_date:
            # Skip weekends if needed (optional - remove if you want 7 days/week)
            # if current_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
            #     current_date += timedelta(days=1)
            #     continue
            
            # Create time slots for this day
            current_time = time(8, 0)  # 8:00 AM
            end_time = time(18, 0)  # 6:00 PM
            
            while current_time < end_time:
                # Calculate end time for this slot
                slot_end_datetime = datetime.combine(current_date, current_time) + timedelta(minutes=interval)
                slot_end_time = slot_end_datetime.time()
                
                # Don't create slots that go past 6:00 PM
                if slot_end_time > end_time:
                    break
                
                # Check if slot already exists
                slot_exists = TimeSlot.objects.filter(
                    date=current_date,
                    start_time=current_time,
                    end_time=slot_end_time
                ).exists()
                
                if not slot_exists:
                    TimeSlot.objects.create(
                        date=current_date,
                        start_time=current_time,
                        end_time=slot_end_time,
                        max_capacity=3,
                        is_active=True
                    )
                    created_count += 1
                else:
                    skipped_count += 1
                
                # Move to next slot
                current_time = slot_end_time
            
            current_date += timedelta(days=1)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} time slots. '
                f'Skipped {skipped_count} existing slots.'
            )
        )

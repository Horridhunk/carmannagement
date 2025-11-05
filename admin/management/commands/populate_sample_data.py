from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from clients.models import Client, Vehicle, WashOrder
from washers.models import Washer
from django.utils import timezone
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Populate the database with sample data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clients',
            type=int,
            default=10,
            help='Number of sample clients to create'
        )
        parser.add_argument(
            '--washers',
            type=int,
            default=5,
            help='Number of sample washers to create'
        )
        parser.add_argument(
            '--orders',
            type=int,
            default=20,
            help='Number of sample orders to create'
        )

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Sample data
        client_names = [
            ('John', 'Doe'), ('Jane', 'Smith'), ('Mike', 'Johnson'),
            ('Sarah', 'Williams'), ('David', 'Brown'), ('Lisa', 'Davis'),
            ('Chris', 'Miller'), ('Amy', 'Wilson'), ('Tom', 'Moore'),
            ('Emma', 'Taylor'), ('James', 'Anderson'), ('Maria', 'Garcia')
        ]

        washer_names = [
            ('Alex', 'Rodriguez'), ('Sam', 'Thompson'), ('Jordan', 'Lee'),
            ('Casey', 'White'), ('Morgan', 'Clark'), ('Taylor', 'Lewis'),
            ('Jamie', 'Walker'), ('Riley', 'Hall')
        ]

        car_makes = ['Toyota', 'Honda', 'Ford', 'BMW', 'Mercedes', 'Audi', 'Nissan', 'Hyundai']
        car_models = ['Sedan', 'SUV', 'Hatchback', 'Coupe', 'Truck', 'Convertible']
        wash_types = ['basic', 'premium', 'deluxe', 'express']
        statuses = ['pending', 'in_progress', 'completed', 'cancelled']

        # Create clients
        clients_created = 0
        for i in range(options['clients']):
            if i < len(client_names):
                first_name, last_name = client_names[i]
            else:
                first_name, last_name = f'Client{i}', f'User{i}'

            try:
                # Create Django User first
                username = f'{first_name.lower()}{last_name.lower()}{i}'
                email = f'{username}@example.com'
                
                if not User.objects.filter(username=username).exists():
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password='password123',
                        first_name=first_name,
                        last_name=last_name
                    )

                    # Create Client
                    client = Client.objects.create(
                        user=user,
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        phone=f'+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
                        address=f'{random.randint(100, 9999)} Main St, City, State {random.randint(10000, 99999)}'
                    )

                    # Create 1-2 vehicles for each client
                    for v in range(random.randint(1, 2)):
                        Vehicle.objects.create(
                            client=client,
                            make=random.choice(car_makes),
                            model=random.choice(car_models),
                            year=random.randint(2010, 2024),
                            license_plate=f'{random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")}{random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")}{random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")}-{random.randint(100, 999)}',
                            color=random.choice(['Red', 'Blue', 'Black', 'White', 'Silver', 'Gray'])
                        )

                    clients_created += 1

            except Exception as e:
                self.stdout.write(f'Error creating client {first_name} {last_name}: {e}')

        # Create washers
        washers_created = 0
        for i in range(options['washers']):
            if i < len(washer_names):
                first_name, last_name = washer_names[i]
            else:
                first_name, last_name = f'Washer{i}', f'Staff{i}'

            try:
                # Create Django User first
                username = f'{first_name.lower()}{last_name.lower()}_washer{i}'
                email = f'{username}@carwash.com'
                
                if not User.objects.filter(username=username).exists():
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password='password123',
                        first_name=first_name,
                        last_name=last_name
                    )

                    # Create Washer
                    Washer.objects.create(
                        user=user,
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        phone=f'+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
                        hire_date=timezone.now().date(),
                        hourly_rate=Decimal(f'{random.randint(15, 25)}.{random.randint(0, 99):02d}'),
                        is_available=random.choice([True, False])
                    )

                    washers_created += 1

            except Exception as e:
                self.stdout.write(f'Error creating washer {first_name} {last_name}: {e}')

        # Create orders
        orders_created = 0
        clients = list(Client.objects.all())
        washers = list(Washer.objects.all())
        
        if clients:
            for i in range(options['orders']):
                try:
                    client = random.choice(clients)
                    vehicles = list(client.vehicles.all())
                    
                    if vehicles:
                        vehicle = random.choice(vehicles)
                        washer = random.choice(washers) if washers and random.choice([True, False]) else None
                        
                        # Create order with random date in the last 30 days
                        order_date = timezone.now() - timezone.timedelta(days=random.randint(0, 30))
                        
                        WashOrder.objects.create(
                            client=client,
                            vehicle=vehicle,
                            washer=washer,
                            wash_type=random.choice(wash_types),
                            status=random.choice(statuses),
                            price=Decimal(f'{random.randint(20, 100)}.{random.randint(0, 99):02d}'),
                            scheduled_time=order_date,
                            created_at=order_date,
                            notes=f'Sample order #{i+1} for testing purposes'
                        )
                        
                        orders_created += 1

                except Exception as e:
                    self.stdout.write(f'Error creating order {i+1}: {e}')

        # Summary
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created sample data:')
        )
        self.stdout.write(f'  - {clients_created} clients')
        self.stdout.write(f'  - {washers_created} washers')
        self.stdout.write(f'  - {orders_created} orders')
        self.stdout.write(f'  - {Vehicle.objects.count()} vehicles')
        
        self.stdout.write(
            self.style.WARNING('Sample users created with password: password123')
        )
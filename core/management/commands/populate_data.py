from django.core.management.base import BaseCommand
from core.models import Customer, Transaction
from django.utils import timezone
from django.db import transaction

class Command(BaseCommand):
    help = 'Populates the database with sample customer and transaction data.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Populating sample data...'))

        try:
            with transaction.atomic():
                # Create sample customers
                customer1, created = Customer.objects.get_or_create(
                    Account='ACC001234567890', # Updated to 15 chars
                    defaults={'Name': 'Alice Smith', 'Balance': 1500.00}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created customer: {customer1.Name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Customer {customer1.Name} already exists.'))

                customer2, created = Customer.objects.get_or_create(
                    Account='ACC002345678901', # Updated to 15 chars
                    defaults={'Name': 'Bob Johnson', 'Balance': 250.75}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created customer: {customer2.Name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Customer {customer2.Name} already exists.'))

                # Generate unique references for transactions
                next_ref_num = Transaction.objects.count() + 1

                Transaction.objects.create(
                    Account=customer1,
                    Date=timezone.now(), # Added Date field
                    Amount=100.00,
                    DC='D',
                    Reference=f'INV{next_ref_num:07d}' # Added Reference field with unique value
                )
                self.stdout.write(self.style.SUCCESS(f'Created transaction for {customer1.Name}'))
                next_ref_num += 1

                Transaction.objects.create(
                    Account=customer1,
                    Date=timezone.now(), # Added Date field
                    Amount=50.00,
                    DC='C',
                    Reference=f'INV{next_ref_num:07d}' # Added Reference field with unique value
                )
                self.stdout.write(self.style.SUCCESS(f'Created transaction for {customer1.Name}'))
                next_ref_num += 1

                Transaction.objects.create(
                    Account=customer2,
                    Date=timezone.now(), # Added Date field
                    Amount=200.00,
                    DC='D',
                    Reference=f'INV{next_ref_num:07d}' # Added Reference field with unique value
                )
                self.stdout.write(self.style.SUCCESS('Sample data population complete.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))
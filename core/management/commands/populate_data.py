from django.core.management.base import BaseCommand
from core.models import Customer, Transaction

class Command(BaseCommand):
    help = 'Populates the database with sample customer and transaction data.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Populating sample data...'))

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

        # Create sample transactions
        Transaction.objects.create(
            Account=customer1,
            Amount=100.00,
            DC='D',
            Reference='REF0000001' # Added Reference field
        )
        self.stdout.write(self.style.SUCCESS(f'Created transaction for {customer1.Name}'))

        Transaction.objects.create(
            Account=customer1,
            Amount=50.00,
            DC='C',
            Reference='REF0000002' # Added Reference field
        )
        self.stdout.write(self.style.SUCCESS(f'Created transaction for {customer1.Name}'))

        Transaction.objects.create(
            Account=customer2,
            Amount=200.00,
            DC='D',
            Reference='REF0000003' # Added Reference field
        )
        self.stdout.write(self.style.SUCCESS(f'Created transaction for {customer2.Name}'))

        self.stdout.write(self.style.SUCCESS('Sample data population complete.'))
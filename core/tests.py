from django.test import TestCase
from core.models import Customer, Transaction
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone

class CustomerModelTest(TestCase):

    def test_customer_creation(self):
        customer = Customer.objects.create(
            Account='TEST00123456789',
            Name='Test Customer',
            Balance=Decimal('1000.00')
        )
        self.assertEqual(customer.Account, 'TEST00123456789')
        self.assertEqual(customer.Name, 'Test Customer')
        self.assertEqual(customer.Balance, Decimal('1000.00'))

    def test_customer_account_validation(self):
        # Test invalid length
        customer = Customer(
            Account='TOO_SHORT',
            Name='Invalid Customer',
            Balance=Decimal('100.00')
        )
        with self.assertRaises(ValidationError):
            customer.full_clean()

        customer = Customer(
            Account='TOO_LONG_1234567890',
            Name='Invalid Customer',
            Balance=Decimal('100.00')
        )
        with self.assertRaises(ValidationError):
            customer.full_clean()

        # Test invalid characters
        customer = Customer(
            Account='INVALID-CHARS!!',
            Name='Invalid Customer',
            Balance=Decimal('100.00')
        )
        with self.assertRaises(ValidationError):
            customer.full_clean()

    def test_customer_str(self):
        customer = Customer.objects.create(
            Account='TEST00234567890',
            Name='Another Customer',
            Balance=Decimal('500.50')
        )
        self.assertEqual(str(customer), 'Another Customer')

class TransactionModelTest(TestCase):

    def setUp(self):
        self.customer = Customer.objects.create(
            Account='CUST00123456789',
            Name='Transaction Customer',
            Balance=Decimal('2000.00')
        )

    def test_transaction_creation(self):
        transaction = Transaction.objects.create(
            Account=self.customer,
            Date=timezone.now(),
            Amount=Decimal('150.00'),
            DC='D',
            Reference='REF1234567'
        )
        self.assertEqual(transaction.Account, self.customer)
        self.assertEqual(transaction.Amount, Decimal('150.00'))
        self.assertEqual(transaction.DC, 'D')
        self.assertEqual(transaction.Reference, 'REF1234567')
        self.assertIsNotNone(transaction.Number)
        self.assertIsNotNone(transaction.Date)

    def test_transaction_reference_validation(self):
        # Test invalid length
        transaction = Transaction(
            Account=self.customer,
            Amount=Decimal('10.00'),
            DC='C',
            Reference='SHORT'
        )
        with self.assertRaises(ValidationError):
            transaction.full_clean()

        transaction = Transaction(
            Account=self.customer,
            Amount=Decimal('10.00'),
            DC='C',
            Reference='TOO_LONG_REF123'
        )
        with self.assertRaises(ValidationError):
            transaction.full_clean()

        # Test invalid characters
        transaction = Transaction(
            Account=self.customer,
            Amount=Decimal('10.00'),
            DC='C',
            Reference='INVALID-REF!'
        )
        with self.assertRaises(ValidationError):
            transaction.full_clean()

    def test_transaction_str(self):
        transaction = Transaction.objects.create(
            Account=self.customer,
            Date=timezone.now(),
            Amount=Decimal('75.00'),
            DC='C',
            Reference='REF9876543'
        )
        self.assertEqual(str(transaction), f'Transaction {transaction.Number} for {self.customer.Account}')

    def test_transaction_dc_display(self):
        transaction_debit = Transaction.objects.create(
            Account=self.customer,
            Date=timezone.now(),
            Amount=Decimal('100.00'),
            DC='D',
            Reference='REF1111111'
        )
        transaction_credit = Transaction.objects.create(
            Account=self.customer,
            Date=timezone.now(),
            Amount=Decimal('200.00'),
            DC='C',
            Reference='REF2222222'
        )
        self.assertEqual(transaction_debit.get_DC_display(), 'Debit')
        self.assertEqual(transaction_credit.get_DC_display(), 'Credit')

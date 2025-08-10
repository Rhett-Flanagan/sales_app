from django.test import TestCase
from core.models import Customer, Transaction
from decimal import Decimal

class CustomerModelTest(TestCase):

    def test_customer_creation(self):
        customer = Customer.objects.create(
            Account='TEST001',
            Name='Test Customer',
            Balance=Decimal('1000.00')
        )
        self.assertEqual(customer.Account, 'TEST001')
        self.assertEqual(customer.Name, 'Test Customer')
        self.assertEqual(customer.Balance, Decimal('1000.00'))

    def test_customer_str(self):
        customer = Customer.objects.create(
            Account='TEST002',
            Name='Another Customer',
            Balance=Decimal('500.50')
        )
        self.assertEqual(str(customer), 'Another Customer')

class TransactionModelTest(TestCase):

    def setUp(self):
        self.customer = Customer.objects.create(
            Account='CUST001',
            Name='Transaction Customer',
            Balance=Decimal('2000.00')
        )

    def test_transaction_creation(self):
        transaction = Transaction.objects.create(
            Account=self.customer,
            Amount=Decimal('150.00'),
            DC='D'
        )
        self.assertEqual(transaction.Account, self.customer)
        self.assertEqual(transaction.Amount, Decimal('150.00'))
        self.assertEqual(transaction.DC, 'D')
        self.assertIsNotNone(transaction.Number)
        self.assertIsNotNone(transaction.Date)

    def test_transaction_str(self):
        transaction = Transaction.objects.create(
            Account=self.customer,
            Amount=Decimal('75.00'),
            DC='C'
        )
        self.assertEqual(str(transaction), f'Transaction {transaction.Number} for {self.customer.Account}')

    def test_transaction_dc_display(self):
        transaction_debit = Transaction.objects.create(
            Account=self.customer,
            Amount=Decimal('100.00'),
            DC='D'
        )
        transaction_credit = Transaction.objects.create(
            Account=self.customer,
            Amount=Decimal('200.00'),
            DC='C'
        )
        self.assertEqual(transaction_debit.get_DC_display(), 'Debit')
        self.assertEqual(transaction_credit.get_DC_display(), 'Credit')
from django.test import TestCase, Client
from django.urls import reverse
from core.models import Customer, Transaction
from decimal import Decimal
from datetime import datetime
from django.utils import timezone

class CustomerViewsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.customer1 = Customer.objects.create(
            Account='CUST00123456789',
            Name='Alpha Customer',
            Balance=Decimal('1000.00')
        )
        self.customer2 = Customer.objects.create(
            Account='CUST00987654321',
            Name='Beta Customer',
            Balance=Decimal('2000.00')
        )

    def test_customer_list_view(self):
        response = self.client.get(reverse('customer_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/customer_list.html')
        self.assertContains(response, self.customer1.Name)
        self.assertContains(response, self.customer2.Name)

    def test_customer_list_view_search(self):
        response = self.client.get(reverse('customer_list'), {'q': 'Alpha'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.customer1.Name)
        self.assertNotContains(response, self.customer2.Name)

    def test_customer_list_view_sort(self):
        response = self.client.get(reverse('customer_list'), {'sort_by': 'Name', 'order': 'desc'})
        self.assertEqual(response.status_code, 200)
        # Assuming Beta comes after Alpha, so with desc order, Beta should appear first
        self.assertIn(self.customer2, response.context['customers'])
        self.assertIn(self.customer1, response.context['customers'])
        self.assertTrue(response.context['customers'][0].Name == 'Beta Customer')
        self.assertTrue(response.context['customers'][1].Name == 'Alpha Customer')

    def test_customer_create_view(self):
        response = self.client.post(reverse('customer_add'), {
            'Account': 'NEWCUST12345678',
            'Name': 'New Customer',
            'Balance': '500.00'
        })
        self.assertEqual(response.status_code, 302) # Redirects on success
        self.assertTrue(Customer.objects.filter(Account='NEWCUST12345678').exists())

    def test_customer_update_view(self):
        response = self.client.post(reverse('customer_edit', args=[self.customer1.pk]), {
            'Account': self.customer1.Account,
            'Name': 'Updated Alpha Customer',
            'Balance': self.customer1.Balance
        })
        self.assertEqual(response.status_code, 302) # Redirects on success
        self.customer1.refresh_from_db()
        self.assertEqual(self.customer1.Name, 'Updated Alpha Customer')

    def test_customer_delete_view(self):
        response = self.client.post(reverse('customer_delete', args=[self.customer1.pk]))
        self.assertEqual(response.status_code, 302) # Redirects on success
        self.assertFalse(Customer.objects.filter(pk=self.customer1.pk).exists())

class TransactionViewsTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_transaction_list_view(self):
        customer = Customer.objects.create(Account='CUST001', Name='Test', Balance=Decimal('1000.00'))
        transaction = Transaction.objects.create(
            Account=customer,
            Date=timezone.now(),
            Amount=Decimal('100.00'),
            DC='D',
            Reference='REF1234567'
        )
        response = self.client.get(reverse('transaction_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/transaction_list.html')
        self.assertContains(response, transaction.Reference)

    def test_transaction_list_view_search(self):
        customer = Customer.objects.create(Account='CUST002', Name='Test', Balance=Decimal('1000.00'))
        transaction = Transaction.objects.create(
            Account=customer,
            Date=timezone.now(),
            Amount=Decimal('100.00'),
            DC='D',
            Reference='REF1234567'
        )
        response = self.client.get(reverse('transaction_list'), {'q': 'REF1234567'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, transaction.Reference)

    def test_transaction_list_view_filter_by_date(self):
        customer = Customer.objects.create(Account='CUST003', Name='Test', Balance=Decimal('1000.00'))
        transaction = Transaction.objects.create(
            Account=customer,
            Date=datetime(2025, 8, 11, 12, 0, 0),
            Amount=Decimal('100.00'),
            DC='D',
            Reference='REF1234567'
        )
        response = self.client.get(reverse('transaction_list'), {'start_date': '2025-08-11', 'end_date': '2025-08-11'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, transaction.Reference)

    def test_transaction_create_view_updates_balance(self):
        customer = Customer.objects.create(Account='CUST004', Name='Test', Balance=Decimal('1000.00'))
        initial_balance = customer.Balance
        response = self.client.post(reverse('transaction_add'), {
            'Account': customer.Account,
            'Date': '2025-08-11 12:00:00',
            'Amount': '50.00',
            'DC': 'C',
            'Reference': 'NEWREF1234'
        })
        self.assertEqual(response.status_code, 302)
        customer.refresh_from_db()
        self.assertEqual(customer.Balance, initial_balance - Decimal('50.00'))

    def test_transaction_update_view_updates_balance(self):
        customer = Customer.objects.create(Account='CUST005', Name='Test', Balance=Decimal('1000.00'))
        # First, create a transaction to be updated
        response = self.client.post(reverse('transaction_add'), {
            'Account': customer.Account,
            'Date': '2025-08-11 12:00:00',
            'Amount': '100.00',
            'DC': 'D',
            'Reference': 'REF1234567'
        })
        self.assertEqual(response.status_code, 302)
        transaction = Transaction.objects.get(Reference='REF1234567')

        # Now, update the transaction
        response = self.client.post(reverse('transaction_edit', args=[transaction.pk]), {
            'Account': customer.Account,
            'Date': transaction.Date.strftime('%Y-%m-%d %H:%M:%S'),
            'Amount': '150.00',
            'DC': 'C',
            'Reference': transaction.Reference
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        customer.refresh_from_db()
        self.assertEqual(customer.Balance, Decimal('850.00'))

    def test_transaction_delete_view_updates_balance(self):
        customer = Customer.objects.create(Account='CUST006', Name='Test', Balance=Decimal('1000.00'))
        transaction = Transaction.objects.create(
            Account=customer,
            Date=timezone.now(),
            Amount=Decimal('100.00'),
            DC='D',
            Reference='REF1234567'
        )
        customer.Balance += transaction.Amount
        customer.save()

        response = self.client.post(reverse('transaction_delete', args=[transaction.pk]))
        self.assertEqual(response.status_code, 302)
        customer.refresh_from_db()
        self.assertEqual(customer.Balance, Decimal('1000.00'))

    def test_bulk_add_transactions_view(self):
        customer = Customer.objects.create(Account='CUST007', Name='Test', Balance=Decimal('1000.00'))
        initial_balance = customer.Balance
        response = self.client.post(reverse('bulk_add_transactions'), {
            'form-0-Account': customer.Account,
            'form-0-Date': '2025-08-11 12:00:00',
            'form-0-Amount': '20.00',
            'form-0-DC': 'D',
            'form-0-Reference': 'BULKREF001',
            'form-1-Account': customer.Account,
            'form-1-Date': '2025-08-11 12:01:00',
            'form-1-Amount': '30.00',
            'form-1-DC': 'C',
            'form-1-Reference': 'BULKREF002',
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
        })
        self.assertEqual(response.status_code, 302)
        customer.refresh_from_db()
        self.assertEqual(customer.Balance, initial_balance + Decimal('20.00') - Decimal('30.00'))
        self.assertTrue(Transaction.objects.filter(Reference='BULKREF001').exists())
        self.assertTrue(Transaction.objects.filter(Reference='BULKREF002').exists())

class EnquiryViewsTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_enquiry_customer_list_view(self):
        customer = Customer.objects.create(Account='CUST008', Name='Enquiry Customer', Balance=Decimal('5000.00'))
        response = self.client.get(reverse('enquiry_customer_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/enquiry_customer_list.html')
        self.assertContains(response, customer.Name)

    def test_enquiry_transaction_details_view(self):
        customer = Customer.objects.create(Account='CUST009', Name='Enquiry Customer', Balance=Decimal('5000.00'))
        transaction = Transaction.objects.create(
            Account=customer,
            Date=timezone.now(),
            Amount=Decimal('500.00'),
            DC='D',
            Reference='ENQREF1234'
        )
        response = self.client.get(reverse('enquiry_transaction_details', args=[customer.Account]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/enquiry_transaction_details.html')
        self.assertContains(response, customer.Name)
        self.assertContains(response, transaction.Reference)

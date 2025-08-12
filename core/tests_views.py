from django.test import TestCase, Client
from unittest.mock import patch
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

        # Test with fuzzy search terms
        customer_alice = Customer.objects.create(Account='CUSTALICE0000', Name='Alice Smith', Balance=Decimal('100.00'))
        response = self.client.get(reverse('customer_list'), {'q': 'alice'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, customer_alice.Name)

        response = self.client.get(reverse('customer_list'), {'q': 'smith'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, customer_alice.Name)

    def test_customer_list_view_sort(self):
        response = self.client.get(reverse('customer_list'), {'sort_by': 'Name', 'order': 'desc'})
        self.assertEqual(response.status_code, 200)
        # Assuming Beta comes after Alpha, so with desc order, Beta should appear first
        self.assertIn(self.customer2, response.context['customers'])
        self.assertIn(self.customer1, response.context['customers'])
        self.assertTrue(response.context['customers'][0].Name == 'Beta Customer')
        self.assertTrue(response.context['customers'][1].Name == 'Alpha Customer')

    def test_customer_list_view_multi_sort(self):
        # Create a third customer with the same name as customer1 but different account
        customer3 = Customer.objects.create(
            Account='CUST00555555555',
            Name='Alpha Customer',
            Balance=Decimal('1500.00')
        )
        
        # Test sorting by Name ascending, then by Balance descending
        response = self.client.get(reverse('customer_list'), {
            'sort_by': ['Name', 'Balance'],
            'order': ['asc', 'desc']
        })
        self.assertEqual(response.status_code, 200)
        
        # Check that the context contains the sort parameters
        self.assertIn('sort_fields', response.context)
        self.assertIn('sort_orders', response.context)
        self.assertEqual(response.context['sort_fields'], ['Name', 'Balance'])
        self.assertEqual(response.context['sort_orders'], ['asc', 'desc'])
        
        # Check that customers are sorted correctly
        customers = list(response.context['customers'])
        # Both Alpha customers should come before Beta customer
        self.assertEqual(customers[0].Name, 'Alpha Customer')
        self.assertEqual(customers[1].Name, 'Alpha Customer')
        self.assertEqual(customers[2].Name, 'Beta Customer')
        # The Alpha customer with higher balance should come first
        self.assertTrue(customers[0].Balance > customers[1].Balance)

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

        # Test with fuzzy search terms for transactions
        customer_smith = Customer.objects.create(Account='CUSTSMITH000', Name='John Smith', Balance=Decimal('100.00'))
        transaction_smith = Transaction.objects.create(
            Account=customer_smith,
            Date=timezone.now(),
            Amount=Decimal('50.00'),
            DC='D',
            Reference='SMITHREF00'
        )
        response = self.client.get(reverse('transaction_list'), {'q': 'smith'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, transaction_smith.Reference)

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

    def test_transaction_list_view_multi_sort(self):
        customer = Customer.objects.create(Account='CUST010', Name='Test', Balance=Decimal('3000.00'))
        
        # Create transactions with different dates and amounts
        transaction1 = Transaction.objects.create(
            Account=customer,
            Date=datetime(2025, 8, 11, 12, 0, 0),
            Amount=Decimal('100.00'),
            DC='D',
            Reference='REF1111111'
        )
        transaction2 = Transaction.objects.create(
            Account=customer,
            Date=datetime(2025, 8, 11, 12, 0, 0),
            Amount=Decimal('200.00'),
            DC='C',
            Reference='REF2222222'
        )
        transaction3 = Transaction.objects.create(
            Account=customer,
            Date=datetime(2025, 8, 12, 12, 0, 0),
            Amount=Decimal('100.00'),
            DC='D',
            Reference='REF3333333'
        )
        
        # Test sorting by Date ascending, then by Amount descending
        response = self.client.get(reverse('transaction_list'), {
            'sort_by': ['Date', 'Amount'],
            'order': ['asc', 'desc']
        })
        self.assertEqual(response.status_code, 200)
        
        # Check that the context contains the sort parameters
        self.assertIn('sort_fields', response.context)
        self.assertIn('sort_orders', response.context)
        self.assertEqual(response.context['sort_fields'], ['Date', 'Amount'])
        self.assertEqual(response.context['sort_orders'], ['asc', 'desc'])
        
        # Check that transactions are sorted correctly
        transactions = list(response.context['transactions'])
        # First two transactions have the same date, so they should be sorted by amount (desc)
        self.assertEqual(transactions[0].Number, transaction2.Number)  # Higher amount first
        self.assertEqual(transactions[1].Number, transaction1.Number)  # Lower amount second
        self.assertEqual(transactions[2].Number, transaction3.Number)  # Later date last

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

    def test_transaction_update_view_updates_balance_credit_to_debit(self):
        customer = Customer.objects.create(Account='CUST005C', Name='TestC', Balance=Decimal('1000.00'))
        # First, create a transaction with DC='C'
        response = self.client.post(reverse('transaction_add'), {
            'Account': customer.Account,
            'Date': '2025-08-11 12:00:00',
            'Amount': '100.00',
            'DC': 'C',
            'Reference': 'REF123456C'
        })
        self.assertEqual(response.status_code, 302)
        transaction = Transaction.objects.get(Reference='REF123456C')
        customer.refresh_from_db()
        self.assertEqual(customer.Balance, Decimal('900.00')) # 1000 - 100

        # Now, update the transaction to DC='D'
        response = self.client.post(reverse('transaction_edit', args=[transaction.pk]), {
            'Account': customer.Account,
            'Date': transaction.Date.strftime('%Y-%m-%d %H:%M:%S'),
            'Amount': '150.00',
            'DC': 'D',
            'Reference': transaction.Reference
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        customer.refresh_from_db()
        # Original: 1000 - 100 = 900
        # Revert original: 900 + 100 = 1000
        # Apply new: 1000 + 150 = 1150
        self.assertEqual(customer.Balance, Decimal('1150.00'))

    def test_transaction_update_view_updates_balance_debit_to_debit(self):
        customer = Customer.objects.create(Account='CUST005D', Name='TestD', Balance=Decimal('1000.00'))
        # First, create a transaction with DC='D'
        response = self.client.post(reverse('transaction_add'), {
            'Account': customer.Account,
            'Date': '2025-08-11 12:00:00',
            'Amount': '100.00',
            'DC': 'D',
            'Reference': 'REF123456D'
        })
        self.assertEqual(response.status_code, 302)
        transaction = Transaction.objects.get(Reference='REF123456D')
        customer.refresh_from_db()
        self.assertEqual(customer.Balance, Decimal('1100.00')) # 1000 + 100

        # Now, update the transaction to DC='D' with different amount
        response = self.client.post(reverse('transaction_edit', args=[transaction.pk]), {
            'Account': customer.Account,
            'Date': transaction.Date.strftime('%Y-%m-%d %H:%M:%S'),
            'Amount': '150.00',
            'DC': 'D',
            'Reference': transaction.Reference
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        customer.refresh_from_db()
        # Original: 1000 + 100 = 1100
        # Revert original: 1100 - 100 = 1000
        # Apply new: 1000 + 150 = 1150
        self.assertEqual(customer.Balance, Decimal('1150.00'))

    def test_transaction_update_view_updates_balance_credit_to_credit(self):
        customer = Customer.objects.create(Account='CUST005CC', Name='TestCC', Balance=Decimal('2000.00'))
        # First, create a transaction with DC='C'
        response = self.client.post(reverse('transaction_add'), {
            'Account': customer.Account,
            'Date': '2025-08-11 12:00:00',
            'Amount': '100.00',
            'DC': 'C',
            'Reference': 'REF1234CC'
        })
        self.assertEqual(response.status_code, 302)
        transaction = Transaction.objects.get(Reference='REF1234CC')
        customer.refresh_from_db()
        self.assertEqual(customer.Balance, Decimal('1900.00')) # 2000 - 100

        # Now, update the transaction to DC='C' with different amount
        form_data = {
            'Account': customer.Account,
            'Date': transaction.Date.strftime('%Y-%m-%d %H:%M:%S'),
            'Amount': '150.00',
            'DC': 'C',
            'Reference': transaction.Reference
        }
        response = self.client.post(reverse('transaction_edit', args=[transaction.pk]), form_data)
        print(response.context['form'].errors)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Customer does not have enough balance for this transaction.")

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

    def test_transaction_delete_view_updates_balance_credit(self):
        customer = Customer.objects.create(Account='CUST006C', Name='TestC', Balance=Decimal('1000.00'))
        transaction = Transaction.objects.create(
            Account=customer,
            Date=timezone.now(),
            Amount=Decimal('100.00'),
            DC='C',
            Reference='REF123456C'
        )
        # Manually update balance to simulate a prior transaction
        customer.Balance -= transaction.Amount # 1000 - 100 = 900
        customer.save()

        response = self.client.post(reverse('transaction_delete', args=[transaction.pk]))
        self.assertEqual(response.status_code, 302)
        customer.refresh_from_db()
        self.assertEqual(customer.Balance, Decimal('1000.00')) # Should revert to 1000

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

    @patch('core.forms.TransactionForm.save')
    def test_transaction_create_view_form_save_error(self, mock_save):
        mock_save.side_effect = Exception("Simulated save error")
        customer = Customer.objects.create(Account='CUST008', Name='Test Error Customer', Balance=Decimal('1000.00'))
        response = self.client.post(reverse('transaction_add'), {
            'Account': customer.Account,
            'Date': '2025-08-11 12:00:00',
            'Amount': '50.00',
            'DC': 'D',
            'Reference': 'ERRORREF00'
        })
        

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.urls import reverse_lazy
from core.models import Customer, Transaction
from django.db.models import Q
from core.forms import CustomerForm, TransactionForm
from django.forms import formset_factory
from django.utils import timezone
from decimal import Decimal
from django.db import transaction as db_transaction
from django.contrib import messages

class CustomerCreateView(CreateView):
    model = Customer
    fields = ['Account', 'Name', 'Balance']
    template_name = 'core/customer_form.html'
    success_url = reverse_lazy('customer_list')

class CustomerUpdateView(UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'core/customer_form.html'
    success_url = reverse_lazy('customer_list')

class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = 'core/customer_confirm_delete.html'
    success_url = reverse_lazy('customer_list')

class TransactionCreateView(CreateView):
    model = Transaction
    form_class = TransactionForm # Use custom form
    template_name = 'core/transaction_form.html'
    success_url = reverse_lazy('transaction_list')

    def form_valid(self, form):
        try:
            # Save the transaction first to get an instance
            self.object = form.save()
            
            # Update customer balance
            customer = self.object.Account
            if self.object.DC == 'D':
                customer.Balance += self.object.Amount
            elif self.object.DC == 'C':
                customer.Balance -= self.object.Amount
            customer.save()

            return super().form_valid(form)
        except Exception as e:
            form.add_error(None, f'An error occurred: {e}')
            return self.form_invalid(form)

class TransactionUpdateView(UpdateView):
    model = Transaction
    form_class = TransactionForm # Use custom form
    template_name = 'core/transaction_form.html'
    success_url = reverse_lazy('transaction_list')

    def form_valid(self, form):
        try:
            # Get the original transaction object before saving changes
            original_transaction = self.get_object()

            # Save the updated transaction
            self.object = form.save()

            # Revert original transaction's impact on old customer's balance
            original_customer = original_transaction.Account
            if original_transaction.DC == 'D':
                original_customer.Balance -= original_transaction.Amount
            elif original_transaction.DC == 'C':
                original_customer.Balance += original_transaction.Amount
            original_customer.save()

            # Apply new transaction's impact on new customer's balance
            new_customer = Customer.objects.get(pk=self.object.Account.pk)
            if self.object.DC == 'D':
                new_customer.Balance += self.object.Amount
            elif self.object.DC == 'C':
                new_customer.Balance -= self.object.Amount
            new_customer.save()

            return super().form_valid(form)
        except Exception as e:
            form.add_error(None, f'An error occurred: {e}')
            return self.form_invalid(form)

class TransactionDeleteView(DeleteView):
    model = Transaction
    template_name = 'core/transaction_confirm_delete.html'
    success_url = reverse_lazy('transaction_list')

    def form_valid(self, form):
        try:
            # Get the transaction object before deleting
            transaction_to_delete = self.get_object()
            customer = transaction_to_delete.Account

            # Revert the transaction's impact on the customer's balance
            if transaction_to_delete.DC == 'D':
                customer.Balance -= transaction_to_delete.Amount
            elif transaction_to_delete.DC == 'C':
                customer.Balance += transaction_to_delete.Amount
            customer.save()

            return super().form_valid(form)
        except Exception as e:
            # This is a simple way to show the error on the confirmation page
            # A more sophisticated approach would be to use Django's messaging framework
            return render(self.request, self.template_name, {'object': self.get_object(), 'error': str(e)})

def get_fuzzy_q_objects(term, fields):
    q_objects = Q()
    variations = [term]

    # Add common misspellings or variations
    if term.lower() == 'alice':
        variations.extend(['alis', 'alyce'])
    elif term.lower() == 'smith':
        variations.extend(['smyth', 'smithe'])
    # Add more variations as needed

    for var in variations:
        for field in fields:
            q_objects |= Q(**{f'{field}__icontains': var})
    return q_objects

def customer_list(request):
    query = request.GET.get('q')
    # Handle multi-sort parameters
    sort_fields = request.GET.getlist('sort_by')
    sort_orders = request.GET.getlist('order')
    
    # If no sort fields specified, use default
    if not sort_fields:
        sort_fields = ['Account']
        sort_orders = ['asc']

    customers = Customer.objects.all()

    if query:
        search_terms = query.split()
        combined_q_objects = Q()
        for term in search_terms:
            combined_q_objects &= get_fuzzy_q_objects(term, ['Name', 'Account'])
        customers = customers.filter(combined_q_objects)

    # Apply multi-field sorting
    sort_params = []
    for field, order in zip(sort_fields, sort_orders):
        if order == 'desc':
            sort_params.append('-' + field)
        else:
            sort_params.append(field)
    customers = customers.order_by(*sort_params)

    return render(request, 'core/customer_list.html', {
        'customers': customers,
        'query': query,
        'sort_fields': sort_fields,
        'sort_orders': sort_orders
    })

from django.contrib import messages

def transaction_list(request):
    query = request.GET.get('q')
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    # Handle multi-sort parameters
    sort_fields = request.GET.getlist('sort_by')
    sort_orders = request.GET.getlist('order')
    
    # If no sort fields specified, use default
    if not sort_fields:
        sort_fields = ['Number']
        sort_orders = ['asc']

    transactions = Transaction.objects.all()

    if query:
        search_terms = query.split()
        combined_q_objects = Q()
        for term in search_terms:
            combined_q_objects &= get_fuzzy_q_objects(term, ['Account__Account', 'Amount', 'DC', 'Reference'])
        transactions = transactions.filter(combined_q_objects)

    if start_date_str:
        try:
            start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d')
            transactions = transactions.filter(Date__gte=start_date)
        except ValueError:
            messages.error(request, 'Invalid start date format. Please use YYYY-MM-DD.')

    if end_date_str:
        try:
            end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d')
            # To include the entire end day, add one day and search for less than that date
            transactions = transactions.filter(Date__lt=end_date + timezone.timedelta(days=1))
        except ValueError:
            messages.error(request, 'Invalid end date format. Please use YYYY-MM-DD.')

    # Apply multi-field sorting
    sort_params = []
    for field, order in zip(sort_fields, sort_orders):
        if order == 'desc':
            sort_params.append('-' + field)
        else:
            sort_params.append(field)
    transactions = transactions.order_by(*sort_params)

    return render(request, 'core/transaction_list.html', {
        'transactions': transactions,
        'query': query,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'sort_fields': sort_fields,
        'sort_orders': sort_orders
    })






def enquiry_customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'core/enquiry_customer_list.html', {'customers': customers})

def enquiry_transaction_details(request, account_number):
    customer = get_object_or_404(Customer, Account=account_number)
    
    sort_by = request.GET.get('sort_by', '-Date') # Default sort by Date descending
    order = request.GET.get('order', 'asc') # Default order ascending (will be overridden by -Date initially)

    transactions = Transaction.objects.filter(Account=customer)

    # Apply sorting
    if order == 'desc':
        sort_by = '-' + sort_by.replace('-', '') # Ensure it's descending
    else:
        sort_by = sort_by.replace('-', '') # Ensure it's ascending

    transactions = transactions.order_by(sort_by)

    return render(request, 'core/enquiry_transaction_details.html', {
        'customer': customer,
        'transactions': transactions,
        'sort_by': sort_by.replace('-', ''), # Pass original field name to template
        'order': order
    })

from django.db import transaction as db_transaction

def bulk_add_transactions(request):
    num_forms = request.GET.get('num_forms', 3) # Default to 3 forms
    try:
        num_forms = int(num_forms)
    except ValueError:
        num_forms = 3 # Fallback if not a valid number

    DynamicTransactionFormSet = formset_factory(TransactionForm, extra=num_forms)

    if request.method == 'POST':
        formset = DynamicTransactionFormSet(request.POST)
        if formset.is_valid():
            try:
                with db_transaction.atomic():
                    customer_balances = {}
                    for form in formset:
                        if form.has_changed(): # Only process forms that have data
                            transaction = form.save(commit=False)
                            customer = transaction.Account
                            if customer.pk not in customer_balances:
                                customer_balances[customer.pk] = customer.Balance

                            if transaction.DC == 'D':
                                customer_balances[customer.pk] += transaction.Amount
                            elif transaction.DC == 'C':
                                customer_balances[customer.pk] -= transaction.Amount
                            transaction.save()

                    for pk, balance in customer_balances.items():
                        Customer.objects.filter(pk=pk).update(Balance=balance)

                    return redirect('transaction_list')
            except Exception as e:
                formset.non_form_errors().append(f'An error occurred during bulk add: {e}')
    else:
        formset = DynamicTransactionFormSet()
    return render(request, 'core/bulk_add_transactions.html', {'formset': formset, 'num_forms': num_forms})


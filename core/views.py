from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.urls import reverse_lazy
from core.models import Customer, Transaction
from django.db.models import Q
from core.forms import CustomerForm, TransactionForm
from django.utils import timezone

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

class TransactionUpdateView(UpdateView):
    model = Transaction
    form_class = TransactionForm # Use custom form
    template_name = 'core/transaction_form.html'
    success_url = reverse_lazy('transaction_list')

class TransactionDeleteView(DeleteView):
    model = Transaction
    template_name = 'core/transaction_confirm_delete.html'
    success_url = reverse_lazy('transaction_list')

def customer_list(request):
    query = request.GET.get('q')
    sort_by = request.GET.get('sort_by', 'Account') # Default sort by Account
    order = request.GET.get('order', 'asc') # Default order ascending

    customers = Customer.objects.all()

    if query:
        customers = customers.filter(Q(Name__icontains=query) | Q(Account__icontains=query))

    # Apply sorting
    if order == 'desc':
        sort_by = '-' + sort_by
    customers = customers.order_by(sort_by)

    return render(request, 'core/customer_list.html', {
        'customers': customers,
        'query': query,
        'sort_by': sort_by.replace('-', ''), # Pass original field name to template
        'order': order
    })

def transaction_list(request):
    query = request.GET.get('q')
    sort_by = request.GET.get('sort_by', 'Number') # Default sort by Number
    order = request.GET.get('order', 'asc') # Default order ascending

    transactions = Transaction.objects.all()

    if query:
        transactions = transactions.filter(Q(Account__Account__icontains=query) | Q(Amount__icontains=query) | Q(DC__icontains=query))

    # Apply sorting
    if order == 'desc':
        sort_by = '-' + sort_by
    transactions = transactions.order_by(sort_by)

    return render(request, 'core/transaction_list.html', {
        'transactions': transactions,
        'query': query,
        'sort_by': sort_by.replace('-', ''), # Pass original field name to template
        'order': order
    })

# Removed print_transactions view

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

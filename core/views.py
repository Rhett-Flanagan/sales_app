from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.urls import reverse_lazy
from core.models import Customer, Transaction

class CustomerCreateView(CreateView):
    model = Customer
    fields = ['Account', 'Name', 'Balance']
    template_name = 'core/customer_form.html'
    success_url = reverse_lazy('customer_list')

class CustomerUpdateView(UpdateView):
    model = Customer
    fields = ['Account', 'Name', 'Balance']
    template_name = 'core/customer_form.html'
    success_url = reverse_lazy('customer_list')

class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = 'core/customer_confirm_delete.html'
    success_url = reverse_lazy('customer_list')

class TransactionCreateView(CreateView):
    model = Transaction
    fields = ['Account', 'Amount', 'DC']
    template_name = 'core/transaction_form.html'
    success_url = reverse_lazy('transaction_list')

class TransactionUpdateView(UpdateView):
    model = Transaction
    fields = ['Account', 'Amount', 'DC']
    template_name = 'core/transaction_form.html'
    success_url = reverse_lazy('transaction_list')

class TransactionDeleteView(DeleteView):
    model = Transaction
    template_name = 'core/transaction_confirm_delete.html'
    success_url = reverse_lazy('transaction_list')

def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'core/customer_list.html', {'customers': customers})

def transaction_list(request):
    transactions = Transaction.objects.all()
    return render(request, 'core/transaction_list.html', {'transactions': transactions})
from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.urls import reverse_lazy
from core.models import Customer, Transaction
from django.db.models import Q

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
    query = request.GET.get('q')
    customers = Customer.objects.all()
    if query:
        customers = customers.filter(Q(Name__icontains=query) | Q(Account__icontains=query))
    return render(request, 'core/customer_list.html', {'customers': customers, 'query': query})

def transaction_list(request):
    query = request.GET.get('q')
    transactions = Transaction.objects.all()
    if query:
        transactions = transactions.filter(Q(Account__Account__icontains=query) | Q(Amount__icontains=query) | Q(DC__icontains=query))
    return render(request, 'core/transaction_list.html', {'transactions': transactions, 'query': query})
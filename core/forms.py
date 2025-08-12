from django import forms
from core.models import Customer, Transaction

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['Name']

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['Account', 'Date', 'Amount', 'DC', 'Reference']
        widgets = {
            'Date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

# TransactionFormSet will be created dynamically in the view
# TransactionFormSet = formset_factory(TransactionForm, extra=3)
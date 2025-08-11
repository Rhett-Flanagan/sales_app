from django import forms
from core.models import Customer, Transaction
from django.forms import formset_factory

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

    def clean(self):
        cleaned_data = super().clean()
        dc = cleaned_data.get('DC')
        amount = cleaned_data.get('Amount')
        customer = cleaned_data.get('Account')

        if dc == 'C' and customer and amount and customer.Balance < amount:
            raise forms.ValidationError('Customer does not have enough balance for this transaction.')

        return cleaned_data

# TransactionFormSet will be created dynamically in the view
# TransactionFormSet = formset_factory(TransactionForm, extra=3)
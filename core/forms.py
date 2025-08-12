from django import forms
from core.models import Customer, Transaction

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['Name']

class TransactionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Store the initial instance for update scenarios
        self.original_instance = kwargs.get('instance')

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

        # Adjust customer balance for update scenarios before validation
        adjusted_balance = customer.Balance
        if self.original_instance and self.original_instance.pk:
            # If updating, revert the impact of the original transaction on the balance
            if self.original_instance.DC == 'D':
                adjusted_balance -= self.original_instance.Amount
            elif self.original_instance.DC == 'C':
                adjusted_balance += self.original_instance.Amount

        if dc == 'C' and customer and amount and adjusted_balance < amount:
            raise forms.ValidationError('Customer does not have enough balance for this transaction.')

        return cleaned_data

# TransactionFormSet will be created dynamically in the view
# TransactionFormSet = formset_factory(TransactionForm, extra=3)
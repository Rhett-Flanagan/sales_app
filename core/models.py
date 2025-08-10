from django.db import models

class Customer(models.Model):
    Account = models.CharField(max_length=15, unique=True)
    Name = models.CharField(max_length=30)
    Balance = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.Name

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('D', 'Debit'),
        ('C', 'Credit'),
    ]

    Number = models.AutoField(primary_key=True)
    Account = models.ForeignKey(Customer, to_field='Account', on_delete=models.CASCADE)
    Date = models.DateTimeField(auto_now_add=True)
    Amount = models.DecimalField(max_digits=10, decimal_places=2)
    DC = models.CharField(max_length=1, choices=TRANSACTION_TYPES)

    def __str__(self):
        return f"Transaction {self.Number} for {self.Account.Account}"
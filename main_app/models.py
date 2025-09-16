# main_app/models.py
from django.db import models
from django.urls import reverse
from datetime import date
from django.utils import timezone

class Goal(models.Model):
    image = models.ImageField(upload_to='goal_images/', blank=True, null=True)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    target_amount = models.FloatField()
    amount_saved = models.FloatField()
    target_date = models.DateField()
    status = models.CharField(max_length=100)
    
     # Calculate simple interest
    def calculate_interest(self):
        time_period = (self.target_date - date.today()).days / 365  # Time in years
        interest = self.target_amount * (self.interest_rate / 100) * time_period  # Simple Interest formula
        return interest

    # new code below
    def __str__(self):
        return self.name


# Add the account model
class Account(models.Model):
    name = models.CharField(max_length=50)
    balance = models.FloatField()
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Prevent modification of "Checking" and "Savings" accounts
        if self.name in ['Checking', 'Savings'] and self.pk is not None:
            raise ValueError(f"The {self.name} account cannot be modified.")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('account-detail', kwargs={'pk': self.id})
    
    
    def update_balance(self, saving_amount, checking_amount, transaction_type):
            # If the transaction type is income, increase the balances
            if transaction_type == 'income':
                self.saving_balance += saving_amount
                self.checking_balance += checking_amount
            # If the transaction type is expenditure, decrease the balances
            elif transaction_type == 'expenditure':
                self.saving_balance -= saving_amount
                self.checking_balance -= checking_amount
            
            self.save()  # Save the updated balances to the database
    

# Add the Transaction model
class Transaction(models.Model):
    INCOME = 'income'
    EXPENDITURE = 'expenditure'
    TRANSACTION_TYPE_CHOICES = [
        (INCOME, 'Income'),
        (EXPENDITURE, 'Expenditure'),
    ]

    image = models.ImageField(upload_to='transaction_images/', blank=True, null=True)
    name = models.CharField(max_length=200, default="Untitled Transaction")
    description = models.CharField(max_length=500, blank=True, null=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES, default=INCOME)
    saving_goal = models.ForeignKey("Goal", on_delete=models.SET_NULL, blank=True, null=True, related_name="transactions")

    amount = models.FloatField(default=0)
    saving_amount = models.FloatField()
    checking_amount = models.FloatField()
    transaction_date = models.DateField(default=timezone.localdate)

    def save(self, *args, **kwargs):
        # Ensure totals match before saving
        total_split = round((self.saving_amount or 0) + (self.checking_amount or 0), 2)
        total = round(self.amount or 0, 2)

        if total_split != total:
            raise ValueError(
                f"Invalid transaction: Total ({self.amount}) must equal Saving ({self.saving_amount}) + Checking ({self.checking_amount})."
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("transaction-detail", kwargs={"pk": self.id})
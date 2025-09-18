from django.db import models
from django.urls import reverse
from datetime import date
from django.utils import timezone
from decimal import Decimal  # Ensure we are importing Decimal
from django.contrib.auth.models import User

class Goal(models.Model):
    image = models.ImageField(upload_to='goal_images/', blank=True, null=True)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    target_amount = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal('0.000'))  # Use Decimal
    amount_saved = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal('0.000'))  # Use Decimal
    target_date = models.DateField()
    status = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# Add the account model
class Saving_Account(models.Model):
    balance = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal('0.000'))  # Use Decimal
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
         return f"Savings Account — {self.balance:.3f}"

    def get_absolute_url(self):
        return reverse('saving-account-detail', kwargs={'pk': self.id})


# Add the Checking Account model
class Checking_Account(models.Model):
    balance = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal('0.000'))  # Use Decimal
    last_updated = models.DateTimeField(auto_now=True)  # Auto-updates on every save

    def __str__(self):
        return f"Checking Account — {self.balance:.3f}"

    def get_absolute_url(self):
        return reverse('checking-account-detail', kwargs={'pk': self.id})


# Add the Transaction model
class Transaction(models.Model):
    INCOME = 'income'
    EXPENDITURE = 'expenditure'
    TRANSACTION_TYPE_CHOICES = [
        (INCOME, 'Income'),
        (EXPENDITURE, 'Expenditure'),
    ]

    name = models.CharField(max_length=200, default="Untitled Transaction")
    description = models.CharField(max_length=500, blank=True, null=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES, default=INCOME)
    saving_goal = models.ForeignKey('Goal', on_delete=models.SET_NULL, blank=True, null=True, related_name='transactions')

    amount = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal('0.000'))  # Use Decimal
    saving_amount = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal('0.000'))  # Use Decimal
    checking_amount = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal('0.000'))  # Use Decimal
    transaction_date = models.DateField(default=timezone.localdate)

    def save(self, *args, **kwargs):
        # If it's an update, get the old transaction data
        if self.pk:
            old_transaction = Transaction.objects.get(pk=self.pk)
            old_saving_amount = old_transaction.saving_amount
            old_checking_amount = old_transaction.checking_amount
            old_transaction_type = old_transaction.transaction_type
        else:
            old_saving_amount = Decimal('0.000')  # Initialize as Decimal
            old_checking_amount = Decimal('0.000')
            old_transaction_type = None

        # Ensure that the sum of saving_amount and checking_amount equals the total amount
        if (self.saving_amount + self.checking_amount) != self.amount:
            raise ValueError("The sum of saving_amount and checking_amount must equal the total amount.")

        # Handle saving account balance update if needed
        saving_account = Saving_Account.objects.first()  # Assuming one Saving Account

        # Handle Checking Account balance update if needed
        checking_account = Checking_Account.objects.first()  # Assuming one Checking Account

        # **Check if Checking_Account exists, create if not**
        if not checking_account:
            checking_account = Checking_Account.objects.create(balance=Decimal('0.000'))  # Create Checking_Account with default balance 0

        # Handle income logic for Saving_Account or Checking_Account
        if self.transaction_type == self.INCOME:
            if self.saving_goal:
                # If a goal is selected, add the saving_amount to the goal's amount_saved
                self.saving_goal.amount_saved += (self.saving_amount - old_saving_amount)  # Use Decimal
                self.saving_goal.save()  # Save updated goal amount_saved
            else:
                # If no goal is selected, add the saving_amount to the Saving_Account balance
                if saving_account:
                    saving_account.balance += (self.saving_amount - old_saving_amount)  # Use Decimal
                    saving_account.save()

            # Income logic for Checking_Account
            if checking_account:
                checking_account.balance += (self.checking_amount - old_checking_amount)  # Use Decimal
                checking_account.save()

        # Handle expenditure logic for Saving_Account or Checking_Account
        elif self.transaction_type == self.EXPENDITURE:
            if self.saving_goal:
                # If a goal is selected, subtract the saving_amount from the goal's amount_saved
                self.saving_goal.amount_saved -= (self.saving_amount - old_saving_amount)  # Use Decimal
                self.saving_goal.save()  # Save updated goal amount_saved
            else:
                # If no goal is selected, subtract the saving_amount from the Saving_Account balance
                if saving_account:
                    saving_account.balance -= (self.saving_amount - old_saving_amount)  # Use Decimal
                    saving_account.save()

            # Expenditure logic for Checking_Account
            if checking_account:
                checking_account.balance -= (self.checking_amount - old_checking_amount)  # Use Decimal
                checking_account.save()

        # If the transaction type changes (from income to expenditure or vice versa), adjust the balance
        if old_transaction_type != self.transaction_type:
            # If it was income and now it's expenditure, adjust Checking_Account balance
            if old_transaction_type == self.INCOME:
                if checking_account:
                    checking_account.balance -= old_checking_amount  # Use Decimal
                    checking_account.balance -= self.checking_amount  # Use Decimal
                    checking_account.save()

            # If it was expenditure and now it's income, adjust Checking_Account balance
            elif old_transaction_type == self.EXPENDITURE:
                if checking_account:
                    checking_account.balance += old_checking_amount  # Use Decimal
                    checking_account.balance += self.checking_amount  # Use Decimal
                    checking_account.save()

        # Now save the transaction
        super().save(*args, **kwargs)


    def delete(self, *args, **kwargs):
        # Case 1: If the transaction is linked to a goal
        if self.saving_goal:
            # If the transaction is income, subtract the saving_amount from the goal's amount_saved
            if self.transaction_type == self.INCOME:
                self.saving_goal.amount_saved -= self.saving_amount
            # If the transaction is expenditure, add the saving_amount to the goal's amount_saved
            elif self.transaction_type == self.EXPENDITURE:
                self.saving_goal.amount_saved += self.saving_amount
            
            # Save the updated goal's amount_saved after the change
            self.saving_goal.save()

        # Case 2: If the transaction is not linked to any goal, update the Saving_Account balance
        if not self.saving_goal:
            try:
                # Fetch the first available Saving_Account (assuming only one exists)
                saving_account = Saving_Account.objects.first()
                if saving_account:
                    # If the transaction is income, subtract the saving_amount from the Saving_Account balance
                    if self.transaction_type == self.INCOME:
                        saving_account.balance -= self.saving_amount
                    # If the transaction is expenditure, add the saving_amount to the Saving_Account balance
                    elif self.transaction_type == self.EXPENDITURE:
                        saving_account.balance += self.saving_amount

                    # Save the updated Saving_Account balance
                    saving_account.save()
                else:
                    # If no Saving_Account exists, log the issue or handle accordingly
                    print("No Saving_Account found. Skipping balance update.")

            except Saving_Account.DoesNotExist:
                # If no Saving_Account exists, log the issue
                print("Saving_Account does not exist. Cannot update balance.")

        # Update the Checking Account balance
        checking_account = Checking_Account.objects.first()  # Assuming one Checking Account
        if checking_account:
            if self.transaction_type == self.INCOME:
                checking_account.balance -= self.checking_amount  # Use Decimal for income
            elif self.transaction_type == self.EXPENDITURE:
                checking_account.balance += self.checking_amount  # Use Decimal for expenditure
            checking_account.save()

        # Now, proceed with deleting the transaction after the balance updates
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("transaction-detail", kwargs={"pk": self.id})

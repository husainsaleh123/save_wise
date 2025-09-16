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

    # new code below
    def __str__(self):
        return self.name


# Add the account model
class Saving_Account(models.Model):
    balance = models.FloatField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
         return f"Savings Account — {self.balance:.2f}"

    def get_absolute_url(self):
        return reverse('saving-account-detail', kwargs={'pk': self.id})
    
    
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
    saving_goal = models.ForeignKey('Goal', on_delete=models.SET_NULL, blank=True, null=True, related_name='transactions')

    amount = models.FloatField(default=0)
    saving_amount = models.FloatField()
    checking_amount = models.FloatField()
    transaction_date = models.DateField(default=timezone.localdate)

    def save(self, *args, **kwargs):
        # If it's an update, get the old transaction data
        if self.pk:
            old_transaction = Transaction.objects.get(pk=self.pk)
            old_saving_amount = old_transaction.saving_amount
            old_transaction_type = old_transaction.transaction_type
        else:
            old_saving_amount = 0  # For new transactions, there's no old amount
            old_transaction_type = None

        # Ensure that the sum of saving_amount and checking_amount equals amount
        if round(self.saving_amount + self.checking_amount, 2) != round(self.amount, 2):
            raise ValueError("The sum of saving_amount and checking_amount must equal the total amount.")

        # Handle income logic
        if self.transaction_type == self.INCOME:
            if self.saving_goal:
                # If a goal is selected, add the saving_amount to the goal's amount_saved
                self.saving_goal.amount_saved += self.saving_amount - old_saving_amount  # Adjust for updates
                self.saving_goal.save()  # Save updated goal amount_saved
            else:
                # If no goal is selected, add the saving_amount to the Saving_Account balance
                saving_account = Saving_Account.objects.first()  # Get the first available Saving_Account
                if saving_account:
                    saving_account.balance += self.saving_amount - old_saving_amount  # Adjust for updates
                    saving_account.save()

        # Handle expenditure logic
        elif self.transaction_type == self.EXPENDITURE:
            if self.saving_goal:
                # If a goal is selected, subtract the saving_amount from the goal's amount_saved
                self.saving_goal.amount_saved -= self.saving_amount - old_saving_amount  # Adjust for updates
                self.saving_goal.save()  # Save updated goal amount_saved
            else:
                # If no goal is selected, subtract the saving_amount from the Saving_Account balance
                saving_account = Saving_Account.objects.first()  # Get the first available Saving_Account
                if saving_account:
                    saving_account.balance -= self.saving_amount - old_saving_amount  # Adjust for updates
                    saving_account.save()

        # If the transaction type changes (from income to expenditure or vice versa), adjust the balance
        if old_transaction_type != self.transaction_type:
            # If it was income and now it's expenditure, subtract the saving_amount twice
            if old_transaction_type == self.INCOME:
                if self.saving_goal:
                    self.saving_goal.amount_saved -= old_saving_amount  # Revert old income change (subtract once)
                    self.saving_goal.amount_saved -= self.saving_amount  # Subtract for the new expenditure
                    self.saving_goal.save()  # Save updated goal amount_saved
                else:
                    saving_account = Saving_Account.objects.first()  # Get the first available Saving_Account
                    if saving_account:
                        saving_account.balance -= old_saving_amount  # Revert old income change (subtract once)
                        saving_account.balance -= self.saving_amount  # Subtract for the new expenditure
                        saving_account.save()

            # If it was expenditure and now it's income, add the saving_amount twice
            elif old_transaction_type == self.EXPENDITURE:
                if self.saving_goal:
                    self.saving_goal.amount_saved += old_saving_amount  # Revert old expenditure change (add once)
                    self.saving_goal.amount_saved += self.saving_amount  # Add for the new income
                    self.saving_goal.save()  # Save updated goal amount_saved
                else:
                    saving_account = Saving_Account.objects.first()  # Get the first available Saving_Account
                    if saving_account:
                        saving_account.balance += old_saving_amount  # Revert old expenditure change (add once)
                        saving_account.balance += self.saving_amount  # Add for the new income
                        saving_account.save()

        # Now save the transaction
        super().save(*args, **kwargs)


    def delete(self, *args, **kwargs):
        # Handle the deletion of transaction and revert balances
        if self.saving_goal:
            if self.transaction_type == self.INCOME:
                self.saving_goal.amount_saved -= self.saving_amount
            elif self.transaction_type == self.EXPENDITURE:
                self.saving_goal.amount_saved += self.saving_amount
            self.saving_goal.save()  # Save updated goal amount_saved
        
        # Ensure the Saving_Account is updated
        if self.saving_goal:
            saving_account = Saving_Account.objects.get(id=self.saving_goal.id)
            if self.transaction_type == self.INCOME:
                saving_account.balance -= self.saving_amount
            elif self.transaction_type == self.EXPENDITURE:
                saving_account.balance += self.saving_amount
            saving_account.save()  # Save updated Saving_Account balance

        super().delete(*args, **kwargs)  # Proceed with deleting the transaction

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("transaction-detail", kwargs={"pk": self.id})
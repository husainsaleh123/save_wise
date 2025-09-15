# main_app/models.py
from django.db import models
from django.urls import reverse
from datetime import date

class Goal(models.Model):
    image = models.ImageField(upload_to='goal_images/', blank=True, null=True)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    target_amount = models.FloatField()
    amount_saved = models.FloatField()
    interest_rate = models.FloatField()
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
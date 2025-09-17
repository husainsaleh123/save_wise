# main_app/views.py

from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView # add these 
from .models import Goal, Saving_Account, Checking_Account, Transaction
from django import forms
from datetime import date

# Ensures the user cannot enter a date in the past
class GoalForm(forms.ModelForm):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed')
    ]

    status = forms.ChoiceField(choices=STATUS_CHOICES, required=True)
    class Meta:
        model = Goal
        fields = ['image', 'name', 'description', 'target_amount', 'amount_saved', 'target_date', 'status']

    def clean_target_date(self):
        target_date = self.cleaned_data['target_date']
        if target_date < date.today():
            raise forms.ValidationError("The target date cannot be in the past.")
        return target_date

    def clean_amount_saved(self):
        amount_saved = self.cleaned_data['amount_saved']
        target_amount = self.cleaned_data['target_amount']
        if amount_saved > target_amount:
            raise forms.ValidationError("The amount saved cannot be greater than the target amount.")
        return amount_saved
    
    image = forms.ImageField(required=False)  # Image is not required

    def clean_status(self):
        amount_saved = self.cleaned_data.get('amount_saved', 0)
        target_amount = self.cleaned_data.get('target_amount', 0)
        
        # Set the status based on amount_saved
        if amount_saved == 0:
            return 'Not started'
        elif amount_saved < target_amount:
            return 'ongoing'
        elif amount_saved >= target_amount:
            return 'completed'
        return self.cleaned_data['status']


class GoalCreate(CreateView):
    model = Goal
    form_class = GoalForm  # Use the custom form
    success_url = '/goals/'  # Redirect to the goals index page after successful creation

# Define the home view function
def home(request):
    # You can make this a basic landing page or redirect to accounts page
    return render(request, 'home.html')  # Basic landing page


# Create a new view to list both Saving and Checking accounts
def accounts_list(request):
    # Fetch all saving and checking accounts
    saving_accounts = Saving_Account.objects.all()
    checking_accounts = Checking_Account.objects.all()

    # Pass these objects to the template
    return render(request, 'main_app/account_list.html', {
        'saving_accounts': saving_accounts,
        'checking_accounts': checking_accounts
    })


def goal_index(request):
    goals = Goal.objects.all()
    for g in goals:
        try:
            g.progress = max(0, min(100, round((g.amount_saved / g.target_amount) * 100))) if g.target_amount else 0
        except Exception:
            g.progress = 0
    return render(request, 'goals/index.html', {'goals': goals})

def goal_detail(request, goal_id):
    # Fetch the specific goal using the goal_id
    goal = get_object_or_404(Goal, id=goal_id)
    return render(request, 'goals/detail.html', {'goal': goal})

class GoalUpdate(UpdateView):
    model = Goal
    form_class = GoalForm  # Use the custom form
    success_url = '/goals/'

class GoalDelete(DeleteView):
    model = Goal
    success_url = '/goals/'

# Goal update view with restriction for "Checking" and "Savings" accounts
class SavingAccountUpdate(UpdateView):
    model = Saving_Account
    fields = ['balance']
    success_url = '/saving_account/'

class CheckingAccountUpdate(UpdateView):
    model = Checking_Account
    fields = ['balance']
    success_url = '/checking_accounts/'  # Redirect after successful update

class GoalDelete(DeleteView):
    model = Goal
    success_url = '/goals/'


def saving_account_list(request):
    # Fetch all accounts from the database
    saving_accounts = Saving_Account.objects.all()
    return render(request, 'main_app/account_list.html', {'saving_accounts':saving_accounts})

class SavingAccountDetail(DetailView):
    model = Saving_Account


def checking_account_list(request):
    # Fetch all accounts from the database
    checking_accounts = Checking_Account.objects.all()
    return render(request, 'main_app/account_list.html', {'checking_accounts':checking_accounts})

class CheckingAccountDetail(DetailView):
    model = Checking_Account

class TransactionCreate(CreateView):
    model = Transaction
    fields = ['image', 'name', 'transaction_type', 'description', 'saving_goal', 
              'amount', 'saving_amount', 'checking_amount', 'transaction_date']
    success_url = '/transactions/'  # Redirect to the transaction list after successful creation

    def form_valid(self, form):
            try:
                form.save()  # This will call the model's save() method
            except ValueError as e:
                form.add_error('saving_amount', str(e))  # Add error to saving_amount field
                form.add_error('checking_amount', str(e))  # Add error to checking_amount field
                return self.form_invalid(form)  # Redisplay the form with errors
            return super().form_valid(form)
            
    
# Add other views like TransactionList, TransactionDetail, etc.

class TransactionList(ListView):
    model = Transaction
    template_name = 'main_app/transaction_list.html'
    context_object_name = 'transactions'   

class TransactionDetail(DetailView):
    model = Transaction
    template_name = 'main_app/transaction_detail.html'
    context_object_name = 'transaction'

class TransactionUpdate(UpdateView):
    model = Transaction
    fields = ['image','name','transaction_type','description','saving_goal',
              'amount','saving_amount','checking_amount','transaction_date']
    success_url = '/transactions/'  # Redirect to the transaction list after successful update

    def form_valid(self, form):
            try:
                form.save()  # This will call the model's save() method
            except ValueError as e:
                form.add_error('saving_amount', str(e))  # Add error to saving_amount field
                form.add_error('checking_amount', str(e))  # Add error to checking_amount field
                return self.form_invalid(form)  # Redisplay the form with errors
            return super().form_valid(form)
            
    
class TransactionDelete(DeleteView):
    model = Transaction
    success_url = '/transactions/'  # Redirect to the transaction list after successful deletion

    def delete(self, request, *args, **kwargs):
        # Fetch the transaction to be deleted
        transaction = self.get_object()

        # First, handle the case where the transaction is linked to a goal
        if transaction.saving_goal:
            # Subtract the saving_amount from the goal's amount_saved
            transaction.saving_goal.amount_saved -= transaction.saving_amount
            transaction.saving_goal.save()  # Save the updated goal amount_saved
        else:
            # If no goal is linked, we should update the Saving_Account balance
            saving_account = Saving_Account.objects.first()  # Get the first available Saving_Account
            if saving_account:
                saving_account.balance -= transaction.saving_amount
                saving_account.save()  # Save the updated Saving_Account balance
            else:
                # If no Saving_Account exists, log or handle the issue here
                print("No Saving Account found. Skipping balance update.")

        # Now delete the transaction, regardless of Saving_Account existence
        response = super().delete(request, *args, **kwargs)

        # Return the response after the transaction deletion to ensure proper redirection
        return response
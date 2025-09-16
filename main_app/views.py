# main_app/views.py

from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView # add these 
from .models import Goal, Account, Transaction
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
            return 'not_started'
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
    # Send a simple HTML response
    return render(request, 'home.html')

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
class AccountUpdate(UpdateView):
    model = Account
    fields = ['name', 'balance', 'last_updated']

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Prevent modification of Checking and Savings accounts
        if obj.name in ['Checking', 'Savings']:
            raise ValueError(f"The {obj.name} account cannot be modified.")
        return obj


class GoalDelete(DeleteView):
    model = Goal
    success_url = '/goals/'


def account_list(request):
    # Fetch all accounts from the database
    accounts = Account.objects.all()
    return render(request, 'main_app/account_list.html', {'accounts': accounts})

class AccountDetail(DetailView):
    model = Account


class TransactionCreate(CreateView):
    model = Transaction
    fields = ['image','name','transaction_type','description','saving_goal',
              'amount','saving_amount','checking_amount','transaction_date']
    success_url = '/transactions/'

    def form_valid(self, form):
        # --- future date validation ---
        t_date = form.data.get('transaction_date')
        if t_date:
            try:
                # Convert string to Python date
                entered_date = date.fromisoformat(t_date)
                if entered_date > date.today():
                    form.add_error('transaction_date', "Transaction date cannot be in the future.")
                    return self.form_invalid(form)
            except Exception:
                # If conversion fails, let Django handle it
                return self.form_invalid(form)


        # Use raw form.data (no cleaned_data)
        try:
            amount = float(form.data.get('amount') or 0)
            saving_amount = float(form.data.get('saving_amount') or 0)
            checking_amount = float(form.data.get('checking_amount') or 0)
        except (TypeError, ValueError):
            # If conversion failed, let the default field errors surface
            return self.form_invalid(form)

        if round(saving_amount + checking_amount, 2) != round(amount, 2):
            msg = (
                f"Total ({amount}) must equal "
                f"Saving ({saving_amount}) + Checking ({checking_amount})."
            )
            # Put the error exactly where the user typed the numbers
            form.add_error('saving_amount', msg)
            form.add_error('checking_amount', msg)
            return self.form_invalid(form)

        return super().form_valid(form)

    

# Add other views like TransactionList, TransactionDetail, etc.

class TransactionList(ListView):
    model = Transaction
    template_name = 'main_app/transaction_list.html'
    context_object_name = 'transactions'   # <-- matches your template

class TransactionDetail(DetailView):
    model = Transaction
    template_name = 'main_app/transaction_detail.html'
    context_object_name = 'transaction'

class TransactionUpdate(UpdateView):
    model = Transaction
    fields = ['image','name','transaction_type','description','saving_goal',
              'amount','saving_amount','checking_amount','transaction_date']
    success_url = '/transactions/'

    def form_valid(self, form):
            # --- future date validation ---
            t_date = form.data.get('transaction_date')
            if t_date:
                try:
                    # Convert string to Python date
                    entered_date = date.fromisoformat(t_date)
                    if entered_date > date.today():
                        form.add_error('transaction_date', "Transaction date cannot be in the future.")
                        return self.form_invalid(form)
                except Exception:
                # If conversion fails, let Django handle it
                    return self.form_invalid(form)
            
            # --- existing balance validation ---
            try:
                amount = float(form.data.get('amount') or 0)
                saving_amount = float(form.data.get('saving_amount') or 0)
                checking_amount = float(form.data.get('checking_amount') or 0)
            except (TypeError, ValueError):
                return self.form_invalid(form)

            if round(saving_amount + checking_amount, 2) != round(amount, 2):
                msg = (
                    f"Total ({amount}) must equal "
                    f"Saving ({saving_amount}) + Checking ({checking_amount})."
                )
                form.add_error('saving_amount', msg)
                form.add_error('checking_amount', msg)
                return self.form_invalid(form)

            return super().form_valid(form)

class TransactionDelete(DeleteView):
    model = Transaction
    fields = '__all__'
    success_url = '/transactions/'
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
        fields = ['image', 'name', 'description', 'target_amount', 'amount_saved', 'interest_rate', 'target_date', 'status']

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
    
    # Set image and interest_rate as optional (not required)
    image = forms.ImageField(required=False)  # Image is not required
    interest_rate = forms.FloatField(required=False)  # Interest rate is not required


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
    fields = '__all__'


class TransactionList(ListView):
    model = Transaction

class TransactionDetail(DetailView):
    model = Transaction

class TransactionUpdate(UpdateView):
    model = Transaction
    fields = '__all__'


class TransactionDelete(DeleteView):
    model = Transaction
    fields = '__all__'
    success_url = '/transactions/'
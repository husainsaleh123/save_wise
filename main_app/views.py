# main_app/views.py

from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Goal


class GoalCreate(CreateView):
    model = Goal
    fields = ['image', 'name', 'description', 'target_amount', 'amount_saved','interest_rate','target_date','status']
    success_url = '/goals/'

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
    fields = ['image', 'name', 'description', 'target_amount', 'amount_saved','interest_rate','target_date','status']
    success_url = '/goals/'

class GoalDelete(DeleteView):
    model = Goal
    success_url = '/goals/'
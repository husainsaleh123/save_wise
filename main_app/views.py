# main_app/views.py

from django.shortcuts import render
from .models import Goal

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
    goal = Goal.objects.get(id=goal_id)
    return render(request, 'goals/detail.html', {'goal': goal})
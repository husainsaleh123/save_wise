# main_app/views.py

from django.shortcuts import render

# Import HttpResponse to send text-based responses
from django.http import HttpResponse

# Define the home view function
def home(request):
    # Send a simple HTML response
    return render(request, 'home.html')

# views.py

class Goal:
    def __init__(self, image, name, description, target_amount, amount_saved, interest_rate, target_date, status):
        self.image = image
        self.name = name
        self.description = description
        self.target_amount = target_amount
        self.amount_saved = amount_saved
        self.interest_rate = interest_rate
        self.target_date = target_date
        self.status = status

# Create a list of Cat instances
goals = [
    Goal('images/completed.png','Going to Maldives','My dream trip',10000,0,0,'1/1/2030','Ongoing'),
]

def goal_index(request):
    # Render the cats/index.html template with the cats data
    return render(request, 'goals/index.html', {'goals': goals})
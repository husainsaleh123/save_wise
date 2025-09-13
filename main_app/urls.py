from django.urls import path
from . import views # Import views to connect routes to view functions

urlpatterns = [
   path('home/', views.home, name='home'),
   path('goals/', views.goal_index, name='goal-index'),
]
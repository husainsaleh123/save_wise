#main_app/urls.py

from django.urls import path
from . import views # Import views to connect routes to view functions

urlpatterns = [
   path('home/', views.home, name='home'),
   path('goals/', views.goal_index, name='goal-index'),
   path('goals/<int:goal_id>/', views.goal_detail, name='goal-detail'),
   path('goals/create/', views.GoalCreate.as_view(), name='goal-create'),
   path('goals/<int:pk>/update/', views.GoalUpdate.as_view(), name='goal-update'),
   path('goals/<int:pk>/delete/', views.GoalDelete.as_view(), name='goal-delete'),
   path('accounts/<int:pk>/', views.AccountDetail.as_view(), name='account-detail'),
    path('accounts/', views.account_list, name='account-list'),
]
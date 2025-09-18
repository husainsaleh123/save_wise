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
   path('accounts_balance/<int:pk>/', views.SavingAccountDetail.as_view(), name='saving-account-detail'),
   path('accounts_balance/', views.accounts_list, name='account-list'),
    # Checking Account URLs (added for Checking_Account)
    path('checking_accounts/', views.checking_account_list, name='checking-account-list'),
    path('checking_accounts/<int:pk>/', views.CheckingAccountDetail.as_view(), name='checking-account-detail'),
    path('checking_accounts/<int:pk>/update/', views.CheckingAccountUpdate.as_view(), name='checking-account-update'),
   path('transactions/create/', views.TransactionCreate.as_view(), name='transaction-create'),
   path('transactions/', views.TransactionList.as_view(), name='transaction-index'),
   path('transactions/<int:pk>/', views.TransactionDetail.as_view(), name='transaction-detail'),
   path('transactions/<int:pk>/update/', views.TransactionUpdate.as_view(), name='transaction-update'),
   path('transactions/<int:pk>/delete/', views.TransactionDelete.as_view(), name='transaction-delete'),
]
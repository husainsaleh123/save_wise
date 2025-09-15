from django.contrib import admin
from .models import Goal, Account, Transaction

admin.site.register(Goal)
admin.site.register(Account)
admin.site.register(Transaction)
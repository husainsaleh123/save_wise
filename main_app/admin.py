from django.contrib import admin
from .models import Goal, Saving_Account, Checking_Account, Transaction

admin.site.register(Goal)
admin.site.register(Saving_Account)
admin.site.register(Checking_Account)
admin.site.register(Transaction)
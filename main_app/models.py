from django.db import models

class Goal(models.Model):
    image = models.ImageField(upload_to='goals/', null=True, blank=True)  # Add an image field (optional)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    target_amount = models.FloatField()
    amount_saved = models.FloatField()
    interest_rate = models.FloatField()
    target_date = models.DateField()
    status = models.CharField(max_length=100)

    # new code below
    def __str__(self):
        return self.name
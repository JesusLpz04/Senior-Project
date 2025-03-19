from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    USER_TYPES = [
        ('president', 'President'),
        ('treasurer', 'Treasurer'), 
        ('member', 'Member')
    ]
    
    # One user correlates to one user profile.
    user = models.OneToOneField(
        User, #primary attributes of the default user are: username, password, email, first_name, last_name
        on_delete=models.CASCADE
    )
    
    user_type = models.CharField(
        max_length=10, 
        choices=USER_TYPES
    )
    
    def __str__(self):
        return f"{self.user.username} - {self.user_type}"

class Poll(models.Model):
    question = models.TextField()
    option_one = models.CharField(max_length=50)
    option_two = models.CharField(max_length=50)
    option_three = models.CharField(max_length=50)
    option_one_count = models.IntegerField(default=0)
    option_two_count = models.IntegerField(default=0)
    option_three_count = models.IntegerField(default=0)

    def total(self):
        return self.option_one_count + self.option_two_count + self.option_three_count

class CreateTicket(models.Model):
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()  
    confirmation = models.CharField(max_length=100)
    receipt = models.FileField(upload_to='receipts/', null=True, blank=True)

    def __str__(self):
        return f"Ticket created {self.id}: {self.amount} on {self.date}"

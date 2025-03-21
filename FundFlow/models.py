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
        return f"{self.user.email} - {self.user_type}"
class Organization(models.Model):
    name= models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    #president = models.ForeignKey(User, on_delete=models.CASCADE, related_name='president_of')
    members = models.ManyToManyField(User, related_name='organizations', blank=True)
    pending_members = models.ManyToManyField(User, related_name='pending_organizations', blank=True)
    
    def request_membership(self, user):
        if user not in self.members.all() and user not in self.pending_members.all():
            self.pending_members.add(user)

    def approve_membership(self, user):
        if user in self.pending_members.all():
            self.pending_members.remove(user)
            self.members.add(user)

    def deny_membership(self, user):
        if user in self.pending_members.all():
            self.pending_members.remove(user)

    def get_pending_requests(self):
        return self.pending_members.all()

    def get_accepted_members(self):
        return self.members.all()
    def __str__(self):
        return self.name

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

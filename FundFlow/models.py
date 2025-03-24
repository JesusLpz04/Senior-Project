from django.db import models
from django.db.models import Sum, F, Case, When, DecimalField
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

# #for the drop down menu of category types
# class CustomCategory(models.Model):
#     name = models.CharField(max_length=50, unique=True)

#     def __str__(self):
#         return self.name
    
class TicketManager(models.Manager):
    def get_balance(self):
        return self.aggregate(
            total=Sum(
                Case(
                    When(operation='add', then=F('amount')),
                    When(operation='minus', then=-F('amount')),
                    default=0,
                    output_field=DecimalField()
                )
            )
        )['total'] or 0
    #call like:
    #balance = CreateTicket.objects.get_balance()
        
class CreateTicket(models.Model):
    CATEGORY_CHOICES = [
        ('supplies', 'Supplies'), 
        ('reimbursements', 'Reimbursements'), 
        ('food', 'Food'), 
        ('travel', 'Travel'),
        ('membershipfee', 'Membership Fee'),
        ('other', 'Other'),
    ]
    MODIFY_CHOICES = [
        ('add', '+'), 
        ('minus', '-')        
    ]
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()  
    operation = models.CharField(
        max_length = 20, 
        choices = MODIFY_CHOICES,
        default = 'add',
    )
    expense_category = models.CharField(
        max_length=20, 
        choices=CATEGORY_CHOICES, 
        default = 'supplies',
    ) 
    # custom_category = models.ForeignKey(
    #     CustomCategory, 
    #     on_delete=models.SET_NULL, 
    #     null=True, 
    #     blank=True
    # )   
    receipt = models.FileField(upload_to='receipts/', null=True, blank=True)
    objects = TicketManager()
    
    def save(self, *args, **kwargs):
        # if self.expense_category == 'other' and self.custom_category: #if already exists
        #     self.custom_category, _ = CustomCategory.objects.get_or_create(name=self.custom_category.name)#reuse
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Ticket {self.id} created ({self.date}), balance: ${self.__class__.objects.get_balance()}"


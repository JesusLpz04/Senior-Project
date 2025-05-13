from django.db import models
from django.contrib.auth.models import User

from django.db.models import Sum, F, Case, When, DecimalField


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

    current_Org=models.ForeignKey(
        'Organization',
        on_delete=models.SET_NULL,  # <- this makes sure UserProfile isn't deleted
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.user.email} - {self.user_type}"
    
class Organization(models.Model):
    name= models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    president = models.ForeignKey(User, on_delete=models.CASCADE, related_name='president_of', blank=True, null=True)
    treasurer = models.ForeignKey(User, on_delete=models.SET_NULL ,related_name='treasurer_of', blank=True, null=True)
    members = models.ManyToManyField(User, related_name='organizations', blank=True)
    pending_members = models.ManyToManyField(User, related_name='pending_organizations', blank=True)
    bank_email= models.EmailField(verbose_name='Email Address', unique=False, blank=True, null=True)
    tickets=models.ManyToManyField('CreateTicket', related_name='tickets', blank=True)
    
        
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

#MARKET PLACE 
#Pres/Treasurer use
class Tag(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

class Item(models.Model):
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE, related_name='items')
    item_name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.FileField(upload_to='merchIMG/', null=True, blank=True)
    quantity = models.PositiveIntegerField()
    tags = models.ManyToManyField(Tag, related_name='items')

    def __str__(self):
        tag_names = ', '.join(tag.name for tag in self.tags.all())
        return f"Item {self.item_name} (${self.price}). {self.quantity} left. Tags: {tag_names}."


class Poll(models.Model):
    question = models.TextField()
    option_one = models.CharField(max_length=50)
    option_two = models.CharField(max_length=50)
    option_three = models.CharField(max_length=50)
    option_one_count = models.IntegerField(default=0)
    option_two_count = models.IntegerField(default=0)
    option_three_count = models.IntegerField(default=0)
    pub_date = models.DateTimeField()
    expiration_date = models.DateTimeField()

    # Add organization field
    organization = models.ForeignKey(
        'Organization', 
        on_delete=models.CASCADE, 
        related_name='polls',
        null=True  # Make it nullable for existing records
    )

    # Track who created the poll
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_polls',
        null=True
    )

    def total(self):
        return self.option_one_count + self.option_two_count + self.option_three_count


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
    description = models.TextField(default = 'Description Here')
    receipt = models.FileField(upload_to='receipts/', null=True, blank=True)
    objects = TicketManager()
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Ticket {self.id} created ({self.date}), balance: ${self.__class__.objects.get_balance()}"
    
class FundingRequest(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('review', 'Under Review'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
    ]
    
    subject = models.CharField(max_length=255)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    link = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Add organization field
    organization = models.ForeignKey(
        'Organization', 
        on_delete=models.CASCADE, 
        related_name='funding_requests',
        null=True  # Make it nullable for existing records
    )

    # Track who created the funding requests
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_funding_requests',
        null=True
    )
    
    def __str__(self):
        return f"{self.subject} (${self.amount}) - {self.status}"
    







 
    

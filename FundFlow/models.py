from django.db import models
from django.contrib.auth.models import User

from django.db.models import Sum, F, Case, When, DecimalField
from datetime import datetime

#Role-Based Access Control Models

#Organization position will determine permissions. 
class Organization(models.Model):
    name= models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    #Functions for managing student/member role changes and checking statuses
   
    #change view so that it says view org instead of join for already members)
    #same logic will apply for admin
    
    #For student use 
    def request_membership(self, user):  #'student' user requesting to join
        membership = Membership.objects.filter(user=user, organization=self).first()

        if membership:
            if membership.role == 'student' and membership.status == 'not_requested':
                membership.status = 'pending'
                membership.save()
        else:
            Membership.objects.create(
                user=user,
                organization=self,
                role='student',
                status='pending'
            )
        
    #For President Use    
    def approve_membership(self, user):
        membership = Membership.objects.filter( #user is a student who requested to join org
            user=user,
            organization=self,
            role='student',
            status='pending'
        ).first()

        if membership: 
            membership.role = 'member'
            membership.status = 'active'
            membership.save() #user has changed roles, now an active member 

    #For President Use 
    def deny_membership(self, user): #user is a student whose status will change from pending back to not_requested
        membership = Membership.objects.get(user=user, organization=self)

        if membership.role == 'student' and membership.status == 'pending':
            membership.status = 'not_requested' 
            membership.save()

    #For President use
    def get_pending_requests(self):
        return Membership.objects.filter(organization=self,  role='student', status='pending',)
    
    #For President Use
    def get_members(self): #retrieves all including treasurer and pres
        return Membership.objects.filter(organization=self, status='active')

    #for President Use
    def remove_member(self, user):
        membership = Membership.objects.filter(
            user=user,
            organization=self,
            status='active'
        ).first()

        if membership:
            membership.status = 'not_requested'
            membership.role = 'student'
            membership.save()
            
    def __str__(self):
        return self.name


class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('guest', 'Guest'),
        ('admin', 'Site Admin'),  # not per-org admin, but global #approves treasurer/president requests , has their own pg
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='student')

    def __str__(self):
        return self.user.username



#We arent using the built-in Groups model because roles vary per org
class Membership(models.Model): #connecting users to unique organiztions (Many to Many)
    
    ROLE_CHOICES = [
        ('president', 'President'),
        ('treasurer', 'Treasurer'), 
        ('member', 'Member'),
        ('student', 'Student') #default upon join
    ]
    role = models.CharField( #was user_type
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='student'
    )
    
    STATUS_CHOICES = [
        ('not_requested', 'Has not requested'),
        ('pending', 'Pending'),
        ('active', 'Active')
    ]
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='not_requested'
    )

    # One user correlates to one user profile
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Creating a users role for each organization
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'organization')  # no duplicate memberships

    def __str__(self):
        return f"{self.user.username} in {self.organization.name} as {self.role}"
    

#Filter based on Org and user roles
class Poll(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    question = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    #make this scalable 
    option_one = models.CharField(max_length=50)
    option_two = models.CharField(max_length=50)
    option_three = models.CharField(max_length=50)
    option_one_count = models.IntegerField(default=0)
    option_two_count = models.IntegerField(default=0)
    option_three_count = models.IntegerField(default=0)

    def total(self):
        return self.option_one_count + self.option_two_count + self.option_three_count
    def __str__(self):
        return f"Poll made by {self.created_by} in {self.organization.name}"


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
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    
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
    receipt = models.FileField(upload_to='receipts/', null=True, blank=True)
    objects = TicketManager()
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Ticket {self.id} created ({self.date}), balance: ${self.__class__.objects.get_balance()}"
    
class FundingRequest(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    
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
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Connect to User model for tracking who submitted the request
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='funding_requests')
    
    def __str__(self):
        return f"{self.subject} (${self.amount}) - {self.status}"
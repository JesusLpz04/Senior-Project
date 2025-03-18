from django.db import models

# Create your models here.

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

    def __str__(self):
        return f"Ticket created {self.id}: {self.amount} on {self.date}"

class Balance(models.Model):
    balance= models.DecimalField(max_digits=10, decimal_places=2)
    add =  models.DecimalField(max_digits=10, decimal_places=2)
    sub=  models.DecimalField(max_digits=10, decimal_places=2)
    def total(self):
        return self.balance
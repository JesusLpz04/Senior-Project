from django.forms import ModelForm
from django import forms
from .models import Poll

class CreatePollForm(ModelForm):
    class Meta: 
        model = Poll
        fields = ['question', 'option_one', 'option_two', 'option_three']
        
        
from .models import CreateTicket

class CreateTicketForm(ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'})) 

    class Meta:
        model = CreateTicket
        fields = ['balance', 'amount', 'date', 'confirmation']
    
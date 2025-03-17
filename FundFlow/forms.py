from django.forms import ModelForm
from django import forms
from .models import Poll, CreateTicket, UserProfile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True)
    user_type = forms.ChoiceField(
        choices=UserProfile.USER_TYPES,
        required=True,
        widget=forms.RadioSelect
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'user_type')
        

class CreatePollForm(ModelForm):
    class Meta: 
        model = Poll
        fields = ['question', 'option_one', 'option_two', 'option_three']
        

class CreateTicketForm(ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'})) 

    class Meta:
        model = CreateTicket
        fields = ['balance', 'amount', 'date', 'confirmation']
    
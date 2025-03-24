from django.forms import ModelForm
from django import forms
from .models import Poll, CreateTicket #, CustomCategory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')
        

class CreatePollForm(ModelForm):
    class Meta: 
        model = Poll
        fields = ['question', 'option_one', 'option_two', 'option_three']

class CreateTicketForm(ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    receipt = forms.FileField(required=False, widget=forms.FileInput(attrs={'accept': 'image/jpeg,image/png,application/pdf'}))

    class Meta:
        model = CreateTicket
        fields = ['amount', 'date', 'operation', 'expense_category', 'receipt'] #'custom_category'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #custom_categories = [(cat.name, cat.name) for cat in CustomCategory.objects.all()] # grab custom categories
        self.fields['expense_category'].choices #+= custom_categories # Append custom categories to default choices
    
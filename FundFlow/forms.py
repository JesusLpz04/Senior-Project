from django.forms import ModelForm
from django import forms
from .models import Poll, CreateTicket, FundingRequest, UserProfile
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
        fields = ['amount', 'date', 'operation', 'expense_category', 'receipt'] 
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['expense_category'].choices 
    
class FundingRequestForm(ModelForm):
    class Meta:
        model = FundingRequest
        fields = ['subject', 'description', 'amount', 'link']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'amount': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
            'link': forms.URLInput(attrs={'placeholder': 'https://example.com'})
        }
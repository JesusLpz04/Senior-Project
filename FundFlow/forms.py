from django.forms import ModelForm
from django import forms
from .models import Poll, CreateTicket, FundingRequest, Item,  Tag, Organization, UserProfile #, CartItem, Tag
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User



class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')
        

class CreatePollForm(forms.ModelForm):
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.none(),  # Will be set in __init__
        required=True,
        label="Organization"
    )
    
    class Meta:
        model = Poll
        fields = ['question', 'option_one', 'option_two', 'option_three', 'pub_date', 'expiration_date', 'organization']
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'date'}),
            'expiration_date': forms.DateTimeInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(CreatePollForm, self).__init__(*args, **kwargs)
        
        if user:
            # Only show organizations where the user has appropriate permissions
            if user.userprofile.user_type in ['president', 'treasurer']:
                if user.userprofile.user_type == 'president':
                    # Presidents can create polls for orgs they're president of
                    self.fields['organization'].queryset = Organization.objects.filter(president=user)
                else:
                    # Treasurers can create polls for orgs they're members of
                    self.fields['organization'].queryset = Organization.objects.filter(members=user)
    
class CreateTicketForm(ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    receipt = forms.FileField(required=False, widget=forms.FileInput(attrs={'accept': 'image/jpeg,image/png,application/pdf'}))

    class Meta:
        model = CreateTicket
        fields = ['amount', 'date', 'operation', 'expense_category', 'description', 'receipt'] 
        fields = ['amount', 'date', 'operation', 'expense_category', 'description', 'receipt'] 
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['expense_category'].choices 
    


class CreateItemForm(ModelForm):
    image = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/jpeg,image/png,application/pdf'})
    )

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Item
        fields = ['item_name', 'price', 'quantity', 'tags', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



class CreateItemForm(ModelForm):
    image = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/jpeg,image/png,application/pdf'})
    )

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Item
        fields = ['item_name', 'price', 'quantity', 'tags', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class FundingRequestForm(ModelForm):
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.none(),  # Will be set in __init__
        required=True,
        label="Organization"
    )
    
    class Meta:
        model = FundingRequest
        fields = ['subject', 'description', 'amount', 'link', 'organization']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'amount': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
            'link': forms.URLInput(attrs={'placeholder': 'https://example.com'})
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(FundingRequestForm, self).__init__(*args, **kwargs)
        
        if user:
            # Show organizations where the user is a member
            self.fields['organization'].queryset = Organization.objects.filter(members=user)
from django.contrib import admin
from .models import UserProfile, Poll, CreateTicket

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Poll)
admin.site.register(CreateTicket)
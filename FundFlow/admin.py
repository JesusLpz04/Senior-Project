from django.contrib import admin
from .models import UserProfile, Membership, Organization, Poll, CreateTicket

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Membership)
admin.site.register(Organization)
admin.site.register(Poll)
admin.site.register(CreateTicket)
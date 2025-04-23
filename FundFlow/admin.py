from django.contrib import admin
from .models import UserProfile, Organization, Poll, CreateTicket, CartItem, CreateItem, Tag

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Organization)
admin.site.register(Poll)
admin.site.register(CreateTicket)
admin.site.register(CartItem)
admin.site.register(CreateItem)
admin.site.register(Tag)
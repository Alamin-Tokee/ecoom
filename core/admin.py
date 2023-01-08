from django.contrib import admin
from .models import UserProfile, Item

# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Item)

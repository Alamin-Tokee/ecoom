from django.contrib import admin
from .models import UserProfile, Item, OrderItem, Order, Address, Coupon, Payment, Refund

# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Address)
admin.site.register(Coupon)

admin.site.register(Payment)
admin.site.register(Refund)
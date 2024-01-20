from django.contrib import admin
from .models import Train, Schedule, Booking
# Register your models here.
admin.site.register(Train)
admin.site.register(Schedule)
admin.site.register(Booking)
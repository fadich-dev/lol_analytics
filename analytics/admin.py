from django.contrib import admin
from .models import Account, Champion, Match

# Register your models here.

admin.site.register(Account)
admin.site.register(Champion)
admin.site.register(Match)

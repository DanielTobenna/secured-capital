from django.contrib import admin

from .models import *

# Register your models here.

admin.site.register(Client)
admin.site.register(Payment_id)
admin.site.register(Withdrawal_request)
admin.site.register(Transaction)

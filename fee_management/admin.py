from django.contrib import admin
from .models import FeePayment,FeeStructure,TransactionLog

admin.site.register(FeePayment)
admin.site.register(FeeStructure)
admin.site.register(TransactionLog)
from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('tx_ref', 'amount', 'currency', 'email', 'status', 'created_at')
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('tx_ref', 'email', 'first_name', 'last_name')
    readonly_fields = ('tx_ref', 'created_at', 'updated_at', 'chapa_reference')

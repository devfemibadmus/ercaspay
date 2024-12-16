from django.contrib import admin
from .models import Transaction
from django.contrib import messages
from .django import ercaspay

def cancel_transaction(modeladmin, request, queryset):
    for transaction in queryset:
        if transaction.status != 'PENDING':
            messages.error(request, f"Can only cancel PENDING Transactions.")
        else:
            response = ercaspay.cancel(transaction.ercaspay_reference)
            if response.get('errorCode'):
                messages.error(request, f"Transaction {transaction.full_name} {response.get('explanation')}.")
            else:
                update_status(modeladmin, request, queryset.filter(pk=transaction.pk))

def update_status(modeladmin, request, queryset):
    for transaction in queryset:
        response = ercaspay.status(transaction.ercaspay_reference)
        print(response)
        if response.get('errorCode'):
            messages.error(request, f"Transaction {transaction.full_name} {response.get('explanation')}.")
        else:
            status = response.get('responseBody', {}).get('status', transaction.status)
            transaction.status = status
            transaction.save()
            messages.success(request, f"Transaction {transaction.full_name} status has been updated.")


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'formatted_amount', 'ercaspay_reference', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'currency')
    search_fields = ('full_name', 'email', 'ercaspay_reference', 'payment_reference')
    ordering = ('-created_at', 'currency')
    list_per_page = 20
    actions = [cancel_transaction, update_status]

    fieldsets = (
        (None, {
            'fields': ('full_name', 'email', 'amount', 'currency', 'phone_number')  # Add currency here
        }),
        ('Payment Details', {
            'fields': ('ercaspay_reference', 'payment_reference', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )
    def formatted_amount(self, obj):
        return f"{obj.currency} {obj.amount:,.2f}"
    formatted_amount.short_description = 'Amount'
    readonly_fields = ('created_at',)

admin.site.register(Transaction, TransactionAdmin)

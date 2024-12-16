from django.db import models
from django.utils.formats import number_format

class Transaction(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    ercaspay_reference = models.CharField(max_length=255, unique=True)
    payment_reference = models.CharField(max_length=255, unique=True)
    currency = models.CharField(max_length=50, default='NGN')
    status = models.CharField(max_length=50, default='PENDING')
    # status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def formatted_amount(self):
        return number_format(self.amount, decimal_pos=2, use_l10n=True)

    def __str__(self):
        return f"{self.full_name} - {self.amount}"



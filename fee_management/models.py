from django.db import models, transaction
from django.conf import settings
from students.models import Student
from django.utils import timezone
import uuid
import logging
import razorpay
from django.db.models.signals import pre_save
from django.dispatch import receiver

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

logger = logging.getLogger('fee_management')

class FeeStructure(models.Model):
    
    grade = models.CharField(max_length=10)
    academic_year = models.CharField(max_length=10)  
    tuition_fee = models.DecimalField(max_digits=10, decimal_places=2)
    library_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lab_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fine_per_day = models.DecimalField(max_digits=6, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('grade', 'academic_year')

    def __str__(self):
        return f"{self.grade} - {self.academic_year}"


@receiver(pre_save, sender=FeeStructure)
def prevent_edit(sender, instance, **kwargs):
    if instance.pk:
        raise ValueError("Fee structures cannot be edited once created.")

class FeePayment(models.Model):
    STATUS_CHOICES = [
        (0, 'Pending'),
        (1, 'Completed'),
        (2, 'Failed'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_payments')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fine_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    payment_date = models.DateTimeField(null=True, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)  # Numeric status
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    receipt = models.FileField(upload_to='receipts/', null=True, blank=True)
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            self.__class__.objects.select_for_update().get(pk=self.pk) if self.pk else None
            super().save(*args, **kwargs)
            logger.info(f"Fee payment {self.transaction_id} for student {self.student} - Status: {self.get_status_display()}")

    def calculate_fine(self):
        if self.status == 0 and timezone.now().date() > self.due_date:  
            days_overdue = (timezone.now().date() - self.due_date).days
            self.fine_amount = days_overdue * self.fee_structure.fine_per_day
            self.total_amount = self.amount + self.fine_amount
            self.save()

    def __str__(self):
        return f"{self.student} - {self.fee_structure} - {self.total_amount}"

class TransactionLog(models.Model):
    transaction_id = models.UUIDField()
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.IntegerField()  
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField()

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.status}"
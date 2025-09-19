from rest_framework import serializers
from .models import FeePayment,FeeStructure
from django.utils import timezone
from datetime import timedelta
from .utils import get_razorpay_client
import logging

logger = logging.getLogger('fee_management')

class FeeStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model=FeeStructure
        fields=['grade', 'academic_year', 'tuition_fee', 'library_fee', 'lab_fee', 'fine_per_day']
        def validate_academic_year(self, value):
            try:
                start_year, end_year = map(int, value.split('-'))
                if start_year >= end_year or len(value) != 9:
                    raise serializers.ValidationError("Academic year must be in format 'YYYY-YYYY' with valid years.")
            except ValueError:
                raise serializers.ValidationError("Academic year must be in format 'YYYY-YYYY'.")
            return value

        def validate_tuition_fee(self, value):
            if value <= 0:
                raise serializers.ValidationError("Tuition fee must be positive.")
            return value

        def validate_library_fee(self, value):
            if value < 0:
                raise serializers.ValidationError("Library fee cannot be negative.")
            return value

        def validate_lab_fee(self, value):
            if value < 0:
                raise serializers.ValidationError("Lab fee cannot be negative.")
            return value

        def validate_fine_per_day(self, value):
            if value <= 0:
                raise serializers.ValidationError("Fine per day must be positive.")
            return value

        def validate(self, data):
            if FeeStructure.objects.filter(grade=data['grade'], academic_year=data['academic_year']).exists():
                raise serializers.ValidationError("Fee structure for this grade and academic year already exists.")
            return data
        
class PaymentCallbackSerializer(serializers.Serializer):

    razorpay_order_id = serializers.CharField(max_length=100)
    razorpay_payment_id= serializers.CharField(max_length=100)
    razorpay_signature= serializers.CharField(max_length=200)

    def validate(self,data):
        try:
            razorpay_client=get_razorpay_client()
        except Exception as e:
            raise serializers.ValidationError(f"Payment service unavailable: {str(e)}")
        
        try:
            razorpay_client.utility.verify_payment_signature(data)
            logger.info(f"Signature verification passed for order: {data['razorpay_order_id']}")
        except Exception as e:
            logger.error(f"signature verification failed:{str(e)}")
            raise serializers.ValidationError("Invalid payment signature.")
        
        try:
            payment = FeePayment.objects.select_for_update().get(
                razorpay_order_id=data['razorpay_order_id']
            )
        except FeePayment.DoesNotExist:
            logger.warning(f"Order not found:{data['razorpay_order_id']}")
            serializers.ValidationError("order not found")

        if payment.status!=0:
            logger.warning(f"Payment already processed: {payment.id},Status: {payment.get_status_display()}")
            raise serializers.ValidationError(f"payment already {payment.get_status_display().lower()}")
        
        if payment.due_date < timezone.now().date() - timedelta(days=365):
            raise serializers.ValidationError("Payment is expired and cannot be processed.")
        
        self.context['payment'] = payment
        logger.info(f" Payment validation passed: {payment.id} for {payment.student}")
        
        return data
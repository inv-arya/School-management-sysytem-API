from django.shortcuts import render
from rest_framework import generics , status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.db import transaction
from .models import FeeStructure,FeePayment,TransactionLog
from .serializers import FeeStructureSerializer
from django.conf import settings
import razorpay
import logging

logger = logging.getLogger('fee_management')

def get_razorpay_client():
    """Initialize Razorpay client on-demand in views"""
    try:
        if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
            raise ValueError("Razorpay API keys not configured")
        
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        return client
    except Exception as e:
        logger.error(f"Razorpay client initialization failed: {str(e)}")
        raise ValidationError(f"Payment service unavailable: {str(e)}")

#fee structure creation view

class CreateFeeStructureView(generics.CreateAPIView):
    permission_classes=[IsAuthenticated,IsAdminUser]
    serializer_class=FeeStructureSerializer
    
    def perform_create(self, serializer):
        try:
            serializer.save()
            logger.info(f"Fee structure created for {serializer.validated_data['grade']} - {serializer.validated_data['academic_year']}")
        except Exception as e:
            logger.error(f"Error creating fee structure: {str(e)}")
            raise

#fee payment initiation view

class InitiatePaymentView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        # Basic validation
        try:
            payment = FeePayment.objects.get(id=pk, status=0)
        except FeePayment.DoesNotExist:
            return Response(
                {'error': 'Payment not found or already processed'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check amount
        if payment.total_amount <= 0:
            return Response(
                {'error': 'Invalid payment amount'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Idempotency check
        if payment.razorpay_order_id:
            return Response({
                'order_id': payment.razorpay_order_id,
                'is_retry': True
            }, status=status.HTTP_200_OK)
        
        # Create order
        try:
            razorpay_client = get_razorpay_client()  # ADDED: Use the function
            
            # Create order
            with transaction.atomic():
                payment.calculate_fine()
                order_data = {
                    'amount': int(payment.total_amount * 100),
                    'currency': 'INR',
                    'receipt': str(payment.transaction_id),
                    'payment_capture': 1
                }
                # FIXED: Now razorpay_client is defined
                order = razorpay_client.order.create(data=order_data)
                payment.razorpay_order_id = order['id']
                payment.save()
            
            logger.info(f"Payment initiated: {payment.id}")
            return Response({'order_id': order['id']}, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Payment initiation failed for {pk}: {str(e)}")
            return Response(
                {'error': 'Payment service temporarily unavailable'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
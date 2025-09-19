from django.shortcuts import render
from rest_framework import generics , status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from django.db import transaction
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.conf import settings
from .models import FeePayment,TransactionLog
from .serializers import FeeStructureSerializer,PaymentCallbackSerializer
from .utils import get_razorpay_client
import pdfkit
import logging

logger = logging.getLogger('fee_management')


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
        
class PaymentCallbackView(generics.GenericAPIView):
    permission_classes = []  
    
    serializer_class = PaymentCallbackSerializer

    def post(self, request):
        logger.info(f"Payment callback received: {request.data}")
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        payment = serializer.context['payment']
        
        with transaction.atomic():
            payment.status = 1  # Completed
            payment.razorpay_payment_id = data['razorpay_payment_id']
            payment.payment_date = timezone.now()
            
            # Generate PDF receipt
            pdf_content = render_to_string('fee_management/receipt_template.html', {'payment': payment})
            pdf_file = pdfkit.from_string(pdf_content, False)
            payment.receipt.save(f'receipt_{payment.transaction_id}.pdf', ContentFile(pdf_file))
            payment.save()
            
            # Log transaction
            TransactionLog.objects.create(
                transaction_id=payment.transaction_id,
                student=payment.student,
                amount=payment.total_amount,
                status=1,
                details=str(data)
            )
            
            # Send confirmation email
            try:
                send_mail(
                    'Payment Successful',
                    f'Your payment of {payment.total_amount} has been received successfully.',
                    settings.DEFAULT_FROM_EMAIL,
                    [payment.student.email],
                    fail_silently=True
                )
                logger.info(f"Payment {payment.transaction_id} completed for {payment.student}")
            except Exception as e:
                logger.error(f"Failed to send confirmation email for payment {payment.id}: {str(e)}")
        
        return Response(status=status.HTTP_200_OK)
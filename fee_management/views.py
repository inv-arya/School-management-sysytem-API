from django.shortcuts import render
from rest_framework import generics , status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from .models import FeeStructure,FeePayment,TransactionLog,razorpay_client
from.serializers import FeeStructureSerializer
import logging
logger = logging.getLogger('fee_management')

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
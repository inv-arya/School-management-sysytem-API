from django.urls import path
from .views import CreateFeeStructureView,InitiatePaymentView,PaymentCallbackView

urlpatterns = [
    path('create/',CreateFeeStructureView.as_view(), name='create_fee_structure'),
    path('pay/<int:pk>/', InitiatePaymentView.as_view(), name='initiate_payment'),
    path('callback/', PaymentCallbackView.as_view(), name='payment_callback'),
]

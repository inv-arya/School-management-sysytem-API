from django.urls import path
from .views import CreateFeeStructureView

urlpatterns = [
    path('create/',CreateFeeStructureView.as_view(), name='create_fee_structure')
]

from django.urls import path
from .views import CustomTokenObtainPairView, MyProfileView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', MyProfileView.as_view(), name='my_profile'),
]

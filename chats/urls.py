from django.urls import path
from . import views

urlpatterns = [
    path('create-chat-request/', views.ChatRequestCreateView.as_view(), name='create_chat_request'),
    path('requests/approve/<uuid:token>/', views.ChatRequestApproveView.as_view(), name='approve_chat'),
    path('requests/cancel/<uuid:token>/', views.ChatRequestCancelView.as_view(), name='cancel_chat'),
    path('send-message/', views.ChatMessageCreateView.as_view(), name='send_message'),
    path('get-messages/<int:chat_id>/', views.ChatMessageListView.as_view(), name='get_messages'),
]


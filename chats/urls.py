from django.urls import path
from . import views

urlpatterns = [
    path('create-chat-request/', views.ChatRequestCreateView.as_view(), name='create_chat_request'),
    path('requests/approve/<uuid:token>/', views.ChatRequestApproveView.as_view(), name='approve_chat'),
    path('requests/cancel/<uuid:token>/', views.ChatRequestCancelView.as_view(), name='cancel_chat'),
    
    path('get-messages/<int:chat_id>/', views.ChatMessageListView.as_view(), name='get_messages'),
    path('check-status/<int:student_id>/', views.ChatStatusCheckView.as_view(), name='check_chat_status'),
    path('check-status-by-id/<int:chat_id>/', views.ChatStatusByIdView.as_view(), name='check_chat_status_by_id'),
    path('requests/bulk-cancel-by-teacher/<int:teacher_id>/', views.CancelChatRequestsByTeacherView.as_view(), name='bulk_cancel_by_teacher'),
]

    
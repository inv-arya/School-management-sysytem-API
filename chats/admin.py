from django.contrib import admin
from .models import ChatMessage
from .models import ChatRequest

admin.site.register(ChatMessage)
admin.site.register(ChatRequest)

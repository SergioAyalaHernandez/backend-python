from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_message),
    path('list/', views.get_messages),
    path('update/<str:message_id>/', views.update_message),
    path('delete/<str:message_id>/', views.delete_message),
    path('questions/', views.list_questions),
    path('answer/<str:message_id>/', views.get_answer),
]

from django.urls import path
from .views import register_view, login_view, refresh_view, user_detail_view, users_list_view, delete_user_view, update_user_view

urlpatterns = [
    path('register/', register_view),
    path('login/', login_view),
    path('refresh/', refresh_view),
    path('list/', users_list_view), 
    path('detail/<str:user_id>/', user_detail_view),  
    path('update/<str:user_id>/', update_user_view), 
    path('delete/<str:user_id>/', delete_user_view), 
]
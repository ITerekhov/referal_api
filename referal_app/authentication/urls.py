from django.urls import path
from .views import LoginAPIView, UserRetrieveUpdateAPIView
app_name = 'authentication'

urlpatterns = [
    path('user', UserRetrieveUpdateAPIView.as_view()),
    path('login', LoginAPIView.as_view()),
]
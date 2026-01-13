from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .api import (
    HabitViewSet, HabitLogViewSet,
    DashboardAPIView, CustomAuthToken
)

router = DefaultRouter()
router.register(r'habits', HabitViewSet, basename='habit')
router.register(r'logs', HabitLogViewSet, basename='log')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', DashboardAPIView.as_view(), name='api_dashboard'),
    path('auth/token/', CustomAuthToken.as_view(), name='api_token_auth'),
    path('auth/', include('rest_framework.urls')),  # Session authentication
]
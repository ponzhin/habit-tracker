from django.urls import path
from . import views
from .views import reminder_settings_view

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_habit, name='create_habit'),
    path('<int:habit_id>/log/', views.log_habit, name='log_habit'),
    path('<int:habit_id>/calendar/', views.calendar_view, name='calendar'),
    path('<int:habit_id>/statistics/', views.statistics_view, name='statistics'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('reminders/settings/', reminder_settings_view, name='reminder_settings'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_habit, name='create_habit'),
    path('<int:habit_id>/log/', views.log_habit, name='log_habit'),
    path('<int:habit_id>/calendar/', views.calendar_view, name='calendar'),
]
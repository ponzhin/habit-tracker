from django.urls import path
from . import views
from .views import reminder_settings_view
from .social_views import achievements_list, public_achievements, share_achievement

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_habit, name='create_habit'),
    path('<int:habit_id>/log/', views.log_habit, name='log_habit'),
    path('<int:habit_id>/calendar/', views.calendar_view, name='calendar'),
    path('<int:habit_id>/statistics/', views.statistics_view, name='statistics'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('reminders/settings/', reminder_settings_view, name='reminder_settings'),
    path('achievements/', achievements_list, name='achievements_list'),
    path('achievements/public/', public_achievements, name='public_achievements'),
    path('achievements/<int:achievement_id>/share/', share_achievement, name='share_achievement'),
]
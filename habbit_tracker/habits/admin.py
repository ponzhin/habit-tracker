from django.contrib import admin
from .models import Habit, HabitLog

@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'frequency', 'target', 'is_active']
    list_filter = ['frequency', 'is_active']
    search_fields = ['name', 'description']

@admin.register(HabitLog)
class HabitLogAdmin(admin.ModelAdmin):
    list_display = ['habit', 'date', 'completed']
    list_filter = ['date', 'completed']
    date_hierarchy = 'date'
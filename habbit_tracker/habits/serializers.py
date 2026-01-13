from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Habit, HabitLog


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class HabitLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitLog
        fields = ['id', 'date', 'completed', 'notes']
        read_only_fields = ['id']


class HabitSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    logs = HabitLogSerializer(many=True, read_only=True)
    current_streak = serializers.SerializerMethodField()
    completion_rate = serializers.SerializerMethodField()

    class Meta:
        model = Habit
        fields = [
            'id', 'user', 'name', 'description', 'frequency',
            'target', 'created_at', 'is_active', 'logs',
            'current_streak', 'completion_rate'
        ]
        read_only_fields = ['id', 'user', 'created_at']

    def get_current_streak(self, obj):
        return obj.get_current_streak()

    def get_completion_rate(self, obj):
        return obj.get_completion_percentage()

    def create(self, validated_data):
        # Автоматически назначаем текущего пользователя
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class HabitStatisticsSerializer(serializers.Serializer):
    """Сериализатор для статистики"""
    habit_id = serializers.IntegerField()
    name = serializers.CharField()
    current_streak = serializers.IntegerField()
    completion_rate = serializers.IntegerField()
    total_completed = serializers.IntegerField()
    best_streak = serializers.IntegerField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class DailyCompletionSerializer(serializers.Serializer):
    """Сериализатор для ежедневной статистики"""
    date = serializers.DateField()
    completed = serializers.BooleanField()
    streak = serializers.IntegerField()
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from .models import Habit, HabitLog
from .serializers import (
    HabitSerializer, HabitLogSerializer,
    HabitStatisticsSerializer, DailyCompletionSerializer,
    UserSerializer
)


class CustomAuthToken(ObtainAuthToken):
    """Кастомный endpoint для получения токена"""
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'username': user.username
        })


class HabitViewSet(viewsets.ModelViewSet):
    """ViewSet для привычек"""
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def log_today(self, request, pk=None):
        """Отметить выполнение на сегодня"""
        habit = self.get_object()
        today = timezone.now().date()

        log, created = HabitLog.objects.get_or_create(
            habit=habit,
            date=today,
            defaults={'completed': True}
        )

        if not created:
            log.completed = not log.completed
            log.save()

        serializer = HabitLogSerializer(log)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Получить статистику по привычке"""
        habit = self.get_object()

        # Данные за 30 дней
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)

        logs = HabitLog.objects.filter(
            habit=habit,
            date__range=[start_date, end_date]
        ).order_by('date')

        # Подготовка данных для графика
        daily_data = []
        current_date = start_date
        current_streak = 0

        while current_date <= end_date:
            log = logs.filter(date=current_date).first()
            completed = log.completed if log else False

            if completed:
                current_streak += 1
            else:
                current_streak = 0

            daily_data.append({
                'date': current_date,
                'completed': completed,
                'streak': current_streak
            })

            current_date += timedelta(days=1)

        # Лучшая серия
        streaks = []
        current_streak = 0
        for day in daily_data:
            if day['completed']:
                current_streak += 1
            else:
                if current_streak > 0:
                    streaks.append(current_streak)
                current_streak = 0

        if current_streak > 0:
            streaks.append(current_streak)

        best_streak = max(streaks) if streaks else 0

        # Подготовка ответа
        stats = {
            'habit_id': habit.id,
            'name': habit.name,
            'current_streak': habit.get_current_streak(),
            'completion_rate': habit.get_completion_percentage(),
            'total_completed': habit.logs.filter(completed=True).count(),
            'best_streak': best_streak,
            'daily_data': daily_data[-7:],  # Последние 7 дней
        }

        serializer = HabitStatisticsSerializer(stats)
        return Response(serializer.data)


class HabitLogViewSet(viewsets.ModelViewSet):
    """ViewSet для отметок выполнения"""
    serializer_class = HabitLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return HabitLog.objects.filter(habit__user=self.request.user)

    def perform_create(self, serializer):
        habit_id = self.request.data.get('habit')
        habit = get_object_or_404(Habit, id=habit_id, user=self.request.user)
        serializer.save(habit=habit)


class DashboardAPIView(generics.GenericAPIView):
    """API для дашборда"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        habits = Habit.objects.filter(user=request.user, is_active=True)

        stats = []
        total_completion = 0

        for habit in habits:
            completion_rate = habit.get_completion_percentage()
            current_streak = habit.get_current_streak()

            stats.append({
                'id': habit.id,
                'name': habit.name,
                'completion_rate': completion_rate,
                'current_streak': current_streak,
                'total_logs': habit.logs.count(),
                'total_completed': habit.logs.filter(completed=True).count(),
            })

            total_completion += completion_rate

        average_completion = round(total_completion / len(stats)) if stats else 0

        # Ежедневная статистика (последние 7 дней)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=7)

        daily_stats = []
        for i in range(7):
            date = start_date + timedelta(days=i)
            daily_logs = HabitLog.objects.filter(
                habit__user=request.user,
                date=date,
                completed=True
            )
            daily_stats.append({
                'date': date,
                'completed_habits': daily_logs.count(),
                'total_habits': habits.count(),
            })

        return Response({
            'stats': stats,
            'summary': {
                'total_habits': len(stats),
                'average_completion': average_completion,
                'total_completed_logs': sum(s['total_completed'] for s in stats),
            },
            'daily_stats': daily_stats,
        })
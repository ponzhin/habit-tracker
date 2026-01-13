from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Habit, HabitLog
from .forms import HabitForm, HabitLogForm


@login_required
def index(request):
    """Главная страница со списком привычек"""
    habits = Habit.objects.filter(user=request.user, is_active=True)

    # Получаем сегодняшнюю дату
    today = timezone.now().date()

    # Для каждой привычки проверяем, есть ли отметка на сегодня
    for habit in habits:
        habit.today_log = HabitLog.objects.filter(
            habit=habit,
            date=today
        ).first()

    return render(request, 'habits/index.html', {'habits': habits, 'today': today})


@login_required
def create_habit(request):
    """Создание новой привычки"""
    if request.method == 'POST':
        form = HabitForm(request.POST)
        if form.is_valid():
            habit = form.save(commit=False)
            habit.user = request.user
            habit.save()
            messages.success(request, 'Привычка создана!')
            return redirect('index')
    else:
        form = HabitForm()

    return render(request, 'habits/create_habit.html', {'form': form})


@login_required
def log_habit(request, habit_id):
    """Отметка выполнения привычки"""
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    today = timezone.now().date()

    # Получаем или создаем запись на сегодня
    log, created = HabitLog.objects.get_or_create(
        habit=habit,
        date=today,
        defaults={'completed': False}
    )

    if request.method == 'POST':
        form = HabitLogForm(request.POST, instance=log)
        if form.is_valid():
            form.save()
            messages.success(request, 'Статус обновлен!')
            return redirect('index')
    else:
        form = HabitLogForm(instance=log)

    return render(request, 'habits/log_habit.html', {'form': form, 'habit': habit})


@login_required
def calendar_view(request, habit_id):
    """Календарь выполнения привычки"""
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)

    # Получаем логи за последние 30 дней
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)

    logs = HabitLog.objects.filter(
        habit=habit,
        date__range=[start_date, end_date]
    ).order_by('date')

    # Создаем словарь для удобства отображения
    log_dict = {log.date: log for log in logs}

    # Генерируем список дней
    days = []
    current_date = start_date
    while current_date <= end_date:
        days.append({
            'date': current_date,
            'log': log_dict.get(current_date)
        })
        current_date += timedelta(days=1)

    return render(request, 'habits/calendar.html', {
        'habit': habit,
        'days': days
    })
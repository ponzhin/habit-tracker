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

@login_required
def statistics_view(request, habit_id):
    """Детальная статистика привычки с графиками"""
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)

    # Данные за последние 30 дней
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)

    logs = HabitLog.objects.filter(
        habit=habit,
        date__range=[start_date, end_date]
    ).order_by('date')

    # Подготовка данных для графиков
    dates = []
    completed_data = []
    streak_data = []

    current_streak = 0
    current_date = start_date

    while current_date <= end_date:
        log = logs.filter(date=current_date).first()
        is_completed = log.completed if log else False

        dates.append(current_date.strftime('%d.%m'))
        completed_data.append(1 if is_completed else 0)

        if is_completed:
            current_streak += 1
        else:
            current_streak = 0

        streak_data.append(current_streak)
        current_date += timedelta(days=1)

    # Еженедельная статистика
    weekly_stats = []
    for i in range(0, len(dates), 7):
        week_dates = dates[i:i+7]
        week_completed = completed_data[i:i+7]
        weekly_stats.append({
            'week': f"Неделя {i//7 + 1}",
            'completed': sum(week_completed),
            'total': len(week_dates),
            'percentage': round((sum(week_completed) / len(week_dates)) * 100) if week_dates else 0
        })

    # Общая статистика
    total_days = 30
    completed_days = sum(completed_data)
    completion_rate = round((completed_days / total_days) * 100)

    context = {
        'habit': habit,
        'dates': dates,
        'completed_data': completed_data,
        'streak_data': streak_data,
        'weekly_stats': weekly_stats,
        'total_days': total_days,
        'completed_days': completed_days,
        'completion_rate': completion_rate,
        'best_streak': max(streak_data) if streak_data else 0,
    }

    return render(request, 'habits/statistics.html', context)


@login_required
def dashboard_view(request):
    """Общая статистика всех привычек"""
    habits = Habit.objects.filter(user=request.user, is_active=True)

    stats = []
    for habit in habits:
        completion_rate = habit.get_completion_percentage()
        current_streak = habit.get_current_streak()

        stats.append({
            'habit': habit,
            'completion_rate': completion_rate,
            'current_streak': current_streak,
            'status': 'excellent' if completion_rate >= 80 else
                     'good' if completion_rate >= 60 else
                     'average' if completion_rate >= 40 else 'poor'
        })

    # Сортируем по проценту выполнения
    stats.sort(key=lambda x: x['completion_rate'], reverse=True)

    # Подготовка данных для круговой диаграммы
    habit_names = [stat['habit'].name for stat in stats]
    completion_rates = [stat['completion_rate'] for stat in stats]

    context = {
        'stats': stats,
        'habit_names': habit_names,
        'completion_rates': completion_rates,
        'total_habits': len(habits),
        'average_completion': round(sum(completion_rates) / len(completion_rates)) if completion_rates else 0,
    }

    return render(request, 'habits/dashboard.html', context)

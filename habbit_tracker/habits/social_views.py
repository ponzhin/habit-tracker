from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Achievement, Habit


@login_required
def achievements_list(request):
    """Список достижений пользователя"""
    achievements = Achievement.objects.filter(user=request.user)

    # Статистика
    total_achievements = achievements.count()
    best_streak = achievements.order_by('-streak_length').first()

    return render(request, 'habits/achievements.html', {
        'achievements': achievements,
        'total_achievements': total_achievements,
        'best_streak': best_streak,
    })


@login_required
def public_achievements(request):
    """Публичные достижения всех пользователей"""
    achievements = Achievement.objects.filter(is_public=True).select_related('user', 'habit')

    # Пагинация
    paginator = Paginator(achievements, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Топ пользователей по количеству достижений
    from django.db.models import Count
    top_users = Achievement.objects.filter(
        is_public=True
    ).values(
        'user__username'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10]

    return render(request, 'habits/public_achievements.html', {
        'page_obj': page_obj,
        'top_users': top_users,
    })


@login_required
def share_achievement(request, achievement_id):
    """Поделиться достижением"""
    achievement = get_object_or_404(Achievement, id=achievement_id, user=request.user)

    if request.method == 'POST':
        is_public = request.POST.get('is_public') == 'on'
        achievement.is_public = is_public
        achievement.save()

        messages.success(request,
            'Достижение опубликовано!' if is_public else 'Достижение скрыто'
        )
        return redirect('achievements_list')

    return render(request, 'habits/share_achievement.html', {
        'achievement': achievement
    })
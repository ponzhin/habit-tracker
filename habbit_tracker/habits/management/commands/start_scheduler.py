from django.core.management.base import BaseCommand
from habits.tasks import start_scheduler


class Command(BaseCommand):
    help = 'Запускает планировщик задач для напоминаний'

    def handle(self, *args, **options):
        self.stdout.write('Запуск планировщика задач...')
        try:
            start_scheduler()
        except KeyboardInterrupt:
            self.stdout.write('Планировщик остановлен')
        except Exception as e:
            self.stdout.write(f'Ошибка: {e}')
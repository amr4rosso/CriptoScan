from django.core.management.base import BaseCommand
from scanner.scanner import scan_and_send

class Command(BaseCommand):
    help = 'Сканирует коины и отправляет сигналы в ntfy'

    def add_arguments(self, parser):
        parser.add_argument('--mode', type=str, default='One per Trend', help='Режим: Frequent, Filtered, One per Trend')

    def handle(self, *args, **options):
        mode = options['mode']
        self.stdout.write('Запуск сканера в режиме: ' + mode)
        scan_and_send(mode=mode)
        self.stdout.write(self.style.SUCCESS('Готово!'))

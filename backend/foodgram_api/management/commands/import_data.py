import csv

from django.core.management.base import BaseCommand

from foodgram_api.models import Ingredient


class Command(BaseCommand):
    """Класс команды."""

    help = 'Импортирует данные из CSV-файлов'

    def add_arguments(self, parser):
        """Функция аргументов."""
        parser.add_argument(
            'csv_files',
            nargs='+',
            type=str,
            help='Пути к файлам CSV')

    def handle(self, *args, **options):
        """Функция команды."""
        for csv_file in options['csv_files']:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row_1, row_2 in reader:
                    ingredient = Ingredient(name=row_1, measurement_unit=row_2)
                    ingredient.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        'Успешный импорт из {}'.format(csv_file)))

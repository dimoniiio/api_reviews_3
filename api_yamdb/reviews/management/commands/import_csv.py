import csv
from datetime import datetime

from django.core.management.base import BaseCommand

from reviews.models import (Category, Comment, Genre, GenreTitle, Review,
                            Title, User)


class Command(BaseCommand):
    """Класс для импорта данных из CSV файлов в базу данных."""

    help = 'Импортирует данные из CSV файлов в базу данных'

    model_mapping = {
        'category.csv': Category,
        'genre.csv': Genre,
        'users.csv': User,
        'titles.csv': Title,
        'genre_title.csv': GenreTitle,
        'comments.csv': Comment,
        'review.csv': Review,
    }

    def handle(self, *args, **kwargs):
        for file_name, model in self.model_mapping.items():
            file_path = f'static/data/{file_name}'

            try:
                with open(file_path, newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        try:
                            instance = self.create_instance(model, row)
                            instance.save()
                            self.stdout.write(
                                self.style.SUCCESS(f'Добавлена запись: {row}')
                            )
                        except Exception as e:
                            self.stderr.write(
                                self.style.ERROR(
                                    f'Ошибка при добавлении записи: '
                                    f'{row}. Ошибка: {e}'
                                )
                            )

                self.stdout.write(
                    self.style.SUCCESS(f'Импорт из {file_name} завершен!')
                )
            except FileNotFoundError:
                self.stderr.write(
                    self.style.ERROR(f'Файл {file_path} не найден.')
                )

    def create_instance(self, model, row):
        """Создает экземпляр модели на основе данных из строки CSV."""
        fields = {}
        for key, value in row.items():
            if value.isdigit():
                fields[key] = int(value)
            elif '.' in value and value.replace('.', '', 1).isdigit():
                fields[key] = float(value)
            elif key.endswith('_at'):
                fields[key] = self.parse_date(value)
            else:
                fields[key] = value

        if model == Title:
            fields['category'] = Category.objects.get(
                id=fields.pop('category_id', None)
            )
        elif model == GenreTitle:
            fields['title'] = Title.objects.get(
                id=fields.pop('title_id', None)
            )
            fields['genre'] = Genre.objects.get(
                id=fields.pop('genre_id', None)
            )
        elif model == Review:
            fields['author'] = User.objects.get(
                id=fields.pop('author_id', None)
            )
        elif model == Comment:
            fields['review'] = Review.objects.get(
                id=fields.pop('review_id', None)
            )
            fields['author'] = User.objects.get(
                id=fields.pop('author_id', None)
            )

        return model(**fields)

    def parse_date(self, date_str):
        """Парсит строку даты в объект datetime."""
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return None

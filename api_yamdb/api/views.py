from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets

from titles.models import CHAR_LIMIT, Title
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Предсталение отзыва на произведение."""
    serializer_class = ReviewSerializer

    @property
    def reviewed_title(self):
        """Метод получения объекта класса произведение по id."""
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        """Метод получения всех отзывов к произведению."""
        return self.reviewed_title.reviews.all()

    def perform_create(self, serializer):
        """Метод переопределения автора и произведения у отзыва."""
        serializer.save(author=self.request.user, title=self.reviewed_title)

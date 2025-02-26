from rest_framework import viewsets
from rest_framework import filters, viewsets
from rest_framework.pagination import (
    PageNumberPagination,
)

from reviews.models import Title, Category, Genre
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
)
from .viewsets import CreateListDeleteViewSet
from .permissions import IsReadOnlyOrAdmin


class CategoryViewSet(CreateListDeleteViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    filterset_fields = ('name')
    permission_classes = (IsReadOnlyOrAdmin, )


class GenreViewSet(CreateListDeleteViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsReadOnlyOrAdmin, )


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    filterset_fields = ('category', 'genre', 'name', 'year')
    permission_classes = (IsReadOnlyOrAdmin, )

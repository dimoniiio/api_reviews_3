from rest_framework import mixins, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination

from .pagination import CustomPageNumberPagination
from .permissions import IsAdminOrReadOnly


class CreateListDeleteViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                              mixins.DestroyModelMixin,
                              viewsets.GenericViewSet):
    """Базовый класс для наследования.
    """
    pagination_class = CustomPageNumberPagination
    filter_backends = (SearchFilter, )
    search_fields = ('name', )
    permission_classes = (IsAdminOrReadOnly, )
    lookup_field = 'slug'

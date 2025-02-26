from rest_framework import mixins, viewsets


class CreateListDeleteViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                              mixins.DestroyModelMixin,
                              viewsets.GenericViewSet):
    """Базовый класс для наследования.
    """

from rest_framework import mixins, viewsets


class CreateListDeleteViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                              mixins.DestroyModelMixin,
                              viewsets.GenericViewSet):
    """Базовый класс для наследования.
    """


# class CreateListDeleteRetrieveViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
#                               mixins.DestroyModelMixin, mixins.RetrieveModelMixin,
#                               viewsets.GenericViewSet):
#     """Базовый класс для наследования.
#     """

#     def retrieve(self, request, *args, **kwargs):
#         if 
#         return super().retrieve(request, *args, **kwargs)

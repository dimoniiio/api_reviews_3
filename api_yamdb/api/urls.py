from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AuthViewSet, CategoryViewSet, GenreViewSet, ReviewViewSet, TitleViewSet
)

app_name = 'api'

v1_router = DefaultRouter()
v1_router.register('auth', AuthViewSet, basename='auth')
v1_router.register('titles', TitleViewSet, basename='titles')
v1_router.register('categories', CategoryViewSet, basename='categories')
v1_router.register('genres', GenreViewSet, basename='genres')
v1_router.register(
    r'posts/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
)

urlpatterns = [
    path('v1/', include(v1_router.urls)),
]

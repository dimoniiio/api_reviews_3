from django.urls import include, path
from rest_framework import routers

from api.views import ReviewSerializer

app_name = 'api'

v1_router = routers.DefaultRouter()
v1_router.register(
    r'posts/(?P<title_id>\d+)/reviews', ReviewSerializer, basename='reviews'
)

urlpatterns = [
    path('v1/', include(v1_router.urls)),
]
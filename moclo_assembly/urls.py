from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('Moclo', views.MocloView)

urlpatterns = [
    path('', include(router.urls))
]
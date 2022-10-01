from django.urls import path

from . import views

app_name = 'createUserPersona'
urlpatterns = [
    path('', views.index, name='index'),
    path('process', views.letsGo, name='letsGo')
]
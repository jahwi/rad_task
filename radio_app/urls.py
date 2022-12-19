from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name='index'),
    path("list_stations/", views.list_stations, name="list_stations"),
    path("get_station/<id>", views.get_station, name="get_station"),
    path("get_user/<usern>", views.get_user, name="get_user"),
    path("add_station/", views.add_station, name="add_station")
]
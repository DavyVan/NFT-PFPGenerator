from django.urls import path

from . import views

urlpatterns = [
    path("new", views.new),
    path("check", views.check),
    path("ping", views.ping),
    path("from_excel", views.from_excel)
]

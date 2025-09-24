from django.urls import path
from . import views

app_name = 'card_maker'

urlpatterns = [
    path("", views.index, name="index"),
    path("generate/", views.generate_card, name="generate_card"),
    path("download/<str:filename>/", views.download_card, name="download_card"),
]
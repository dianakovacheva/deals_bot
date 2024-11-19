from django.urls import path

from . import views

urlpatterns = [
    path("deals/", views.index, name="index"),
    path("create-deal/", views.create_deal_endpoint, name="create_deal"),
]

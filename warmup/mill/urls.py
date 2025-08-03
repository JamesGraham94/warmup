from django.urls import path
from . import views
from .views import UpdateFormView



urlpatterns = [

    path('', views.home, name='home'),
    path('form/<int:pk>', UpdateFormView.as_view(), name='form'),
    path('fanuc/<int:pk>', views.fanuc, name='fanuc'),




    ]
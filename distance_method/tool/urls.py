from django.urls import path
from . import views

urlpatterns = [
    path('', views.web),
    path('run_distance/', views.ScreenerDistance),
    
]
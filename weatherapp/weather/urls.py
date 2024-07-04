from django.urls import path
from . import views

urlpatterns = [
    path('api/hello/', views.VisitorsView.as_view(), name='visitor'),
]

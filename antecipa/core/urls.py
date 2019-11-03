from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from .views import DashboardView

app_name = 'core'

urlpatterns = [
    path('', DashboardView.as_view(), name='home'),
    path('login/', LoginView.as_view(template_name='adminlte/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]

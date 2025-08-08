from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = 'authentication'

urlpatterns = [
    path('', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='authentication:login'), name='logout'),
    path('login/redirect/', views.login_redirect_view, name='login_redirect'),
]
from django.urls import path, include
from tickets.admin import custom_admin_site

urlpatterns = [
    path('admin/', custom_admin_site.urls),
    path('', include('authentication.urls')),
    path('chamados/', include('tickets.urls')),
]
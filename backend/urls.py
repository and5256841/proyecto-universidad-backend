from django.contrib import admin
from django.urls import path
from proyectos.views import dashboard_view

urlpatterns = [
    path('admin/dashboard/', dashboard_view, name='admin_dashboard'),
    path('admin/', admin.site.urls),
]
"""
URL configuration for giggles_project project.

"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing_view, name='landing'),
    path('accounts/', include('accounts.urls')),
    path('lessons/', include('lessons.urls')),
    path('learning/', include('learning.urls')),

]



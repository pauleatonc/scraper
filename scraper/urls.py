from django.contrib import admin
from django.urls import path, include
from applications.scraper import views

urlpatterns = [
    path('', views.home, name='home'), 
    path('admin/', admin.site.urls),
    path('scraper/', include('applications.scraper.urls')),
]
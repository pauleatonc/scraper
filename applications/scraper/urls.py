from django.urls import path
from . import views

urlpatterns = [
    path('scrape-general/', views.start_general_scraping, name='start_general_scraping'),
    path('scrape-details/', views.start_detail_scraping, name='start_detail_scraping'),
]
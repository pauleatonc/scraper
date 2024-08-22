from django.shortcuts import render, redirect
from django.http import HttpResponse
from .services.vehicles_scraping import scrape_general_data, scrape_detail_data

def start_general_scraping(request):
    scrape_general_data()
    return HttpResponse("Scraping general completado.")

def start_detail_scraping(request):
    scrape_detail_data()
    return HttpResponse("Scraping de detalles completado.")

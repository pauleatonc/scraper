from django.shortcuts import render, redirect, HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from .services.vehicles_scraping import scrape_general_data, scrape_detail_data, get_proxies
from django.core.management import call_command

def start_general_scraping(request):
    proxy_method = request.POST.get('proxy_method', 'none')  # Obtener el método del proxy de la solicitud
    proxies = get_proxies(proxy_method)  # Obtener la lista de proxies según el método
    scrape_general_data(proxies)  # Pasar la lista de proxies al método de scraping
    return HttpResponse("Scraping general completado.")

def start_detail_scraping(request):
    proxy_method = request.POST.get('proxy_method', 'none')  # Obtener el método del proxy de la solicitud
    proxies = get_proxies(proxy_method)  # Obtener la lista de proxies según el método
    scrape_detail_data(proxies)  # Pasar la lista de proxies al método de scraping
    return HttpResponse("Scraping de detalles completado.")

def start_generate_json(request):
    call_command('generate_json')
    return HttpResponse("JSON generado con éxito.")

from django.shortcuts import render
from .services.vehicles_scraping import scrape_general_data, scrape_detail_data, get_proxies
from django.core.management import call_command
from django.contrib import messages

def home(request):
    if request.method == 'POST':
        proxy_method = request.POST.get('proxy_method', 'none')
        proxies = get_proxies(proxy_method)  # Obtener la lista de proxies según el método

        if 'scrape_general' in request.POST:
            scrape_general_data(proxies)  # Pasar la lista de proxies al método de scraping
            messages.success(request, "Scraping general completado.")
        elif 'scrape_detail' in request.POST:
            scrape_detail_data(proxies)  # Pasar la lista de proxies al método de scraping
            messages.success(request, "Scraping de detalles completado.")
        elif 'generate_json' in request.POST:
            call_command('generate_json')
            messages.success(request, "JSON generado.")

    return render(request, 'general/home.html')
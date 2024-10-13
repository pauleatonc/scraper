from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .services.vehicles_scraping import scrape_general_data, scrape_detail_data
from django.core.management import call_command

def start_general_scraping(request):
    scrape_general_data()
    return HttpResponse("Scraping general completado.")

def start_detail_scraping(request):
    scrape_detail_data()
    return HttpResponse("Scraping de detalles completado.")

def start_generate_json(request):
    call_command('generate_json')
    return HttpResponse("JSON generado con éxito.")

def home(request):
    if request.method == 'POST':
        if 'scrape_general' in request.POST:
            scrape_general_data()  # Llama al método que ejecuta el scraping general
            messages.success(request, 'Scraping general completado exitosamente.')
            return HttpResponseRedirect(reverse('home'))  # Redirigir nuevamente a la página de inicio
        elif 'scrape_detail' in request.POST:
            scrape_detail_data()  # Llama al método que ejecuta el scraping de detalles
            messages.success(request, 'Scraping de detalles completado exitosamente.')
            return HttpResponseRedirect(reverse('home'))  # Redirigir nuevamente a la página de inicio
        elif 'generate_json' in request.POST:
            return start_generate_json(request)

    return render(request, 'general/home.html')

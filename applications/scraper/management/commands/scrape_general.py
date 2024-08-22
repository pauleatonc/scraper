from django.core.management.base import BaseCommand
from scraper.services.vehicles_scraping import scrape_general_data

class Command(BaseCommand):
    help = 'Realiza scraping general de vehículos'

    def handle(self, *args, **kwargs):
        scrape_general_data()
        self.stdout.write(self.style.SUCCESS('Scraping general completado.'))

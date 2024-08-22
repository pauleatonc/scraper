from django.core.management.base import BaseCommand
from applications.scraper.services.vehicles_scraping import scrape_detail_data

class Command(BaseCommand):
    help = 'Realiza scraping de detalles adicionales de vehículos'

    def handle(self, *args, **kwargs):
        scrape_detail_data()
        self.stdout.write(self.style.SUCCESS('Scraping de detalles completado.'))

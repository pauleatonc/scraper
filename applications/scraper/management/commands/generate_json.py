import json
from django.core.management.base import BaseCommand
from applications.vehicles.models import Vehicle
from applications.vehicles.models import VehicleJSONRecord
from datetime import datetime

class Command(BaseCommand):
    help = 'Genera un archivo JSON con la información de todos los vehículos en la BD'

    def handle(self, *args, **kwargs):
        vehicles = Vehicle.objects.all()
        vehicle_data = []

        # Número relativo de cada vehículo
        for idx, vehicle in enumerate(vehicles, start=1):
            vehicle_data.append({
                'relative_number': idx,
                'listing_id': vehicle.listing_id,
                'title': vehicle.title,
                'price': vehicle.price,
                'odometer': vehicle.odometer,
                'fuel_economy': vehicle.fuel_economy,
                'listing_url': vehicle.listing_url,
                'detail_url': vehicle.detail_url,
                'image_urls': vehicle.image_urls,
                'scraped_at': vehicle.scraped_at.strftime('%Y-%m-%d %H:%M:%S'),
                'full_description': vehicle.full_description,
                'color': vehicle.color.color if hasattr(vehicle, 'color') else None,
                'year': vehicle.year.year if hasattr(vehicle, 'year') else None,
                'engine_capacity': vehicle.engine_capacity.capacity if hasattr(vehicle, 'engine_capacity') else None,
                'comuna': vehicle.comuna.comuna if hasattr(vehicle, 'comuna') else None,
            })

        # Guardar el JSON en un archivo
        json_filename = f'/app/vehicles_data/vehicles_data_{datetime.now().strftime("%Y%m%d%H%M%S")}.json'
        with open(json_filename, 'w') as json_file:
            json.dump(vehicle_data, json_file, indent=4)

        # Guardar un registro en la base de datos
        VehicleJSONRecord.objects.create(filename=json_filename)

        self.stdout.write(self.style.SUCCESS(f'JSON de vehículos generado con éxito: {json_filename}'))


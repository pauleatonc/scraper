import requests
from bs4 import BeautifulSoup
from applications.vehicles.models import Vehicle, SellerType, BodyStyle, Brand, VehicleModel, Location, Year, Color, EngineCapacity, Comuna

def scrape_general_data():
    base_url = "https://www.chileautos.cl/vehiculos/autos-veh%C3%ADculo/"
    
    for page_num in range(10):  # Revisar las primeras 10 páginas
        offset = page_num * 12  # El offset incrementa de 12 en 12 para cambiar de página
        url = f"{base_url}?offset={offset}"
        
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Encuentra todos los listados de vehículos en la página
        vehicle_listings = soup.find_all('div', class_='listing-item')

        for listing in vehicle_listings:
            listing_id = listing['data-webm-networkid']
            title = listing.find('a', class_='js-encode-search').get_text().strip()  # Extraer el título
            make = listing['data-webm-make']
            model = listing['data-webm-model']
            price = listing['data-webm-price']
            seller_type = listing['data-webm-vehcategory']
            body_style = listing['data-webm-bodystyle']
            location = listing['data-webm-state']
            detail_url = f"https://www.chileautos.cl{listing.find('a', class_='js-encode-search')['href']}"
            images = [img['src'] for img in listing.find_all('img')]  # Recolectar las imágenes
            
            # Verifica si ya existe el vehículo para evitar duplicados
            if not Vehicle.objects.filter(listing_id=listing_id).exists():
                # Crear el vehículo
                vehicle = Vehicle.objects.create(
                    listing_id=listing_id,
                    title=title,  # Guardar el título
                    price=int(price),
                    listing_url=url,
                    detail_url=detail_url,
                    image_urls=images,
                    full_description=f"{make} {model}"
                )

                # Asocia los datos a los otros modelos relacionados
                SellerType.objects.create(vehicle=vehicle, type=seller_type)
                BodyStyle.objects.create(vehicle=vehicle, style=body_style)
                Brand.objects.create(vehicle=vehicle, name=make)
                VehicleModel.objects.create(vehicle=vehicle, name=model)
                Location.objects.create(vehicle=vehicle, location=location)

                print(f"Vehículo {vehicle.listing_id} - {vehicle.title} guardado.")


def scrape_detail_data():
    vehicles = Vehicle.objects.all()
    
    for vehicle in vehicles:
        # Evitar duplicados, por ejemplo, verificando si ya se extrajo algún detalle
        if vehicle.full_description and not vehicle.color_set.exists():  # Suponemos que no tiene detalles si no tiene color
            response = requests.get(vehicle.detail_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            full_description = soup.find('div', class_='features-item-value-vehculo').get_text().strip()
            color = soup.find('div', class_='features-item-value-color').get_text().strip()
            engine_capacity = soup.find('div', class_='features-item-value-litros-motor').get_text().strip()
            comuna = soup.find('div', class_='features-item-value-comuna').get_text().strip()
            year = int(full_description.split()[0])  # Extraemos el año del título completo

            # Actualizar el campo full_description y los detalles adicionales
            vehicle.full_description = full_description
            vehicle.save()

            # Crear los registros de los modelos relacionados
            Year.objects.create(vehicle=vehicle, year=year)
            Color.objects.create(vehicle=vehicle, color=color)
            EngineCapacity.objects.create(vehicle=vehicle, capacity=engine_capacity)
            Comuna.objects.create(vehicle=vehicle, comuna=comuna)

            print(f"Detalles del vehículo {vehicle.listing_id} actualizados.")

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time
import requests
from applications.vehicles.models import Vehicle, SellerType, BodyStyle, Brand, VehicleModel, Location, Year, Color, EngineCapacity, Comuna

# Configura Selenium para usar el navegador Firefox
def init_driver():
    firefox_options = Options()
    firefox_options.add_argument("--headless")  # Ejecutar en modo headless
    firefox_options.add_argument("--no-sandbox")  # Evitar sandbox
    firefox_options.add_argument("--disable-gpu")
    firefox_options.add_argument("--disable-dev-shm-usage")  # Evitar problemas con memoria compartida

    driver = webdriver.Firefox(service=Service("/usr/local/bin/geckodriver"), options=firefox_options)
    return driver


def scrape_general_data():
    driver = init_driver()
    base_url = "https://www.chileautos.cl/vehiculos/autos-veh%C3%ADculo/"
    print("Iniciando scraping en la web:", base_url)

    for page_num in range(10):  # Revisar las primeras 10 páginas
        offset = page_num * 12  # El offset incrementa de 12 en 12 para cambiar de página
        url = f"{base_url}?offset={offset}"
        print(f"Scrapeando página {page_num + 1} con offset {offset}: {url}")
        
        # Cargar la página en Selenium
        driver.get(url)
        time.sleep(5)  # Espera a que el contenido dinámico (JavaScript) se cargue

        # Usar BeautifulSoup para procesar el HTML
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        print(f"Contenido HTML parseado con BeautifulSoup para la página {page_num + 1}")

        # Encuentra todos los listados de vehículos en la página
        vehicle_listings = soup.find_all('div', class_='listing-item')
        print(f"{len(vehicle_listings)} vehículos encontrados en la página {page_num + 1}")

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
            
            images = []
            for img in listing.find_all('img'):
                img_url = img.get('src') or img.get('data-src')
                if img_url:
                    images.append(img_url)

            print(f"Procesando vehículo {listing_id}: {title}, {make} {model}, {price} CLP")

            # Verifica si ya existe el vehículo para evitar duplicados
            if not Vehicle.objects.filter(listing_id=listing_id).exists():
                print(f"Vehículo {listing_id} no existe en la base de datos, creando...")

                # Crear el vehículo
                vehicle = Vehicle.objects.create(
                    listing_id=listing_id,
                    title=title,
                    price=int(price),
                    listing_url=url,
                    detail_url=detail_url,
                    image_urls=images,
                    full_description=f"{make} {model}"
                )

                print(f"Vehículo {vehicle.listing_id} creado con éxito en la base de datos.")

                # Asocia los datos a los otros modelos relacionados
                SellerType.objects.create(vehicle=vehicle, type=seller_type)
                BodyStyle.objects.create(vehicle=vehicle, style=body_style)
                Brand.objects.create(vehicle=vehicle, name=make)
                VehicleModel.objects.create(vehicle=vehicle, name=model)
                Location.objects.create(vehicle=vehicle, location=location)

                print(f"Vehículo {vehicle.listing_id} - {vehicle.title} guardado correctamente.")
            else:
                print(f"Vehículo {listing_id} ya existe en la base de datos, saltando...")

    driver.quit()
    print("Scraping finalizado.")

def scrape_detail_data():
    vehicles = Vehicle.objects.all()  # Obtener todos los vehículos

    driver = init_driver()  # Inicializa Selenium WebDriver

    for vehicle in vehicles:
        # Verificar si ya se extrajo algún detalle usando el related_name definido
        if vehicle.full_description and not hasattr(vehicle, 'color'):  # Verificar si el vehículo ya tiene detalles
            try:
                driver.get(vehicle.detail_url)
                time.sleep(2)  # Asegurarse de dar tiempo para que la página se cargue completamente

                soup = BeautifulSoup(driver.page_source, 'html.parser')

                full_description = soup.find('div', class_='features-item-value-vehculo')
                color = soup.find('div', class_='features-item-value-color')
                engine_capacity = soup.find('div', class_='features-item-value-litros-motor')
                comuna = soup.find('div', class_='features-item-value-comuna')

                if full_description:
                    full_description = full_description.get_text().strip()
                else:
                    full_description = vehicle.full_description

                if color:
                    color = color.get_text().strip()
                else:
                    color = None

                if engine_capacity:
                    engine_capacity = engine_capacity.get_text().strip()
                else:
                    engine_capacity = None

                if comuna:
                    comuna = comuna.get_text().strip()
                else:
                    comuna = None

                if full_description:
                    try:
                        year = int(full_description.split()[0])  # Extraer el año desde la primera parte del texto
                    except (ValueError, IndexError):
                        year = None
                else:
                    year = None

                vehicle.full_description = full_description
                vehicle.save()

                if year:
                    Year.objects.get_or_create(vehicle=vehicle, year=year)

                if color:
                    Color.objects.get_or_create(vehicle=vehicle, color=color)

                if engine_capacity:
                    try:
                        engine_capacity_value = float(engine_capacity)  # Convertir a decimal o float
                        EngineCapacity.objects.get_or_create(vehicle=vehicle, capacity=engine_capacity_value)
                    except ValueError:
                        print(f"Error al convertir engine_capacity para {vehicle.listing_id}: {engine_capacity}")

                if comuna:
                    Comuna.objects.get_or_create(vehicle=vehicle, comuna=comuna)

                print(f"Detalles del vehículo {vehicle.listing_id} actualizados.")
            
            except Exception as e:
                print(f"Error al procesar los detalles del vehículo {vehicle.listing_id}: {e}")

    driver.quit()  # Cerrar el driver después de terminar
from fake_useragent import UserAgent
from django.conf import settings 
import os
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import requests
from applications.vehicles.models import Vehicle, SellerType, BodyStyle, Brand, VehicleModel, Location, Year, Color, EngineCapacity, Comuna


# Función para obtener la lista de proxies desde ProxyScrape
def get_proxies(proxy_method='none'):

    if proxy_method == 'api':
        url = "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&proxy_format=protocolipport&format=text&anonymity=elite"
        try:
            response = requests.get(url)
            response.raise_for_status()
            proxies = response.text.splitlines()
            valid_proxies = [proxy for proxy in proxies if ':' in proxy]
            print(f"Proxies obtenidos de la API: {valid_proxies}")
            return valid_proxies if valid_proxies else None
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener proxies de la API: {e}")
            return None

    elif proxy_method == 'file':
        file_path = os.path.join('/app/proxies.txt')
        if not os.path.exists(file_path):
            print(f"El archivo {file_path} no existe.")
            return None

        with open(file_path, 'r') as file:
            proxies = file.read().splitlines()
            valid_proxies = [proxy for proxy in proxies if ':' in proxy]
            print(f"Proxies obtenidos del archivo: {valid_proxies}")
            return valid_proxies if valid_proxies else None

    else:
        print("No se usará proxy.")
        return None    


def init_selenium_driver(proxy=None):
    chrome_options = Options()
    # Quitar el modo headless para ver la interacción
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36')

    if proxy:
        chrome_options.add_argument(f'--proxy-server={proxy}')
        print(f"Usando proxy en Selenium: {proxy}")

    driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=chrome_options)
    return driver

def scrape_general_data(proxies=None):
    base_url = "https://www.chileautos.cl/vehiculos/autos-veh%C3%ADculo/"

    for page_num in range(1):  # Revisar las primeras X páginas
        offset = page_num * 12
        url = f"{base_url}?offset={offset}"
        print(f"Scrapeando página {page_num + 1} con offset {offset}: {url}")

        success = False  # Bandera para saber si se pudo cargar la página

        # Intentar cargar con Selenium y proxies si están disponibles
        if proxies:
            for proxy in proxies:
                try:
                    driver = init_selenium_driver(proxy=proxy)
                    driver.get(url)
                    time.sleep(5)  # Esperar a que se cargue la página
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    print(soup.prettify())
                    success = True
                    print(f"Página cargada con éxito con el proxy {proxy}")
                    driver.quit()  # Cerrar el driver si se carga con éxito
                    break  # Salir del bucle si se carga con éxito
                except Exception as e:
                    print(f"Error al cargar la página {url} con Selenium y el proxy {proxy}: {e}")
                    if driver:
                        driver.quit()  # Cerrar el driver si hubo un error
                    continue  # Intentar con el siguiente proxy

        # Si no tuvo éxito con los proxies o no hay proxies, intentar sin proxy
        if not success:
            print("Intentando cargar la página sin proxy...")
            try:
                driver = init_selenium_driver()
                driver.get(url)
                time.sleep(5)  # Esperar a que se cargue la página
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                success = True
                print("Página cargada con éxito sin proxy")
            except Exception as e:
                print(f"Error al cargar la página {url} con Selenium sin proxy: {e}")
            finally:
                if driver:
                    driver.quit()

        if success:
            # Encuentra todos los listados de vehículos en la página
            vehicle_listings = soup.find_all('div', class_='listing-item')
            print(f"{len(vehicle_listings)} vehículos encontrados en la página {page_num + 1}")

            for listing in vehicle_listings:
                listing_id = listing['data-webm-networkid']
                make = listing['data-webm-make']
                model = listing['data-webm-model']
                price = listing['data-webm-price']
                seller_type = listing['data-webm-vehcategory']
                body_style = listing['data-webm-bodystyle']
                location = listing['data-webm-state']
                detail_url = f"https://www.chileautos.cl{listing.find('a', class_='js-encode-search')['href']}"
                title = listing.find('a', class_='js-encode-search').get_text().strip()  # Extraer el título
                images = [img['src'] for img in listing.find_all('img') if 'src' in img.attrs]  # Recolectar las imágenes

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

    print("Scraping general finalizado.")

    
def scrape_detail_data(proxies=None):
    vehicles = Vehicle.objects.all()  # Obtener todos los vehículos

    for vehicle in vehicles:
        # Verificar si ya se extrajo algún detalle usando el related_name definido
        if vehicle.full_description and not hasattr(vehicle, 'color'):  # Verificar si el vehículo ya tiene detalles
            success = False
            while not success:
                # Inicializa el WebDriver con o sin proxy según la lista de proxies
                proxy = random.choice(proxies) if proxies else None
                driver = init_driver(proxy)  # Si proxy es None, no se usará un proxy
                driver.set_page_load_timeout(10)

                try:
                    driver.get(vehicle.detail_url)
                    time.sleep(2)  # Espera a que la página se cargue completamente

                    # Procesar el HTML
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    full_description = soup.find('div', class_='features-item-value-vehculo')
                    color = soup.find('div', class_='features-item-value-color')
                    engine_capacity = soup.find('div', class_='features-item-value-litros-motor')
                    comuna = soup.find('div', class_='features-item-value-comuna')

                    # Actualizar detalles del vehículo si existen nuevos datos
                    if full_description:
                        vehicle.full_description = full_description.get_text().strip()

                    vehicle.save()  # Actualizar el vehículo con los nuevos datos

                    # Actualizar o crear las relaciones
                    if color:
                        Color.objects.update_or_create(vehicle=vehicle, defaults={'color': color.get_text().strip()})
                    if engine_capacity:
                        try:
                            engine_capacity_value = float(engine_capacity.get_text().strip())
                            EngineCapacity.objects.update_or_create(vehicle=vehicle, defaults={'capacity': engine_capacity_value})
                        except ValueError:
                            print(f"Error al convertir engine_capacity para {vehicle.listing_id}")
                    if comuna:
                        Comuna.objects.update_or_create(vehicle=vehicle, defaults={'comuna': comuna.get_text().strip()})

                    print(f"Detalles del vehículo {vehicle.listing_id} actualizados.")
                    success = True  # Si se completa con éxito, salir del bucle
                except Exception as e:
                    print(f"Error al procesar los detalles del vehículo {vehicle.listing_id}: {e}")
                    if proxies:
                        proxies.remove(proxy)  # Remover el proxy fallido de la lista si se usó un proxy
                    continue
                finally:
                    driver.quit()  # Cerrar el WebDriver después de cada vehículo

    print("Scraping de detalles finalizado.")

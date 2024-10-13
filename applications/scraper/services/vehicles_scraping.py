from fake_useragent import UserAgent
import random
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time
import requests
from applications.vehicles.models import Vehicle, SellerType, BodyStyle, Brand, VehicleModel, Location, Year, Color, EngineCapacity, Comuna


# Función para obtener la lista de proxies desde ProxyScrape
def get_proxies():
    url = "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&proxy_format=protocolipport&format=text&anonymity=elite"
    response = requests.get(url)
    proxies = response.text.splitlines()
    # Simplemente verifica si hay un ':' en la cadena
    valid_proxies = [proxy for proxy in proxies if ':' in proxy]
    print(f"Proxies obtenidos: {valid_proxies}")  # Imprime la lista de proxies obtenidos
    return valid_proxies


def init_driver(proxy=None):
    # Crear una instancia de UserAgent para obtener agentes aleatorios
    ua = UserAgent()

    # Configuración de las opciones de Firefox
    firefox_options = Options()
    firefox_options.add_argument("--headless")  # Ejecutar en modo headless
    firefox_options.add_argument("--no-sandbox")  # Evitar sandbox
    firefox_options.add_argument("--disable-gpu")
    firefox_options.add_argument("--disable-dev-shm-usage")  # Evitar problemas con memoria compartida

    # Añadir User-Agent rotativo
    user_agent = ua.random
    firefox_options.set_preference("general.useragent.override", user_agent)
    
    if proxy:
        # Determinar el tipo de proxy
        if proxy.startswith("http://") or proxy.startswith("https://"):
            proxy_type = 1  # HTTP Proxy
            proxy = proxy.replace("http://", "").replace("https://", "")
        elif proxy.startswith("socks4://"):
            proxy_type = 2  # SOCKS4 Proxy
            proxy = proxy.replace("socks4://", "")
        else:
            raise ValueError(f"Tipo de proxy no soportado: {proxy}")

        try:
            proxy_host, proxy_port = proxy.split(':')
            proxy_port = int(proxy_port)
        except ValueError:
            raise ValueError(f"Formato de proxy no válido: {proxy}")

        print(f"Usando el proxy: {proxy_host}:{proxy_port} ({'HTTP' if proxy_type == 1 else 'SOCKS4'})")
        print(f"User-Agent utilizado: {user_agent}")  # Imprimir el User-Agent para depuración

        # Configurar el proxy en las preferencias de Firefox
        firefox_options.set_preference("network.proxy.type", proxy_type)
        firefox_options.set_preference("network.proxy.http", proxy_host)
        firefox_options.set_preference("network.proxy.http_port", proxy_port)
        firefox_options.set_preference("network.proxy.ssl", proxy_host)
        firefox_options.set_preference("network.proxy.ssl_port", proxy_port)

        if proxy_type == 2:  # Configurar SOCKS Proxy
            firefox_options.set_preference("network.proxy.socks", proxy_host)
            firefox_options.set_preference("network.proxy.socks_port", proxy_port)

    # Inicializar el WebDriver de Firefox con las opciones
    driver = webdriver.Firefox(service=Service("/usr/local/bin/geckodriver"), options=firefox_options)
    
    return driver

def scrape_general_data():
    proxies = get_proxies()  # Obtener lista de proxies desde ProxyScrape

    for page_num in range(15):  # Revisar las primeras 10 páginas
        if not proxies:
            print("No hay proxies válidos disponibles.")
            break

        success = False
        while not success and proxies:  # Reintentar con diferentes proxies hasta tener éxito o agotar la lista
            proxy = random.choice(proxies)  # Seleccionar un proxy aleatorio
            driver = init_driver(proxy)  # Inicializar el WebDriver con el proxy seleccionado
            driver.set_page_load_timeout(10)
            base_url = "https://www.chileautos.cl/vehiculos/autos-veh%C3%ADculo/"
            offset = page_num * 12  # El offset incrementa de 12 en 12 para cambiar de página
            url = f"{base_url}?offset={offset}"
            print(f"Scrapeando página {page_num + 1} con offset {offset}: {url}")

            try:
                # Cargar la página en Selenium
                driver.get(url)
                time.sleep(5)  # Espera a que el contenido dinámico (JavaScript) se cargue
                
                # Verificar si la página se cargó correctamente
                response = requests.get(url, proxies={"http": proxy, "https": proxy})
                if response.status_code in [403, 429]:
                    print(f"Proxy {proxy} bloqueado con código de respuesta {response.status_code}")
                    driver.quit()
                    proxies.remove(proxy)  # Remover proxy fallido de la lista
                    continue
                
                success = True  # Si la página carga con éxito, salir del bucle
            except Exception as e:
                print(f"Error al cargar la página {url} con el proxy {proxy}: {str(e)}")
                driver.quit()
                proxies.remove(proxy)  # Remover proxy fallido de la lista
                continue
        
        if success:
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

                # Verifica si ya existe el vehículo para actualizar o crear
                vehicle, created = Vehicle.objects.update_or_create(
                    listing_id=listing_id,
                    defaults={
                        'title': title,
                        'price': int(price),
                        'listing_url': url,
                        'detail_url': detail_url,
                        'image_urls': images,
                        'full_description': f"{make} {model}"
                    }
                )

                if created:
                    print(f"Vehículo {vehicle.listing_id} creado con éxito.")
                else:
                    print(f"Vehículo {vehicle.listing_id} actualizado con éxito.")

                # Asocia o actualiza los datos a los otros modelos relacionados
                SellerType.objects.update_or_create(vehicle=vehicle, defaults={'type': seller_type})
                BodyStyle.objects.update_or_create(vehicle=vehicle, defaults={'style': body_style})
                Brand.objects.update_or_create(vehicle=vehicle, defaults={'name': make})
                VehicleModel.objects.update_or_create(vehicle=vehicle, defaults={'name': model})
                Location.objects.update_or_create(vehicle=vehicle, defaults={'location': location})

            driver.quit()
        else:
            print(f"No se pudo cargar la página {page_num + 1} después de intentar con todos los proxies disponibles.")
            break

    print("Scraping general finalizado.")

    
def scrape_detail_data():
    vehicles = Vehicle.objects.all()  # Obtener todos los vehículos
    proxies = get_proxies()  # Obtener la lista de proxies

    if not proxies:
        print("No hay proxies válidos disponibles.")
        return

    for vehicle in vehicles:
        if vehicle.full_description and not hasattr(vehicle, 'color'):  # Verificar si el vehículo ya tiene detalles
            success = False
            while not success and proxies:  # Reintentar con diferentes proxies hasta tener éxito o agotar la lista
                proxy = random.choice(proxies)  # Seleccionar un proxy aleatorio
                driver = init_driver(proxy)  # Inicializar el WebDriver con el proxy seleccionado
                driver.set_page_load_timeout(10)

                try:
                    driver.get(vehicle.detail_url)
                    time.sleep(2)  # Asegurarse de dar tiempo para que la página se cargue completamente

                    soup = BeautifulSoup(driver.page_source, 'html.parser')

                    # Extraer detalles del vehículo
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
                    print(f"Error al procesar los detalles del vehículo {vehicle.listing_id} con el proxy {proxy}: {e}")
                    driver.quit()
                    proxies.remove(proxy)  # Remover el proxy fallido de la lista
                    continue

            driver.quit()  # Cerrar el driver después de terminar con cada vehículo

    print("Scraping de detalles finalizado.")

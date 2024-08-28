from django.db import models

class Vehicle(models.Model):
    # ID del anuncio y datos principales
    listing_id = models.CharField(max_length=20, unique=True)  # CP-AD-8379942    
    title = models.CharField(max_length=255, blank=True, null=True)  # Título completo extraído del div
    price = models.BigIntegerField()  # 7,780,000 (Precio en CLP)    
    # Datos adicionales del vehículo
    odometer = models.CharField(max_length=50, blank=True, null=True)  # 136,769 km
    fuel_economy = models.CharField(max_length=50, blank=True, null=True)  # 12.3 Kms/Lt.    
    # URL del anuncio y enlace de detalles
    listing_url = models.URLField(max_length=255)  # URL completa del anuncio
    detail_url = models.URLField(max_length=255)  # URL del enlace "Ver detalle"    
    # Imágenes
    image_urls = models.JSONField(default=list)  # Lista de URLs de las imágenes    
    # Timestamps
    scraped_at = models.DateTimeField(auto_now_add=True)  # Cuándo se hizo el scraping
    full_description = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.listing_id} - {self.price} CLP"
    
    
class SellerType(models.Model):
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE, related_name="seller_type")
    type = models.CharField(max_length=50)  # Agencia, Automotora Usado

    def __str__(self):
        return self.type


class BodyStyle(models.Model):
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE, related_name="body_style")
    style = models.CharField(max_length=50)  # SUV, Sedán, etc.

    def __str__(self):
        return self.style
    

class Brand(models.Model):
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE, related_name="brand")
    name = models.CharField(max_length=50)  # Hyundai

    def __str__(self):
        return self.name


class VehicleModel(models.Model):
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE, related_name="model")
    name = models.CharField(max_length=100)  # Tucson

    def __str__(self):
        return self.name
    

class Year(models.Model):
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE, related_name="year")
    year = models.IntegerField()  # Año del vehículo

    def __str__(self):
        return str(self.year)

class Location(models.Model):
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE, related_name="location")
    location = models.CharField(max_length=100)  # Metropolitana de Santiago

    def __str__(self):
        return self.location


class Comuna(models.Model):
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE, related_name="comuna")
    comuna = models.CharField(max_length=100)  # San Miguel

    def __str__(self):
        return self.comuna


class Transmission(models.Model):
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE, related_name="transmission")
    transmission_type = models.CharField(max_length=50, blank=True, null=True)  # Automática

    def __str__(self):
        return self.transmission_type


class FuelType(models.Model):
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE, related_name="fuel_type")
    fuel = models.CharField(max_length=50, blank=True, null=True)  # Bencina

    def __str__(self):
        return self.fuel


class Color(models.Model):
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE, related_name="color")
    color = models.CharField(max_length=50)  # Rojo

    def __str__(self):
        return self.color


class EngineCapacity(models.Model):
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE, related_name="engine_capacity")
    capacity = models.DecimalField(max_digits=4, decimal_places=1)  # 2.0 (litros)

    def __str__(self):
        return str(self.capacity)

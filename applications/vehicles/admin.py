from django.contrib import admin
from .models import Vehicle, SellerType, BodyStyle, Brand, VehicleModel

# Registrar el modelo Vehicle en el admin
@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('listing_id', 'title', 'price', 'scraped_at')  # Columnas que se mostrarán en la lista
    search_fields = ('listing_id', 'title')  # Barra de búsqueda por listing_id o título
    list_filter = ('price', 'scraped_at')  # Filtros en el admin

admin.site.register(SellerType)
admin.site.register(BodyStyle)
admin.site.register(Brand)
admin.site.register(VehicleModel)


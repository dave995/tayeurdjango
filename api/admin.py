from django.contrib import admin
from django.utils.html import format_html
from .models import Workshop, WorkshopImage, Review, ClothingModel, ModelImage, Measurements, Order

class WorkshopImageInline(admin.TabularInline):
    model = WorkshopImage
    extra = 1

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ('date',)

@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'rating', 'price_range_display', 'delivery_time', 'logo_preview', 'user')
    list_filter = ('rating', 'specialties')
    search_fields = ('name', 'address', 'description')
    readonly_fields = ('logo_preview',)
    inlines = [WorkshopImageInline, ReviewInline]
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'description', 'logo', 'logo_preview', 'address', 'user')
        }),
        ('Détails professionnels', {
            'fields': ('rating', 'specialties', 'estimated_delivery_time')
        }),
        ('Tarification', {
            'fields': ('price_range_min', 'price_range_max')
        }),
    )

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;" />', obj.logo.url)
        return "Pas de logo"
    logo_preview.short_description = 'Aperçu du logo'

    def price_range_display(self, obj):
        return f"{obj.price_range_min}€ - {obj.price_range_max}€"
    price_range_display.short_description = 'Fourchette de prix'

    def delivery_time(self, obj):
        return f"{obj.estimated_delivery_time} jours"
    delivery_time.short_description = 'Délai de livraison estimé'

    def save_model(self, request, obj, form, change):
        if not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)

class ModelImageInline(admin.TabularInline):
    model = ModelImage
    extra = 1

@admin.register(ClothingModel)
class ClothingModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'estimated_time', 'featured')
    list_filter = ('category', 'featured')
    search_fields = ('name', 'description')
    inlines = [ModelImageInline]

@admin.register(Measurements)
class MeasurementsAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'standard_size', 'created_at')
    list_filter = ('standard_size', 'created_at')
    search_fields = ('user__username', 'name')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'model', 'workshop', 'status', 'payment_status', 'total_price', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('user__username', 'workshop__name', 'model__name')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Informations client', {
            'fields': ('user', 'measurements')
        }),
        ('Détails de la commande', {
            'fields': ('model', 'workshop', 'total_price', 'notes')
        }),
        ('Statut', {
            'fields': ('status', 'payment_status', 'estimated_delivery')
        }),
        ('Dates', {
            'fields': ('created_at',)
        }),
    ) 
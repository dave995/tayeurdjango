from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import Workshop, WorkshopImage, Review, ClothingModel, ModelImage, Measurements, Order, User

class WorkshopImageInline(admin.TabularInline):
    model = WorkshopImage
    extra = 1

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ('date',)

class WorkshopAdminForm(forms.ModelForm):
    specialties_input = forms.CharField(
        label="Spécialités (une par ligne) - Optionnel",
        widget=forms.Textarea(attrs={
            'rows': 8, 
            'placeholder': 'costume\nrobe\nchemise\npantalon\njupe\nveste\nmanteau\nuniforme\ntenue_traditionnelle\ntenue_cérémonie\ntenue_mariage\ntenue_business\ntenue_casual\ntenue_sport\naccessoires\nretouche\nsur_mesure\nprêt_porter\nhaute_couture\ncouture_africaine\ncouture_européenne\ncouture_asiatique'
        }),
        required=False,
        help_text="Entrez une spécialité par ligne (optionnel). Styles disponibles : costume, robe, chemise, pantalon, jupe, veste, manteau, uniforme, tenue_traditionnelle, tenue_cérémonie, tenue_mariage, tenue_business, tenue_casual, tenue_sport, accessoires, retouche, sur_mesure, prêt_porter, haute_couture, couture_africaine, couture_européenne, couture_asiatique"
    )

    class Meta:
        model = Workshop
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.specialties:
            # Convertir la liste JSON en texte pour l'affichage
            specialties_list = self.instance.specialties if isinstance(self.instance.specialties, list) else []
            self.fields['specialties_input'].initial = '\n'.join(specialties_list)

    def clean_specialties_input(self):
        specialties_text = self.cleaned_data.get('specialties_input', '')
        if specialties_text:
            # Convertir le texte en liste
            specialties_list = [s.strip() for s in specialties_text.split('\n') if s.strip()]
            return specialties_list
        return []

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Mettre à jour le champ specialties avec les données du formulaire
        instance.specialties = self.cleaned_data.get('specialties_input', [])
        if commit:
            instance.save()
        return instance

@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    form = WorkshopAdminForm
    list_display = ['name', 'user', 'address', 'is_verified', 'is_active', 'average_rating']
    list_filter = ['is_verified', 'is_active', 'created_at']
    search_fields = ['name', 'address', 'user__username']
    readonly_fields = ['average_rating', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('user', 'name', 'description', 'logo')
        }),
        ('Contact', {
            'fields': ('address', 'phone')
        }),
        ('Spécialités', {
            'fields': ('specialties_input',),
            'description': 'Entrez les spécialités de l\'atelier (optionnel)'
        }),
        ('Tarifs et délais', {
            'fields': ('estimated_delivery_time', 'price_range_min', 'price_range_max')
        }),
        ('Statut', {
            'fields': ('is_verified', 'is_active', 'rating')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
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
    list_display = ['name', 'category', 'price', 'featured', 'is_active']
    list_filter = ['category', 'featured', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    inlines = [ModelImageInline]

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['workshop', 'user', 'rating', 'date', 'is_verified']
    list_filter = ['rating', 'is_verified', 'date']
    search_fields = ['workshop__name', 'user__username', 'comment']

@admin.register(Measurements)
class MeasurementsAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'measurement_type', 'created_at']
    list_filter = ['measurement_type', 'created_at']
    search_fields = ['user__username', 'name']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'workshop', 'model', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['user__username', 'workshop__name', 'model__name']
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

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'user_type', 'is_active']
    list_filter = ['user_type', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name'] 
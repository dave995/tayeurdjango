from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('client', 'Client'),
        ('workshop', 'Atelier'),
        ('admin', 'Administrateur'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='client')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)

    # Ajout des related_name pour résoudre les conflits
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',
        related_query_name='custom_user'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',
        related_query_name='custom_user'
    )

class Workshop(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='workshop_profile')
    name = models.CharField(max_length=100)
    description = models.TextField()
    logo = models.ImageField(upload_to='workshops/logos/')
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=15, blank=True, help_text="Numéro de téléphone de l'atelier")
    rating = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0
    )
    specialties = models.JSONField()
    estimated_delivery_time = models.IntegerField(help_text="En jours")
    price_range_min = models.DecimalField(max_digits=10, decimal_places=2)
    price_range_max = models.DecimalField(max_digits=10, decimal_places=2)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def average_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return 0
        return sum(review.rating for review in reviews) / len(reviews)

class ClothingModel(models.Model):
    CATEGORY_CHOICES = [
        ('shirt', 'Chemise'),
        ('dress', 'Robe'),
        ('suit', 'Costume'),
        ('pants', 'Pantalon'),
        ('skirt', 'Jupe'),
        ('other', 'Autre'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_time = models.IntegerField(help_text="En jours")
    featured = models.BooleanField(default=False)
    styles = models.JSONField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    model_3d_url = models.URLField(blank=True, help_text="URL du modèle 3D")

    def __str__(self):
        return self.name

class ModelImage(models.Model):
    model = models.ForeignKey(ClothingModel, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='models/')
    is_preview = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

class WorkshopImage(models.Model):
    workshop = models.ForeignKey(Workshop, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='workshops/')
    is_preview = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

class Review(models.Model):
    workshop = models.ForeignKey(Workshop, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date']

class Measurements(models.Model):
    SIZE_CHOICES = [
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
    ]

    MEASUREMENT_TYPE_CHOICES = [
        ('standard', 'Taille standard'),
        ('custom', 'Mesures personnalisées'),
        ('tailor', 'Mesures par tailleur'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)
    measurement_type = models.CharField(max_length=10, choices=MEASUREMENT_TYPE_CHOICES, default='standard')
    standard_size = models.CharField(max_length=3, choices=SIZE_CHOICES, blank=True, null=True)
    custom_measurements = models.JSONField(null=True, blank=True)
    tailor_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('in_progress', 'En cours'),
        ('ready', 'Prête'),
        ('delivered', 'Livrée'),
        ('cancelled', 'Annulée'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('paid', 'Payé'),
        ('refunded', 'Remboursé'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('card', 'Carte bancaire'),
        ('transfer', 'Virement'),
        ('cash', 'Espèces'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    model = models.ForeignKey(ClothingModel, on_delete=models.PROTECT)
    workshop = models.ForeignKey(Workshop, on_delete=models.PROTECT)
    measurements = models.ForeignKey(Measurements, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estimated_delivery = models.DateTimeField()
    actual_delivery = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    payment_id = models.CharField(max_length=100, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    cancellation_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

class OrderStatusUpdate(models.Model):
    order = models.ForeignKey(Order, related_name='status_updates', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-created_at']

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class MaterialCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Material Categories"
        ordering = ['name']

class Material(models.Model):
    UNIT_CHOICES = [
        ('m', 'Mètre'),
        ('cm', 'Centimètre'),
        ('kg', 'Kilogramme'),
        ('g', 'Gramme'),
        ('pcs', 'Pièce'),
        ('roll', 'Rouleau'),
        ('sheet', 'Feuille'),
    ]

    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=50, unique=True, help_text="Code produit unique")
    category = models.ForeignKey(MaterialCategory, on_delete=models.PROTECT)
    description = models.TextField()
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    min_stock_level = models.DecimalField(max_digits=10, decimal_places=2, help_text="Niveau minimum de stock pour les alertes")
    current_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    location = models.CharField(max_length=100, blank=True, help_text="Emplacement dans l'atelier")
    color = models.CharField(max_length=50, blank=True)
    width = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Largeur en cm")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.sku})"

    class Meta:
        ordering = ['category', 'name']

class StockMovement(models.Model):
    MOVEMENT_TYPE_CHOICES = [
        ('in', 'Entrée'),
        ('out', 'Sortie'),
        ('adjustment', 'Ajustement'),
        ('return', 'Retour'),
    ]

    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name='movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reference = models.CharField(max_length=100, blank=True, help_text="Numéro de facture, commande, etc.")
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.material.name} ({self.quantity})"

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Mettre à jour le stock du matériau
        if self.movement_type in ['in', 'return']:
            self.material.current_stock += self.quantity
        elif self.movement_type in ['out', 'adjustment']:
            self.material.current_stock -= self.quantity
        self.material.save()
        super().save(*args, **kwargs)

class MaterialImage(models.Model):
    material = models.ForeignKey(Material, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='materials/')
    is_preview = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
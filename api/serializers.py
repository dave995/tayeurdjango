from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    User, Workshop, ClothingModel, ModelImage, WorkshopImage,
    Review, Measurements, Order, OrderStatusUpdate, Supplier, MaterialCategory,
    MaterialImage, Material, StockMovement
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                 'user_type', 'phone', 'address', 'profile_picture')
        read_only_fields = ('id',)

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirmation = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirmation',
                 'first_name', 'last_name', 'user_type', 'phone', 'address')

    def validate(self, data):
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirmation')
        user = User.objects.create_user(**validated_data)
        
        # If user is a workshop, create a corresponding Workshop profile
        if user.user_type == 'workshop':
            Workshop.objects.create(
                user=user,
                name=user.username,
                description="",
                logo=None,
                address="",
                is_active=True,
                specialties=[],
                estimated_delivery_time=7,
                price_range_min=0.00,
                price_range_max=0.00,
            )
            # Note: You might want to set other default fields for the workshop here

        return user

class WorkshopImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkshopImage
        fields = ('id', 'image', 'is_preview', 'order')

class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ('id', 'user', 'user_name', 'rating', 'comment', 'date', 'is_verified')
        read_only_fields = ('user', 'date', 'is_verified')

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

class WorkshopSerializer(serializers.ModelSerializer):
    images = WorkshopImageSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)
    phone = serializers.SerializerMethodField()

    name = serializers.CharField(allow_null=True, required=False)
    description = serializers.CharField(allow_null=True, required=False)
    logo = serializers.ImageField(allow_null=True, required=False)
    address = serializers.CharField(allow_null=True, required=False)
    rating = serializers.FloatField(allow_null=True, required=False)
    specialties = serializers.JSONField(allow_null=True, required=False)
    estimated_delivery_time = serializers.IntegerField(allow_null=True, required=False)
    price_range_min = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True, required=False)
    price_range_max = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True, required=False)
    is_verified = serializers.BooleanField(allow_null=True, required=False)
    is_active = serializers.BooleanField(allow_null=True, required=False)
    created_at = serializers.DateTimeField(allow_null=True, required=False)
    updated_at = serializers.DateTimeField(allow_null=True, required=False)

    class Meta:
        model = Workshop
        fields = ('id', 'user', 'name', 'description', 'logo', 'address',
                 'rating', 'specialties', 'estimated_delivery_time',
                 'price_range_min', 'price_range_max', 'is_verified',
                 'is_active', 'images', 'reviews', 'average_rating',
                 'created_at', 'updated_at', 'phone')
        read_only_fields = ('rating', 'is_verified', 'created_at', 'updated_at')

    def get_average_rating(self, obj):
        return obj.average_rating()

    def get_phone(self, obj):
        return obj.user.phone if obj.user else None

class ModelImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelImage
        fields = ('id', 'image', 'is_preview', 'order')

class ClothingModelSerializer(serializers.ModelSerializer):
    images = ModelImageSerializer(many=True, read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = ClothingModel
        fields = ('id', 'name', 'category', 'category_display', 'description',
                 'price', 'estimated_time', 'featured', 'styles',
                 'is_active', 'images', 'model_3d_url', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

class MeasurementsSerializer(serializers.ModelSerializer):
    measurement_type_display = serializers.CharField(source='get_measurement_type_display', read_only=True)
    standard_size_display = serializers.CharField(source='get_standard_size_display', read_only=True)

    class Meta:
        model = Measurements
        fields = ('id', 'user', 'name', 'measurement_type', 'measurement_type_display',
                 'standard_size', 'standard_size_display', 'custom_measurements',
                 'tailor_notes', 'created_at', 'updated_at')
        read_only_fields = ('user', 'created_at', 'updated_at')

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = OrderStatusUpdate
        fields = ('id', 'status', 'status_display', 'notes', 'created_at', 'created_by_name')
        read_only_fields = ('created_at',)

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None

class OrderSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    model_details = ClothingModelSerializer(source='model', read_only=True)
    workshop_details = WorkshopSerializer(source='workshop', read_only=True)
    measurements_details = MeasurementsSerializer(source='measurements', read_only=True)
    status_updates = OrderStatusUpdateSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'model', 'model_details', 'workshop', 'workshop_details',
                 'measurements', 'measurements_details', 'status', 'status_display',
                 'total_price', 'created_at', 'updated_at', 'estimated_delivery',
                 'actual_delivery', 'notes', 'payment_status', 'payment_status_display',
                 'payment_method', 'payment_method_display', 'payment_id',
                 'tracking_number', 'cancellation_reason', 'status_updates')
        read_only_fields = ('user', 'created_at', 'updated_at', 'status_updates')

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ('id', 'name', 'contact_name', 'email', 'phone', 'address',
                 'notes', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

class MaterialCategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source='parent.name', read_only=True)

    class Meta:
        model = MaterialCategory
        fields = ('id', 'name', 'description', 'parent', 'parent_name',
                 'children', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

    def get_children(self, obj):
        if obj.children.exists():
            return MaterialCategorySerializer(obj.children.all(), many=True).data
        return []

class MaterialImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialImage
        fields = ('id', 'image', 'is_preview', 'order')

class MaterialSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)
    images = MaterialImageSerializer(many=True, read_only=True)
    stock_status = serializers.SerializerMethodField()

    class Meta:
        model = Material
        fields = ('id', 'name', 'sku', 'category', 'category_name',
                 'description', 'unit', 'unit_display', 'unit_price',
                 'supplier', 'supplier_name', 'min_stock_level',
                 'current_stock', 'location', 'color', 'width',
                 'is_active', 'images', 'stock_status',
                 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at', 'current_stock')

    def get_stock_status(self, obj):
        if obj.current_stock <= 0:
            return 'out_of_stock'
        elif obj.current_stock <= obj.min_stock_level:
            return 'low_stock'
        return 'in_stock'

class StockMovementSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='material.name', read_only=True)
    movement_type_display = serializers.CharField(source='get_movement_type_display', read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = StockMovement
        fields = ('id', 'material', 'material_name', 'movement_type',
                 'movement_type_display', 'quantity', 'unit_price',
                 'reference', 'notes', 'created_by', 'created_by_name',
                 'created_at')
        read_only_fields = ('created_at',)

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None
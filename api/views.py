from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import (
    User, Workshop, ClothingModel, ModelImage, WorkshopImage,
    Review, Measurements, Order, OrderStatusUpdate, Supplier, MaterialCategory,
    Material, MaterialImage, StockMovement
)
from .serializers import (
    UserSerializer, UserRegistrationSerializer, WorkshopSerializer,
    ClothingModelSerializer, ModelImageSerializer, WorkshopImageSerializer,
    ReviewSerializer, MeasurementsSerializer, OrderSerializer,
    OrderStatusUpdateSerializer, SupplierSerializer, MaterialCategorySerializer,
    MaterialSerializer, MaterialImageSerializer, StockMovementSerializer
)
from django.db.models import Q, F

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAuthenticated] # Commented out

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        # Allow authenticated users to access their own details via /me/
        elif self.action == 'me':
             return [permissions.IsAuthenticated()]
        # For other actions (list, retrieve, update, delete), require authentication
        # You might want stricter permissions here depending on your needs
        return [permissions.IsAuthenticated()]

    # Add custom action for /api/users/me/
    @action(detail=False, methods=['get'])
    def me(self, request):
        if request.user.is_authenticated:
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        # Should not reach here due to IsAuthenticated permission, but good practice
        return Response({'detail': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)

    def get_queryset(self):
        # Limit queryset for non-admin users if they are not accessing /me/
        if self.request.user.is_authenticated and self.request.user.user_type != 'admin' and self.action != 'me':
             # Allow users to see their own profile when requesting /users/{id}/ if id matches their user id
            if self.action == 'retrieve' and str(self.request.user.id) == self.kwargs.get('pk'):
                 return User.objects.filter(id=self.request.user.id)
            # Deny listing all users for non-admins
            return User.objects.none() # Return empty queryset for non-admin non-/me/ requests
        # Admins can see all users, and /me/ action bypasses this filter
        return User.objects.all()

class WorkshopViewSet(viewsets.ModelViewSet):
    queryset = Workshop.objects.filter(is_active=True)
    serializer_class = WorkshopSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Workshop.objects.filter(is_active=True)
        specialties = self.request.query_params.getlist('specialties', None)
        min_rating = self.request.query_params.get('min_rating', None)
        max_price = self.request.query_params.get('max_price', None)

        if specialties:
            queryset = queryset.filter(specialties__overlap=specialties)
        if min_rating:
            queryset = queryset.filter(rating__gte=min_rating)
        if max_price:
            queryset = queryset.filter(price_range_max__lte=max_price)

        return queryset

    @action(detail=True, methods=['post'])
    def add_review(self, request, pk=None):
        workshop = self.get_object()
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(workshop=workshop, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClothingModelViewSet(viewsets.ModelViewSet):
    queryset = ClothingModel.objects.filter(is_active=True)
    serializer_class = ClothingModelSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = ClothingModel.objects.filter(is_active=True)
        category = self.request.query_params.get('category', None)
        featured = self.request.query_params.get('featured', None)
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)

        if category:
            queryset = queryset.filter(category=category)
        if featured:
            queryset = queryset.filter(featured=True)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        return queryset

class ModelImageViewSet(viewsets.ModelViewSet):
    queryset = ModelImage.objects.all()
    serializer_class = ModelImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        model_id = self.kwargs.get('model_pk')
        return ModelImage.objects.filter(model_id=model_id)

class WorkshopImageViewSet(viewsets.ModelViewSet):
    queryset = WorkshopImage.objects.all()
    serializer_class = WorkshopImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        workshop_id = self.kwargs.get('workshop_pk')
        return WorkshopImage.objects.filter(workshop_id=workshop_id)

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        workshop_id = self.kwargs.get('workshop_pk')
        return Review.objects.filter(workshop_id=workshop_id)

    def perform_create(self, serializer):
        workshop = get_object_or_404(Workshop, pk=self.kwargs.get('workshop_pk'))
        serializer.save(user=self.request.user, workshop=workshop)

class MeasurementsViewSet(viewsets.ModelViewSet):
    queryset = Measurements.objects.all()
    serializer_class = MeasurementsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Measurements.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Admin can see all orders, other users only their own
        if self.request.user.user_type == 'admin':
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                order=order,
                created_by=request.user,
                status=serializer.validated_data['status']
            )
            order.status = serializer.validated_data['status']
            order.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status not in ['pending', 'confirmed']:
            return Response(
                {"error": "Seules les commandes en attente ou confirmées peuvent être annulées"},
                status=status.HTTP_400_BAD_REQUEST
            )
        order.status = 'cancelled'
        order.cancellation_reason = request.data.get('reason', '')
        order.save()
        return Response(OrderSerializer(order).data)

class OrderStatusUpdateViewSet(viewsets.ModelViewSet):
    queryset = OrderStatusUpdate.objects.all()
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter status updates by the order they belong to
        order_id = self.kwargs.get('order_pk')
        if order_id:
            # Ensure the user has permission to view the order
            order = get_object_or_404(Order, pk=order_id)
            if self.request.user.user_type == 'admin' or order.user == self.request.user:
                 return OrderStatusUpdate.objects.filter(order=order)
            return OrderStatusUpdate.objects.none() # User doesn't have permission for this order
        
        # Optional: Decide if listing all status updates without filtering by order is allowed
        # Currently, this will return an empty queryset unless the user is an admin viewing all orders
        if self.request.user.user_type == 'admin':
            return OrderStatusUpdate.objects.all()
        return OrderStatusUpdate.objects.none()

    def perform_create(self, serializer):
        # Ensure the user creating the status update is allowed to modify the order
        order = get_object_or_404(Order, pk=self.kwargs.get('order_pk'))
        if self.request.user.user_type == 'admin' or order.user == self.request.user:
            serializer.save(order=order, created_by=self.request.user)
        else:
            # Raise a permission denied error
            raise permissions.PermissionDenied("You do not have permission to add status updates to this order.")

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Supplier.objects.all()
        search = self.request.query_params.get('search', None)
        is_active = self.request.query_params.get('is_active', None)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(contact_name__icontains=search) |
                Q(email__icontains=search)
            )
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return queryset

class MaterialCategoryViewSet(viewsets.ModelViewSet):
    queryset = MaterialCategory.objects.all()
    serializer_class = MaterialCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # Allow non-authenticated users to list categories if needed, otherwise restrict
        # If you only want authenticated users to see categories, add permissions.IsAuthenticated
        return MaterialCategory.objects.all()

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Material.objects.all()
        search = self.request.query_params.get('search', None)
        category = self.request.query_params.get('category', None)
        supplier = self.request.query_params.get('supplier', None)
        stock_status = self.request.query_params.get('stock_status', None)
        is_active = self.request.query_params.get('is_active', None)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(sku__icontains=search) |
                Q(description__icontains=search)
            )
        if category:
            queryset = queryset.filter(category_id=category)
        if supplier:
            queryset = queryset.filter(supplier_id=supplier)
        if stock_status:
            if stock_status == 'out_of_stock':
                queryset = queryset.filter(current_stock=0)
            elif stock_status == 'low_stock':
                queryset = queryset.filter(current_stock__lte=F('min_stock_level'))
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return queryset

    @action(detail=True, methods=['post'])
    def add_stock(self, request, pk=None):
        material = self.get_object()
        serializer = StockMovementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                material=material,
                movement_type='in',
                created_by=request.user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def remove_stock(self, request, pk=None):
        material = self.get_object()
        serializer = StockMovementSerializer(data=request.data)
        if serializer.is_valid():
            quantity = serializer.validated_data['quantity']
            if material.current_stock < quantity:
                return Response(
                    {"error": "Stock insuffisant"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.save(
                material=material,
                movement_type='out',
                created_by=request.user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MaterialImageViewSet(viewsets.ModelViewSet):
    queryset = MaterialImage.objects.all()
    serializer_class = MaterialImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        material_id = self.kwargs.get('material_pk')
        return MaterialImage.objects.filter(material_id=material_id)

    def perform_create(self, serializer):
        material = get_object_or_404(Material, pk=self.kwargs.get('material_pk'))
        # Optional: Check if user has permissions to add images to this material
        serializer.save(material=material)

class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = StockMovement.objects.all()
        material_id = self.request.query_params.get('material', None)
        movement_type = self.request.query_params.get('movement_type', None)

        if material_id:
            queryset = queryset.filter(material_id=material_id)
        if movement_type:
            queryset = queryset.filter(movement_type=movement_type)
        
        # Optional: Restrict to only showing movements related to materials the user has access to
        # This depends on how material permissions are handled.

        # Admins can see all stock movements
        if self.request.user.user_type == 'admin':
            return queryset

        # Non-admins can't see all stock movements by default unless filtered by their materials
        # For now, returning empty to prevent accidental exposure
        return StockMovement.objects.none()

    def perform_create(self, serializer):
        # Optional: Check if the user has permission to create stock movements for this material
        serializer.save(created_by=self.request.user)
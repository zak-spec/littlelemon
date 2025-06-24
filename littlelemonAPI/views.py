from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions, filters
from rest_framework.decorators import api_view, permission_classes, throttle_classes, action
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from .serializers import (
    Categoryserializer, MenuItemserializers, Cartserializers, 
    Orderserializers, OrderItemserializers, UserSerializer,
    UserCreateSerializer, GroupSerializer, GroupDetailSerializer
)
from .models import Category, MenuItem, Cart, Order, OrderItem
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Q
from decimal import Decimal


# ========================= CUSTOM PERMISSIONS =========================

class IsManagerOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado que permite lectura a usuarios autenticados
    y escritura solo a managers o staff
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return (request.user.is_staff or 
                request.user.groups.filter(name="Manager").exists())


class IsOwnerOrManager(permissions.BasePermission):
    """
    Permiso que permite acceso al propietario del objeto o a managers
    """
    def has_object_permission(self, request, view, obj):
        # Lectura permitida para propietarios
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        
        # Managers tienen acceso completo
        return (request.user.is_staff or 
                request.user.groups.filter(name="Manager").exists())


class IsDeliveryCrewOrManager(permissions.BasePermission):
    """
    Permiso para delivery crew y managers
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return (request.user.is_staff or 
                request.user.groups.filter(name__in=["Manager", "Delivery_crew"]).exists())


# ========================= CUSTOM PAGINATION =========================

class StandardResultsSetPagination(PageNumberPagination):
    """
    Paginación estándar para todos los ViewSets
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


# ========================= VIEWSETS =========================

class CategoryViewSet(ModelViewSet):
    """
    ViewSet para gestión de categorías
    Permisos: Lectura para autenticados, escritura para managers
    """
    queryset = Category.objects.all()
    serializer_class = Categoryserializer
    permission_classes = [IsManagerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['title']
    search_fields = ['title']
    ordering_fields = ['title', 'created_at']
    ordering = ['title']

    def destroy(self, request, *args, **kwargs):
        """
        Override para prevenir eliminación de categorías con menús
        """
        category = self.get_object()
        if category.menu_items.exists():
            return Response(
                {"error": "No se puede eliminar la categoría porque tiene elementos de menú asociados"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


class MenuItemViewSet(ModelViewSet):
    """
    ViewSet para gestión de elementos del menú
    Incluye filtros avanzados y búsqueda
    """
    queryset = MenuItem.objects.select_related('featured').filter(available=True)
    serializer_class = MenuItemserializers
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['featured__title', 'available']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'price', 'created_at']
    # ordering = ['title']

    def get_queryset(self):
        """
        Filtros personalizados para precio y categoría
        """
        queryset = super().get_queryset()
        
        # Filtro por categoría
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(featured__title__icontains=category)
        
        # Filtro por precio máximo
        to_price = self.request.query_params.get('to_price')
        if to_price:
            try:
                to_price = Decimal(to_price)
                queryset = queryset.filter(price__lte=to_price)
            except (ValueError, TypeError):
                pass
        
        return queryset

    def get_permissions(self):
        """
        Permisos dinámicos: lectura libre, escritura para managers
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsManagerOrReadOnly]
        else:
            permission_classes = [AllowAny]
        
        return [permission() for permission in permission_classes]


class CartViewSet(ModelViewSet):
    """
    ViewSet para gestión del carrito de compras
    Solo permite acceso a elementos del propio usuario
    """
    serializer_class = Cartserializers
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """
        Solo mostrar elementos del carrito del usuario actual
        """
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Crear elemento en el carrito del usuario actual
        """
        menu_item = serializer.validated_data['MenuItem']
        quantity = serializer.validated_data.get('quantity', 1)
        
        # Verificar si ya existe el item en el carrito
        existing_item = Cart.objects.filter(
            user=self.request.user,
            MenuItem=menu_item
        ).first()
        
        if existing_item:
            # Actualizar cantidad si ya existe
            existing_item.quantity += quantity
            existing_item.save()
            return existing_item
        else:
            # Crear nuevo item
            serializer.save(
                user=self.request.user,
                unit_price=menu_item.price,
                price=menu_item.price * quantity
            )

    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """
        Acción personalizada para vaciar el carrito
        """
        Cart.objects.filter(user=request.user).delete()
        return Response(
            {"message": "Carrito vaciado exitosamente"},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """
        Acción personalizada para añadir items al carrito
        """
        menu_item_id = request.data.get('menu_item_id')
        quantity = int(request.data.get('quantity', 1))
        
        if not menu_item_id:
            return Response(
                {"error": "Se requiere menu_item_id"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            menu_item = MenuItem.objects.get(id=menu_item_id, available=True)
        except MenuItem.DoesNotExist:
            return Response(
                {"error": "El elemento del menú no existe o no está disponible"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Buscar item existente en el carrito
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            MenuItem=menu_item,
            defaults={
                'quantity': quantity,
                'unit_price': menu_item.price,
                'price': menu_item.price * quantity
            }
        )
        
        if not created:
            # Actualizar cantidad si ya existe
            cart_item.quantity += quantity
            cart_item.price = cart_item.unit_price * cart_item.quantity
            cart_item.save()
        
        serializer = self.get_serializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderViewSet(ModelViewSet):
    """
    ViewSet para gestión de órdenes
    Incluye diferentes permisos según el tipo de usuario
    """
    serializer_class = Orderserializers
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'date']
    ordering_fields = ['date', 'total', 'created_at']
    ordering = ['-date']

    def get_queryset(self):
        """
        Queryset dinámico según el tipo de usuario
        """
        user = self.request.user
        
        if user.is_staff or user.groups.filter(name="Manager").exists():
            # Managers ven todas las órdenes
            return Order.objects.all()
        elif user.groups.filter(name="Delivery_crew").exists():
            # Delivery crew ve órdenes asignadas a ellos
            return Order.objects.filter(
                Q(delivery_crew=user) | Q(delivery_crew__isnull=True)
            )
        else:
            # Usuarios normales solo ven sus propias órdenes
            return Order.objects.filter(user=user)

    def perform_create(self, serializer):
        """
        Crear orden desde el carrito del usuario
        """
        cart_items = Cart.objects.filter(user=self.request.user)
        
        if not cart_items.exists():
            raise ValidationError("El carrito está vacío")
        
        total = sum(item.price for item in cart_items)
        
        # Crear la orden
        order = serializer.save(
            user=self.request.user,
            total=total,
            date=timezone.now().date()
        )
        
        # Crear los OrderItems
        order_items = []
        for cart_item in cart_items:
            order_items.append(OrderItem(
                order=order,
                menuitem=cart_item.MenuItem,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                price=cart_item.price
            ))
        
        OrderItem.objects.bulk_create(order_items)
        
        # Limpiar el carrito
        cart_items.delete()

    @action(detail=True, methods=['patch'], permission_classes=[IsDeliveryCrewOrManager])
    def update_status(self, request, pk=None):
        """
        Actualizar solo el estado de la orden
        """
        order = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {"error": "Se requiere el campo 'status'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar si el nuevo estado es válido
        valid_statuses = [choice[0] for choice in Order.OrderStatus.choices]
        if new_status not in valid_statuses:
            return Response(
                {"error": f"Estado inválido. Opciones: {valid_statuses}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = new_status
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], permission_classes=[IsManagerOrReadOnly])
    def assign_crew(self, request, pk=None):
        """
        Asignar delivery crew a una orden (solo managers)
        """
        order = self.get_object()
        crew_ids = request.data.get('delivery_crew_ids', [])
        
        if not isinstance(crew_ids, list):
            crew_ids = [crew_ids]
        
        # Validar que los usuarios existen y son delivery crew
        crew_members = []
        for crew_id in crew_ids:
            try:
                user = User.objects.get(pk=crew_id)
                if not user.groups.filter(name="Delivery_crew").exists():
                    return Response(
                        {"error": f"Usuario {crew_id} no es parte del delivery crew"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                crew_members.append(user)
            except User.DoesNotExist:
                return Response(
                    {"error": f"Usuario {crew_id} no existe"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Asignar crew (solo uno por simplicidad)
        if crew_members:
            order.delivery_crew = crew_members[0]
            order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """
        Obtener items de una orden específica
        """
        order = self.get_object()
        
        # Verificar permisos para ver los items
        if (order.user != request.user and 
            not request.user.is_staff and 
            not request.user.groups.filter(name__in=["Manager", "Delivery_crew"]).exists()):
            return Response(
                {"error": "No tienes permisos para ver estos items"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        items = OrderItem.objects.filter(order=order)
        serializer = OrderItemserializers(items, many=True)
        return Response(serializer.data)


class UserViewSet(ModelViewSet):
    """
    ViewSet para gestión de usuarios
    Solo managers y staff pueden gestionar usuarios
    """
    queryset = User.objects.all()
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'email', 'date_joined']
    ordering = ['username']

    def get_serializer_class(self):
        """
        Usar diferentes serializers según la acción
        """
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        """
        Permisos dinámicos según la acción
        """
        if self.action == 'create':
            # Registro abierto
            permission_classes = [AllowAny]
        elif self.action in ['list', 'update', 'partial_update', 'destroy']:
            # Solo managers pueden gestionar usuarios
            permission_classes = [IsManagerOrReadOnly]
        else:
            # Retrieve: usuario puede ver su propio perfil
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]

    def get_object(self):
        """
        Permitir que usuarios accedan a su propio perfil con 'me'
        """
        pk = self.kwargs.get('pk')
        if pk == 'me':
            return self.request.user
        return super().get_object()

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Endpoint para obtener información del usuario actual
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsManagerOrReadOnly])
    def add_to_group(self, request, pk=None):
        """
        Añadir usuario a un grupo
        """
        user = self.get_object()
        group_name = request.data.get('group_name')
        
        if not group_name:
            return Response(
                {"error": "Se requiere group_name"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
            return Response(
                {"message": f"Usuario añadido al grupo {group_name}"},
                status=status.HTTP_200_OK
            )
        except Group.DoesNotExist:
            return Response(
                {"error": f"Grupo {group_name} no existe"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['delete'], permission_classes=[IsManagerOrReadOnly])
    def remove_from_group(self, request, pk=None):
        """
        Remover usuario de un grupo
        """
        user = self.get_object()
        group_name = request.data.get('group_name')
        
        if not group_name:
            return Response(
                {"error": "Se requiere group_name"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            group = Group.objects.get(name=group_name)
            user.groups.remove(group)
            return Response(
                {"message": f"Usuario removido del grupo {group_name}"},
                status=status.HTTP_200_OK
            )
        except Group.DoesNotExist:
            return Response(
                {"error": f"Grupo {group_name} no existe"},
                status=status.HTTP_404_NOT_FOUND
            )


class GroupViewSet(ModelViewSet):
    """
    ViewSet para gestión de grupos
    Solo staff puede gestionar grupos
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']

    def get_permissions(self):
        """
        Solo staff puede crear/modificar/eliminar grupos
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [IsManagerOrReadOnly]
        
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """
        Obtener usuarios de un grupo específico
        """
        group = self.get_object()
        users = group.user_set.all()
        
        # Aplicar paginación manual si es necesario
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(users, request)
        
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


# ========================= UTILITY VIEWS =========================

class UtilityViewSet(ViewSet):
    """
    ViewSet para funciones utilitarias y testing
    """
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny], 
            throttle_classes=[AnonRateThrottle])
    def throttle_check(self, request):
        """
        Endpoint para probar throttling para usuarios anónimos
        """
        return Response({
            "message": "Throttle test successful",
            "user": "anonymous",
            "timestamp": timezone.now().isoformat()
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], 
            throttle_classes=[UserRateThrottle])
    def throttle_check_auth(self, request):
        """
        Endpoint para probar throttling para usuarios autenticados
        """
        return Response({
            "message": "Authenticated throttle test successful",
            "user": request.user.username,
            "user_id": request.user.id,
            "timestamp": timezone.now().isoformat()
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def secret(self, request):
        """
        Endpoint secreto para usuarios autenticados
        """
        if request.user.groups.filter(name='Manager').exists():
            return Response({
                "message": "Secret message for managers",
                "level": "manager"
            })
        else:
            return Response({
                "message": "Secret message for authenticated users",
                "level": "user"
            })


# ========================= FUNCIÓN PARA REGISTRO =========================

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Endpoint para registro de usuarios (mantiene compatibilidad con FBV)
    """
    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")
    
    if not all([username, email, password]):
        return Response(
            {"error": "Se requieren username, email y password."}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(email=email).exists():
        return Response(
            {"error": "El email ya está en uso."}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "El username ya está en uso."}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        validate_password(password)
    except Exception as e:
        return Response(
            {"error": "Contraseña no válida", "details": e.messages}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        return Response({
            "message": "Usuario creado exitosamente",
            "username": user.username,
            "email": user.email,
            "id": user.id
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {"error": "Error al crear el usuario", "details": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
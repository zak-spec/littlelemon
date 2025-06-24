from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from .serializers import (
    Categoryserializer, MenuItemserializers, Cartserializers, 
    Orderserializers, OrderItemserializers, UserSerializer,
    UserCreateSerializer, GroupSerializer, GroupDetailSerializer
)
from .models import Category, MenuItem, Cart, Order, OrderItem
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
def hello_world(request):
    return Response("Hello, world!")

@api_view(['POST'])
@permission_classes([AllowAny])  # Permitir acceso a todos para este endpoint
def register_user(request):
    """
    Endpoint para registrar un nuevo usuario.
    """
    if request.method == 'POST':
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")
        if not username or not email or not password:
            return Response({"error": "Se requieren username, email y password."}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=request.data['email']).exists():
            return Response({"error": "El email de usuario ya existe."}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            validate_password(request.data['password'])
        except Exception as e:
            return Response({"error": "Contraseña no válida", "details": 
                 e.messages}, status=status.HTTP_400_BAD_REQUEST )
            
        try:
            user=User.objects.create_user(
                  username=request.data['username'],
                 email=request.data['email'],
                password=request.data['password']
                 )
                
            return Response({
                     "message": "Usuario creado exitosamente",
                      "username": user.username,
                      "email": user.email
                 }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": "Error al crear el usuario", "details": 
                str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    
            
            

        


@api_view(['GET','POST'])
# @permission_classes([IsAuthenticated])  # Comentado para usar IsAuthenticatedOrReadOnly global
def menu_items(request):
    if request.method == 'GET':
        items = MenuItem.objects.select_related('featured').all()
        category_name = request.query_params.get('category')
        to_price = request.query_params.get('to_price')
        search = request.query_params.get('search')
        ordering = request.query_params.get('ordering')
        perpage = request.query_params.get('perpage', default=5)
        page = request.query_params.get('page', default=1)
        if category_name:
            items = items.filter(Category__title=category_name)
        if to_price:
            items = items.filter(price__lte=to_price)
        if search:
            items = items.filter(title__icontains=search)
        if ordering:
            ordering_fields = ordering.split(",")
            print(*ordering_fields)
            items = items.order_by(*ordering_fields)
        paginator = Paginator(items, per_page=perpage)
        try:
            items = paginator.page(number=page)
        except EmptyPage:
            items = []
        serializer = MenuItemserializers(items, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = MenuItemserializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([AllowAny])  # Permitir acceso a todos para GET, pero PATCH y DELETE requieren autenticación en configuración global
def menu_itemsbuscar(request, pk):
    item = get_object_or_404(MenuItem, id=pk)
    if request.method == 'GET':
        serializer = MenuItemserializers(item)
        return Response(serializer.data)
    elif request.method == 'PATCH':
        serializer = MenuItemserializers(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200)
    elif request.method == 'DELETE':
        item.delete()
        return Response(status=204)

@api_view(['GET'])
def Categoria(request):
    Categoria_item = Category.objects.all()
    serialized_category = Categoryserializer(Categoria_item, many=True)
    return Response(serialized_category.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def secret(request):
    if request.user.groups.filter(name='Manager').exists():
        return Response({"message": "Some secret message"})
    else:
        return Response(status=403)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def secretv2(request):
    return Response({"message": "This is a secret message for authenticated users."})

@api_view(['GET'])  # Especificar métodos explícitamente
@permission_classes([AllowAny])  # Usar AllowAny en lugar de lista vacía
@throttle_classes([AnonRateThrottle])
def throttle_check(request):
    return Response({"message": "successful"})


@api_view(['GET']) 
@permission_classes([IsAuthenticated])  # Asegurar que solo usuarios autenticados accedan
@throttle_classes([UserRateThrottle]) 
def throttle_check_auth(request):
    return Response({"message": "message for the logged in users only"})

@api_view(["POST"])
def create_user(request):
    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")
    if not username or not email or not password:
        return Response({"error": "Se requieren username, email y password."}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(username=username).exists():
        return Response({"error": "El usuario ya existe."}, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.create_user(username=username, email=email, password=password)
    return Response({"message": "Usuario creado exitosamente.", "user_id": user.id}, status=status.HTTP_201_CREATED)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user(request):
    user = request.user
    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_managers(request):
    managers = User.objects.filter(groups__name="Manager")
    managers_data = [{"id": u.id, "username": u.username, "email": u.email} for u in managers]
    return Response(managers_data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def assign_to_manager_group(request):
    user = request.user
    try:
        group = Group.objects.get(name="managers")
    except Group.DoesNotExist:
        return Response({"error": "El grupo Manager no existe."}, status=status.HTTP_400_BAD_REQUEST)
    user.groups.add(group)
    return Response({"message": "Usuario asignado al grupo de gerentes."}, status=status.HTTP_201_CREATED)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_from_manager_group(request):
    user = request.user
    try:
        group = Group.objects.get(name="managers")
    except Group.DoesNotExist:
        return Response({"error": "El grupo Manager no existe."}, status=status.HTTP_404_NOT_FOUND)
    if group not in user.groups.all():
        return Response({"error": "Usuario no pertenece al grupo de gerentes."}, status=status.HTTP_404_NOT_FOUND)
    user.groups.remove(group)
    return Response({"message": "Usuario eliminado del grupo de gerentes."}, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_delivery_crew(request):
    delivery_users = User.objects.filter(groups__name="Delivery_crew")
    data = [{"id": u.id, "username": u.username, "email": u.email} for u in delivery_users]
    return Response(data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def assign_to_delivery_crew(request):
    try:
        group = Group.objects.get(name="Delivery_crew")
    except Group.DoesNotExist:
        return Response({"error": "El grupo Delivery_crew no existe."}, status=status.HTTP_400_BAD_REQUEST)
    request.user.groups.add(group)
    return Response({"message": "Usuario asignado al grupo de Delivery_crew."}, status=201)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_from_delivery_crew(request, userId):
    try:
        group = Group.objects.get(name="Delivery_crew")
    except Group.DoesNotExist:
        return Response({"error": "El grupo Delivery_crew no existe."}, status=status.HTTP_404_NOT_FOUND)
    try:
        target_user = User.objects.get(pk=userId)
    except User.DoesNotExist:
        return Response({"error": "El usuario no existe."}, status=status.HTTP_404_NOT_FOUND)
    if group not in target_user.groups.all():
        return Response({"error": "El usuario no pertenece al grupo Delivery_crew."}, status=status.HTTP_404_NOT_FOUND)
    target_user.groups.remove(group)
    return Response({"message": "Usuario eliminado del grupo de Delivery_crew."}, status=200)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    serializer = Cartserializers(cart_items, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    menu_item_id = request.data.get("menu_item_id")
    quantity = request.data.get("quantity", 1)
    if not menu_item_id:
        return Response({"error": "Se requiere menu_item_id."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        menu_item = MenuItem.objects.get(id=menu_item_id)
    except MenuItem.DoesNotExist:
        return Response({"error": "El elemento del menú no existe."}, status=status.HTTP_404_NOT_FOUND)
    try:
        quantity = int(quantity)
    except ValueError:
        return Response({"error": "Cantidad inválida."}, status=status.HTTP_400_BAD_REQUEST)
    unit_price = menu_item.price
    total_price = unit_price * quantity
    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        MenuItem=menu_item,
        defaults={'quantity': quantity, 'unit_price': unit_price, 'price': total_price}
    )
    if not created:
        cart_item.quantity += quantity
        cart_item.price = cart_item.quantity * unit_price
        cart_item.save()
    serializer = Cartserializers(cart_item)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    Cart.objects.filter(user=request.user).delete()
    return Response({"message": "Carrito vaciado."}, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def view_orders(request):
    orders = Order.objects.filter(user=request.user)
    serializer = Orderserializers(orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_order(request):
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items.exists():
        return Response({"error": "El carrito está vacío."}, status=status.HTTP_400_BAD_REQUEST)
    total = sum(item.price for item in cart_items)
    order = Order.objects.create(
        user=request.user,
        total=total,
        date=timezone.now().date()
    )
    order_items = []
    for item in cart_items:
        order_items.append(OrderItem(
            order=order,
            menuitem=item.MenuItem,
            quantity=item.quantity,
            unit_price=item.unit_price,
            price=item.price
        ))
    OrderItem.objects.bulk_create(order_items)
    cart_items.delete()
    serializer = Orderserializers(order)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_order_items(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.user != request.user:
        return Response({"error": "Acceso no autorizado."}, status=status.HTTP_403_FORBIDDEN)
    order_items = OrderItem.objects.filter(order=order)
    serializer = OrderItemserializers(order_items, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def view_all_orders(request):
    if not request.user.is_staff:
        return Response({"error": "Acceso no autorizado."}, status=status.HTTP_403_FORBIDDEN)
    orders = Order.objects.all()
    serializer = Orderserializers(orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_order(request, pk):
    if not request.user.groups.filter(name="Manager").exists():
        return Response({"error": "Acceso no autorizado."}, status=status.HTTP_403_FORBIDDEN)
    order = get_object_or_404(Order, pk=pk)
    if "status" in request.data:
        new_status = request.data["status"]
        try:
            new_status = int(new_status)
        except (ValueError, TypeError):
            return Response({"error": "Valor de status inválido."}, status=status.HTTP_400_BAD_REQUEST)
        if new_status not in [0, 1]:
            return Response({"error": "El status debe ser 0 o 1."}, status=status.HTTP_400_BAD_REQUEST)
        order.status = bool(new_status)
    if "delivery_crew_ids" in request.data:
        crew_ids = request.data["delivery_crew_ids"]
        if not isinstance(crew_ids, list):
            crew_ids = [crew_ids]
        delivery_users = []
        for uid in crew_ids:
            try:
                user = User.objects.get(pk=uid)
            except User.DoesNotExist:
                return Response({"error": f"El usuario con id {uid} no existe."}, status=status.HTTP_400_BAD_REQUEST)
            if not user.groups.filter(name="Delivery_crew").exists():
                return Response({"error": f"El usuario con id {uid} no pertenece al grupo de entrega."}, status=status.HTTP_400_BAD_REQUEST)
            delivery_users.append(user)
        order.delivery_crew.set(delivery_users)
    order.save()
    serializer = Orderserializers(order)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_order_status_delivery(request, pk):
    if not request.user.groups.filter(name="Delivery_crew").exists():
        return Response({"error": "Acceso no autorizado."}, status=status.HTTP_403_FORBIDDEN)
    order = get_object_or_404(Order, pk=pk)
    if "status" not in request.data:
        return Response({"error": "El campo 'status' es requerido."}, status=status.HTTP_400_BAD_REQUEST)
    new_status = request.data["status"]
    try:
        new_status = int(new_status)
    except (ValueError, TypeError):
        return Response({"error": "Valor de status inválido."}, status=status.HTTP_400_BAD_REQUEST)
    if new_status not in [0, 1]:
        return Response({"error": "El status debe ser 0 o 1."}, status=status.HTTP_400_BAD_REQUEST)
    order.status = bool(new_status)
    order.save()
    serializer = Orderserializers(order)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.user != request.user and not request.user.groups.filter(name="Manager").exists():
        return Response({"error": "Acceso no autorizado."}, status=status.HTTP_403_FORBIDDEN)
    order.delete()
    return Response({"message": "Pedido eliminado."}, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def view_delivery_orders(request):
    if not request.user.groups.filter(name__in=["Manager", "Delivery_crew"]).exists():
        return Response({"error": "Acceso no autorizado."}, status=status.HTTP_403_FORBIDDEN)
    orders = Order.objects.filter(delivery_crew__isnull=False).distinct()
    serializer = Orderserializers(orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_category(request):
    """
    Crear una nueva categoría
    Requiere permisos de administrador o gerente
    """
    if not request.user.is_staff and not request.user.groups.filter(name="Manager").exists():
        return Response({"error": "Acceso no autorizado."}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = Categoryserializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def category_detail(request, pk):
    """
    Recuperar, actualizar o eliminar una categoría
    """
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = Categoryserializer(category)
        return Response(serializer.data)
    
    # Verificar permisos para modificaciones
    if not request.user.is_staff and not request.user.groups.filter(name="Manager").exists():
        return Response({"error": "Acceso no autorizado."}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'PUT' or request.method == 'PATCH':
        partial = request.method == 'PATCH'
        serializer = Categoryserializer(category, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        # Verificar si hay elementos de menú asociados
        if MenuItem.objects.filter(featured=category).exists():
            return Response(
                {"error": "No se puede eliminar la categoría porque tiene elementos de menú asociados"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_list(request):
    """
    Listar todos los usuarios del sistema.
    Requiere permisos de administrador o gerente
    """
    if not request.user.is_staff and not request.user.groups.filter(name="Manager").exists():
        return Response({"error": "Acceso no autorizado."}, status=status.HTTP_403_FORBIDDEN)
    
    # Soporte para paginación y filtrado
    page = int(request.query_params.get('page', 1))
    per_page = int(request.query_params.get('per_page', 10))
    search = request.query_params.get('search', '')
    
    # Filtrar usuarios
    users = User.objects.all().order_by('username')
    if search:
        users = users.filter(username__icontains=search) | users.filter(email__icontains=search)
    
    # Paginar resultados
    paginator = Paginator(users, per_page)
    try:
        users = paginator.page(page)
    except EmptyPage:
        users = []
    
    serializer = UserSerializer(users, many=True)
    
    return Response({
        'count': paginator.count,
        'pages': paginator.num_pages,
        'current_page': page,
        'results': serializer.data
    })

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def user_detail(request, pk):
    """
    Recuperar, actualizar o desactivar un usuario
    """
    # Solo administradores, gerentes o el propio usuario pueden acceder
    if not (request.user.is_staff or 
            request.user.groups.filter(name="Manager").exists() or 
            request.user.id == int(pk)):
        return Response({"error": "Acceso no autorizado."}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        groups = [group.name for group in user.groups.all()]
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_active': user.is_active,
            'groups': groups,
            'date_joined': user.date_joined
        }
        return Response(data)
    
    # Solo administradores o gerentes pueden modificar usuarios (excepto el propio usuario)
    if request.method in ['PUT', 'PATCH'] and not (request.user.is_staff or 
            request.user.groups.filter(name="Manager").exists()) and request.user.id != int(pk):
        return Response({"error": "No tienes permisos para modificar este usuario."},
                        status=status.HTTP_403_FORBIDDEN)
    
    if request.method in ['PUT', 'PATCH']:
        # Proteger campos sensibles
        allowed_fields = ['first_name', 'last_name', 'email']
        
        # Staff puede cambiar más campos
        if request.user.is_staff:
            allowed_fields.extend(['is_active', 'username'])
        
        # Filtrar solo los campos permitidos
        filtered_data = {}
        for field in allowed_fields:
            if field in request.data:
                filtered_data[field] = request.data[field]
        
        # Actualizar usuario
        for key, value in filtered_data.items():
            setattr(user, key, value)
        
        try:
            user.save()
            return Response({"message": "Usuario actualizado correctamente"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'DELETE':
        # Solo permitir a staff deshabilitar usuarios
        if not request.user.is_staff:
            return Response({"error": "Solo administradores pueden desactivar usuarios."},
                          status=status.HTTP_403_FORBIDDEN)
        
        # En lugar de eliminar, desactivamos el usuario
        user.is_active = False
        user.save()
        return Response({"message": "Usuario desactivado correctamente"},
                       status=status.HTTP_200_OK)

@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def cart_item_detail(request, pk):
    """
    Recuperar, actualizar o eliminar un elemento específico del carrito
    """
    try:
        cart_item = Cart.objects.get(pk=pk, user=request.user)
    except Cart.DoesNotExist:
        return Response({"error": "Elemento no encontrado en el carrito."}, 
                      status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = Cartserializers(cart_item)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        # Actualizar cantidad del ítem en el carrito
        quantity = request.data.get('quantity')
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                return Response({"error": "La cantidad debe ser mayor que cero."},
                              status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({"error": "Cantidad inválida."},
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Actualizar el ítem
        cart_item.quantity = quantity
        cart_item.price = cart_item.unit_price * quantity
        cart_item.save()
        
        serializer = Cartserializers(cart_item)
        return Response(serializer.data)
    
    elif request.method == 'DELETE':
        # Eliminar solo este ítem del carrito
        cart_item.delete()
        return Response({"message": "Elemento eliminado del carrito."},
                       status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def group_list(request):
    """
    Listar todos los grupos o crear un nuevo grupo
    Requiere permisos de administrador o gerente
    """
    if not request.user.is_staff and not request.user.groups.filter(name="Manager").exists():
        return Response({"error": "Acceso no autorizado."}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        groups = Group.objects.all().order_by('name')
        data = []
        for group in groups:
            data.append({
                'id': group.id,
                'name': group.name,
                'user_count': group.user_set.count()
            })
        return Response(data)
    
    elif request.method == 'POST':
        if not request.user.is_staff:  # Solo administradores pueden crear grupos
            return Response({"error": "Solo administradores pueden crear grupos."},
                          status=status.HTTP_403_FORBIDDEN)
        
        name = request.data.get('name')
        if not name:
            return Response({"error": "Se requiere un nombre para el grupo."},
                          status=status.HTTP_400_BAD_REQUEST)
        
        if Group.objects.filter(name=name).exists():
            return Response({"error": "Ya existe un grupo con este nombre."},
                          status=status.HTTP_400_BAD_REQUEST)
        
        group = Group.objects.create(name=name)
        return Response({
            'id': group.id,
            'name': group.name,
            'message': 'Grupo creado correctamente'
        }, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def group_detail(request, pk):
    """
    Recuperar, actualizar o eliminar un grupo
    """
    if not request.user.is_staff and not request.user.groups.filter(name="Manager").exists():
        return Response({"error": "Acceso no autorizado."}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        group = Group.objects.get(pk=pk)
    except Group.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        # Obtener usuarios del grupo con paginación
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 20))
        
        users = group.user_set.all().order_by('username')
        paginator = Paginator(users, per_page)
        
        try:
            paginated_users = paginator.page(page)
        except EmptyPage:
            paginated_users = []
        
        users_data = []
        for user in paginated_users:
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email
            })
        
        return Response({
            'id': group.id,
            'name': group.name,
            'user_count': group.user_set.count(),
            'users': users_data,
            'page': page,
            'pages': paginator.num_pages
        })
    
    elif request.method == 'PUT':
        if not request.user.is_staff:  # Solo administradores pueden modificar grupos
            return Response({"error": "Solo administradores pueden modificar grupos."},
                          status=status.HTTP_403_FORBIDDEN)
        
        name = request.data.get('name')
        if not name:
            return Response({"error": "Se requiere un nombre para el grupo."},
                          status=status.HTTP_400_BAD_REQUEST)
        
        if Group.objects.filter(name=name).exclude(pk=pk).exists():
            return Response({"error": "Ya existe otro grupo con este nombre."},
                          status=status.HTTP_400_BAD_REQUEST)
        
        group.name = name
        group.save()
        
        return Response({
            'id': group.id,
            'name': group.name,
            'message': 'Grupo actualizado correctamente'
        })
    
    elif request.method == 'DELETE':
        if not request.user.is_staff:  # Solo administradores pueden eliminar grupos
            return Response({"error": "Solo administradores pueden eliminar grupos."},
                          status=status.HTTP_403_FORBIDDEN)
        
        group.delete()
        return Response({"message": "Grupo eliminado correctamente."},
                       status=status.HTTP_200_OK)

@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def group_users(request, pk):
    """
    Añadir o eliminar usuarios de un grupo
    """
    if not request.user.is_staff and not request.user.groups.filter(name="Manager").exists():
        return Response({"error": "Acceso no autorizado."}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        group = Group.objects.get(pk=pk)
    except Group.DoesNotExist:
        return Response({"error": "Grupo no encontrado."}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'POST':
        # Añadir usuario(s) al grupo
        user_ids = request.data.get('user_ids', [])
        if not isinstance(user_ids, list):
            user_ids = [user_ids]
        
        if not user_ids:
            return Response({"error": "Se requiere al menos un ID de usuario."},
                          status=status.HTTP_400_BAD_REQUEST)
        
        added_users = []
        errors = []
        
        for user_id in user_ids:
            try:
                user = User.objects.get(pk=user_id)
                if user not in group.user_set.all():
                    group.user_set.add(user)
                    added_users.append({
                        'id': user.id,
                        'username': user.username
                    })
                else:
                    errors.append(f"Usuario {user.username} ya pertenece al grupo.")
            except User.DoesNotExist:
                errors.append(f"Usuario con ID {user_id} no encontrado.")
        
        return Response({
            'message': f"Se añadieron {len(added_users)} usuarios al grupo.",
            'added_users': added_users,
            'errors': errors
        })
    
    elif request.method == 'DELETE':
        # Eliminar usuario(s) del grupo
        user_ids = request.data.get('user_ids', [])
        if not isinstance(user_ids, list):
            user_ids = [user_ids]
        
        if not user_ids:
            return Response({"error": "Se requiere al menos un ID de usuario."},
                          status=status.HTTP_400_BAD_REQUEST)
        
        removed_users = []
        errors = []
        
        for user_id in user_ids:
            try:
                user = User.objects.get(pk=user_id)
                if user in group.user_set.all():
                    group.user_set.remove(user)
                    removed_users.append({
                        'id': user.id,
                        'username': user.username
                    })
                else:
                    errors.append(f"Usuario {user.username} no pertenece al grupo.")
            except User.DoesNotExist:
                errors.append(f"Usuario con ID {user_id} no encontrado.")
        
        return Response({
            'message': f"Se eliminaron {len(removed_users)} usuarios del grupo.",
            'removed_users': removed_users,
            'errors': errors
        })
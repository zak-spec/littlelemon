from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from .serializers import Categoryserializer, MenuItemserializers, Cartserializers, Orderserializers, OrderItemserializers
from .models import Category, MenuItem, Cart, Order, OrderItem
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.contrib.auth.models import User, Group
from django.utils import timezone

def hello_world(request):
    return Response("Hello, world!")

@api_view(['GET','POST'])
# @permission_classes([AllowAny])  # Permitir acceso a todos para GET, pero POST requiere autenticación en configuración global
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
def menu_itemsbuscar(request, id):
    item = get_object_or_404(MenuItem, id=id)
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
@permission_classes([IsAuthenticated]) 
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
def get_order_items(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
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
def update_order(request, order_id):
    if not request.user.groups.filter(name="Manager").exists():
        return Response({"error": "Acceso no autorizado."}, status=status.HTTP_403_FORBIDDEN)
    order = get_object_or_404(Order, pk=order_id)
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
def update_order_status_delivery(request, order_id):
    if not request.user.groups.filter(name="Delivery_crew").exists():
        return Response({"error": "Acceso no autorizado."}, status=status.HTTP_403_FORBIDDEN)
    order = get_object_or_404(Order, pk=order_id)
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
def delete_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
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
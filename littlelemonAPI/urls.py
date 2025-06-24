from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token
urlpatterns = [
    path('register/', views.register_user, name="register_user"),
    path('users/users/me/', views.current_user, name="current_user"),
    path('secret/', views.secretv2, name="secreto"),
    path('throttle-check/', views.throttle_check, name="throttle_check"),  # Asegurando que la URL es correcta
    path("throttle-check-auth/", views.throttle_check_auth, name="throttle_check_auth"),
    path('token-auth/', obtain_auth_token, name="api_token_auth"),
    # Rutas para menú
    path('menu-items/', views.menu_items, name="menu_items"),
    path('menu-items/<str:pk>/', views.menu_itemsbuscar, name="menu_item_detail"),
    
    # Rutas para categorías
    path('categories/', views.create_category, name="create_category"),
    path('categories/<int:pk>/', views.category_detail, name="category_detail"),
    
    # Rutas para usuarios
    path('users/', views.user_list, name="user_list"),
    path('users/<int:pk>/', views.user_detail, name="user_detail"),
    
    # Rutas para grupos
    path('groups/', views.group_list, name="group_list"),
    path('groups/<int:pk>/', views.group_detail, name="group_detail"),
    path('groups/<int:pk>/users/', views.group_users, name="group_users"),
    path('groups/manager/users/', views.get_managers, name="get_managers"),
    path('groups/manager/users/<str:userId>/', views.remove_from_manager_group, name="remove_manager"),
    path('groups/delivery-crew/users/', views.get_delivery_crew, name="get_delivery_crew"),
    path('groups/delivery-crew/users/<str:userId>/', views.remove_from_delivery_crew, name="remove_delivery_crew"),
    
    # Rutas para carrito
    path('cart/menu-items/', views.view_cart, name="view_cart"),
    path('cart/menu-items/<int:pk>/', views.cart_item_detail, name="cart_item_detail"),
    path('cart/menu-items/add/', views.add_to_cart, name="add_to_cart"),
    path('cart/menu-items/clear/', views.clear_cart, name="clear_cart"),
    
    # Rutas para pedidos
    path('orders/', views.view_orders, name="view_orders"),
    path('orders/create/', views.create_order, name="create_order"),
    path('orders/<int:pk>/', views.get_order_items, name="get_order_items"),
    path('orders/all/', views.view_all_orders, name="view_all_orders"),
    path('orders/<int:pk>/update/', views.update_order, name="update_order"),
    path('orders/<int:pk>/delete/', views.delete_order, name="delete_order"),
    path('orders/delivery/', views.view_delivery_orders, name="view_delivery_orders"),
    path('orders/<int:pk>/status/', views.update_order_status_delivery, name="update_order_status_delivery"),
]
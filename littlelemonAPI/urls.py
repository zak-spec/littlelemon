from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token
urlpatterns = [    path('users/', views.create_user, name="create-user"),
    path('users/users/me/', views.current_user, name="current-user"),
    path('secret/', views.secretv2 , name="secreto"),
    path('throttle-check/', views.throttle_check, name="throttle-check"),  # Asegurando que la URL es correcta
    path("throttle-check-auth/", views.throttle_check_auth, name="throttle-check-auth"),
    path('token-auth/', obtain_auth_token, name="api-token-auth"),
    path('menu-items/', views.menu_items, name="menu-items"),
    path('menu-items/<str:id>/', views.menu_itemsbuscar, name="menu-item-detail"),    path('groups/manager/users/', views.get_managers, name="get-managers"),
    path('groups/manager/users/<str:userId>/', views.remove_from_manager_group, name="remove-manager"),
    path('groups/delivery-crew/users/', views.get_delivery_crew, name="get-delivery-crew"),
    path('groups/delivery-crew/users/<str:userId>/', views.remove_from_delivery_crew, name="remove-delivery-crew"),
    path('cart/menu-items/', views.view_cart, name="view-cart"),
    path('cart/menu-items/add/', views.add_to_cart, name="add-to-cart"),
    path('cart/menu-items/clear/', views.clear_cart, name="clear-cart"),
    path('orders/', views.view_orders, name="view-orders"),
    path('orders/create/', views.create_order, name="create-order"),
    path('orders/<int:order_id>/', views.get_order_items, name="get-order-items"),
    path('orders/all/', views.view_all_orders, name="view-all-orders"),
    path('orders/<int:order_id>/update/', views.update_order, name="update-order"),
    path('orders/<int:order_id>/delete/', views.delete_order, name="delete-order"),
    path('orders/delivery/', views.view_delivery_orders, name="view-delivery-orders"),    
    path('orders/<int:order_id>/status/', views.update_order_status_delivery, name="update-order-status-delivery"),
]
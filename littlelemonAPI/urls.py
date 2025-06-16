from django.urls import path
from . import views

urlpatterns = [
     path('users/', views.create_user),
    path('users/users/me/', views.current_user),
    # path('token/login/', obtain_auth_token),
    path('menu-items/', views.menu_items),
    path('menu-items/<str:id>/', views.menu_itemsbuscar),
    path('groups/manager/users/', views.get_managers),
    path('groups/manager/users/<str:userId>/', views.remove_from_manager_group),
    path('groups/delivery-crew/users/', views.get_delivery_crew),
    path('groups/delivery-crew/users/<str:userId>/', views.remove_from_delivery_crew),
    path('cart/menu-items/', views.view_cart),
    path('cart/menu-items/add/', views.add_to_cart),
    path('cart/menu-items/clear/', views.clear_cart),
    path('orders/', views.view_orders),
    path('orders/create/', views.create_order),
    path('orders/<str:orderId>/', views.get_order_items),
    path('orders/all/', views.view_all_orders),
    path('orders/<str:orderId>/update/', views.update_order),
    path('orders/<str:orderId>/delete/', views.delete_order),
    path('orders/delivery/', views.view_delivery_orders),
    path('orders/<str:orderId>/status/', views.update_order_status_delivery),
]
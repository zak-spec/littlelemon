from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import views

# Crear router para ViewSets
router = DefaultRouter()

# Registrar ViewSets con el router
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'menu-items', views.MenuItemViewSet, basename='menuitem')
router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'groups', views.GroupViewSet, basename='group')
router.register(r'utils', views.UtilityViewSet, basename='utils')

urlpatterns = [
    # ========================= RUTAS DEL ROUTER =========================
    # Todas las rutas de ViewSets se incluyen automáticamente
    path('', include(router.urls)),
    
    # ========================= RUTAS ADICIONALES =========================
    
    # Autenticación
    path('token-auth/', obtain_auth_token, name='api_token_auth'),
    
    # Registro de usuarios (mantiene compatibilidad con FBV)
    path('register/', views.register_user, name='register_user'),
    
    # ========================= RUTAS PERSONALIZADAS DE VIEWSETS =========================
    # Las siguientes rutas son ejemplos de cómo acceder a acciones personalizadas de ViewSets:
    
    # Categories ViewSet
    # GET,POST    /api/categories/                     - Listar/crear categorías
    # GET,PUT,DELETE /api/categories/{id}/             - Detalle/actualizar/eliminar categoría
    
    # MenuItems ViewSet  
    # GET,POST    /api/menu-items/                     - Listar/crear items del menú
    # GET,PUT,DELETE /api/menu-items/{id}/             - Detalle/actualizar/eliminar item
    
    # Cart ViewSet
    # GET,POST    /api/cart/                           - Ver/añadir items al carrito
    # GET,PUT,DELETE /api/cart/{id}/                   - Detalle/actualizar/eliminar item del carrito
    # DELETE      /api/cart/clear/                     - Vaciar carrito
    # POST        /api/cart/add_item/                  - Añadir item específico al carrito
    
    # Orders ViewSet
    # GET,POST    /api/orders/                         - Ver/crear órdenes
    # GET,PUT,DELETE /api/orders/{id}/                 - Detalle/actualizar/eliminar orden
    # PATCH       /api/orders/{id}/update_status/      - Actualizar estado de orden
    # PATCH       /api/orders/{id}/assign_crew/        - Asignar delivery crew
    # GET         /api/orders/{id}/items/              - Ver items de una orden
    
    # Users ViewSet
    # GET,POST    /api/users/                          - Listar/crear usuarios
    # GET,PUT,DELETE /api/users/{id}/                  - Detalle/actualizar/eliminar usuario
    # GET         /api/users/me/                       - Información del usuario actual
    # POST        /api/users/{id}/add_to_group/        - Añadir usuario a grupo
    # DELETE      /api/users/{id}/remove_from_group/   - Remover usuario de grupo
    
    # Groups ViewSet
    # GET,POST    /api/groups/                         - Listar/crear grupos
    # GET,PUT,DELETE /api/groups/{id}/                 - Detalle/actualizar/eliminar grupo
    # GET         /api/groups/{id}/users/              - Ver usuarios de un grupo
    
    # Utils ViewSet
    # GET         /api/utils/throttle_check/           - Test throttling anónimo
    # GET         /api/utils/throttle_check_auth/      - Test throttling autenticado
    # GET         /api/utils/secret/                   - Endpoint secreto
]

# ========================= RUTAS DISPONIBLES =========================
"""
ENDPOINTS PRINCIPALES:

AUTENTICACIÓN:
- POST   /api/token-auth/                   - Obtener token JWT
- POST   /api/register/                     - Registro de usuario

CATEGORÍAS:
- GET    /api/categories/                   - Listar categorías (paginado, filtrable)
- POST   /api/categories/                   - Crear categoría (solo managers)
- GET    /api/categories/{id}/              - Detalle de categoría
- PUT    /api/categories/{id}/              - Actualizar categoría (solo managers)
- DELETE /api/categories/{id}/              - Eliminar categoría (solo managers)

ELEMENTOS DEL MENÚ:
- GET    /api/menu-items/                   - Listar items (filtros: category, to_price, search)
- POST   /api/menu-items/                   - Crear item (solo managers)
- GET    /api/menu-items/{id}/              - Detalle de item
- PUT    /api/menu-items/{id}/              - Actualizar item (solo managers)
- DELETE /api/menu-items/{id}/              - Eliminar item (solo managers)

CARRITO:
- GET    /api/cart/                         - Ver carrito del usuario
- POST   /api/cart/                         - Añadir item al carrito
- GET    /api/cart/{id}/                    - Detalle de item en carrito
- PUT    /api/cart/{id}/                    - Actualizar cantidad
- DELETE /api/cart/{id}/                    - Eliminar item del carrito
- DELETE /api/cart/clear/                   - Vaciar carrito completo
- POST   /api/cart/add_item/                - Añadir item específico

ÓRDENES:
- GET    /api/orders/                       - Ver órdenes (filtrado por usuario/rol)
- POST   /api/orders/                       - Crear orden desde carrito
- GET    /api/orders/{id}/                  - Detalle de orden
- PUT    /api/orders/{id}/                  - Actualizar orden
- DELETE /api/orders/{id}/                  - Eliminar orden
- GET    /api/orders/{id}/items/            - Items de una orden específica
- PATCH  /api/orders/{id}/update_status/    - Actualizar estado (delivery crew/manager)
- PATCH  /api/orders/{id}/assign_crew/      - Asignar delivery crew (solo managers)

USUARIOS:
- GET    /api/users/                        - Listar usuarios (solo managers)
- POST   /api/users/                        - Crear usuario (registro abierto)
- GET    /api/users/{id}/                   - Detalle de usuario
- PUT    /api/users/{id}/                   - Actualizar usuario
- DELETE /api/users/{id}/                   - Desactivar usuario (solo staff)
- GET    /api/users/me/                     - Información del usuario actual
- POST   /api/users/{id}/add_to_group/      - Añadir a grupo (solo managers)
- DELETE /api/users/{id}/remove_from_group/ - Remover de grupo (solo managers)

GRUPOS:
- GET    /api/groups/                       - Listar grupos
- POST   /api/groups/                       - Crear grupo (solo staff)
- GET    /api/groups/{id}/                  - Detalle de grupo
- PUT    /api/groups/{id}/                  - Actualizar grupo (solo staff)
- DELETE /api/groups/{id}/                  - Eliminar grupo (solo staff)
- GET    /api/groups/{id}/users/            - Usuarios del grupo

UTILIDADES:
- GET    /api/utils/throttle_check/         - Test throttling anónimo
- GET    /api/utils/throttle_check_auth/    - Test throttling autenticado
- GET    /api/utils/secret/                 - Endpoint secreto para usuarios autenticados

FILTROS Y PARÁMETROS:
- ?page=N&page_size=N                      - Paginación en todos los endpoints
- ?search=texto                            - Búsqueda en campos específicos
- ?ordering=campo                          - Ordenamiento
- ?category=nombre                         - Filtro por categoría (menu-items)
- ?to_price=precio                         - Filtro por precio máximo (menu-items)
- ?status=estado                           - Filtro por estado (orders)
"""
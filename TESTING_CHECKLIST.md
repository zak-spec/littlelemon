# 🧪 CHECKLIST DE TESTING - API LITTLE LEMON

## 📋 Testing Checklist Completo

### ⚙️ Preparación del Entorno

- [ ] **Servidor ejecutándose**: `python manage.py runserver`
- [ ] **Base de datos migrada**: `python manage.py migrate`
- [ ] **Superusuario creado**: `python manage.py createsuperuser`
- [ ] **Grupos creados**: Manager, Delivery Crew
- [ ] **Token de prueba obtenido**: `/api/token-auth/`

---

## 🔐 Testing de Autenticación

### Obtener Token
- [ ] **POST** `/api/token-auth/` con credenciales válidas
- [ ] **POST** `/api/token-auth/` con credenciales inválidas
- [ ] Verificar formato de respuesta del token

### Usar Token
- [ ] Request con token válido en header
- [ ] Request con token inválido
- [ ] Request sin token cuando se requiere

---

## 📂 Testing de Categorías

### CRUD Completo
- [ ] **GET** `/api/categories/` (lista)
- [ ] **POST** `/api/categories/` (crear nueva)
- [ ] **GET** `/api/categories/{pk}/` (detalle)
- [ ] **PUT** `/api/categories/{pk}/` (actualizar completo)
- [ ] **PATCH** `/api/categories/{pk}/` (actualizar parcial)
- [ ] **DELETE** `/api/categories/{pk}/` (eliminar)

### Validaciones
- [ ] Crear categoría sin título (debe fallar)
- [ ] Crear categoría con título duplicado
- [ ] Eliminar categoría con menús asociados (debe fallar)

### Permisos
- [ ] Admin puede crear/editar/eliminar
- [ ] Manager puede crear/editar/eliminar
- [ ] Customer puede solo leer
- [ ] Usuario no autenticado puede leer

---

## 🍕 Testing de Menú

### Funcionalidad Existente
- [ ] **GET** `/api/menu-items/` (lista)
- [ ] **POST** `/api/menu-items/` (crear)
- [ ] **GET** `/api/menu-items/{title}/` (buscar por título)

### Validaciones
- [ ] Precio mínimo $2.00
- [ ] Título único
- [ ] Categoría válida (featured_id)

### Permisos
- [ ] Solo Admin/Manager pueden crear/editar
- [ ] Todos pueden leer

---

## 👥 Testing de Usuarios

### CRUD Completo
- [ ] **GET** `/api/users/` (lista con paginación)
- [ ] **GET** `/api/users/{pk}/` (detalle)
- [ ] **PUT** `/api/users/{pk}/` (actualizar completo)
- [ ] **PATCH** `/api/users/{pk}/` (actualizar parcial)
- [ ] **DELETE** `/api/users/{pk}/` (desactivar)

### Paginación y Filtrado
- [ ] **GET** `/api/users/?page=1&per_page=5`
- [ ] **GET** `/api/users/?search=john`
- [ ] **GET** `/api/users/?search=@example.com`

### Permisos
- [ ] Admin puede ver/editar todos los usuarios
- [ ] Manager puede ver/editar usuarios
- [ ] Usuario puede ver/editar solo su perfil
- [ ] Solo Admin puede desactivar usuarios

### Validaciones
- [ ] Email único
- [ ] Campos requeridos
- [ ] Protección de campos sensibles

---

## 👥 Testing de Grupos

### CRUD Completo
- [ ] **GET** `/api/groups/` (lista)
- [ ] **POST** `/api/groups/` (crear nuevo)
- [ ] **GET** `/api/groups/{pk}/` (detalle)
- [ ] **PUT** `/api/groups/{pk}/` (actualizar)
- [ ] **DELETE** `/api/groups/{pk}/` (eliminar)

### Gestión de Usuarios
- [ ] **POST** `/api/groups/{pk}/users/` (añadir usuarios)
- [ ] **DELETE** `/api/groups/{pk}/users/` (eliminar usuarios)

### Casos Especiales
- [ ] Añadir múltiples usuarios al grupo
- [ ] Intentar añadir usuario ya existente
- [ ] Eliminar usuario no existente del grupo

### Permisos
- [ ] Solo Admin puede crear/eliminar grupos
- [ ] Manager puede gestionar usuarios de grupos

---

## 🛒 Testing de Carrito

### Funcionalidad Existente
- [ ] **GET** `/api/cart/menu-items/` (ver carrito)
- [ ] **POST** `/api/cart/menu-items/add/` (añadir al carrito)
- [ ] **DELETE** `/api/cart/menu-items/clear/` (limpiar carrito)

### Nueva Funcionalidad
- [ ] **GET** `/api/cart/menu-items/{pk}/` (ítem específico)
- [ ] **PUT** `/api/cart/menu-items/{pk}/` (actualizar cantidad)
- [ ] **DELETE** `/api/cart/menu-items/{pk}/` (eliminar ítem)

### Validaciones
- [ ] Cantidad debe ser positiva
- [ ] MenuItem debe existir
- [ ] Usuario solo ve su carrito

### Casos de Negocio
- [ ] Añadir mismo ítem (debe actualizar cantidad)
- [ ] Precio se calcula correctamente
- [ ] Solo el propietario puede modificar

---

## 📦 Testing de Pedidos

### Funcionalidad Existente
- [ ] **GET** `/api/orders/` (mis pedidos)
- [ ] **POST** `/api/orders/create/` (crear desde carrito)
- [ ] **GET** `/api/orders/{pk}/` (detalles)
- [ ] **GET** `/api/orders/all/` (todos - Admin/Manager)
- [ ] **PUT** `/api/orders/{pk}/update/` (actualizar - Admin/Manager)
- [ ] **DELETE** `/api/orders/{pk}/delete/` (eliminar - Admin)
- [ ] **GET** `/api/orders/delivery/` (asignados - Delivery)
- [ ] **PATCH** `/api/orders/{pk}/status/` (actualizar estado - Delivery)

### Casos de Negocio
- [ ] Crear pedido con carrito vacío (debe fallar)
- [ ] Crear pedido limpia el carrito
- [ ] Estados de pedido válidos
- [ ] Asignación de delivery crew

### Permisos por Rol
- [ ] Customer: Solo sus pedidos
- [ ] Manager: Todos los pedidos, puede asignar
- [ ] Delivery: Solo pedidos asignados, cambiar estado
- [ ] Admin: Acceso completo

---

## 🔄 Testing de Grupos Específicos

### Managers
- [ ] **GET** `/api/groups/manager/users/`
- [ ] **DELETE** `/api/groups/manager/users/{userId}/`

### Delivery Crew
- [ ] **GET** `/api/groups/delivery-crew/users/`
- [ ] **DELETE** `/api/groups/delivery-crew/users/{userId}/`

---

## 🚨 Testing de Errores

### Códigos de Estado
- [ ] **200**: Operación exitosa
- [ ] **201**: Recurso creado
- [ ] **204**: Sin contenido
- [ ] **400**: Datos inválidos
- [ ] **401**: No autenticado
- [ ] **403**: Sin permisos
- [ ] **404**: No encontrado
- [ ] **500**: Error del servidor

### Mensajes de Error
- [ ] Errores descriptivos en español
- [ ] Formato JSON consistente
- [ ] Detalles de validación claros

---

## 📊 Testing de Performance

### Paginación
- [ ] Respuesta rápida con 1000+ registros
- [ ] Límites de paginación respetados
- [ ] Metadatos de paginación correctos

### Queries
- [ ] No queries N+1
- [ ] Índices funcionando
- [ ] Tiempos de respuesta < 200ms

---

## 🔒 Testing de Seguridad

### Autenticación
- [ ] Token expira correctamente
- [ ] Múltiples tokens por usuario
- [ ] Rate limiting funciona

### Autorización
- [ ] Usuarios no pueden acceder a datos ajenos
- [ ] Roles respetados estrictamente
- [ ] Escalación de privilegios bloqueada

### Validación
- [ ] Inyección SQL bloqueada
- [ ] XSS prevention funciona
- [ ] Datos sanitizados correctamente

---

## 📝 Testing de Documentación

### Endpoints Documentados
- [ ] Todos los endpoints en documentación
- [ ] Ejemplos de request/response
- [ ] Códigos de error explicados
- [ ] Permisos requeridos claros

### Ejemplos Funcionales
- [ ] Todos los curl examples funcionan
- [ ] Postman collection importable
- [ ] Variables de entorno configurables

---

## ✅ Checklist Final

### Pre-Producción
- [ ] Todos los tests pasan
- [ ] No errores en logs
- [ ] Performance aceptable
- [ ] Documentación completa
- [ ] Ejemplos verificados

### Entrega
- [ ] Código limpio y comentado
- [ ] Migraciones incluidas
- [ ] Requirements.txt actualizado
- [ ] README con instrucciones
- [ ] Documentación de API completa

---

## 🚀 Comandos de Testing Rápido

### Setup Inicial
```bash
# Instalar dependencias
pip install -r requirements.txt

# Migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Crear grupos
python manage.py shell
>>> from django.contrib.auth.models import Group
>>> Group.objects.create(name='Manager')
>>> Group.objects.create(name='Delivery Crew')
>>> exit()

# Ejecutar servidor
python manage.py runserver
```

### Testing con HTTPie
```bash
# Obtener token
http POST localhost:8000/api/token-auth/ username=admin password=admin123

# Test categoría
http GET localhost:8000/api/categories/ "Authorization:Token YOUR_TOKEN"
http POST localhost:8000/api/categories/ title="Test Category" "Authorization:Token YOUR_TOKEN"

# Test usuarios
http GET localhost:8000/api/users/ "Authorization:Token YOUR_TOKEN"
http GET localhost:8000/api/users/1/ "Authorization:Token YOUR_TOKEN"
```

---

**Nota**: Ejecutar este checklist completo antes de considerar la API lista para producción.

**Tiempo estimado**: 2-3 horas para testing completo
**Herramientas recomendadas**: Postman, HTTPie, Django Test Client

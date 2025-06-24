# Ejemplos de Uso - API Little Lemon

## 🔐 Autenticación

### Obtener Token
```bash
curl -X POST http://localhost:8000/api/token-auth/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "tu_usuario",
    "password": "tu_password"
  }'
```

**Respuesta:**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

### Usar Token en Requests
```bash
# Incluir en headers
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

## 📂 Categorías

### Crear Categoría
```bash
curl -X POST http://localhost:8000/api/categories/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{
    "title": "Bebidas"
  }'
```

### Obtener Categoría
```bash
curl -X GET http://localhost:8000/api/categories/1/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### Actualizar Categoría
```bash
curl -X PATCH http://localhost:8000/api/categories/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{
    "title": "Bebidas Refrescantes"
  }'
```

### Eliminar Categoría
```bash
curl -X DELETE http://localhost:8000/api/categories/1/ \
  -H "Authorization: Token YOUR_TOKEN"
```

## 🍕 Menú

### Listar Items del Menú
```bash
curl -X GET http://localhost:8000/api/menu-items/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### Crear Item del Menú (Solo Gerentes/Admin)
```bash
curl -X POST http://localhost:8000/api/menu-items/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{
    "title": "Pizza Margherita",
    "price": "15.99",
    "featured_id": 1
  }'
```

### Obtener Item Específico
```bash
curl -X GET http://localhost:8000/api/menu-items/pizza-margherita/ \
  -H "Authorization: Token YOUR_TOKEN"
```

## 👥 Usuarios

### Listar Usuarios (Solo Admin/Gerentes)
```bash
curl -X GET "http://localhost:8000/api/users/?page=1&per_page=10&search=john" \
  -H "Authorization: Token YOUR_TOKEN"
```

**Respuesta:**
```json
{
  "count": 25,
  "pages": 3,
  "current_page": 1,
  "results": [
    {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "groups": ["Customer"],
      "is_active": true
    }
  ]
}
```

### Obtener Usuario Específico
```bash
curl -X GET http://localhost:8000/api/users/1/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### Actualizar Usuario
```bash
curl -X PATCH http://localhost:8000/api/users/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{
    "first_name": "Johnny",
    "email": "johnny@example.com"
  }'
```

### Desactivar Usuario (Solo Admin)
```bash
curl -X DELETE http://localhost:8000/api/users/1/ \
  -H "Authorization: Token YOUR_TOKEN"
```

## 👥 Grupos

### Listar Grupos
```bash
curl -X GET http://localhost:8000/api/groups/ \
  -H "Authorization: Token YOUR_TOKEN"
```

**Respuesta:**
```json
[
  {
    "id": 1,
    "name": "Manager",
    "user_count": 3
  },
  {
    "id": 2,
    "name": "Delivery Crew",
    "user_count": 8
  }
]
```

### Crear Grupo (Solo Admin)
```bash
curl -X POST http://localhost:8000/api/groups/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{
    "name": "VIP Customers"
  }'
```

### Obtener Detalles del Grupo
```bash
curl -X GET http://localhost:8000/api/groups/1/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### Añadir Usuarios al Grupo
```bash
curl -X POST http://localhost:8000/api/groups/1/users/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{
    "user_ids": [5, 6, 7]
  }'
```

### Eliminar Usuarios del Grupo
```bash
curl -X DELETE http://localhost:8000/api/groups/1/users/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{
    "user_ids": [5, 6]
  }'
```

## 🛒 Carrito

### Ver Carrito
```bash
curl -X GET http://localhost:8000/api/cart/menu-items/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### Añadir al Carrito
```bash
curl -X POST http://localhost:8000/api/cart/menu-items/add/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{
    "menuitem": 1,
    "quantity": 2
  }'
```

### Obtener Item Específico del Carrito
```bash
curl -X GET http://localhost:8000/api/cart/menu-items/1/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### Actualizar Cantidad en Carrito
```bash
curl -X PUT http://localhost:8000/api/cart/menu-items/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{
    "quantity": 3
  }'
```

### Eliminar Item del Carrito
```bash
curl -X DELETE http://localhost:8000/api/cart/menu-items/1/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### Limpiar Carrito Completo
```bash
curl -X DELETE http://localhost:8000/api/cart/menu-items/clear/ \
  -H "Authorization: Token YOUR_TOKEN"
```

## 📦 Pedidos

### Ver Mis Pedidos
```bash
curl -X GET http://localhost:8000/api/orders/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### Crear Pedido desde Carrito
```bash
curl -X POST http://localhost:8000/api/orders/create/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{
    "note": "Sin cebolla, por favor"
  }'
```

### Obtener Detalles de Pedido
```bash
curl -X GET http://localhost:8000/api/orders/1/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### Ver Todos los Pedidos (Solo Gerentes/Admin)
```bash
curl -X GET http://localhost:8000/api/orders/all/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### Actualizar Pedido (Solo Gerentes/Admin)
```bash
curl -X PUT http://localhost:8000/api/orders/1/update/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{
    "status": "in_preparation",
    "delivery_crew": 3
  }'
```

### Ver Pedidos Asignados (Delivery Crew)
```bash
curl -X GET http://localhost:8000/api/orders/delivery/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### Actualizar Estado de Entrega
```bash
curl -X PATCH http://localhost:8000/api/orders/1/status/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{
    "status": "delivered"
  }'
```

### Eliminar Pedido (Solo Admin)
```bash
curl -X DELETE http://localhost:8000/api/orders/1/delete/ \
  -H "Authorization: Token YOUR_TOKEN"
```

## 🔄 Gestión de Grupos Específicos

### Gerentes

#### Obtener Lista de Gerentes
```bash
curl -X GET http://localhost:8000/api/groups/manager/users/ \
  -H "Authorization: Token YOUR_TOKEN"
```

#### Eliminar Gerente
```bash
curl -X DELETE http://localhost:8000/api/groups/manager/users/5/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### Repartidores

#### Obtener Lista de Repartidores
```bash
curl -X GET http://localhost:8000/api/groups/delivery-crew/users/ \
  -H "Authorization: Token YOUR_TOKEN"
```

#### Eliminar Repartidor
```bash
curl -X DELETE http://localhost:8000/api/groups/delivery-crew/users/8/ \
  -H "Authorization: Token YOUR_TOKEN"
```

## 🚨 Manejo de Errores

### Error de Autenticación
```json
{
  "detail": "Las credenciales de autenticación no se proveyeron."
}
```

### Error de Permisos
```json
{
  "error": "Acceso no autorizado."
}
```

### Error de Validación
```json
{
  "title": ["Este campo es requerido."],
  "price": ["Asegúrese de que este valor sea mayor o igual a 2."]
}
```

### Error 404
```json
{
  "detail": "No encontrado."
}
```

## 📊 Códigos de Estado HTTP

- **200 OK**: Operación exitosa
- **201 Created**: Recurso creado exitosamente
- **204 No Content**: Operación exitosa sin contenido
- **400 Bad Request**: Datos de entrada inválidos
- **401 Unauthorized**: No autenticado
- **403 Forbidden**: Sin permisos
- **404 Not Found**: Recurso no encontrado
- **500 Internal Server Error**: Error del servidor

## 🧪 Testing con Postman

### Configurar Environment
```
BASE_URL: http://localhost:8000/api
TOKEN: {{auth_token}}
```

### Collection de Requests
1. Importar ejemplos como collection
2. Configurar variables de entorno
3. Ejecutar tests en secuencia
4. Verificar respuestas y códigos de estado

---

**Nota**: Reemplaza `YOUR_TOKEN` con el token real obtenido del endpoint de autenticación.
**Puerto**: Ajusta el puerto según tu configuración local (8000 es el default de Django).

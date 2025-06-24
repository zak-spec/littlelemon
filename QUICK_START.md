# 🚀 Little Lemon API - Guía Rápida de ViewSets

## ⚡ Inicio Rápido

### 1. Ejecutar el servidor
```bash
python manage.py runserver
```

### 2. Probar la API
```bash
# Test completo de migración
python test_viewsets_migration.py

# O probar manualmente:
curl http://localhost:8000/api/menu-items/
```

---

## 📚 Endpoints Principales

### 🔐 Autenticación
```bash
# Registrar usuario
POST /api/register/
{
    "username": "usuario",
    "email": "email@example.com", 
    "password": "password123"
}

# Obtener token
POST /api/token-auth/
{
    "username": "usuario",
    "password": "password123"
}

# Usar token en headers
Authorization: Token <token>
```

### 🍕 Menu Items
```bash
# Listar (público)
GET /api/menu-items/

# Con filtros
GET /api/menu-items/?search=pizza&category=main&to_price=15.99&page=1&page_size=10

# Crear (solo managers)
POST /api/menu-items/
{
    "title": "Nueva Pizza",
    "price": "12.99",
    "featured": 1,
    "description": "Deliciosa pizza"
}
```

### 🛒 Carrito
```bash
# Ver carrito
GET /api/cart/

# Añadir item
POST /api/cart/add_item/
{
    "menu_item_id": 1,
    "quantity": 2
}

# Vaciar carrito
DELETE /api/cart/clear/
```

### 📦 Órdenes
```bash
# Ver mis órdenes
GET /api/orders/

# Crear orden desde carrito
POST /api/orders/

# Ver items de orden
GET /api/orders/1/items/

# Actualizar estado (delivery crew/manager)
PATCH /api/orders/1/update_status/
{
    "status": "delivered"
}
```

### 👥 Usuarios
```bash
# Mi perfil
GET /api/users/me/

# Listar usuarios (solo managers)
GET /api/users/

# Añadir a grupo (solo managers)
POST /api/users/1/add_to_group/
{
    "group_name": "Manager"
}
```

---

## 🔧 Características Técnicas

### Paginación
Todos los endpoints soportan:
- `?page=N` - Número de página
- `?page_size=N` - Items por página (máx. 100)

### Filtros Comunes
- `?search=texto` - Búsqueda de texto
- `?ordering=campo` - Ordenamiento
- `?ordering=-campo` - Ordenamiento descendente

### Respuestas Estándar
```json
// Lista paginada
{
    "count": 25,
    "next": "http://api/endpoint/?page=2",
    "previous": null,
    "results": [...]
}

// Error
{
    "error": "Mensaje de error",
    "details": "Información adicional"
}
```

---

## 🛡️ Permisos por Rol

| Endpoint | Anónimo | Usuario | Manager | Staff |
|----------|---------|---------|---------|-------|
| Menu Items (GET) | ✅ | ✅ | ✅ | ✅ |
| Menu Items (POST/PUT/DELETE) | ❌ | ❌ | ✅ | ✅ |
| Categories | ❌ | 👁️ | ✅ | ✅ |
| Cart | ❌ | ✅ | ✅ | ✅ |
| Orders | ❌ | 👤 | ✅ | ✅ |
| Users | ❌ | ❌ | ✅ | ✅ |

**Leyenda**: ✅ = Acceso completo, 👁️ = Solo lectura, 👤 = Solo propios recursos

---

## 🧪 Testing Rápido

### Script Automatizado
```bash
python test_viewsets_migration.py
```

### Tests Manuales con cURL
```bash
# Test servidor activo
curl http://localhost:8000/api/menu-items/

# Test con autenticación
curl -H "Authorization: Token <token>" \
     http://localhost:8000/api/cart/

# Test POST
curl -X POST \
     -H "Content-Type: application/json" \
     -H "Authorization: Token <token>" \
     -d '{"menu_item_id": 1, "quantity": 2}' \
     http://localhost:8000/api/cart/add_item/
```

---

## 🐛 Debugging

### Logs Útiles
```bash
# Ver logs de Django
python manage.py runserver --verbosity=2

# Verificar configuración
python manage.py check

# Ver rutas disponibles
python manage.py show_urls
```

### Errores Comunes
```bash
# Error 403: Sin permisos
# Solución: Verificar token y grupos del usuario

# Error 404: Endpoint no encontrado  
# Solución: Verificar URL (usar /api/ prefix)

# Error 400: Datos inválidos
# Solución: Revisar formato JSON y campos requeridos
```

---

## 🔗 URLs Útiles

- **API Base**: http://localhost:8000/api/
- **Admin**: http://localhost:8000/admin/
- **Documentación**: Ver `MIGRATION_SUMMARY.md`

---

**¿Necesitas ayuda?** Consulta el archivo `MIGRATION_SUMMARY.md` para documentación completa.

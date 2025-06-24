from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from decimal import Decimal
import uuid
from django.utils import timezone

class TimeStampedModel(models.Model):
    """
    Modelo abstracto que proporciona campos de auditoría de timestamp
    """
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Category(TimeStampedModel):
    """
    Categoría de productos del menú
    """
    slug = models.SlugField(unique=True, max_length=255)
    title = models.CharField(max_length=255, db_index=True, unique=True)
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['title']
        indexes = [
            # Índice para búsquedas rápidas por título
            models.Index(fields=['title'], name='idx_category_title_lookup'),
            # Índice para filtros por slug
            models.Index(fields=['slug'], name='idx_category_slug'),
            # Índice compuesto para ordenamiento optimizado
            models.Index(fields=['title', 'created_at'], name='idx_category_title_created'),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class MenuItem(TimeStampedModel):
    """
    Elemento del menú disponible para compra
    """
    title = models.CharField(max_length=255, db_index=True, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True, 
                              validators=[MinValueValidator(Decimal('0.01'))])
    featured = models.ForeignKey(Category, on_delete=models.PROTECT, 
                               related_name='menu_items')
    description = models.TextField(blank=True)
    available = models.BooleanField(default=True, db_index=True)
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Elemento del menú'
        verbose_name_plural = 'Elementos del menú'
        ordering = ['id']
        indexes = [
            # Índice para filtros de precio (usado en tu vista)
            models.Index(fields=['price'], name='idx_menuitem_price_filter'),
            # Índice para búsquedas por categoría (Category__title en tu código)
            models.Index(fields=['featured'], name='idx_menuitem_category'),
            # Índice compuesto para consultas por categoría y precio
            models.Index(fields=['featured', 'price'], name='idx_menuitem_category_price'),
            # Índice para búsquedas de texto en título (title__icontains)
            models.Index(fields=['title'], name='idx_menuitem_title_search'),
            # Índice para filtros de disponibilidad
            models.Index(fields=['available'], name='idx_menuitem_available'),
            # Índice compuesto para consultas complejas de filtrado
            models.Index(fields=['available', 'featured', 'price'], name='idx_menuitem_filters'),
            # Índice para ordenamiento por precio
            models.Index(fields=['-price'], name='idx_menuitem_price_desc'),
        ]
    
    def __str__(self):
        return f"{self.title} - ${self.price}"
    
    @property
    def is_on_sale(self):
        """Verificar si el precio está por debajo de $5.00"""
        return self.price < Decimal('5.00')

class Cart(TimeStampedModel):
    """
    Carrito de compras del usuario
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    MenuItem = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveSmallIntegerField(default=1, 
                                          validators=[MinValueValidator(1), MaxValueValidator(100)])
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    class Meta:
        verbose_name = 'Ítem de carrito'
        verbose_name_plural = 'Ítems de carrito'
        unique_together = ('MenuItem', 'user')
        ordering = ['-created_at']
        indexes = [
            # Índice principal para consultas de carrito por usuario (Cart.objects.filter(user=request.user))
            models.Index(fields=['user'], name='idx_cart_user'),
            # Índice compuesto para consultas específicas de usuario y item
            models.Index(fields=['user', 'MenuItem'], name='idx_cart_user_item'),
            # Índice para consultas por elemento del menú
            models.Index(fields=['MenuItem'], name='idx_cart_menuitem'),
            # Índice para ordenamiento temporal
            models.Index(fields=['user', '-created_at'], name='idx_cart_user_recent'),
        ]
    
    def __str__(self):
        return f"Carrito de {self.user.username}: {self.quantity}x {self.MenuItem.title}"
    
    def save(self, *args, **kwargs):
        """Actualiza el precio total al guardar"""
        if self.MenuItem:
            self.unit_price = self.MenuItem.price
            self.price = self.unit_price * Decimal(str(self.quantity))
        super().save(*args, **kwargs)

class OrderStatus(models.TextChoices):
    """Opciones de estado para órdenes"""
    PENDING = 'PENDING', 'Pendiente'
    PREPARING = 'PREPARING', 'En preparación'
    READY = 'READY', 'Listo para entrega'
    IN_DELIVERY = 'IN_DELIVERY', 'En entrega'
    DELIVERED = 'DELIVERED', 'Entregado'
    CANCELLED = 'CANCELLED', 'Cancelado'

class Order(TimeStampedModel):
    """
    Orden realizada por un usuario
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='orders')
    delivery_crew = models.ForeignKey(User, on_delete=models.SET_NULL, 
                                    related_name='delivery_orders', 
                                    null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        db_index=True
    )
    total = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateField(db_index=True, default=timezone.now)
    delivery_address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Orden'
        verbose_name_plural = 'Órdenes'
        ordering = ['-date', '-created_at']
        permissions = [
            ('can_assign_crew', 'Can assign delivery crew'),
            ('can_deliver', 'Can deliver orders'),
        ]
        indexes = [
            # Índice principal para consultas por usuario (Order.objects.filter(user=request.user))
            models.Index(fields=['user'], name='idx_order_user'),
            # Índice compuesto para consultas por usuario y fecha
            models.Index(fields=['user', '-date'], name='idx_order_user_date'),
            # Índice para consultas por estado (filtros de administración)
            models.Index(fields=['status'], name='idx_order_status'),
            # Índice para consultas de delivery crew (delivery_crew__isnull=False)
            models.Index(fields=['delivery_crew'], name='idx_order_delivery_crew'),
            # Índice compuesto para consultas complejas de delivery
            models.Index(fields=['status', 'delivery_crew'], name='idx_order_status_crew'),
            # Índice para consultas por fecha (reportes)
            models.Index(fields=['-date'], name='idx_order_date_desc'),
            # Índice compuesto para dashboard administrativo
            models.Index(fields=['status', '-date'], name='idx_order_status_date'),
            # Índice para órdenes activas (no entregadas ni canceladas)
            models.Index(fields=['user', 'status'], name='idx_order_user_status'),
        ]
    
    def __str__(self):
        return f"Orden {self.id} de {self.user.username} ({self.get_status_display()})"
    
    @property
    def is_delivered(self):
        return self.status == OrderStatus.DELIVERED
    
    @property
    def is_cancelled(self):
        return self.status == OrderStatus.CANCELLED
    
    @property
    def can_be_cancelled(self):
        """Una orden puede ser cancelada si no está en entrega o ya entregada"""
        return self.status not in [OrderStatus.IN_DELIVERY, OrderStatus.DELIVERED, OrderStatus.CANCELLED]
    
    def assign_crew(self, delivery_person, notes=None):
        """Asignar repartidor y actualizar estado"""
        self.delivery_crew = delivery_person
        if self.status == OrderStatus.READY:
            self.status = OrderStatus.IN_DELIVERY
        if notes:
            if self.notes:
                self.notes += f"\n{notes}"
            else:
                self.notes = notes
        self.save()
        # Crear un registro en el historial (modelo que puedes implementar después)
        # OrderStatusHistory.objects.create(order=self, status=self.status, notes=notes)
        return self

class OrderItem(TimeStampedModel):
    """
    Ítem específico dentro de una orden
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menuitem = models.ForeignKey(MenuItem, on_delete=models.PROTECT, related_name='order_items')
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    class Meta:
        verbose_name = 'Ítem de orden'
        verbose_name_plural = 'Ítems de orden'
        unique_together = ('order', 'menuitem')
        ordering = ['menuitem__title']
        indexes = [
            # Índice principal para consultas por orden (OrderItem.objects.filter(order=order))
            models.Index(fields=['order'], name='idx_orderitem_order'),
            # Índice para consultas por elemento del menú (análisis de popularidad)
            models.Index(fields=['menuitem'], name='idx_orderitem_menuitem'),
            # Índice compuesto para consultas específicas
            models.Index(fields=['order', 'menuitem'], name='idx_orderitem_order_menu'),
            # Índice para análisis de ventas por precio
            models.Index(fields=['menuitem', 'unit_price'], name='idx_orderitem_menu_price'),
        ]
    
    def __str__(self):
        return f"{self.quantity}x {self.menuitem.title} en orden {self.order.id}"
    
    def save(self, *args, **kwargs):
        """Actualiza el precio total al guardar"""
        if not self.unit_price and self.menuitem:
            self.unit_price = self.menuitem.price
        if not self.price:
            self.price = self.unit_price * self.quantity
        super().save(*args, **kwargs)

class OrderStatusHistory(TimeStampedModel):
    """
    Historial de cambios de estado de una orden
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, choices=OrderStatus.choices)
    notes = models.TextField(blank=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='status_changes')
    
    class Meta:
        verbose_name = 'Historial de estado'
        verbose_name_plural = 'Historiales de estado'
        ordering = ['-created_at']
        indexes = [
            # Índice principal para consultas por orden
            models.Index(fields=['order'], name='idx_history_order'),
            # Índice para consultas por estado (reportes)
            models.Index(fields=['status'], name='idx_history_status'),
            # Índice compuesto para auditoría
            models.Index(fields=['order', '-created_at'], name='idx_history_order_date'),
            # Índice para consultas por usuario que realizó el cambio
            models.Index(fields=['changed_by'], name='idx_history_changed_by'),
        ]
    
    def __str__(self):
        return f"Orden {self.order.id} cambió a {self.get_status_display()} el {self.created_at.strftime('%d/%m/%Y %H:%M')}"
from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem
from .Saneamiento import BleachCleanMixin
from rest_framework.validators import UniqueValidator
import bleach

class Categoryserializer(BleachCleanMixin, serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']

    def validate_title(self, value):
        return bleach.clean(value)

class MenuItemserializers(BleachCleanMixin, serializers.ModelSerializer):
    featured = Categoryserializer(read_only=True)
    featured_id = serializers.IntegerField(write_only=True)
    title = serializers.CharField(max_length=255, validators=[UniqueValidator(queryset=MenuItem.objects.all())])
    price = serializers.DecimalField(max_digits=6, decimal_places=2, min_value=2)
    
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'featured_id']

    def validate_title(self, value):
        return bleach.clean(value)

    def validate(self, attrs):
        attrs = self.clean_attrs(attrs)
        if attrs['price'] < 2:
            raise serializers.ValidationError('Price should not be less than 2.0')
        return super().validate(attrs)

class Cartserializers(BleachCleanMixin, serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'user', 'MenuItem', 'quantity', 'unit_price', 'price']

class Orderserializers(BleachCleanMixin, serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date']

class OrderItemserializers(BleachCleanMixin, serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'menuitem', 'quantity', 'unit_price', 'price']

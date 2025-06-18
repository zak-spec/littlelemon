from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Category(models.Model):
    slug=models.SlugField()
    title=models.CharField(max_length=255,db_index=True)
    
class MenuItem(models.Model):
    title=models.CharField(max_length=255,db_index=True)
    price=models.DecimalField(max_digits=6, decimal_places=2, db_index=True)  # modificado
    featured=models.ForeignKey(Category, on_delete=models.PROTECT)
    
    def __str__(self):
        return "title: "+self.title+" | price: "+str(self.price)+" | featured: "+self.featured.title
    
class Cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    MenuItem=models.ForeignKey(MenuItem,on_delete=models.CASCADE)
    quantity=models.SmallIntegerField(default=1)  # quitada la coma extra
    unit_price=models.DecimalField(max_digits=6,decimal_places=2)
    price=models.DecimalField(max_digits=6,decimal_places=2)
    
    class Meta:
        unique_together=('MenuItem','user')
    
class Order(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    delivery_crew=models.ManyToManyField(User, related_name="delivery_orders", blank=True)
    status=models.BooleanField(db_index=True,default=0)
    total=models.DecimalField(max_digits=6,decimal_places=2)
    date=models.DateField(db_index=True)
    
class OrderItem(models.Model):
    order=models.ForeignKey(Order, on_delete=models.CASCADE)  
    menuitem=models.ForeignKey(MenuItem,on_delete=models.CASCADE)
    quantity=models.SmallIntegerField()
    unit_price=models.DecimalField(max_digits=6,decimal_places=2)
    price=models.DecimalField(max_digits=6,decimal_places=2)
    
    class Meta:
        unique_together=('order','menuitem')
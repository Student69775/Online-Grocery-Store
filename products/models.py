from django.db import models
from django.contrib.auth.models import User, auth
from django.db.models import Sum
from decimal import Decimal

# Create your models here.

class Categorie(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    orderid = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255)
    price = models.FloatField()
    stock = models.IntegerField()
    category = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    # since url are of 2083 max characters
    image_url = models.ImageField(upload_to='Images/')

    @staticmethod
    def get_products_by_id(ids):
        return Product.objects.filter(id__in=ids)

    @staticmethod
    def get_all_products_by_categorieid(categorie_id):
        if categorie_id:
            return Product.objects.filter(category=categorie_id)
        else:
            return Product.objects.all()
    
    def __str__(self):
        return self.name

class Offer(models.Model):
    code = models.CharField(max_length=10)
    description = models.CharField(max_length=255)
    discount = models.FloatField()

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=250)
    phone = models.CharField(max_length=13)
    date = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_charge = models.DecimalField(max_digits=10, decimal_places=2, default=100)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    STATUS_CHOICES = [
        ('Order_Placed', 'Order Placed'),
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Order_Placed')

    def calculate_total_cost(self):
        total_price = self.orderitem_set.aggregate(total_price=Sum('price'))['total_price'] or Decimal('0.00')
        total_price += Decimal(str(self.shipping_charge))
        total_price += Decimal(str(self.price))
        return total_price

    def save(self, *args, **kwargs):
        # Calculate total cost before saving
        self.total_cost = self.calculate_total_cost()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id}"

    class Meta:
        db_table = 'products_order'
        verbose_name_plural = 'Orders'
        
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Define price as Decimal field

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

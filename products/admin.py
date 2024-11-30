from django.contrib import admin
# from django.db.models import Sum, Q
from .models import Product, Offer, Order, Categorie, OrderItem

class ProductAdmin(admin.ModelAdmin):
    list_display = ('orderid','name', 'price', 'stock', 'category')

class OfferAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount')

class OrderItemInline(admin.TabularInline):
    model = OrderItem

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'address', 'phone', 'date', 'status', 'total_price', 'shipping_charge', 'total_cost']
    inlines = [OrderItemInline, ]
    list_filter = ['date', 'status']

    def total_price(self, obj):
        # Calculate the total price for the order by summing the prices of all order items
        total_price = sum(item.price * item.quantity for item in obj.orderitem_set.all())
        return f"₹{total_price:.2f}"  # Format the total price as currency
    total_price.short_description = 'Total Price'

    def save_model(self, request, obj, form, change):
        # Calculate total cost before saving the order
        obj.calculate_total_cost()
        super().save_model(request, obj, form, change)

class CategorieAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

admin.site.register(Product, ProductAdmin)
admin.site.register(Offer, OfferAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Categorie, CategorieAdmin)


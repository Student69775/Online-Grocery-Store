from django.shortcuts import render, redirect, get_object_or_404
from .models import OrderItem, Product, Offer, Order, Categorie
from django.contrib import messages
from products.models import Order
from django.db import transaction
from django.contrib import messages
from django.http import HttpResponse

def index(request):
    cart = request.session.get('cart')

    if not cart:
        request.session['cart'] = {}

    categories = Categorie.objects.all()
    categorie_id = request.GET.get('categorie')
    if categorie_id:
        if categorie_id == "10":
            products = Product.objects.all()
        else:
            products = Product.get_all_products_by_categorieid(categorie_id)
    else:
        products = Product.objects.all()
    
    data = {'products': products, 'categories': categories}
    
    if request.method == 'POST':
        product_id = request.POST.get('product')
        product = Product.objects.get(pk=product_id)
        quantity = int(request.POST.get('quantity', 1))
        
        if product.stock < quantity:
            messages.error(request, f"{product.name} is out of stock.")
            print("Message added successfully:", f"{product.name} is out of stock.")
        else:
            if cart.get(product_id):
                if request.POST.get('remove'):
                    cart[product_id] -= 1  # Reduce quantity by 1
                    if cart[product_id] <= 0:
                        cart.pop(product_id)
                else:
                    cart[product_id] += quantity
            else:
                cart[product_id] = quantity
        
        request.session['cart'] = cart
        
        # Ensure to include messages in the context
        data['messages'] = messages.get_messages(request)
        print("Context data:", data)
    
    return render(request, 'index.html', data)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, Offer

def cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        requested_quantity = int(request.POST.get('quantity', 1))
        product = get_object_or_404(Product, pk=product_id)

        # DEBUGGING: Print product details
        print(f"Product: {product.name}, Requested Quantity: {requested_quantity}, Stock: {product.stock}")

        # Ensure requested quantity doesn't exceed available stock
        if requested_quantity > product.stock:
            requested_quantity = product.stock  # Adjust requested quantity to available stock

        cart = request.session.get('cart', {})
        current_quantity = cart.get(product_id, 0)
        # Update cart with the adjusted quantity or add the product with the adjusted quantity
        cart[product_id] = max(current_quantity, requested_quantity)
        request.session['cart'] = cart
        return redirect('cart')  # Redirect back to the cart page after adding the product

    else:
        codes = request.POST.get('getcode')
        offers = Offer.objects.all()
        ids = list(request.session.get('cart', {}).keys())
        products = Product.get_products_by_id(ids)
        return render(request, 'cart.html', {'products': products, 'offers': offers, 'codes': codes})

def track_order(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        try:
            order = Order.objects.get(id=order_id)
            order_items = OrderItem.objects.filter(order=order)  # Fetch associated OrderItems
            return render(request, 'track_order.html', {'order': order, 'order_items': order_items})
        except Order.DoesNotExist:
            error_message = 'Order not found. Please check your order ID.'
            return render(request, 'track_order.html', {'error_message': error_message})
    else:
        # Handle GET request (render the form)
        return render(request, 'track_order.html', {'show_form': True})

from django.db.models import F, Sum
from .models import Product, Order, OrderItem
from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib import messages
from decimal import Decimal
from django.contrib.auth.models import User
import traceback
import logging

logger = logging.getLogger(__name__)

@transaction.atomic
def thank_you(request):
    # Extensive logging and error checking
    try:
        # Verify POST method
        if request.method != 'POST':
            messages.warning(request, "Invalid access method.")
            return redirect('/')
        
        # Debug: Print entire session and POST data
        print("Session data:", request.session.items())
        print("POST data:", request.POST)

        # Check user authentication
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, "User not authenticated. Please log in.")
            return redirect('/login')

        # Validate input
        address = request.POST.get('address', '').strip()
        phone = request.POST.get('phone', '').strip()

        if not address:
            messages.warning(request, 'Please provide a shipping address.')
            return redirect('/products/cart/')
        
        if not phone or not (len(phone) == 10 and phone[0] in "7896"):
            messages.warning(request, 'Please enter a valid 10-digit phone number.')
            return redirect('/products/cart/')

        # Verify cart
        cart = request.session.get('cart', {})
        print("Cart contents:", cart)

        if not cart:
            messages.warning(request, 'Your cart is empty.')
            return redirect('/')

        # Find user
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('/login')

        # Prepare order details with extensive error checking
        total_price = Decimal('0.00')
        total_quantity = 0
        products_to_order = []

        # Validate products in cart
        for product_id, quantity in cart.items():
            try:
                product = Product.objects.select_for_update().get(id=product_id)
                
                # Validate stock
                if product.stock < quantity:
                    messages.warning(request, f'Insufficient stock for {product.name}')
                    return redirect('/products/cart/')
                
                # Calculate item total
                item_total = Decimal(str(product.price)) * Decimal(str(quantity))
                total_price += item_total
                total_quantity += quantity
                
                products_to_order.append((product, quantity, item_total))
            
            except Product.DoesNotExist:
                messages.error(request, f'Product {product_id} not found.')
                return redirect('/')

        # Calculate shipping and total
        shipping_charge = Decimal('100.00')
        total_cost = total_price + shipping_charge

        print(f"Total Price: {total_price}")
        print(f"Shipping Charge: {shipping_charge}")
        print(f"Total Cost: {total_cost}")

        # CRITICAL: Create order explicitly with all required fields
        try:
            order = Order.objects.create(
                user=user,
                address=address, 
                phone=phone, 
                quantity=total_quantity, 
                price=total_price,
                shipping_charge=shipping_charge,
                total_cost=total_cost,
                status='Order_Placed'  # Explicitly set default status
            )
            print(f"Order created with ID: {order.id}")
        except Exception as order_create_error:
            print(f"Order creation error: {order_create_error}")
            print(traceback.format_exc())
            messages.error(request, f"Failed to create order: {order_create_error}")
            return redirect('/products/cart/')

        # Create order items with error handling
        order_items = []
        try:
            for product, quantity, item_total in products_to_order:
                print(f"Creating OrderItem for Product: {product.name}, Quantity: {quantity}")
                order_item = OrderItem.objects.create(
                    order=order,  # Use the order we just created 
                    product=product, 
                    quantity=quantity, 
                    price=item_total
                )
                order_items.append(order_item)
                
                # Update product stock
                product.stock -= quantity
                product.save()
        except Exception as item_create_error:
            print(f"OrderItem creation error: {item_create_error}")
            print(traceback.format_exc())
            messages.error(request, f"Failed to create order items: {item_create_error}")
            return redirect('/products/cart/')

        # Clear cart
        request.session['cart'] = {}
        
        # Success message
        messages.success(request, f'Order placed successfully. Your order ID is {order.id}')
        return render(request, 'thank_you.html', {'order_id': order.id})

    except Exception as global_error:
        # Catch-all error handling
        print(f"Global error: {global_error}")
        print(traceback.format_exc())
        messages.error(request, f"An unexpected error occurred: {global_error}")
        return redirect('/products/cart/')
    


def order_details(request):
    # Your view logic here
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        shipping_charge = order.shipping_charge  # Get the shipping charge from the order
        return render(request, 'order_details.html', {'order': order, 'shipping_charge': shipping_charge})
    else:
        return render(request, 'order_details.html')
    
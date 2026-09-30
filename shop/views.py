import sys
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Product, CartItem, Order, OrderItem

# =========================================================================
# 🏠 HOME & PRODUCT CATALOG VIEWS
# =========================================================================

def product_list(request):
    """Renders the storefront index grid listing hardware catalog products."""
    products = Product.objects.all()
    return render(request, 'store.html', {'products': products})


def product_detail(request, product_id):
    """Renders the specific technical specs detail page layout sheet."""
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_detail.html', {'product': product})


# =========================================================================
# 🔐 SYSTEM ACCOUNT ACCESS AUTHENTICATION VIEWS
# =========================================================================

def login_user(request):
    """
    Validates log in request credentials and pushes error text strings
    to client-side JavaScript toast notifications upon validation failures.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}! Access granted.")
                return redirect('/')
        else:
            messages.error(request, "Access Denied: Invalid username or incorrect password.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'login.html', {'form': form})


def register_user(request):
    """Registers standard customer profiles safely into the database."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully! Welcome to Alpha Store.")
            return redirect('/')
        else:
            messages.error(request, "Registration rejected. Please verify requirement values.")
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


def logout_user(request):
    """Clears out active user profiles browser session identities cleanly."""
    logout(request)
    return redirect('/')


# =========================================================================
# 🛒 SINGLE-PAGE AJAX BASKET STATE MECHANICAL CONTROLS
# =========================================================================

def get_cart_totals(request):
    """Calculates active shopping items subtotals to sync async calculations."""
    total_price = 0.0
    items_count = 0
    item_data = {}

    if request.user.is_authenticated:
        db_items = CartItem.objects.filter(user=request.user)
        items_count = db_items.count()
        for item in db_items:
            sub = float(item.product.price) * int(item.quantity)
            total_price += sub
            item_data[str(item.product.id)] = {
                'quantity': item.quantity,
                'subtotal': f"{sub:.2f}"
            }
    else:
        cart = request.session.get('cart', {})
        for prod_id, qty in cart.items():
            try:
                prod_obj = Product.objects.get(id=int(prod_id))
                sub = float(prod_obj.price) * int(qty)
                total_price += sub
                items_count += 1
                item_data[str(prod_id)] = {
                    'quantity': int(qty),
                    'subtotal': f"{sub:.2f}"
                }
            except Product.DoesNotExist:
                continue

    return {
        'total_price': f"{total_price:.2f}",
        'items_count': items_count,
        'items': item_data
    }


def view_cart(request):
    """Natively renders layout elements inside the user basket table view."""
    items = []
    total_price = 0.0

    if request.user.is_authenticated:
        db_items = CartItem.objects.filter(user=request.user)
        for item in db_items:
            sub = float(item.product.price) * int(item.quantity)
            total_price += sub
            items.append({
                'product': item.product,
                'quantity': int(item.quantity),
                'subtotal': f"{sub:.2f}"
            })
    else:
        session_cart = request.session.get('cart', {})
        for prod_id, qty in session_cart.items():
            try:
                prod_obj = Product.objects.get(id=int(prod_id))
                sub = float(prod_obj.price) * int(qty)
                total_price += sub
                items.append({
                    'product': prod_obj,
                    'quantity': int(qty),
                    'subtotal': f"{sub:.2f}"
                })
            except (Product.DoesNotExist, ValueError):
                continue

    context = {
        'items': items,
        'total_price': f"{total_price:.2f}"
    }
    return render(request, 'cart.html', context)


def add_to_cart(request, product_id):
    """Appends chosen item lines into user baskets safely."""
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user, 
            product=product,
            defaults={'quantity': 1}
        )
        if not created:
            cart_item.quantity += 1
            cart_item.save()
    else:
        cart = request.session.get('cart', {})
        pid_str = str(product_id)
        cart[pid_str] = cart.get(pid_str, 0) + 1
        request.session['cart'] = cart
        request.session.modified = True

    return redirect('/cart/')


def increase_cart(request, product_id):
    """Increments the basket item quantity and returns clean JSON data."""
    if request.user.is_authenticated:
        cart_item = get_object_or_404(CartItem, user=request.user, product_id=product_id)
        cart_item.quantity += 1
        cart_item.save()
    else:
        cart = request.session.get('cart', {})
        pid_str = str(product_id)
        cart[pid_str] = cart.get(pid_str, 0) + 1
        request.session['cart'] = cart
        request.session.modified = True
            
    # 🚀 If it's a background fetch request, return JSON data directly
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return JsonResponse(get_cart_totals(request))
    return redirect('/cart/')


def decrease_cart(request, product_id):
    """Decrements the basket item quantity and returns clean JSON data."""
    removed = False
    if request.user.is_authenticated:
        cart_item = get_object_or_404(CartItem, user=request.user, product_id=product_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
            removed = True
    else:
        cart = request.session.get('cart', {})
        pid_str = str(product_id)
        if pid_str in cart:
            if cart[pid_str] > 1:
                cart[pid_str] -= 1
            else:
                del cart[pid_str]
                removed = True
            request.session['cart'] = cart
            request.session.modified = True
            
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        data = get_cart_totals(request)
        data['removed'] = removed
        return JsonResponse(data)
    return redirect('/cart/')


def remove_from_cart(request, product_id):
    """Completely purges an item row from the shopping basket."""
    if request.user.is_authenticated:
        CartItem.objects.filter(user=request.user, product_id=product_id).delete()
    else:
        cart = request.session.get('cart', {})
        pid_str = str(product_id)
        if pid_str in cart:
            del cart[pid_str]
            request.session['cart'] = cart
            request.session.modified = True
            
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return JsonResponse(get_cart_totals(request))
    return redirect('/cart/')
    """Completely purges item elements rows from active display panels."""
    if request.user.is_authenticated:
        CartItem.objects.filter(user=request.user, product_id=product_id).delete()
    else:
        cart = request.session.get('cart', {})
        pid_str = str(product_id)
        if pid_str in cart:
            del cart[pid_str]
            request.session['cart'] = cart
            request.session.modified = True
            
    return JsonResponse(get_cart_totals(request))


# =========================================================================
# 📦 OPERATIONS ADMIN CONTROL PANELS & PROFILE HISTORY LOGS
# =========================================================================

@login_required(login_url='login')
def customer_profile(request):
    """Retrieves transactional historical records for profiles safely."""
    raw_orders = Order.objects.filter(user=request.user).order_by('-id')
    orders_data = []
    
    for order in raw_orders:
        if hasattr(order, 'total_amount'):
            order_price = order.total_amount
        elif hasattr(order, 'total'):
            order_price = order.total
        elif hasattr(order, 'total_price'):
            order_price = order.total_price
        else:
            order_price = 0.00
            
        orders_data.append({
            'id': order.id,
            'price_display': f"{float(order_price):.2f}"
        })
        
    return render(request, 'profile.html', {'orders': orders_data})


@login_required(login_url='login')
def secret_admin_dashboard(request):
    """Operational Firewall Gatekeeper: Only passes merchant supervisors."""
    if not request.user.is_staff:
        return redirect('/')
    return render(request, 'admin_dashboard.html')


@login_required(login_url='login')
def checkout(request):
    """
    Compiles user baskets into final checkout objects, pre-resolves 
    pricing variables to guarantee template rendering stability.
    """
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        return redirect('/cart/')

    total_price = 0.0
    for item in cart_items:
        total_price += float(item.product.price) * int(item.quantity)

    order = Order(user=request.user)
    
    # Safely match whatever pricing field your Order schema uses
    if hasattr(order, 'total_price'):
        order.total_price = total_price
    elif hasattr(order, 'total_amount'):
        order.total_amount = total_price
    elif hasattr(order, 'total'):
        order.total = total_price
    else:
        try:
            order.total_amount = total_price
        except AttributeError:
            pass

    order.save()
    cart_items.delete()
    
    # 🚀 Pre-format total string to completely shield template compilation layers from crashes
    return render(request, 'order_success.html', {
        'order': order,
        'captured_charge': f"{total_price:.2f}"
    })
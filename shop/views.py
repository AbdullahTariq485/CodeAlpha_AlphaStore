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
    """Renders the storefront index grid listing products directly from database records."""
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
    """Validates login credentials and triggers client-side toast notifications on failures."""
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


# 🚀 ADD THIS IMPORT AT THE TOP OF shop/views.py:
from .forms import CustomRegistrationForm

# 🚀 OVERWRITE YOUR register_user VIEW FUNCTION EXACTLY LIKE THIS:
def register_user(request):
    """Registers standard customer profiles with a mandatory email field inside the database."""
    if request.method == 'POST':
        # Use our custom extended form layer instead of the default one
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account provisioned successfully! Welcome to Alpha Store.")
            return redirect('/')
        else:
            messages.error(request, "Registration rejected. Please verify form attributes.")
    else:
        form = CustomRegistrationForm()
    return render(request, 'register.html', {'form': form})

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
    """Increments table rows count and responds with flash-free async JSON values."""
    if product_id == 0:
        return JsonResponse(get_cart_totals(request))
        
    if request.user.is_authenticated:
        cart_item = get_object_or_404(CartItem, user=request.user, product_id=product_id)
        cart_item.quantity += 1
        cart_item.save()
    else:
        cart = request.session.get('cart', {})
        pid_str = str(product_id)
        if pid_str in cart:
            cart[pid_str] += 1
            request.session['cart'] = cart
            request.session.modified = True
            
    return JsonResponse(get_cart_totals(request))


def decrease_cart(request, product_id):
    """Decrements table rows count and responds with flash-free async JSON values."""
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
            
    data = get_cart_totals(request)
    data['removed'] = removed
    return JsonResponse(data)


def remove_from_cart(request, product_id):
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
    """Retrieves transactional history status straight from database rows."""
    raw_orders = Order.objects.filter(user=request.user).order_by('-id')
    orders_data = []
    
    for order in raw_orders:
        current_status = getattr(order, 'status', 'In Transit')
        
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
            'status': current_status,
            'price_display': f"{float(order_price):.2f}"
        })
        
    return render(request, 'profile.html', {'orders': orders_data})


@login_required(login_url='login')
# Locate your secret_admin_dashboard inside shop/views.py and replace it:

@login_required(login_url='login')
def secret_admin_dashboard(request):
    """
    Live Operational Staff Control Dashboard: Manages real-time fulfillment pipelines,
    revenue counts, and processes new product creation inputs directly into database columns.
    """
    if not request.user.is_staff:
        return redirect('/')
        
    # 🚀 REAL-WORLD FEATURE: Handle new product creation form entries
    if request.method == 'POST' and 'create_product_form' in request.POST:
        name = request.POST.get('prod_name')
        desc = request.POST.get('prod_desc')
        price = request.POST.get('prod_price')
        
        if name and desc and price:
            try:
                Product.objects.create(
                    name=name,
                    description=desc,
                    price=float(price),
                    in_stock=True
                )
                messages.success(request, f"Successfully listed new hardware element: {name}")
            except ValueError:
                messages.error(request, "Product creation rejected. Invalid numeric price format.")
            return redirect('/alpha-staff/')

    products = Product.objects.all()
    raw_orders = Order.objects.all().order_by('-id')
    
    gross_income = 0.0
    active_orders_data = []
    
    for order in raw_orders:
        if hasattr(order, 'total_amount'):
            price_val = order.total_amount
        elif hasattr(order, 'total'):
            price_val = order.total
        elif hasattr(order, 'total_price'):
            price_val = order.total_price
        else:
            price_val = 0.00
            
        gross_income += float(price_val)
        current_status = getattr(order, 'status', 'In Transit')
        
        if current_status == "Delivered":
            continue
            
        active_orders_data.append({
            'id': order.id,
            'user': order.user,
            'status': current_status,
            'price_display': f"{float(price_val):.2f}"
        })
        
    context = {
        'products': products,
        'live_orders': active_orders_data,
        'total_orders_count': len(active_orders_data),
        'gross_income': f"{gross_income:.2f}"
    }
    return render(request, 'admin_dashboard.html', context)

    """Live Operational Staff Control Dashboard: Pulls genuine database structures."""
    if not request.user.is_staff:
        return redirect('/')
        
    products = Product.objects.all()
    raw_orders = Order.objects.all().order_by('-id')
    
    gross_income = 0.0
    active_orders_data = []
    
    for order in raw_orders:
        if hasattr(order, 'total_amount'):
            price_val = order.total_amount
        elif hasattr(order, 'total'):
            price_val = order.total
        elif hasattr(order, 'total_price'):
            price_val = order.total_price
        else:
            price_val = 0.00
            
        gross_income += float(price_val)
        current_status = getattr(order, 'status', 'In Transit')
        
        if current_status == "Delivered":
            continue
            
        active_orders_data.append({
            'id': order.id,
            'user': order.user,
            'status': current_status,
            'price_display': f"{float(price_val):.2f}"
        })
        
    context = {
        'products': products,
        'live_orders': active_orders_data,
        'total_orders_count': len(active_orders_data),
        'gross_income': f"{gross_income:.2f}"
    }
    return render(request, 'admin_dashboard.html', context)


@login_required(login_url='login')
def staff_toggle_stock(request, product_id):
    """Toggles product catalog stock availability states globally inside database fields."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    product = get_object_or_404(Product, id=product_id)
    product.in_stock = not product.in_stock
    product.save()
    
    return JsonResponse({
        'success': True,
        'product_id': product.id,
        'in_stock': product.in_stock
    })


@login_required(login_url='login')
def staff_update_order(request, order_id):
    """Saves shipment log status modifications straight into the database order row."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        next_status = request.POST.get('status_update', 'In Transit')
        
        order.status = next_status
        order.save()
        
        return JsonResponse({
            'success': True,
            'order_id': order.id,
            'new_status': next_status
        })
        
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@login_required(login_url='login')
def checkout(request):
    """Compiles item elements selections into final checkout objects."""
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        return redirect('/cart/')

    total_price = 0.0
    for item in cart_items:
        total_price += float(item.product.price) * int(item.quantity)

    order = Order(user=request.user)
    order.status = 'In Transit'
    order.total_price = total_price
    order.save()
    
    cart_items.delete()
    
    return render(request, 'order_success.html', {
        'order': order,
        'captured_charge': f"{total_price:.2f}"
    })
@login_required(login_url='login')
def staff_edit_product(request, product_id):
    """
    Modifies product catalog records directly inside database columns.
    Handles title re-writes, price re-valuations, and real-time image updates.
    """
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        
        # Pull parameters straight from the incoming multi-part data payload
        product.name = request.POST.get('edit_name', product.name)
        product.description = request.POST.get('edit_desc', product.description)
        product.price = float(request.POST.get('edit_price', product.price))
        
        # 🚀 DATABASE RECORD UPLOADER: If a file stream is captured, commit it to DB
        if 'edit_image' in request.FILES:
            product.image = request.FILES['edit_image']
            
        product.save() # 💥 Permanent SQL Write Lock Commit
        
        return JsonResponse({
            'success': True,
            'product_id': product.id,
            'name': product.name,
            'price': f"{product.price:.2f}",
            'description': product.description
        })
        
    return JsonResponse({'error': 'Invalid request method'}, status=400)

    """Allows administrators to dynamically modify listed product specs, titles, prices, and images."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        
        # Grab updated fields from the AJAX payload
        product.name = request.POST.get('edit_name', product.name)
        product.description = request.POST.get('edit_desc', product.description)
        
        # 🚀 REAL-WORLD MEDIA HANDLE: Capture new image file stream updates if provided
        if 'edit_image' in request.FILES:
            product.image = request.FILES['edit_image']
        
        try:
            product.price = float(request.POST.get('edit_price', product.price))
            product.save()
            
            # Generate valid image URL string fallback if empty
            image_url = product.image.url if product.image else ""
            
            return JsonResponse({
                'success': True,
                'product_id': product.id,
                'name': product.name,
                'price': f"{product.price:.2f}",
                'description': product.description,
                'image_url': image_url  # Send new asset url back to browser
            })
        except ValueError:
            return JsonResponse({'error': 'Invalid numeric price format'}, status=400)
            
    return JsonResponse({'error': 'Invalid request method'}, status=400)

    """Allows administrators to dynamically modify listed product specs, titles, and prices."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        
        # Grab updated fields from the AJAX payload
        product.name = request.POST.get('edit_name', product.name)
        product.description = request.POST.get('edit_desc', product.description)
        
        try:
            product.price = float(request.POST.get('edit_price', product.price))
            product.save()
            return JsonResponse({
                'success': True,
                'product_id': product.id,
                'name': product.name,
                'price': f"{product.price:.2f}",
                'description': product.description
            })
        except ValueError:
            return JsonResponse({'error': 'Invalid numeric price format'}, status=400)
            
    return JsonResponse({'error': 'Invalid request method'}, status=400)

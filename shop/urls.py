from django.urls import path
from . import views

urlpatterns = [
    # 🏠 Catalog and Product Specs
    path('', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    
    # 🔐 Authentication Access Layer
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    
    # 📦 Profile Node and Operational Staff Center Portal Link Node
    path('profile/', views.customer_profile, name='customer_profile'),
    path('alpha-staff/', views.secret_admin_dashboard, name='secret_admin_dashboard'),
    path('alpha-staff/stock/<int:product_id>/', views.staff_toggle_stock, name='staff_toggle_stock'),
    path('alpha-staff/order/<int:order_id>/', views.staff_update_order, name='staff_update_order'),
    
    # 🛒 Basket Actions Matrix
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/increase/<int:product_id>/', views.increase_cart, name='increase_cart'),
    path('cart/decrease/<int:product_id>/', views.decrease_cart, name='decrease_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('alpha-staff/edit-product/<int:product_id>/', views.staff_edit_product, name='staff_edit_product'),

    
    # 💳 Order Processing Execution
    path('checkout/', views.checkout, name='checkout'),
]

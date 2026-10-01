from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('terms/', views.store_policy, {'page_key': 'terms'}, name='terms'),
    path('privacy/', views.store_policy, {'page_key': 'privacy'}, name='privacy'),
    path('shipping-returns/', views.store_policy, {'page_key': 'shipping'}, name='shipping_returns'),
    path('contact/', views.store_policy, {'page_key': 'contact'}, name='contact'),
    
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    
    path('profile/', views.customer_profile, name='customer_profile'),
    path('alpha-staff/', views.secret_admin_dashboard, name='secret_admin_dashboard'),
    path('alpha-staff/stock/<int:product_id>/', views.staff_toggle_stock, name='staff_toggle_stock'),
    path('alpha-staff/order/<int:order_id>/', views.staff_update_order, name='staff_update_order'),
    
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/increase/<int:product_id>/', views.increase_cart, name='increase_cart'),
    path('cart/decrease/<int:product_id>/', views.decrease_cart, name='decrease_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('alpha-staff/edit-product/<int:product_id>/', views.staff_edit_product, name='staff_edit_product'),

    
    path('checkout/', views.checkout, name='checkout'),
]

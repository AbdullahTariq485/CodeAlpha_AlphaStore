from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 🏠 Standard Django Core Administration Router Node
    path('admin/', admin.site.urls),
    
    # 🛒 Main Storefront App Routing Layer
    path('', include('shop.urls')),
]

# 🚀 INDUSTRY-STANDARD FALLBACK ROUTE: Force Django to serve local images automatically
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'shop' / 'static')

from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    in_stock = models.BooleanField(default=True)
    
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    @property
    def has_image(self):
        return bool(self.image and self.image.storage.exists(self.image.name))

    @property
    def category_key(self):
        name = self.name.lower()
        if any(term in name for term in ('mouse', 'keyboard', 'controller', 'webcam')):
            return 'peripherals'
        if any(term in name for term in ('monitor', 'display', 'screen')):
            return 'monitors'
        if any(term in name for term in ('audio', 'headset', 'speaker', 'microphone', 'mic')):
            return 'audio'
        return 'accessories'

    @property
    def category_label(self):
        return {
            'peripherals': 'Keyboards & mice',
            'monitors': 'Monitors & displays',
            'audio': 'Audio',
            'accessories': 'Desk accessories',
        }[self.category_key]

    def __str__(self):
        return self.name


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='In Transit')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order #{self.order.id})"

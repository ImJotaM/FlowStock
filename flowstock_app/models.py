from django.db import models
from django.contrib.auth.models import User

class StockMembership(models.Model):
    ROLE_VIEWER = 'viewer'
    ROLE_EDITOR = 'editor'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = [
        (ROLE_VIEWER, 'Visualizador'),
        (ROLE_EDITOR, 'Editor'),
        (ROLE_ADMIN, 'Administrador'),
    ]

    stock = models.ForeignKey('Stock', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default=ROLE_VIEWER)
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('stock', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.stock.name} ({self.get_role_display()})"



class Stock(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_stocks')
    name = models.CharField(max_length=100)

    members = models.ManyToManyField(
        User,
        through='StockMembership', 
        related_name='shared_stocks',
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
class Item(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='items')
    
    name = models.CharField(max_length=100)
    quantity_needed = models.PositiveIntegerField(default=1)
    quantity_available = models.PositiveIntegerField(default=1)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
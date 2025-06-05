from django.db import models
from django.contrib.auth.models import User

class Stock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)
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
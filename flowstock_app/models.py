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
    
class HistoricoEstoque(models.Model):
    TIPO_ALTERACAO_CHOICES = [
        ('ADI', 'Adição'),
        ('REM', 'Remoção'),
        ('EXC', 'Exclusão'),
        ('ATU', 'Atualização'),
    ]

    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='historicos')
    tipo_alteracao = models.CharField(max_length=3, choices=TIPO_ALTERACAO_CHOICES)
    item_afetado_nome = models.CharField(max_length=100)
    quantidade_alterada = models.IntegerField(default=0)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    data_hora = models.DateTimeField(auto_now_add=True)
    observacoes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_tipo_alteracao_display()} - {self.item_afetado_nome} ({self.data_hora})"
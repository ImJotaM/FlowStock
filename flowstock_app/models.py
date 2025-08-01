from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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

class StockGroupMembership(models.Model):
    stock = models.ForeignKey('Stock', on_delete=models.CASCADE)
    group = models.ForeignKey('UserGroup', on_delete=models.CASCADE)
    role = models.CharField(max_length=15, choices=StockMembership.ROLE_CHOICES, default=StockMembership.ROLE_VIEWER)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('stock', 'group')

    def __str__(self):
        return f"Grupo {self.group.name} -> Estoque {self.stock.name} ({self.get_role_display()})"

class Stock(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_stocks')
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, through='StockMembership', related_name='shared_stocks', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    shared_with_groups = models.ManyToManyField('UserGroup', through='StockGroupMembership', related_name='stocks_shared_with', blank=True)

    def __str__(self):
        return self.name
    
    def get_structured_permissions(self):
        permissions = []
        
        group_memberships = self.stockgroupmembership_set.select_related('group').prefetch_related(
            'group__members', 
            'group__subgroups__members'
        ).all()
        
        all_group_member_ids = set()

        for g_membership in group_memberships:
            group = g_membership.group
            member_details = []
            for member in group.members.all():
                all_group_member_ids.add(member.id)
                
                member_subgroups = [subgroup for subgroup in group.subgroups.all() if member in subgroup.members.all()]
                
                member_details.append({
                    'user': member,
                    'subgroups': member_subgroups
                })

            permissions.append({
                'type': 'group',
                'group_membership': g_membership,
                'member_details': sorted(member_details, key=lambda x: x['user'].username) # Ordena membros por nome
            })

        # 2. Busca membros individuais que NÃO estão em nenhum grupo já listado
        individual_memberships = self.stockmembership_set.select_related('user').exclude(user_id__in=all_group_member_ids)

        for membership in individual_memberships:
            if membership.user != self.owner:
                permissions.append({
                    'type': 'user',
                    'membership': membership
                })
        
        return permissions
    
class Item(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='items')
    
    name = models.CharField(max_length=100)
    quantity_needed = models.PositiveIntegerField(default=1)
    quantity_available = models.PositiveIntegerField(default=1)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_percentage(self):
        if self.quantity_needed == 0:
            return 100

        try:
            ratio = self.quantity_available / self.quantity_needed
        except ZeroDivisionError:
            return 100

        percentage = min(ratio * 100, 100)
        
        return int(percentage)
    
    def __str__(self):
        return self.name
    
    
class UserGroup(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_groups')
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='custom_groups', blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subgroups')

    def __str__(self):
        return f"{self.name} (Dono: {self.owner.username})"

    class Meta:
        unique_together = ('owner', 'name')
        
class History(models.Model):
    ACTION_CHOICES = [
        ('ITEM_CREATED', 'Criação de Item'),
        ('ITEM_UPDATED', 'Atualização de Item'),
        ('ITEM_DELETED', 'Exclusão de Item'),
        ('MEMBER_ADDED', 'Membro Adicionado'),
        ('MEMBER_REMOVED', 'Membro Removido'),
        ('MEMBER_ROLE_UPDATED', 'Permissão de Membro Atualizada'),
        ('GROUP_ADDED', 'Grupo Adicionado'),
        ('GROUP_REMOVED', 'Grupo Removido'),
        ('GROUP_ROLE_UPDATED', 'Permissão de Grupo Atualizada'),
    ]

    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='history_entries', verbose_name="Estoque")
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True, related_name='history_logs', verbose_name="Item Associado")
    item_name_snapshot = models.CharField(max_length=255, null=True, blank=True, verbose_name="Nome do Item (no momento da ação)")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuário")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="Data e Hora")
    action_type = models.CharField(max_length=30, choices=ACTION_CHOICES, verbose_name="Tipo de Ação")
    details = models.TextField(blank=True, null=True, verbose_name="Detalhes")

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Registro de Histórico"
        verbose_name_plural = "Registros de Histórico"

    def __str__(self):
        user_display = self.user.username if self.user else "Sistema"
        return f'{self.get_action_type_display()} em "{self.stock.name}" por {user_display}'
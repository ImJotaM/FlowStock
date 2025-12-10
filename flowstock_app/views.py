from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, update_session_auth_hash, logout
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Stock, Item, StockMembership, UserGroup, StockGroupMembership, History
from django.contrib.auth.models import User
from datetime import date
from django.http import HttpResponse
from django.contrib.staticfiles.finders import find
from django.urls import reverse
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from .forms import ShareStockForm
from urllib.parse import urlparse, urlunparse, urlencode, parse_qs
from decimal import Decimal, InvalidOperation
from django.utils import timezone
import locale

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        return redirect('login')

@login_required
def stock_list(request):
    
    view_filter = request.GET.get('view', 'my_stocks')
    search_query = request.GET.get('search', '')
    context = {
        'current_view': view_filter,
        'search_query': search_query,
        'all_user_groups': UserGroup.objects.filter(owner=request.user),
    }
    
    if view_filter == 'groups':
        groups_qs = UserGroup.objects.filter(
            Q(owner=request.user) | Q(members=request.user),
            parent=None
        ).distinct()
        
        search_query = request.GET.get('search', '')
        if search_query:
            groups_qs = groups_qs.filter(name__icontains=search_query)

        groups_qs = UserGroup.objects.filter(
            Q(owner=request.user) | Q(members=request.user),
            parent=None
        ).distinct()

        admin_count = UserGroup.objects.filter(owner=request.user, parent=None).count()

        subgroups_count = UserGroup.objects.filter(parent__in=groups_qs).count()

        members_count = sum(group.members.count() for group in groups_qs)

        context['groups'] = groups_qs
        context['admin_count'] = admin_count
        context['subgroups_count'] = subgroups_count
        context['members_count'] = members_count

    else: 
        if view_filter == 'shared':
            base_queryset = Stock.objects.filter(members=request.user).exclude(owner=request.user)
        else: 
            base_queryset = Stock.objects.filter(owner=request.user)

        if search_query:
            stock_queryset = base_queryset.filter(name__icontains=search_query).distinct().order_by('-created_at')
        else:
            stock_queryset = base_queryset.distinct().order_by('-created_at')

        stocks_with_values = []
        for stock in stock_queryset:
            total_value = sum(float(item.price) * item.quantity_available for item in stock.items.all())
            stock.total_value = f"{total_value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            stocks_with_values.append(stock)

        paginator = Paginator(stocks_with_values, 8)
        page_number = request.GET.get('page')
        stocks_page = paginator.get_page(page_number)

        user_memberships = StockMembership.objects.filter(
            user=request.user,
            stock__in=stocks_page.object_list
        ).values('stock_id', 'role')
        roles_map = {m['stock_id']: m['role'] for m in user_memberships}

        for stock in stocks_page:
            is_owner = (request.user == stock.owner)
            role = roles_map.get(stock.id)
            
            stock.user_can_edit = is_owner or (role in ['editor', 'admin'])
            stock.user_can_share = is_owner or (role == 'admin')
            stock.user_can_delete = is_owner
        
        context['stocks'] = stocks_page

    return render(request, 'flowstock/home.html', context)


@login_required
def create_stock(request):
    count = Stock.objects.filter(owner=request.user).count()
    stock = Stock.objects.create(owner=request.user, name=f"Estoque #{count + 1}")
    return redirect(f'{reverse("home")}?edit_id={stock.id}')

@login_required
def update_stock(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    membership = StockMembership.objects.filter(stock=stock, user=request.user).first()
    can_edit_name = (request.user == stock.owner) or (membership and membership.role in ['editor', 'admin'])

    if not can_edit_name:
         raise PermissionDenied("Você não tem permissão para alterar o nome deste estoque.")

    if request.method == 'POST':
        new_name = request.POST.get('name')
        new_description = request.POST.get('description', '')
        if new_name:
            stock.name = new_name
        stock.description = new_description
        stock.updated_at = timezone.now()  
        stock.save()

        view_on_page = request.POST.get('view', 'my_stocks')

        redirect_url = f"{reverse('home')}?view={view_on_page}"
        return redirect(redirect_url)

    return redirect('home')


@login_required
def delete_stock(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)

    if request.user != stock.owner:
        raise PermissionDenied("Apenas o dono pode excluir o estoque.")

    if request.method == 'POST':
        stock.members.clear()
        stock.items.all().delete()
        stock.delete()
        messages.info(request, 'Estoque excluído com sucesso!')
        
    return redirect('home')

@login_required
def faqs(request):
    return render(request, 'flowstock/faqs.html')


@login_required
def stock_detail(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    is_owner = (request.user == stock.owner)
    membership = StockMembership.objects.filter(stock=stock, user=request.user).first()
    
    if not is_owner and not membership:
        raise PermissionDenied("Você não tem permissão para acessar este estoque.")

    can_edit = is_owner or (membership and membership.role in ['editor', 'admin'])
    can_share = is_owner or (membership and membership.role == 'admin')

    if request.method == 'POST':
        if not can_edit:
            messages.error(request, "Você não tem permissão para modificar itens neste estoque.", extra_tags='danger')
            return redirect('stock_detail', stock_id=stock.id)

        if 'create' in request.POST:
            count = Item.objects.filter(stock=stock).count()
            item_name = f"Item #{count + 1}"    
            new_item = Item.objects.create(stock=stock, name=item_name, item_type='A definir')
            
            History.objects.create(
                stock=stock,
                user=request.user,
                action_type='ITEM_CREATED',
                item=new_item, 
                item_name_snapshot=new_item.name,
                details="O item foi adicionado ao estoque."
            )
            
            stock.updated_at = timezone.now()
            stock.save()
            messages.success(request, "Item criado com sucesso!")
        
        elif 'update_name' in request.POST:
            item_id = request.POST.get('update_name')
            item = Item.objects.filter(id=item_id, stock=stock).first()
            if item:
                old_name = item.name
                old_qty_available = item.quantity_available
                old_qty_needed = item.quantity_needed
                old_price = item.price
                old_item_type = item.item_type

                new_name = request.POST.get('name', old_name)
                new_qty_available = int(request.POST.get('quantity_available', old_qty_available))
                new_qty_needed = int(request.POST.get('quantity_needed', old_qty_needed))
                new_price = request.POST.get('price', old_price)
                new_item_type = request.POST.get('item_type', old_item_type)
                
                try:
                    new_price = Decimal(new_price)
                except (InvalidOperation, TypeError):
                    new_price = Decimal('0.00')

                details_list = []
                if old_name != new_name:
                    details_list.append(f"Nome alterado de '{old_name}' para '{new_name}'.")
                if old_qty_available != new_qty_available:
                    details_list.append(f"Quantidade disponível alterada de {old_qty_available} para {new_qty_available}.")
                if old_qty_needed != new_qty_needed:
                    details_list.append(f"Quantidade máxima alterada de {old_qty_needed} para {new_qty_needed}.")
                if old_price != new_price:
                    details_list.append(f"Preço alterado de R$ {old_price:.2f} para R$ {new_price:.2f}.")
                if old_item_type != new_item_type:
                    details_list.append(f"Tipo alterado de '{old_item_type}' para '{new_item_type}'.")
                
                if details_list:
                    History.objects.create(
                        stock=stock,
                        user=request.user,
                        action_type='ITEM_UPDATED',
                        item=item,
                        item_name_snapshot=new_name, 
                        details=" ".join(details_list)
                    )
                    item.name = new_name
                    item.quantity_available = new_qty_available
                    item.quantity_needed = new_qty_needed
                    item.price = new_price
                    item.item_type = new_item_type
                    item.save()
                    
                    stock.updated_at = timezone.now()
                    stock.save()
                    messages.success(request, "Item atualizado com sucesso!")

        elif 'delete_id' in request.POST:
            item_id = request.POST.get('delete_id')
            item = Item.objects.filter(id=item_id, stock=stock).first()
            if item:    
                item_name_before_delete = item.name
                History.objects.create(
                    stock=stock,
                    user=request.user,
                    action_type='ITEM_DELETED',
                    item_name_snapshot=item_name_before_delete,
                    details=f"O item foi removido permanentemente."
                )
                item.delete()
                
                stock.updated_at = timezone.now()
                stock.save()
                messages.info(request, "Item excluído com sucesso.")
        
        return redirect('stock_detail', stock_id=stock.id)
    
    items = stock.items.all()
    total_items = items.count()
    
    available_items = items.filter(quantity_available__gt=0).count()
    
    low_stock_items = 0
    for item in items:
        if item.quantity_needed > 0 and item.quantity_available < (item.quantity_needed / 2):
            low_stock_items += 1
    
    total_value = sum(float(item.price) * item.quantity_available for item in items)
    total_value = f"{total_value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    history_list = stock.history_entries.all().select_related('user')
    
    paginator = Paginator(history_list, 15)
    history_page = paginator.get_page(1)

    context = {
        'stock': stock,
        'items': items,
        'can_edit': can_edit,
        'can_share': can_share,
        'history_page': history_page,
        'available_items': available_items,
        'low_stock_items': low_stock_items,
        'total_value': total_value,  
    }
    return render(request, 'flowstock/estoque.html', context)

@login_required
def generate_pdf_stock(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)

    # Lógica de permissão
    if request.user != stock.owner and not stock.members.filter(id=request.user.id).exists():
        raise PermissionDenied("Você não tem permissão para gerar este PDF.")

    # --- 1. Configuração do Documento e Fontes ---
    response = HttpResponse(content_type='application/pdf')
    filename = f"estoque-{stock.name.replace(' ', '-').lower()}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'

    doc = SimpleDocTemplate(response, rightMargin=0.75*inch, leftMargin=0.75*inch, topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    # Tenta registrar as fontes customizadas, com fallback para Helvetica
    try:
        inter_regular_path = find('fonts/Inter-Regular.ttf')
        inter_bold_path = find('fonts/Inter-Bold.ttf')
        pdfmetrics.registerFont(TTFont('Inter', inter_regular_path))
        pdfmetrics.registerFont(TTFont('Inter-Bold', inter_bold_path))
        FONT_FAMILY = 'Inter'
        FONT_FAMILY_BOLD = 'Inter-Bold'
    except:
        FONT_FAMILY = 'Helvetica'
        FONT_FAMILY_BOLD = 'Helvetica-Bold'

    # --- 2. Definição de Cores e Estilos ---
    primary_color = HexColor('#0d6efd')
    text_color = HexColor('#212529')
    muted_color = HexColor('#6c757d')
    background_color = HexColor('#f8f9fa')

    styles = getSampleStyleSheet()
    # Usando nomes únicos para os novos estilos para evitar conflito.
    styles.add(ParagraphStyle(name='CustomTitle', fontName=FONT_FAMILY_BOLD, fontSize=22, leading=26, textColor=text_color, spaceAfter=4))
    styles.add(ParagraphStyle(name='CustomSubtitle', fontName=FONT_FAMILY, fontSize=11, leading=14, textColor=muted_color, spaceAfter=24))
    styles.add(ParagraphStyle(name='CustomTableHeader', fontName=FONT_FAMILY_BOLD, fontSize=9, textColor=primary_color, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='CustomTableCell', fontName=FONT_FAMILY, fontSize=9, textColor=text_color, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='CustomTableCellLeft', fontName=FONT_FAMILY, fontSize=9, textColor=text_color, alignment=TA_LEFT))

    # --- 3. Construção do Conteúdo do PDF ---
    story = []

    # Cabeçalho
    story.append(Paragraph(stock.name, styles['CustomTitle']))
    
    # CORREÇÃO: Define o locale para português para formatar a data corretamente
    try:
        # Tenta o padrão para Linux/macOS
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    except locale.Error:
        try:
            # Tenta o padrão para Windows
            locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
        except locale.Error:
            # Fallback caso nenhum locale funcione
            pass
            
    date_str = date.today().strftime('%d de %B de %Y')
    story.append(Paragraph(f"Relatório gerado em {date_str}", styles['CustomSubtitle']))

    # Preparação dos dados da tabela
    items = stock.items.all().order_by('name')
    
    header = [
        Paragraph('Item', styles['CustomTableHeader']),
        Paragraph('Disponível', styles['CustomTableHeader']),
        Paragraph('Necessário', styles['CustomTableHeader']),
        Paragraph('Faltante', styles['CustomTableHeader']),
        Paragraph('Progresso', styles['CustomTableHeader']),
    ]
    table_data = [header]

    for item in items:
        missing_quantity = item.quantity_needed - item.quantity_available
        missing_display = str(missing_quantity) if missing_quantity > 0 else '—'
        percentage = f"{item.get_percentage()}%" # Usa o método do modelo
        
        row = [
            Paragraph(item.name, styles['CustomTableCellLeft']),
            Paragraph(str(item.quantity_available), styles['CustomTableCell']),
            Paragraph(str(item.quantity_needed), styles['CustomTableCell']),
            Paragraph(missing_display, styles['CustomTableCell']),
            Paragraph(percentage, styles['CustomTableCell']),
        ]
        table_data.append(row)

    # Estilo da Tabela
    if items:
        pdf_table = Table(table_data, colWidths=[2.5*inch, 0.9*inch, 0.9*inch, 0.9*inch, 1.1*inch])
        
        table_style = TableStyle([
            # Estilos gerais
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),

            # Estilos do cabeçalho
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, primary_color),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

            # Estilos das linhas de dados
            ('LINEBELOW', (0, 1), (-1, -1), 0.5, muted_color),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'), # Centraliza colunas numéricas
        ])
        
        # Efeito "Zebra" (linhas alternadas)
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                table_style.add('BACKGROUND', (0, i), (-1, i), background_color)

        pdf_table.setStyle(table_style)
        story.append(pdf_table)
    else:
        story.append(Paragraph("Este estoque não possui nenhum item.", styles['Normal']))

    # Adiciona o logo no final do documento
    story.append(Spacer(1, 0.5*inch))
    
    logo_path = find('flowstock/resources/img/logo.jpg') 
    if logo_path:
        # Usando um tamanho mais sutil para o logo
        logo = Image(logo_path, width=2*inch, height=0.75*inch, hAlign='CENTER')
        story.append(logo)

    # --- 4. Geração do PDF ---
    doc.build(story)
    return response



@login_required
def share_stock(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    is_owner = (request.user == stock.owner)
    membership = StockMembership.objects.filter(stock=stock, user=request.user).first()
    can_share = is_owner or (membership and membership.role == 'admin')
    
    if not can_share:
        raise PermissionDenied("Você não tem permissão para gerenciar o compartilhamento.")

    if request.method == 'POST':
        action_type = None
        details = ""

        if 'add_member' in request.POST:
            form = ShareStockForm(request.POST)
            if form.is_valid():
                identifier = form.cleaned_data['identifier']
                role = request.POST.get('role')
                try:
                    user_to_add = User.objects.get(Q(username__iexact=identifier) | Q(email__iexact=identifier))
                    if user_to_add == request.user:
                        messages.warning(request, "Você não pode compartilhar o estoque com você mesmo.")
                    else:
                        membership, created = StockMembership.objects.update_or_create(
                            stock=stock, user=user_to_add, defaults={'role': role}
                        )
                        role_display = membership.get_role_display()
                        if created:
                            messages.success(request, f"{user_to_add.username} foi adicionado como {role_display}.")
                            action_type = 'MEMBER_ADDED'
                            details = f"Usuário '{user_to_add.username}' adicionado com a permissão de '{role_display}'."
                        else:
                            messages.info(request, f"A permissão de {user_to_add.username} foi atualizada para {role_display}.")
                            action_type = 'MEMBER_ROLE_UPDATED'
                            details = f"Permissão de '{user_to_add.username}' atualizada para '{role_display}'."
                except User.DoesNotExist:
                    messages.error(request, f"Usuário '{identifier}' não encontrado.", extra_tags='danger')

        elif 'remove_member' in request.POST:
            member_id = request.POST.get('member_id')
            member = get_object_or_404(User, id=member_id)
            StockMembership.objects.filter(stock=stock, user=member).delete()
            messages.info(request, "Membro removido do estoque.")
            action_type = 'MEMBER_REMOVED'
            details = f"Usuário '{member.username}' foi removido do estoque."
        
        elif 'update_role' in request.POST:
            member_id = request.POST.get('member_id')
            new_role = request.POST.get('role')
            member = get_object_or_404(User, id=member_id)
            membership = StockMembership.objects.filter(stock=stock, user=member).first()
            if membership:
                membership.role = new_role
                membership.save()
                role_display = membership.get_role_display()
                messages.success(request, "Permissão do membro atualizada.")
                action_type = 'MEMBER_ROLE_UPDATED'
                details = f"Permissão de '{member.username}' atualizada para '{role_display}'."

        elif 'add_group' in request.POST:
            group_id = request.POST.get('group_id')
            role = request.POST.get('role')
            if group_id:
                group = get_object_or_404(UserGroup, id=group_id, owner=request.user)
                StockGroupMembership.objects.update_or_create(stock=stock, group=group, defaults={'role': role})
                for member in group.members.all():
                    if member != request.user: 
                        StockMembership.objects.update_or_create(
                        stock=stock, 
                        user=member, 
                        defaults={'role': role}
                )
                messages.success(request, f"O grupo '{group.name}' foi adicionado com sucesso")
                action_type = 'GROUP_ADDED'
                details = f"Grupo '{group.name}' adicionado com a permissão de '{role}'."
        
        elif 'remove_group' in request.POST:
            group_membership_id = request.POST.get('group_membership_id')
            group_membership = get_object_or_404(StockGroupMembership, id=group_membership_id, stock=stock)
            group = group_membership.group
            group_name = group.name
            members_to_remove = group.members.all()
            StockMembership.objects.filter(stock=stock, user__in=members_to_remove).delete()
            group_membership.delete()
            messages.info(request, f"O compartilhamento com o grupo '{group_name}' foi removido.")
            action_type = 'GROUP_REMOVED'
            details = f"Compartilhamento com o grupo '{group_name}' foi removido."

        elif 'update_group_role' in request.POST:
            group_membership_id = request.POST.get('group_membership_id')
            new_role = request.POST.get('role')
            group_membership = get_object_or_404(StockGroupMembership, id=group_membership_id, stock=stock)
            group_membership.role = new_role
            group_membership.save()
            StockMembership.objects.filter(stock=stock, user__in=group_membership.group.members.all()).update(role=new_role)
            role_display = group_membership.get_role_display()
            messages.success(request, f"A permissão do grupo '{group_membership.group.name}' foi atualizada para {role_display}.")
            action_type = 'GROUP_ROLE_UPDATED'
            details = f"Permissão do grupo '{group_membership.group.name}' atualizada para '{role_display}'."

        if action_type and details:
            History.objects.create(stock=stock, user=request.user, action_type=action_type, details=details)
            stock.updated_at = timezone.now()
            stock.save()
        
        next_url = request.POST.get('next', reverse('home'))
        parsed_url = urlparse(next_url)
        query_params = parse_qs(parsed_url.query)
        query_params['modal'] = ['share']
        query_params['stock_id'] = [str(stock_id)]
        new_query_string = urlencode(query_params, doseq=True)
        redirect_url_parts = list(parsed_url)
        redirect_url_parts[4] = new_query_string
        redirect_url = urlunparse(redirect_url_parts)
        return redirect(redirect_url)
    
    referer_url = request.META.get('HTTP_REFERER', reverse('home'))
    return redirect(f"{referer_url}?modal=share&stock_id={stock_id}")

        

@login_required
def create_group(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        parent_id = request.POST.get('parent')

        if not name:
            messages.error(request, "O nome do grupo não pode ser vazio.")
            return redirect(reverse('home') + '?view=groups')

        if UserGroup.objects.filter(owner=request.user, name__iexact=name).exists():
            messages.error(request, f"Você já possui um grupo chamado '{name}'.")
            return redirect(reverse('home') + '?view=groups')

        parent = get_object_or_404(UserGroup, id=parent_id, owner=request.user) if parent_id else None
        new_group = UserGroup.objects.create(owner=request.user, name=name, parent=parent)
        new_group.members.add(request.user)  # Adiciona o criador como membro/administrador

        messages.success(request, f"Grupo '{name}' criado com sucesso.")
    return redirect(reverse('home') + '?view=groups')



@login_required
def update_group(request, group_id):
    group = get_object_or_404(UserGroup, id=group_id, owner=request.user)
    
    if request.method == 'POST':
        new_name = request.POST.get('name', '').strip()
        
        if not new_name:
            messages.error(request, "O nome do grupo não pode ser vazio.")
            return redirect(reverse('home') + '?view=groups')
        
        # Verifica se já existe outro grupo com esse nome
        if UserGroup.objects.filter(owner=request.user, name__iexact=new_name).exclude(id=group_id).exists():
            messages.error(request, f"Você já possui um grupo chamado '{new_name}'.")
            return redirect(reverse('home') + '?view=groups')
        
        group.name = new_name
        group.save()
        messages.success(request, f"Nome do grupo atualizado para '{new_name}'.")
    
    return redirect(reverse('home') + '?view=groups')



@login_required
def delete_group(request, group_id):
    group = get_object_or_404(UserGroup, id=group_id, owner=request.user)
    if request.method == 'POST':
        group.delete()
        messages.info(request, f"Grupo '{group.name}' e seus subgrupos foram excluídos.")
    return redirect(reverse('home') + '?view=groups')

@login_required
def delete_subgroup(request, subgroup_id):
    subgroup = get_object_or_404(UserGroup, id=subgroup_id)

    if subgroup.parent and subgroup.parent.owner == request.user:
        if request.method == 'POST':
            subgroup_name = subgroup.name
            subgroup.delete()
            messages.info(request, f"Subgrupo '{subgroup_name}' foi excluído com sucesso.")
        else:
            messages.warning(request, "Ação de exclusão inválida.")
    else:
        messages.error(request, "Você не tem permissão para excluir este subgrupo.")
        
    return redirect(reverse('home') + '?view=groups')


@login_required
def add_member_to_group(request, group_id):
    group = get_object_or_404(UserGroup, id=group_id)

    # ✅ Permitir apenas o dono adicionar
    if group.owner != request.user:
        messages.error(request, "Apenas o criador do grupo pode adicionar membros.")
        return redirect(reverse('home') + '?view=groups')

    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        
        if not identifier:
            messages.error(request, "Por favor, digite um e-mail ou nome de usuário.")
            return redirect(reverse('home') + '?view=groups')
        
        try:
            user_to_add = User.objects.get(
                Q(username__iexact=identifier) | Q(email__iexact=identifier)
            )
            
            if user_to_add in group.members.all():
                messages.warning(request, f"{user_to_add.username} já é membro deste grupo.")
            else:
                group.members.add(user_to_add)
                messages.success(request, f"{user_to_add.username} foi adicionado ao grupo '{group.name}'.")
                
        except User.DoesNotExist:
            messages.error(request, f"Usuário '{identifier}' não encontrado. Verifique o nome de usuário ou e-mail.")
    
    return redirect(reverse('home') + '?view=groups')



@login_required
def remove_member_from_group(request, group_id, user_id):
    group = get_object_or_404(UserGroup, id=group_id, owner=request.user)
    user_to_remove = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        group.members.remove(user_to_remove)
        messages.info(request, f"{user_to_remove.username} removido do grupo '{group.name}'.")
        
        stock_ids_shared_with_group = StockGroupMembership.objects.filter(group=group).values_list('stock_id', flat=True)
        if stock_ids_shared_with_group:
            StockMembership.objects.filter(stock_id__in=stock_ids_shared_with_group, user=user_to_remove).delete()
            messages.warning(request, f"O acesso de {user_to_remove.username} aos estoques compartilhados via este grupo foi revogado.")
        
    return redirect(reverse('home') + '?view=groups')


@login_required
def assign_subgroup_to_member(request, group_id, member_id):
    if request.method == 'POST':
        member = get_object_or_404(User, id=member_id)
        subgroup_id = request.POST.get('subgroup_id')
        
        if not subgroup_id:
            messages.error(request, "Nenhum subgrupo selecionado.")
            return redirect(reverse('home') + '?view=groups')

        subgroup = get_object_or_404(UserGroup, id=subgroup_id)
        parent_group = get_object_or_404(UserGroup, id=group_id, owner=request.user)

        if subgroup.parent == parent_group and parent_group.owner == request.user:
            subgroup.members.add(member)
            messages.success(request, f"Tag '{subgroup.name}' adicionada para {member.username}.")
        else:
            messages.error(request, "Operação inválida. Permissão negada ou grupo incorreto.")
            
    return redirect(reverse('home') + '?view=groups')

@login_required
def unassign_subgroup_from_member(request):
    if request.method == 'POST':
        member_id = request.POST.get('member_id')
        subgroup_id = request.POST.get('subgroup_id')
        
        member = get_object_or_404(User, id=member_id)
        subgroup = get_object_or_404(UserGroup, id=subgroup_id)

        if subgroup.parent and subgroup.parent.owner == request.user:
            subgroup.members.remove(member)
            messages.info(request, f"Tag '{subgroup.name}' removida de {member.username}.")
        else:
            messages.error(request, "Você não tem permissão para esta ação.")

    return redirect(reverse('home') + '?view=groups')


@login_required
def stock_history(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)

    is_owner = (request.user == stock.owner)
    membership = StockMembership.objects.filter(stock=stock, user=request.user).first()
    if not is_owner and not membership:
        raise PermissionDenied("Você não tem permissão para ver o histórico deste estoque.")

    history_list = stock.history_entries.all().select_related('user')
    
    paginator = Paginator(history_list, 20) 
    page_number = request.GET.get('page')
    history_page = paginator.get_page(page_number)

    context = {
        'stock': stock,
        'history_page': history_page
    }
    return render(request, 'flowstock/stock_history.html', context)


def landing_page(request):
    return render(request, 'flowstock/landing.html')

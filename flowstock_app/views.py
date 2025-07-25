from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, update_session_auth_hash, logout
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Stock, Item
from django.contrib.auth.models import User
from datetime import date
from django.http import HttpResponse
from django.contrib.staticfiles.finders import find
from django.urls import reverse
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from .forms import ShareStockForm
from django.http import JsonResponse

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.lib.units import inch

def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        return redirect('login')

@login_required
def stock_list(request):
    search_query = request.GET.get('search', '')
    
    stock_queryset = Stock.objects.filter(
        Q(owner=request.user) | Q(members=request.user)
    ).distinct().order_by('name')

    if search_query:
        stock_queryset = stock_queryset.filter(name__icontains=search_query)

    paginator = Paginator(stock_queryset, 8)
    page_number = request.GET.get('page')
    stocks_page = paginator.get_page(page_number)

    return render(request, 'flowstock/home.html', {
        'stocks': stocks_page,
    })


@login_required
def create_stock(request):
    count = Stock.objects.filter(owner=request.user).count()
    stock = Stock.objects.create(owner=request.user, name=f"Estoque #{count + 1}")
    return redirect(f'{reverse("home")}?edit_id={stock.id}')

@login_required
def update_stock(request, stock_id):
    new_name = request.POST.get('name')
    stock = Stock.objects.filter(id=stock_id, owner=request.user).first()

    if request.user != stock.owner:
        raise PermissionDenied("Apenas o dono do estoque pode alterar o nome.")

    if stock:
        stock.name = new_name
        stock.save()
    return redirect('home')


@login_required
def delete_stock(request, stock_id):

    stock = get_object_or_404(Stock, id=stock_id, owner=request.user)

    if request.user != stock.owner:
        raise PermissionDenied("Apenas o dono pode excluir o estoque.")

    if request.method == 'POST':
        stock.delete()
        messages.info(request, 'Estoque excluído com sucesso!')
    return redirect('home')

@login_required
def faqs(request):
    return render(request, 'flowstock/faqs.html')


@login_required
def stock_detail(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)

    if request.user != stock.owner and request.user not in stock.members.all():
            raise PermissionDenied("Você não tem permissão para acessar este estoque.")
    
    if request.method == 'POST':
        if 'create' in request.POST:
            count = Item.objects.filter(stock=stock).count()
            Item.objects.create(stock=stock, name=f"Item #{count + 1}")
            return redirect('stock_detail', stock_id=stock.id)
        elif 'update_name' in request.POST:
            item_id = request.POST.get('update_name')
            item = Item.objects.filter(id=item_id, stock=stock).first()
            if item:
                item.name = request.POST.get('name', item.name)
                try:
                    item.quantity_available = int(request.POST.get('quantity_available', item.quantity_available))
                except (ValueError, TypeError):
                    pass
                try:
                    item.quantity_needed = int(request.POST.get('quantity_needed', item.quantity_needed))
                except (ValueError, TypeError):
                    pass
                item.save()
            return redirect('stock_detail', stock_id=stock.id)
        elif 'delete_id' in request.POST:
            item_id = request.POST.get('delete_id')
            Item.objects.filter(id=item_id, stock=stock).delete()
            return redirect('stock_detail', stock_id=stock.id)

    return render(request, 'flowstock/estoque.html', {
        'stock': stock,
        'items': stock.items.all()
    })


@login_required
def generate_pdf_stock(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)

    if request.user != stock.owner and request.user not in stock.members.all():
        raise PermissionDenied("Você não tem permissão para gerar este PDF.")

    items = stock.items.all().order_by('name')

    response = HttpResponse(content_type='application/pdf')
    filename = f"lista-compra-{stock.name.replace(' ', '-').lower()}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    doc = SimpleDocTemplate(response, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
    
    story = []
    styles = getSampleStyleSheet()

    title_style = styles['h1']
    title_style.alignment = TA_LEFT
    story.append(Paragraph(f"Lista de compra - {stock.name}", title_style))
    
    date_str = date.today().strftime('%d/%m/%Y')
    date_style = styles['Normal']
    date_style.alignment = TA_LEFT
    story.append(Paragraph(f"Data de geração: {date_str}", date_style))
    
    story.append(Spacer(1, 0.4*inch))

    table_data = [
        ['Nome do item', 'Quantidade\ndisponível', 'Quantidade\nmáxima', 'Quantidade\nFaltante']
    ]
    for item in items:
        missing_quantity = item.quantity_needed - item.quantity_available
        missing_display = str(missing_quantity) if missing_quantity > 0 else '-'
        table_data.append([
            item.name,
            str(item.quantity_available),
            str(item.quantity_needed),
            missing_display
        ])

    pdf_table = Table(table_data)
    
    style = TableStyle([
        # Estilos do cabeçalho
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EEEEEE')),
        ('TEXTCOLOR',(0,0),(-1,0),colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        
        # Linhas horizontais
        ('LINEBELOW', (0,0), (-1,0), 1, colors.black),
        ('LINEBELOW', (0,1), (-1,-1), 0.5, colors.lightgrey),

        # Padding (espaçamento interno)
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ])
    
    pdf_table.setStyle(style)
    story.append(pdf_table)
    
    story.append(Spacer(0.5, 0.5*inch))
    
    logo_path = find('flowstock/resources/img/logo.jpg') 
    if logo_path:
        logo = Image(logo_path, width=4*inch, height=1.5*inch)
        logo.hAlign = 'CENTER'
        story.append(logo)

    doc.build(story)
    return response


@login_required
def share_stock(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)

    if request.user != stock.owner:
        raise PermissionDenied("Apenas o dono pode gerenciar o compartilhamento.")

    if request.method == 'POST':
        if 'add_member' in request.POST:
            form = ShareStockForm(request.POST)
            if form.is_valid():
                identifier = form.cleaned_data['identifier']
                try:
                    user_to_add = User.objects.get(
                        Q(username__iexact=identifier) | Q(email__iexact=identifier)
                    )
                    if user_to_add != stock.owner:
                        stock.members.add(user_to_add)
                        messages.success(request, f"Estoque compartilhado com {user_to_add.username}.")
                    else:
                        messages.warning(request, "Você não pode compartilhar o estoque com você mesmo.")
                except User.DoesNotExist:
                    messages.error(request, f"Usuário '{identifier}' não encontrado.")

        elif 'remove_member' in request.POST:
            member_id = request.POST.get('member_id')
            try:
                user_to_remove = User.objects.get(id=member_id)
                stock.members.remove(user_to_remove)
                messages.info(request, f"{user_to_remove.username} foi removido do estoque.")
            except User.DoesNotExist:
                messages.error(request, "Usuário a ser removido não encontrado.")
        
        return redirect(reverse('home') + f'?modal=share&stock_id={stock_id}')
    
    return redirect('home')  # Ou para onde sua página principal está
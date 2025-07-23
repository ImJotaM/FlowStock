from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, update_session_auth_hash, logout
from .forms import SignUpForm, LoginForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Stock, Item
from .forms import StockForm
from django.contrib.auth.models import User
from datetime import date
from django.http import HttpResponse
from django.contrib.staticfiles.finders import find


# Imports do ReportLab
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image # NOVO - Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_LEFT # NOVO - TA_LEFT
from reportlab.lib import colors
from reportlab.lib.units import inch

def root_redirect(request):
	if request.user.is_authenticated:
		return redirect('home')
	else:
		return redirect('login')

def register(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data.get('username')
			messages.success(request, f'Conta criada para {username}!')
			auth_login(request, user)
			return redirect('home')
	else:
		form = SignUpForm()
	return render(request, 'flowstock/register.html', {'form': form})

def login(request):
	if request.method == 'POST':
		form = LoginForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(request, username=username, password=password)
			if user is not None:
				auth_login(request, user)
				messages.success(request, f'Bem-vindo, {username}!')
				return redirect('home')
	else:
		form = LoginForm()
	return render(request, 'flowstock/login.html', {'form': form})

@login_required
def stock_list(request):
    search_query = request.GET.get('search', '')
    
    stock_queryset = Stock.objects.filter(user=request.user).order_by('name')

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
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            stock = form.save(commit=False)
            stock.user = request.user
            stock.save()
            messages.success(request, 'Estoque criado com sucesso!')
            return render(request, 'flowstock/estoque.html', {'stock': stock,'items': stock.items.all()})
    else:
        form = StockForm()
    
    return render(request, 'flowstock/estoque_form.html', {'form': form, 'title': 'Criar Novo Estoque'})


@login_required
def update_stock(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id, user=request.user)
    
    if request.method == 'POST':
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            messages.success(request, 'Estoque atualizado com sucesso!')
            return redirect('home')
    else:
        form = StockForm(instance=stock)

    return render(request, 'flowstock/estoque_form.html', {'form': form, 'title': f'Editando "{stock.name}"'})

@login_required
def delete_stock(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id, user=request.user)
    if request.method == 'POST':
        stock.delete()
        messages.info(request, 'Estoque excluído com sucesso!')
    return redirect('home')

@login_required
def account_detail(request):
    
	if request.method == 'POST':
		if 'delete_id' in request.POST:
			user_id = request.POST.get('delete_id')
			if request.user.id == int(user_id):
       
				logout(request)
				User.objects.filter(id=user_id).delete()
				messages.success(request, 'Sua conta foi excluída com sucesso.')
				return redirect('home')
			else:
				messages.error(request, 'Não foi possível excluir a conta.')
				return redirect('account_detail')

		field = request.POST.get('field')
		new_value = request.POST.get('new_value')
        
		if field == 'name':
			if new_value and len(new_value) > 0:
				request.user.username = new_value
				request.user.save()
				messages.success(request, 'Nome atualizado com sucesso!')
			else:
				messages.error(request, 'O nome não pode estar vazio')
				
		elif field == 'email':
			if not new_value or not new_value.strip():
				messages.error(request, 'O e-mail não pode estar vazio', extra_tags='redefining_email')
			elif new_value.strip() == request.user.email:
				messages.error(request, 'Digite um email diferente do atual', extra_tags='redefining_email')
			elif User.objects.exclude(pk=request.user.pk).filter(email=new_value.strip()).exists():
				messages.error(request, 'Este e-mail já está em uso por outra conta', extra_tags='redefining_email')
			else:
				request.user.email = new_value.strip()
				request.user.save()
				messages.success(request, 'E-mail atualizado com sucesso!', extra_tags='redefining_email')
			
		elif field == 'password':
			if new_value and len(new_value) >= 8:
				request.user.set_password(new_value)
				request.user.save()
				update_session_auth_hash(request, request.user)
				messages.success(request, 'Senha alterada com sucesso!')
			else:
				messages.error(request, 'A senha deve ter pelo menos 8 caracteres')
			
		return redirect('account_detail')
  
	return render(request, 'flowstock/conta.html')

@login_required
def faqs(request):
	return render(request, 'flowstock/faqs.html')

@login_required
def profiles(request):
	return render(request, 'flowstock/perfis.html')

@login_required
def stock_detail(request, stock_id):
	stock = get_object_or_404(Stock, id=stock_id, user=request.user)
    
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
    stock = get_object_or_404(Stock, id=stock_id, user=request.user)
    items = stock.items.all().order_by('name')

    response = HttpResponse(content_type='application/pdf')
    filename = f"lista-compra-{stock.name.replace(' ', '-').lower()}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    doc = SimpleDocTemplate(response, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
    
    story = []
    styles = getSampleStyleSheet()

    # --- ALTERADO: Alinhamento do Título e Data para a Esquerda ---
    title_style = styles['h1']
    title_style.alignment = TA_LEFT
    story.append(Paragraph(f"Lista de compra - {stock.name}", title_style))
    
    date_str = date.today().strftime('%d/%m/%Y')
    date_style = styles['Normal']
    date_style.alignment = TA_LEFT
    story.append(Paragraph(f"Data de geração: {date_str}", date_style))
    
    story.append(Spacer(1, 0.4*inch))

    # --- Sem alterações na preparação dos dados da tabela ---
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
    
    # --- ALTERADO: Novo estilo da tabela para combinar com a imagem ---
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
    
    # --- NOVO: Adicionando o logo no final ---
    story.append(Spacer(0.5, 0.5*inch))
    
    # Substitua 'images/seu_logo.png' pelo caminho correto dentro da sua pasta static
    logo_path = find('flowstock/resources/img/logo.jpg') 
    if logo_path:
        logo = Image(logo_path, width=4*inch, height=1.5*inch) # Ajuste as dimensões
        logo.hAlign = 'CENTER'
        story.append(logo)

    doc.build(story)
    return response
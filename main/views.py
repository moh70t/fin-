import os
from io import BytesIO
from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect, HttpResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from datetime import datetime
from main.models import Product, Cart, CartProduct
from main.forms import ContactForm, SignUpForm, AddToCartForm

def process_order(request):
    cart = get_object_or_404(Cart, user=request.user)
    
    # Créer un PDF de la commande
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    # Contenu du PDF
    elements = []
    
    # Ajouter le logo en haut à gauche
    logo_path = os.path.join(settings.BASE_DIR, 'static/img/logo.png')  # Chemin absolu vers le logo
    if os.path.exists(logo_path):
        elements.append(Paragraph('<img src="{}" width="100" height="100"/>'.format(logo_path), getSampleStyleSheet()['Heading1']))
    
    # Informations sur la commande
    elements.append(Paragraph('Facture ProForma', getSampleStyleSheet()['Heading1']))
    elements.append(Paragraph('Numéro de facture: {}'.format(cart.id), getSampleStyleSheet()['Normal']))
    elements.append(Paragraph('Date: {}'.format(datetime.now().strftime('%d/%m/%Y %H:%M:%S')), getSampleStyleSheet()['Normal']))
    elements.append(Paragraph('<br/><br/>', getSampleStyleSheet()['Normal']))  # Espacement

    # Détails du client
    user = request.user
    elements.append(Paragraph('Détails du client', getSampleStyleSheet()['Heading2']))
    elements.append(Paragraph('Nom: {}'.format(user.get_full_name()), getSampleStyleSheet()['Normal']))
    elements.append(Paragraph('Email: {}'.format(user.email), getSampleStyleSheet()['Normal']))
    elements.append(Paragraph('<br/><br/>', getSampleStyleSheet()['Normal']))  # Espacement
    
    # Tableau des produits commandés
    data = [['Quantité', 'Produit', 'Prix unitaire', 'Total']]
    total_price = 0
    
    for item in CartProduct.objects.filter(cart=cart):
        item_total = item.product.price * item.quantity
        total_price += item_total
        data.append([str(item.quantity), item.product.name, f"{item.product.price} FCFA", f"{item_total} FCFA"])
    
    # Ajouter le tableau au contenu
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alignement horizontal
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alignement vertical correct
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
    ])
    t = Table(data)
    t.setStyle(style)
    elements.append(t)
    
    # Ajouter le montant total en lettres
    montant_en_lettres = "Montant total à payer: {} FCFA".format(total_price)  # À remplacer par votre propre logique de conversion en lettres
    elements.append(Paragraph(montant_en_lettres, getSampleStyleSheet()['Normal']))
    elements.append(Paragraph('<br/><br/>', getSampleStyleSheet()['Normal']))  # Espacement
    
    # Ajouter les remerciements
    remerciements = "Nous vous remercions pour votre commande."
    elements.append(Paragraph(remerciements, getSampleStyleSheet()['Normal']))
    
    # Conditions de paiement
    elements.append(Paragraph('<br/><br/>', getSampleStyleSheet()['Normal']))  # Espacement
    conditions = "Conditions de paiement: Payable sous 30 jours."
    elements.append(Paragraph(conditions, getSampleStyleSheet()['Normal']))
    
    # Construire le PDF
    doc.build(elements)
    
    # Télécharger le PDF pour le client
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="facture_proforma.pdf"'
    
    # Supprimer le panier après la commande
    cart.delete()
    
    
    return response

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_product, created = CartProduct.objects.get_or_create(cart=cart, product=product)
    cart_product.quantity += 1
    cart_product.save()
    return redirect('product_list')

def add_to_cart_view(request, product_id):
    if request.user.is_authenticated:
        return add_to_cart(request, product_id)
    else:
        messages.warning(request, 'Veuillez vous connecter pour ajouter des produits au panier.')
        return redirect('nom_de_votre_page_de_connexion')

def index(request):
    return render(request, 'index.html')

def product(request):
    query = request.GET.get('q')
    category = request.GET.get('category', '')
    all_product = Product.objects.all().order_by('name')

    if query:
        all_product = all_product.filter(name__icontains=query)

    if category:
        all_product = all_product.filter(categorie=category)

    paginator = Paginator(all_product, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Product.objects.values_list('categorie', flat=True).distinct()

    return render(request, 'product.html', {'page_obj': page_obj, 'query': query, 'categories': categories, 'selected_category': category})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

def cart_detail(request):
    cart = get_object_or_404(Cart, user=request.user)
    return render(request, 'cart_detail.html', {'cart': cart})

def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_products = CartProduct.objects.filter(cart=cart)
    total_price = sum(item.product.price * item.quantity for item in cart_products)
    return render(request, 'checkout.html', {'cart_products': cart_products, 'total_price': total_price})

def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            
            # Envoi d'un email
            send_mail(
                f'Message de {name}',
                message,
                email,
                [settings.DEFAULT_FROM_EMAIL],
            )
            
            return render(request, 'contact.html', {'form': form, 'success': True})
    else:
        form = ContactForm()
    
    return render(request, 'contact.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    
    return render(request, 'registration/register.html', {'form': form})

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def terms_of_service(request):
    return render(request, 'terms_of_service.html')

def geolocalisations(request):
    return render(request, 'geolocalisations.html')

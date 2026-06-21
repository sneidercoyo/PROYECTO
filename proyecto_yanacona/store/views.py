from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Category, Artisan, Product, User, Order, OrderItem, Contact, CartItem


def home(request):
    featured = Product.objects.filter(active=True, featured=True)[:6]
    categories = Category.objects.all()
    artisans = Artisan.objects.filter(active=True)[:4]
    return render(request, 'store/home.html', {
        'featured_products': featured,
        'categories': categories,
        'artisans': artisans,
    })


def shop(request):
    products = Product.objects.filter(active=True)
    category_slug = request.GET.get('category')
    search = request.GET.get('search')
    sort = request.GET.get('sort')

    if category_slug:
        products = products.filter(category__slug=category_slug)
    if search:
        products = products.filter(Q(name__icontains=search) | Q(description__icontains=search))
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'name':
        products = products.order_by('name')

    categories = Category.objects.all()
    return render(request, 'store/shop.html', {
        'products': products,
        'categories': categories,
        'current_category': category_slug,
        'search': search,
        'sort': sort,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, active=True)
    related = Product.objects.filter(category=product.category, active=True).exclude(id=product.id)[:4]
    return render(request, 'store/product_detail.html', {
        'product': product,
        'related_products': related,
    })


def artisans(request):
    artisans_list = Artisan.objects.filter(active=True)
    return render(request, 'store/artisans.html', {'artisans': artisans_list})


def artisan_detail(request, slug):
    artisan = get_object_or_404(Artisan, slug=slug, active=True)
    products = Product.objects.filter(artisan=artisan, active=True)
    return render(request, 'store/artisan_detail.html', {
        'artisan': artisan,
        'products': products,
    })


def about(request):
    return render(request, 'store/about.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        Contact.objects.create(name=name, email=email, phone=phone, message=message)
        messages.success(request, "Mensaje enviado exitosamente!")
        return redirect('contact')
    return render(request, 'store/contact.html')


# =============================
# LOGIN WEB — CORREGIDO CON MÉTODOS DEL MODELO
# =============================
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email, active=True)
            if user.check_password(password):
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                request.session['user_role'] = user.role
                messages.success(request, f"Bienvenido, {user.name}!")
                return redirect('home')
            else:
                messages.error(request, "Contraseña incorrecta.")
        except User.DoesNotExist:
            messages.error(request, "Usuario no encontrado.")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    return render(request, 'store/login.html')


def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')

        if User.objects.filter(email=email).exists():
            messages.error(request, "El correo ya está registrado.")
            return redirect('register')

        user = User.objects.create(
            name=name, email=email, phone=phone,
            address=address, city=city
        )
        user.set_password(password)
        user.save()
        request.session['user_id'] = user.id
        request.session['user_name'] = user.name
        request.session['user_role'] = user.role
        messages.success(request, "Registro exitoso!")
        return redirect('home')
    return render(request, 'store/register.html')


def logout_view(request):
    request.session.flush()
    messages.success(request, "Sesión cerrada exitosamente.")
    return redirect('home')


def profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    user = get_object_or_404(User, id=user_id)
    orders = Order.objects.filter(user=user).order_by('-created_at')
    return render(request, 'store/profile.html', {'user': user, 'orders': orders})


def cart(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    items = CartItem.objects.filter(user_id=user_id).select_related('product')
    total = sum(item.subtotal() for item in items)
    return render(request, 'store/cart.html', {'items': items, 'total': total})


def add_to_cart(request, product_id):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Debes iniciar sesión para agregar al carrito.")
        return redirect('login')
    product = get_object_or_404(Product, id=product_id, active=True)
    quantity = int(request.POST.get('quantity', 1))
    item, created = CartItem.objects.get_or_create(user_id=user_id, product=product)
    if not created:
        item.quantity += quantity
    else:
        item.quantity = quantity
    item.save()
    messages.success(request, f"{product.name} agregado al carrito!")
    return redirect('cart')


def update_cart(request, item_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    item = get_object_or_404(CartItem, id=item_id, user_id=user_id)
    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0:
        item.quantity = quantity
        item.save()
    else:
        item.delete()
    return redirect('cart')


def remove_from_cart(request, item_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    item = get_object_or_404(CartItem, id=item_id, user_id=user_id)
    item.delete()
    messages.success(request, "Producto eliminado del carrito.")
    return redirect('cart')


def checkout(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    items = CartItem.objects.filter(user_id=user_id).select_related('product')
    if not items:
        messages.warning(request, "Tu carrito está vacío.")
        return redirect('cart')
    total = sum(item.subtotal() for item in items)
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        shipping_name = request.POST.get('shipping_name')
        shipping_address = request.POST.get('shipping_address')
        shipping_city = request.POST.get('shipping_city')
        shipping_phone = request.POST.get('shipping_phone')
        notes = request.POST.get('notes')

        order = Order.objects.create(
            user=user, total=total,
            shipping_name=shipping_name,
            shipping_address=shipping_address,
            shipping_city=shipping_city,
            shipping_phone=shipping_phone,
            notes=notes
        )
        for item in items:
            OrderItem.objects.create(
                order=order, product=item.product,
                product_name=item.product.name,
                price=item.product.price,
                quantity=item.quantity,
                subtotal=item.subtotal()
            )
            item.product.stock -= item.quantity
            item.product.save()
        items.delete()
        messages.success(request, f"Orden #{order.id} creada exitosamente!")
        return redirect('profile')

    return render(request, 'store/checkout.html', {
        'items': items, 'total': total, 'user': user
    })

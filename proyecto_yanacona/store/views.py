from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify
from .models import Category, Artisan, Product, User, Order, OrderItem, Contact, CartItem
from .decorators import admin_required, artisan_required


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
                if user.role == 'admin':
                    return redirect('admin_dashboard')
                if user.role == 'artisan':
                    return redirect('artisan_dashboard')
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


# =============================
# UTILIDADES
# =============================
def _unique_slug(model, base, instance_id=None):
    """Genera un slug único para el modelo dado."""
    base = slugify(base) or 'item'
    slug = base
    counter = 2
    qs = model.objects.all()
    if instance_id:
        qs = qs.exclude(id=instance_id)
    while qs.filter(slug=slug).exists():
        slug = f"{base}-{counter}"
        counter += 1
    return slug


# =============================
# PANEL DE ADMINISTRADOR
# =============================
@admin_required
def admin_dashboard(request):
    context = {
        'total_users': User.objects.count(),
        'total_products': Product.objects.count(),
        'total_orders': Order.objects.count(),
        'total_artisans': Artisan.objects.count(),
        'recent_orders': Order.objects.order_by('-created_at')[:5],
        'recent_users': User.objects.order_by('-created_at')[:5],
    }
    return render(request, 'store/admin_dashboard.html', context)


@admin_required
def admin_products(request):
    products = Product.objects.all().select_related('category', 'artisan')
    return render(request, 'store/admin_products.html', {'products': products})


@admin_required
def admin_add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug') or name
        category_id = request.POST.get('category') or None
        artisan_id = request.POST.get('artisan') or None
        Product.objects.create(
            name=name,
            slug=_unique_slug(Product, slug),
            description=request.POST.get('description', ''),
            price=request.POST.get('price') or 0,
            stock=request.POST.get('stock') or 0,
            category_id=category_id,
            artisan_id=artisan_id,
            featured='featured' in request.POST,
            active='active' in request.POST,
        )
        messages.success(request, "Producto creado exitosamente.")
        return redirect('admin_products')
    return render(request, 'store/admin_add_product.html', {
        'categories': Category.objects.all(),
        'artisans': Artisan.objects.all(),
    })


@admin_required
def admin_edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description', '')
        product.price = request.POST.get('price') or 0
        product.stock = request.POST.get('stock') or 0
        product.category_id = request.POST.get('category') or None
        product.artisan_id = request.POST.get('artisan') or None
        product.featured = 'featured' in request.POST
        product.active = 'active' in request.POST
        product.save()
        messages.success(request, "Producto actualizado.")
        return redirect('admin_products')
    return render(request, 'store/admin_edit_product.html', {
        'product': product,
        'categories': Category.objects.all(),
        'artisans': Artisan.objects.all(),
    })


@admin_required
def admin_artisans(request):
    artisans = Artisan.objects.all()
    return render(request, 'store/admin_artisans.html', {'artisans': artisans})


@admin_required
def admin_add_artisan(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug') or name
        email = request.POST.get('email')
        password = request.POST.get('password')

        linked_user = None
        # Si se proporcionan credenciales, se crea una cuenta de acceso de artesano.
        if email and password:
            if User.objects.filter(email=email).exists():
                messages.error(request, "Ya existe un usuario con ese correo.")
                return render(request, 'store/admin_add_artisan.html')
            linked_user = User(
                name=name, email=email, role='artisan',
                phone=request.POST.get('phone', ''),
            )
            linked_user.set_password(password)
            linked_user.save()

        Artisan.objects.create(
            name=name,
            slug=_unique_slug(Artisan, slug),
            bio=request.POST.get('bio', ''),
            specialty=request.POST.get('specialty', ''),
            active='active' in request.POST,
            user=linked_user,
        )
        messages.success(request, "Artesano creado exitosamente.")
        return redirect('admin_artisans')
    return render(request, 'store/admin_add_artisan.html')


@admin_required
def admin_edit_artisan(request, artisan_id):
    artisan = get_object_or_404(Artisan, id=artisan_id)
    if request.method == 'POST':
        artisan.name = request.POST.get('name')
        artisan.bio = request.POST.get('bio', '')
        artisan.specialty = request.POST.get('specialty', '')
        artisan.active = 'active' in request.POST
        artisan.save()
        messages.success(request, "Artesano actualizado.")
        return redirect('admin_artisans')
    return render(request, 'store/admin_edit_artisan.html', {'artisan': artisan})


@admin_required
def admin_categories(request):
    categories = Category.objects.all()
    return render(request, 'store/admin_categories.html', {'categories': categories})


@admin_required
def admin_add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug') or name
        Category.objects.create(
            name=name,
            slug=_unique_slug(Category, slug),
            description=request.POST.get('description', ''),
        )
        messages.success(request, "Categoría creada exitosamente.")
        return redirect('admin_categories')
    return render(request, 'store/admin_add_category.html')


@admin_required
def admin_edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.description = request.POST.get('description', '')
        category.save()
        messages.success(request, "Categoría actualizada.")
        return redirect('admin_categories')
    return render(request, 'store/admin_edit_category.html', {'category': category})


@admin_required
def admin_orders(request):
    orders = Order.objects.all().select_related('user')
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    return render(request, 'store/admin_orders.html', {
        'orders': orders, 'status_filter': status_filter,
    })


@admin_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            order.status = new_status
            order.save()
            messages.success(request, "Estado del pedido actualizado.")
        return redirect('admin_order_detail', order_id=order.id)
    items = OrderItem.objects.filter(order=order).select_related('product', 'product__artisan')
    return render(request, 'store/admin_order_detail.html', {'order': order, 'items': items})


@admin_required
def admin_users(request):
    users = User.objects.all()
    return render(request, 'store/admin_users.html', {'users': users})


@admin_required
def admin_edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.name = request.POST.get('name')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone', '')
        user.address = request.POST.get('address', '')
        user.city = request.POST.get('city', '')
        user.role = request.POST.get('role', user.role)
        user.active = 'active' in request.POST
        user.save()
        messages.success(request, "Usuario actualizado.")
        return redirect('admin_users')
    return render(request, 'store/admin_edit_user.html', {'user': user})


@admin_required
def admin_contacts(request):
    contacts = Contact.objects.all()
    return render(request, 'store/admin_contacts.html', {'contacts': contacts})


@admin_required
def admin_contact_detail(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)
    if not contact.read_at:
        contact.read_at = timezone.now()
        contact.save()
    return render(request, 'store/admin_contact_detail.html', {'contact': contact})


# =============================
# PANEL DE ARTESANO
# =============================
def _get_artisan(request):
    """Devuelve el perfil de artesano vinculado al usuario en sesión."""
    return Artisan.objects.filter(user_id=request.session.get('user_id')).first()


def _artisan_order_ids(artisan):
    return OrderItem.objects.filter(product__artisan=artisan).values_list('order_id', flat=True).distinct()


@artisan_required
def artisan_dashboard(request):
    artisan = _get_artisan(request)
    if not artisan:
        messages.error(request, "Tu cuenta no tiene un perfil de artesano asociado. Contacta al administrador.")
        return redirect('home')
    products = Product.objects.filter(artisan=artisan).order_by('-created_at')
    order_ids = _artisan_order_ids(artisan)
    orders = Order.objects.filter(id__in=order_ids)
    return render(request, 'store/artisan_dashboard.html', {
        'artisan': artisan,
        'products': products,
        'total_products': products.count(),
        'total_orders': orders.count(),
        'pending_orders': orders.filter(status='pending').count(),
    })


@artisan_required
def artisan_products(request):
    artisan = _get_artisan(request)
    if not artisan:
        messages.error(request, "Tu cuenta no tiene un perfil de artesano asociado.")
        return redirect('home')
    products = Product.objects.filter(artisan=artisan).select_related('category')
    return render(request, 'store/artisan_products.html', {'products': products})


@artisan_required
def artisan_add_product(request):
    artisan = _get_artisan(request)
    if not artisan:
        messages.error(request, "Tu cuenta no tiene un perfil de artesano asociado.")
        return redirect('home')
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug') or name
        Product.objects.create(
            name=name,
            slug=_unique_slug(Product, slug),
            description=request.POST.get('description', ''),
            price=request.POST.get('price') or 0,
            stock=request.POST.get('stock') or 0,
            category_id=request.POST.get('category') or None,
            artisan=artisan,
            featured='featured' in request.POST,
            active='active' in request.POST,
        )
        messages.success(request, "Producto creado exitosamente.")
        return redirect('artisan_products')
    return render(request, 'store/artisan_add_product.html', {
        'categories': Category.objects.all(),
    })


@artisan_required
def artisan_edit_product(request, product_id):
    artisan = _get_artisan(request)
    if not artisan:
        messages.error(request, "Tu cuenta no tiene un perfil de artesano asociado.")
        return redirect('home')
    product = get_object_or_404(Product, id=product_id, artisan=artisan)
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description', '')
        product.price = request.POST.get('price') or 0
        product.stock = request.POST.get('stock') or 0
        product.category_id = request.POST.get('category') or None
        product.featured = 'featured' in request.POST
        product.active = 'active' in request.POST
        product.save()
        messages.success(request, "Producto actualizado.")
        return redirect('artisan_products')
    return render(request, 'store/artisan_edit_product.html', {
        'product': product,
        'categories': Category.objects.all(),
    })


@artisan_required
def artisan_orders(request):
    artisan = _get_artisan(request)
    if not artisan:
        messages.error(request, "Tu cuenta no tiene un perfil de artesano asociado.")
        return redirect('home')
    orders = Order.objects.filter(id__in=_artisan_order_ids(artisan)).select_related('user')
    return render(request, 'store/artisan_orders.html', {'orders': orders})


@artisan_required
def artisan_order_detail(request, order_id):
    artisan = _get_artisan(request)
    if not artisan:
        messages.error(request, "Tu cuenta no tiene un perfil de artesano asociado.")
        return redirect('home')
    order = get_object_or_404(Order, id=order_id)
    items = OrderItem.objects.filter(order=order, product__artisan=artisan).select_related('product')
    if not items.exists():
        messages.error(request, "Este pedido no contiene productos tuyos.")
        return redirect('artisan_orders')
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            order.status = new_status
            order.save()
            messages.success(request, "Estado del pedido actualizado.")
        return redirect('artisan_order_detail', order_id=order.id)
    return render(request, 'store/artisan_order_detail.html', {'order': order, 'items': items})

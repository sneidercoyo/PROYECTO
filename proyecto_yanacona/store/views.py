from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.db import connection, transaction
from django.utils.text import slugify
from django.utils import timezone
from .models import Category, Artisan, Product, User, Order, OrderItem, Contact, CartItem


# ============================================================
# UTILIDADES
# ============================================================

def require_login(request):
    return request.session.get('user_id')


def require_admin(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    try:
        user = User.objects.get(id=user_id, active=True)
        if user.is_admin():
            return user
        return None
    except User.DoesNotExist:
        return None


def require_artisan(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    try:
        user = User.objects.get(id=user_id, active=True)
        if user.is_artisan() or user.is_admin():
            return user
        return None
    except User.DoesNotExist:
        return None


def unique_slug(model, base_slug):
    """Genera un slug unico agregando -N si existe."""
    slug = base_slug
    counter = 1
    while model.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


def authenticate_user(identifier, password):
    """
    Busca usuario por email O por name.
    Retorna el usuario si la contraseña coincide, None si no.
    """
    user = None
    # Primero intentar por email
    try:
        user = User.objects.get(email=identifier, active=True)
    except User.DoesNotExist:
        pass

    # Si no, intentar por name (para usuarios como ESNEIDER sin email)
    if not user:
        try:
            user = User.objects.get(name=identifier, active=True)
        except User.DoesNotExist:
            pass

    if user and user.check_password(password):
        return user
    return None


# ============================================================
# VISTAS PUBLICAS
# ============================================================

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


# ============================================================
# AUTH — CORREGIDO: acepta email O name
# ============================================================

def login_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('email')  # El campo sigue llamandose 'email' en el form
        password = request.POST.get('password')

        user = authenticate_user(identifier, password)

        if user:
            request.session['user_id'] = user.id
            request.session['user_name'] = user.name
            request.session['user_role'] = user.role
            messages.success(request, f"Bienvenido, {user.name}!")
            return redirect('home')
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")

    return render(request, 'store/login.html')


def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')

        if email and User.objects.filter(email=email).exists():
            messages.error(request, "El correo ya esta registrado.")
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
    messages.success(request, "Sesion cerrada exitosamente.")
    return redirect('home')


def profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    user = get_object_or_404(User, id=user_id)
    orders = Order.objects.filter(user=user).order_by('-created_at')
    return render(request, 'store/profile.html', {'user': user, 'orders': orders})


# ============================================================
# CARRITO
# ============================================================

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
        messages.error(request, "Debes iniciar sesion para agregar al carrito.")
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


# ============================================================
# CHECKOUT
# ============================================================

def checkout(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    items = CartItem.objects.filter(user_id=user_id).select_related('product')
    if not items:
        messages.warning(request, "Tu carrito esta vacio.")
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


# ============================================================
# PANEL ADMINISTRADOR
# ============================================================

def admin_dashboard(request):
    user = require_admin(request)
    if not user:
        messages.error(request, "Acceso restringido a administradores.")
        return redirect('login')

    total_users = User.objects.count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_artisans = Artisan.objects.count()
    recent_orders = Order.objects.order_by('-created_at')[:10]
    recent_users = User.objects.order_by('-created_at')[:10]

    return render(request, 'store/admin_dashboard.html', {
        'total_users': total_users,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_artisans': total_artisans,
        'recent_orders': recent_orders,
        'recent_users': recent_users,
    })


def admin_orders(request):
    user = require_admin(request)
    if not user:
        messages.error(request, "Acceso restringido a administradores.")
        return redirect('login')

    status_filter = request.GET.get('status', '')
    orders_qs = Order.objects.all().order_by('-created_at')
    if status_filter:
        orders_qs = orders_qs.filter(status=status_filter)

    return render(request, 'store/admin_orders.html', {
        'orders': orders_qs,
        'status_filter': status_filter,
    })


def admin_order_detail(request, order_id):
    user = require_admin(request)
    if not user:
        messages.error(request, "Acceso restringido a administradores.")
        return redirect('login')

    order = get_object_or_404(Order, id=order_id)
    items = OrderItem.objects.filter(order=order).select_related('product', 'product__artisan')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f"Estado actualizado a: {order.get_status_display()}")
            return redirect('admin_order_detail', order_id=order.id)

    return render(request, 'store/admin_order_detail.html', {
        'order': order,
        'items': items,
    })


def admin_products(request):
    user = require_admin(request)
    if not user:
        messages.error(request, "Acceso restringido a administradores.")
        return redirect('login')

    products = Product.objects.all().order_by('-created_at')
    return render(request, 'store/admin_products.html', {'products': products})


def admin_add_product(request):
    user = require_admin(request)
    if not user:
        messages.error(request, "Acceso restringido a administradores.")
        return redirect('login')

    categories = Category.objects.all()
    artisans = Artisan.objects.filter(active=True)

    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug') or slugify(name)
        slug = unique_slug(Product, slug)
        description = request.POST.get('description', '')
        price = request.POST.get('price')
        stock = request.POST.get('stock', 0)
        category_id = request.POST.get('category') or None
        artisan_id = request.POST.get('artisan') or None
        featured = request.POST.get('featured') == 'on'
        active = request.POST.get('active') == 'on'

        with connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO products (name, slug, description, price, stock, category_id, artisan_id, featured, active, created_at, updated_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())""",
                [name, slug, description, price, stock, category_id, artisan_id, featured, active]
            )
        messages.success(request, f"Producto '{name}' creado exitosamente!")
        return redirect('admin_products')

    return render(request, 'store/admin_add_product.html', {
        'categories': categories,
        'artisans': artisans,
    })


def admin_edit_product(request, product_id):
    user = require_admin(request)
    if not user:
        messages.error(request, "Acceso restringido a administradores.")
        return redirect('login')

    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()
    artisans = Artisan.objects.filter(active=True)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        price = request.POST.get('price')
        stock = request.POST.get('stock', 0)
        category_id = request.POST.get('category') or None
        artisan_id = request.POST.get('artisan') or None
        featured = request.POST.get('featured') == 'on'
        active = request.POST.get('active') == 'on'

        with connection.cursor() as cursor:
            cursor.execute(
                """UPDATE products SET name=%s, description=%s, price=%s, stock=%s,
                   category_id=%s, artisan_id=%s, featured=%s, active=%s, updated_at=NOW()
                   WHERE id=%s""",
                [name, description, price, stock, category_id, artisan_id, featured, active, product_id]
            )
        messages.success(request, "Producto actualizado exitosamente!")
        return redirect('admin_products')

    return render(request, 'store/admin_edit_product.html', {
        'product': product,
        'categories': categories,
        'artisans': artisans,
    })


def admin_categories(request):
    user = require_admin(request)
    if not user:
        messages.error(request, "Acceso restringido a administradores.")
        return redirect('login')

    categories = Category.objects.all().order_by('name')
    return render(request, 'store/admin_categories.html', {'categories': categories})


def admin_add_category(request):
    user = require_admin(request)
    if not user:
        messages.error(request, "Acceso restringido a administradores.")
        return redirect('login')

    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug') or slugify(name)
        slug = unique_slug(Category, slug)
        description = request.POST.get('description', '')

        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO categories (name, slug, description, created_at) VALUES (%s, %s, %s, NOW())",
                [name, slug, description]
            )
        messages.success(request, f"Categoria '{name}' creada exitosamente!")
        return redirect('admin_categories')

    return render(request, 'store/admin_add_category.html')


def admin_edit_category(request, category_id):
    user = require_admin(request)
    if not user:
        messages.error(request, "Acceso restringido a administradores.")
        return redirect('login')

    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE categories SET name=%s, description=%s WHERE id=%s",
                [name, description, category_id]
            )
        messages.success(request, "Categoria actualizada exitosamente!")
        return redirect('admin_categories')

    return render(request, 'store/admin_edit_category.html', {'category': category})


def admin_artisans(request):
    user = require_admin(request)
    if not user:
        messages.error(request, "Acceso restringido a administradores.")
        return redirect('login')

    artisans_list = Artisan.objects.all().order_by('name')
    return render(request, 'store/admin_artisans.html', {'artisans': artisans_list})


def admin_add_artisan(request):
    user = require_admin(request)
    if not user:
        messages.error(request, "Acceso restringido a administradores.")
        return redirect('login')

    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug') or slugify(name)
        slug = unique_slug(Artisan, slug)
        bio = request.POST.get('bio', '')
        specialty = request.POST.get('specialty', '')
        active = request.POST.get('active') == 'on'

        with connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO artisans (name, slug, bio, specialty, active, created_at)
                   VALUES (%s, %s, %s, %s, %s, NOW())""",
                [name, slug, bio, specialty, active]
            )
        messages.success(request, f"Artesano '{name}' creado exitosamente!")
        return redirect('admin_artisans')

    return render(request, 'store/admin_add_artisan.html')


def admin_edit_artisan(request, artisan_id):
    user = require_admin(request)
    if not user:
        messages.error(request, "Acceso restringido a administradores.")
        return redirect('login')

    artisan = get_object_or_404(Artisan, id=artisan_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        bio = request.POST.get('bio', '')
        specialty = request.POST.get('specialty', '')
        active = request.POST.get('active') == 'on'

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE artisans SET name=%s, bio=%s, specialty=%s, active=%s WHERE id=%s",
                [name, bio, specialty, active, artisan_id]
            )
        messages.success(request, "Artesano actualizado exitosamente!")
        return redirect('admin_artisans')

    return render(request, 'store/admin_edit_artisan.html', {'artisan': artisan})


def admin_users(request):
    user = require_admin(request)
    if not user:
        messages.error(request, "Acceso restringido a administradores.")
        return redirect('login')

    users = User.objects.all().order_by('-created_at')
    return render(request, 'store/admin_users.html', {'users': users})


def admin_edit_user(request, user_id):
    admin_user = require_admin(request)
    if not admin_user:
        messages.error(request, "Acceso restringido a administradores.")
        return redirect('login')

    edit_user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')
        city = request.POST.get('city', '')
        role = request.POST.get('role')
        active = request.POST.get('active') == 'on'

        with connection.cursor() as cursor:
            cursor.execute(
                """UPDATE users SET name=%s, email=%s, phone=%s, address=%s,
                   city=%s, role=%s, active=%s WHERE id=%s""",
                [name, email, phone, address, city, role, active, user_id]
            )
        messages.success(request, "Usuario actualizado exitosamente!")
        return redirect('admin_users')

    return render(request, 'store/admin_edit_user.html', {'user': edit_user})


def admin_contacts(request):
    user = require_admin(request)
    if not user:
        messages.error(request, "Acceso restringido a administradores.")
        return redirect('login')

    contacts = Contact.objects.all().order_by('-created_at')
    return render(request, 'store/admin_contacts.html', {'contacts': contacts})


def admin_contact_detail(request, contact_id):
    user = require_admin(request)
    if not user:
        messages.error(request, "Acceso restringido a administradores.")
        return redirect('login')

    contact = get_object_or_404(Contact, id=contact_id)
    if not contact.read_at:
        contact.read_at = timezone.now()
        contact.save(update_fields=['read_at'])
    return render(request, 'store/admin_contact_detail.html', {'contact': contact})


# ============================================================
# PANEL ARTESANO
# ============================================================

def artisan_dashboard(request):
    user = require_artisan(request)
    if not user:
        messages.error(request, "Acceso restringido a artesanos.")
        return redirect('login')

    artisan_id = request.session.get('artisan_id')
    if not artisan_id:
        artisan = Artisan.objects.filter(name__icontains=user.name.split()[0]).first()
        if not artisan:
            messages.error(request, "No tienes un perfil de artesano asignado.")
            return redirect('home')
        request.session['artisan_id'] = artisan.id
        artisan_id = artisan.id

    products = Product.objects.filter(artisan_id=artisan_id).order_by('-created_at')
    total_products = products.count()

    order_ids = OrderItem.objects.filter(
        product__artisan_id=artisan_id
    ).values_list('order_id', flat=True).distinct()
    orders = Order.objects.filter(id__in=order_ids)
    total_orders = orders.count()
    pending_orders = orders.filter(status='pending').count()

    return render(request, 'store/artisan_dashboard.html', {
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'products': products[:5],
    })


def artisan_products(request):
    user = require_artisan(request)
    if not user:
        messages.error(request, "Acceso restringido a artesanos.")
        return redirect('login')

    artisan_id = request.session.get('artisan_id')
    if not artisan_id:
        return redirect('artisan_dashboard')

    products = Product.objects.filter(artisan_id=artisan_id).order_by('-created_at')
    return render(request, 'store/artisan_products.html', {'products': products})


def artisan_add_product(request):
    user = require_artisan(request)
    if not user:
        messages.error(request, "Acceso restringido a artesanos.")
        return redirect('login')

    artisan_id = request.session.get('artisan_id')
    if not artisan_id:
        return redirect('artisan_dashboard')

    categories = Category.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug') or slugify(name)
        slug = unique_slug(Product, slug)
        description = request.POST.get('description', '')
        price = request.POST.get('price')
        stock = request.POST.get('stock', 0)
        category_id = request.POST.get('category') or None
        featured = request.POST.get('featured') == 'on'
        active = request.POST.get('active') == 'on'

        with connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO products (name, slug, description, price, stock, category_id, artisan_id, featured, active, created_at, updated_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())""",
                [name, slug, description, price, stock, category_id, artisan_id, featured, active]
            )
        messages.success(request, f"Producto '{name}' creado exitosamente!")
        return redirect('artisan_products')

    return render(request, 'store/artisan_add_product.html', {'categories': categories})


def artisan_edit_product(request, product_id):
    user = require_artisan(request)
    if not user:
        messages.error(request, "Acceso restringido a artesanos.")
        return redirect('login')

    artisan_id = request.session.get('artisan_id')
    if not artisan_id:
        return redirect('artisan_dashboard')

    product = get_object_or_404(Product, id=product_id, artisan_id=artisan_id)
    categories = Category.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        price = request.POST.get('price')
        stock = request.POST.get('stock', 0)
        category_id = request.POST.get('category') or None
        featured = request.POST.get('featured') == 'on'
        active = request.POST.get('active') == 'on'

        with connection.cursor() as cursor:
            cursor.execute(
                """UPDATE products SET name=%s, description=%s, price=%s, stock=%s,
                   category_id=%s, featured=%s, active=%s, updated_at=NOW()
                   WHERE id=%s AND artisan_id=%s""",
                [name, description, price, stock, category_id, featured, active, product_id, artisan_id]
            )
        messages.success(request, "Producto actualizado exitosamente!")
        return redirect('artisan_products')

    return render(request, 'store/artisan_edit_product.html', {
        'product': product,
        'categories': categories,
    })


def artisan_orders(request):
    user = require_artisan(request)
    if not user:
        messages.error(request, "Acceso restringido a artesanos.")
        return redirect('login')

    artisan_id = request.session.get('artisan_id')
    if not artisan_id:
        return redirect('artisan_dashboard')

    order_ids = OrderItem.objects.filter(
        product__artisan_id=artisan_id
    ).values_list('order_id', flat=True).distinct()
    orders = Order.objects.filter(id__in=order_ids).order_by('-created_at')

    return render(request, 'store/artisan_orders.html', {'orders': orders})


def artisan_order_detail(request, order_id):
    user = require_artisan(request)
    if not user:
        messages.error(request, "Acceso restringido a artesanos.")
        return redirect('login')

    artisan_id = request.session.get('artisan_id')
    if not artisan_id:
        return redirect('artisan_dashboard')

    order = get_object_or_404(Order, id=order_id)
    items = OrderItem.objects.filter(
        order=order,
        product__artisan_id=artisan_id
    ).select_related('product')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f"Estado actualizado a: {order.get_status_display()}")
            return redirect('artisan_order_detail', order_id=order.id)

    return render(request, 'store/artisan_order_detail.html', {
        'order': order,
        'items': items,
    })

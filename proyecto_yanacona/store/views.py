from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Sum, Count, F
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


def get_artisan_for_user(request, user):
    """Obtiene el objeto Artisan vinculado al usuario artesano."""
    artisan_id = request.session.get('artisan_id')
    if artisan_id:
        try:
            return Artisan.objects.get(id=artisan_id)
        except Artisan.DoesNotExist:
            pass
    # Buscar por nombre
    artisan = Artisan.objects.filter(name__icontains=user.name.split()[0]).first()
    if artisan:
        request.session['artisan_id'] = artisan.id
    return artisan


def unique_slug(model, base_slug):
    slug = base_slug
    counter = 1
    while model.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


def authenticate_user(identifier, password):
    user = None
    try:
        user = User.objects.get(email=identifier, active=True)
    except User.DoesNotExist:
        pass
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
# AUTH
# ============================================================

def login_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate_user(identifier, password)

        if user:
            request.session['user_id'] = user.id
            request.session['user_name'] = user.name
            request.session['user_role'] = user.role
            messages.success(request, f"Bienvenido, {user.name}!")

            # Redirigir según rol
            if user.is_admin():
                return redirect('admin_dashboard')
            elif user.is_artisan():
                # Buscar y guardar el artisan_id en sesión
                artisan = Artisan.objects.filter(name__icontains=user.name.split()[0]).first()
                if artisan:
                    request.session['artisan_id'] = artisan.id
                return redirect('artisan_dashboard')
            else:
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
                price=item.product.sale_price(),
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
        discount_price = request.POST.get('discount_price') or None
        stock = request.POST.get('stock', 0)
        category_id = request.POST.get('category') or None
        artisan_id = request.POST.get('artisan') or None
        featured = request.POST.get('featured') == 'on'
        active = request.POST.get('active') == 'on'

        Product.objects.create(
            name=name, slug=slug, description=description, price=price,
            discount_price=discount_price, stock=stock,
            category_id=category_id, artisan_id=artisan_id,
            featured=featured, active=active
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
        product.name = request.POST.get('name')
        product.description = request.POST.get('description', '')
        product.price = request.POST.get('price')
        dp = request.POST.get('discount_price')
        product.discount_price = dp if dp else None
        product.stock = request.POST.get('stock', 0)
        product.category_id = request.POST.get('category') or None
        product.artisan_id = request.POST.get('artisan') or None
        product.featured = request.POST.get('featured') == 'on'
        product.active = request.POST.get('active') == 'on'
        product.save()
        messages.success(request, "Producto actualizado exitosamente!")
        return redirect('admin_products')

    return render(request, 'store/admin_edit_product.html', {
        'product': product,
        'categories': categories,
        'artisans': artisans,
    })


def admin_delete_product(request, product_id):
    user = require_admin(request)
    if not user:
        messages.error(request, "Acceso restringido a administradores.")
        return redirect('login')

    product = get_object_or_404(Product, id=product_id)
    name = product.name
    product.delete()
    messages.success(request, f"Producto '{name}' eliminado exitosamente.")
    return redirect('admin_products')


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
        Category.objects.create(name=name, slug=slug, description=description)
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
        category.name = request.POST.get('name')
        category.description = request.POST.get('description', '')
        category.save()
        messages.success(request, "Categoria actualizada exitosamente!")
        return redirect('admin_categories')

    return render(request, 'store/admin_edit_category.html', {'category': category})


def admin_delete_category(request, category_id):
    user = require_admin(request)
    if not user:
        messages.error(request, "Acceso restringido a administradores.")
        return redirect('login')

    category = get_object_or_404(Category, id=category_id)
    name = category.name
    category.delete()
    messages.success(request, f"Categoria '{name}' eliminada exitosamente.")
    return redirect('admin_categories')


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
        Artisan.objects.create(name=name, slug=slug, bio=bio, specialty=specialty, active=active)
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
        artisan.name = request.POST.get('name')
        artisan.bio = request.POST.get('bio', '')
        artisan.specialty = request.POST.get('specialty', '')
        artisan.active = request.POST.get('active') == 'on'
        artisan.save()
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
        edit_user.name = request.POST.get('name')
        edit_user.email = request.POST.get('email')
        edit_user.phone = request.POST.get('phone', '')
        edit_user.address = request.POST.get('address', '')
        edit_user.city = request.POST.get('city', '')
        edit_user.role = request.POST.get('role')
        edit_user.active = request.POST.get('active') == 'on'
        edit_user.save()
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
# PANEL ARTESANO - COMPLETO
# ============================================================

def artisan_dashboard(request):
    user = require_artisan(request)
    if not user:
        messages.error(request, "Acceso restringido a artesanos.")
        return redirect('login')

    artisan = get_artisan_for_user(request, user)
    if not artisan:
        messages.error(request, "No tienes un perfil de artesano asignado.")
        return redirect('home')

    products = Product.objects.filter(artisan=artisan)
    total_products = products.count()
    active_products = products.filter(active=True).count()
    out_of_stock = products.filter(stock=0).count()
    on_sale = products.filter(discount_price__isnull=False, discount_price__gt=0).count()

    order_items = OrderItem.objects.filter(product__artisan=artisan)
    total_orders = order_items.values('order').distinct().count()
    total_revenue = order_items.aggregate(total=Sum('subtotal'))['total'] or 0
    total_sold = order_items.aggregate(total=Sum('quantity'))['total'] or 0

    pending_orders = Order.objects.filter(
        id__in=order_items.values_list('order_id', flat=True).distinct(),
        status='pending'
    ).count()

    recent_products = products.order_by('-created_at')[:5]

    return render(request, 'store/artisan_dashboard.html', {
        'artisan': artisan,
        'total_products': total_products,
        'active_products': active_products,
        'out_of_stock': out_of_stock,
        'on_sale': on_sale,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_sold': total_sold,
        'pending_orders': pending_orders,
        'recent_products': recent_products,
    })


def artisan_profile(request):
    user = require_artisan(request)
    if not user:
        messages.error(request, "Acceso restringido a artesanos.")
        return redirect('login')

    artisan = get_artisan_for_user(request, user)
    if not artisan:
        messages.error(request, "No tienes un perfil de artesano asignado.")
        return redirect('home')

    return render(request, 'store/artisan_profile.html', {
        'artisan': artisan,
        'user': user,
    })


def artisan_edit_profile(request):
    user = require_artisan(request)
    if not user:
        messages.error(request, "Acceso restringido a artesanos.")
        return redirect('login')

    artisan = get_artisan_for_user(request, user)
    if not artisan:
        messages.error(request, "No tienes un perfil de artesano asignado.")
        return redirect('home')

    if request.method == 'POST':
        artisan.name = request.POST.get('name')
        artisan.bio = request.POST.get('bio', '')
        artisan.specialty = request.POST.get('specialty', '')
        artisan.active = request.POST.get('active') == 'on'
        if request.FILES.get('image'):
            artisan.image = request.FILES['image']
        artisan.save()

        # Tambien actualizar el usuario
        user.name = request.POST.get('name')
        user.phone = request.POST.get('phone', '')
        user.address = request.POST.get('address', '')
        user.city = request.POST.get('city', '')
        user.save()

        messages.success(request, "Perfil actualizado exitosamente!")
        return redirect('artisan_profile')

    return render(request, 'store/artisan_edit_profile.html', {
        'artisan': artisan,
        'user': user,
    })


def artisan_products(request):
    user = require_artisan(request)
    if not user:
        messages.error(request, "Acceso restringido a artesanos.")
        return redirect('login')

    artisan = get_artisan_for_user(request, user)
    if not artisan:
        return redirect('artisan_dashboard')

    products = Product.objects.filter(artisan=artisan).order_by('-created_at')
    return render(request, 'store/artisan_products.html', {
        'products': products,
        'artisan': artisan,
    })


def artisan_add_product(request):
    user = require_artisan(request)
    if not user:
        messages.error(request, "Acceso restringido a artesanos.")
        return redirect('login')

    artisan = get_artisan_for_user(request, user)
    if not artisan:
        return redirect('artisan_dashboard')

    categories = Category.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug') or slugify(name)
        slug = unique_slug(Product, slug)
        description = request.POST.get('description', '')
        price = request.POST.get('price')
        discount_price = request.POST.get('discount_price') or None
        stock = request.POST.get('stock', 0)
        category_id = request.POST.get('category') or None
        featured = request.POST.get('featured') == 'on'
        active = request.POST.get('active') == 'on'

        product = Product.objects.create(
            name=name, slug=slug, description=description,
            price=price, discount_price=discount_price, stock=stock,
            category_id=category_id, artisan=artisan,
            featured=featured, active=active
        )
        if request.FILES.get('image'):
            product.image = request.FILES['image']
            product.save()

        messages.success(request, f"Producto '{name}' creado exitosamente!")
        return redirect('artisan_products')

    return render(request, 'store/artisan_add_product.html', {
        'categories': categories,
        'artisan': artisan,
    })


def artisan_edit_product(request, product_id):
    user = require_artisan(request)
    if not user:
        messages.error(request, "Acceso restringido a artesanos.")
        return redirect('login')

    artisan = get_artisan_for_user(request, user)
    if not artisan:
        return redirect('artisan_dashboard')

    product = get_object_or_404(Product, id=product_id, artisan=artisan)
    categories = Category.objects.all()

    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description', '')
        product.price = request.POST.get('price')
        dp = request.POST.get('discount_price')
        product.discount_price = dp if dp else None
        product.stock = request.POST.get('stock', 0)
        product.category_id = request.POST.get('category') or None
        product.featured = request.POST.get('featured') == 'on'
        product.active = request.POST.get('active') == 'on'

        if request.FILES.get('image'):
            product.image = request.FILES['image']

        product.save()
        messages.success(request, "Producto actualizado exitosamente!")
        return redirect('artisan_products')

    return render(request, 'store/artisan_edit_product.html', {
        'product': product,
        'categories': categories,
        'artisan': artisan,
    })


def artisan_delete_product(request, product_id):
    user = require_artisan(request)
    if not user:
        messages.error(request, "Acceso restringido a artesanos.")
        return redirect('login')

    artisan = get_artisan_for_user(request, user)
    if not artisan:
        return redirect('artisan_dashboard')

    product = get_object_or_404(Product, id=product_id, artisan=artisan)
    name = product.name
    product.delete()
    messages.success(request, f"Producto '{name}' eliminado exitosamente.")
    return redirect('artisan_products')


def artisan_toggle_product(request, product_id):
    """Activa o desactiva un producto rapidamente."""
    user = require_artisan(request)
    if not user:
        messages.error(request, "Acceso restringido a artesanos.")
        return redirect('login')

    artisan = get_artisan_for_user(request, user)
    if not artisan:
        return redirect('artisan_dashboard')

    product = get_object_or_404(Product, id=product_id, artisan=artisan)
    product.active = not product.active
    product.save()
    status = "activado" if product.active else "desactivado"
    messages.success(request, f"Producto '{product.name}' {status}.")
    return redirect('artisan_products')


def artisan_orders(request):
    user = require_artisan(request)
    if not user:
        messages.error(request, "Acceso restringido a artesanos.")
        return redirect('login')

    artisan = get_artisan_for_user(request, user)
    if not artisan:
        return redirect('artisan_dashboard')

    order_ids = OrderItem.objects.filter(
        product__artisan=artisan
    ).values_list('order_id', flat=True).distinct()
    orders = Order.objects.filter(id__in=order_ids).order_by('-created_at')

    return render(request, 'store/artisan_orders.html', {
        'orders': orders,
        'artisan': artisan,
    })


def artisan_order_detail(request, order_id):
    user = require_artisan(request)
    if not user:
        messages.error(request, "Acceso restringido a artesanos.")
        return redirect('login')

    artisan = get_artisan_for_user(request, user)
    if not artisan:
        return redirect('artisan_dashboard')

    order = get_object_or_404(Order, id=order_id)
    items = OrderItem.objects.filter(
        order=order,
        product__artisan=artisan
    ).select_related('product')

    artisan_total = sum(item.subtotal for item in items)

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
        'artisan_total': artisan_total,
    })


def artisan_stats(request):
    """Estadisticas de ventas del artesano."""
    user = require_artisan(request)
    if not user:
        messages.error(request, "Acceso restringido a artesanos.")
        return redirect('login')

    artisan = get_artisan_for_user(request, user)
    if not artisan:
        return redirect('artisan_dashboard')

    products = Product.objects.filter(artisan=artisan)
    order_items = OrderItem.objects.filter(product__artisan=artisan)

    # Top productos vendidos
    top_products = order_items.values('product__name').annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum('subtotal')
    ).order_by('-total_sold')[:10]

    # Ventas por mes (ultimos 6 meses)
    from django.db.models.functions import TruncMonth
    sales_by_month = order_items.annotate(
        month=TruncMonth('order__created_at')
    ).values('month').annotate(
        total=Sum('subtotal'),
        count=Count('id')
    ).order_by('month')[:6]

    total_revenue = order_items.aggregate(total=Sum('subtotal'))['total'] or 0
    total_sold = order_items.aggregate(total=Sum('quantity'))['total'] or 0
    total_orders = order_items.values('order').distinct().count()

    return render(request, 'store/artisan_stats.html', {
        'artisan': artisan,
        'top_products': top_products,
        'sales_by_month': sales_by_month,
        'total_revenue': total_revenue,
        'total_sold': total_sold,
        'total_orders': total_orders,
    })


def artisan_stock(request):
    """Gestion de inventario del artesano."""
    user = require_artisan(request)
    if not user:
        messages.error(request, "Acceso restringido a artesanos.")
        return redirect('login')

    artisan = get_artisan_for_user(request, user)
    if not artisan:
        return redirect('artisan_dashboard')

    products = Product.objects.filter(artisan=artisan).order_by('stock')

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        new_stock = request.POST.get('new_stock')
        product = get_object_or_404(Product, id=product_id, artisan=artisan)
        product.stock = int(new_stock)
        product.save()
        messages.success(request, f"Stock de '{product.name}' actualizado a {new_stock}.")
        return redirect('artisan_stock')

    low_stock = products.filter(stock__lte=5, stock__gt=0)
    out_of_stock = products.filter(stock=0)

    return render(request, 'store/artisan_stock.html', {
        'products': products,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'artisan': artisan,
    })

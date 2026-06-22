from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import User, Artisan, Category, Product
import bcrypt


def hash_password(password):
    """Genera hash bcrypt con prefijo $2y$ para compatibilidad."""
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8').replace('$2b$', '$2y$')


@receiver(post_migrate)
def create_demo_data(sender, **kwargs):
    """Crea usuarios de prueba, categorías, artesanos y productos demo después de migrar."""
    if sender.name != 'store':
        return

    # ============================================================
    # USUARIOS DE PRUEBA (uno por cada rol)
    # ============================================================

    # ADMINISTRADOR
    admin, created = User.objects.get_or_create(
        email='admin@onel.com',
        defaults={
            'name': 'Administrador ONEL',
            'password': hash_password('admin123'),
            'phone': '3201234567',
            'address': 'Puerto Caicedo, Putumayo',
            'city': 'Puerto Caicedo',
            'role': 'admin',
            'active': True,
        }
    )
    if created:
        print("[DEMO] Usuario ADMIN creado: admin@onel.com / admin123")

    # CLIENTE
    customer, created = User.objects.get_or_create(
        email='cliente@demo.com',
        defaults={
            'name': 'Cliente Demo',
            'password': hash_password('password'),
            'phone': '3209876543',
            'address': 'Calle 10 # 5-20',
            'city': 'Mocoa',
            'role': 'customer',
            'active': True,
        }
    )
    if created:
        print("[DEMO] Usuario CLIENTE creado: cliente@demo.com / password")

    # ARTESANO (sin email, login por nombre)
    artisan_user, created = User.objects.get_or_create(
        name='Maria Yanacona',
        defaults={
            'email': 'maria@artesana.com',
            'password': hash_password('artesana123'),
            'phone': '3205558888',
            'address': 'Vereda El Paraíso',
            'city': 'Puerto Caicedo',
            'role': 'artisan',
            'active': True,
        }
    )
    if created:
        print("[DEMO] Usuario ARTESANO creado: maria@artesana.com / artesana123")

    # ============================================================
    # CATEGORÍAS DEMO
    # ============================================================
    categories_data = [
        {'name': 'Cerámica', 'slug': 'ceramica', 'description': 'Piezas de cerámica tradicional'},
        {'name': 'Cestería', 'slug': 'cesteria', 'description': 'Canastos y tejidos en fibras naturales'},
        {'name': 'Tejidos', 'slug': 'tejidos', 'description': 'Ropa y textiles artesanales'},
        {'name': 'Joyería', 'slug': 'joyeria', 'description': 'Accesorios en semillas y piedras'},
    ]
    for cat in categories_data:
        Category.objects.get_or_create(slug=cat['slug'], defaults=cat)

    # ============================================================
    # ARTESANOS DEMO
    # ============================================================
    artisans_data = [
        {
            'name': 'Maria Yanacona',
            'slug': 'maria-yanacona',
            'bio': 'Artesana de tercera generación especializada en cestería con chambira. Sus piezas reflejan la cosmovisión Yanacona.',
            'specialty': 'Cestería',
            'active': True,
        },
        {
            'name': 'José Caguana',
            'slug': 'jose-caguana',
            'bio': 'Maestro ceramista con más de 30 años de experiencia. Utiliza técnicas precolombinas en sus obras.',
            'specialty': 'Cerámica',
            'active': True,
        },
        {
            'name': 'Ana Waira',
            'slug': 'ana-waira',
            'bio': 'Tejedora que preserva los diseños tradicionales de la comunidad Yanacona en cada prenda.',
            'specialty': 'Tejidos',
            'active': True,
        },
    ]
    for art in artisans_data:
        Artisan.objects.get_or_create(slug=art['slug'], defaults=art)

    # ============================================================
    # PRODUCTOS DEMO
    # ============================================================
    ceramica = Category.objects.filter(slug='ceramica').first()
    cesteria = Category.objects.filter(slug='cesteria').first()
    tejidos = Category.objects.filter(slug='tejidos').first()

    maria = Artisan.objects.filter(slug='maria-yanacona').first()
    jose = Artisan.objects.filter(slug='jose-caguana').first()
    ana = Artisan.objects.filter(slug='ana-waira').first()

    products_data = [
        {
            'name': 'Canasto Yanacona Grande',
            'slug': 'canasto-yanacona-grande',
            'description': 'Canasto tejido a mano con fibra de chambira. Ideal para mercado o decoración.',
            'price': 85000,
            'stock': 12,
            'category': cesteria,
            'artisan': maria,
            'featured': True,
            'active': True,
        },
        {
            'name': 'Vasija Precolombina',
            'slug': 'vasija-precolombina',
            'description': 'Réplica de vasija con técnicas ancestrales de alfarería Yanacona.',
            'price': 120000,
            'stock': 8,
            'category': ceramica,
            'artisan': jose,
            'featured': True,
            'active': True,
        },
        {
            'name': 'Mochila Tejida',
            'slug': 'mochila-tejida',
            'description': 'Mochila tradicional con diseños geométricos de la cultura Yanacona.',
            'price': 95000,
            'stock': 15,
            'category': tejidos,
            'artisan': ana,
            'featured': True,
            'active': True,
        },
        {
            'name': 'Plato Decorativo Cerámica',
            'slug': 'plato-decorativo-ceramica',
            'description': 'Plato con motivos de la fauna del Putumayo. Pintado a mano.',
            'price': 65000,
            'stock': 20,
            'category': ceramica,
            'artisan': jose,
            'featured': False,
            'active': True,
        },
        {
            'name': 'Sombrero de Palma',
            'slug': 'sombrero-de-palma',
            'description': 'Sombrero tradicional tejido en palma de iraca. Fresco y ligero.',
            'price': 45000,
            'stock': 25,
            'category': cesteria,
            'artisan': maria,
            'featured': False,
            'active': True,
        },
        {
            'name': 'Camisa Bordada',
            'slug': 'camisa-bordada',
            'description': 'Camisa con bordados tradicionales en hilos de colores naturales.',
            'price': 110000,
            'stock': 10,
            'category': tejidos,
            'artisan': ana,
            'featured': False,
            'active': True,
        },
    ]

    for prod in products_data:
        if prod['category'] and prod['artisan']:
            Product.objects.get_or_create(slug=prod['slug'], defaults=prod)

    print("[DEMO] Datos de prueba creados exitosamente.")

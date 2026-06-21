"""Inicializa la base de datos SQLite de desarrollo y siembra datos de ejemplo."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_yanacona.settings_dev')
django.setup()

from django.db import connection
from django.apps import apps
from store.models import Category, Artisan, Product, User, Order, OrderItem, Contact, CartItem

# 1. Crear todas las tablas (incluidas las managed=False) si no existen
existing = set(connection.introspection.table_names())
with connection.schema_editor() as editor:
    for model in apps.get_models():
        if model._meta.db_table not in existing:
            try:
                editor.create_model(model)
                print(f"  + tabla creada: {model._meta.db_table}")
            except Exception as e:
                print(f"  ! {model._meta.db_table}: {e}")

# 2. Sembrar datos solo si no hay usuarios
if User.objects.exists():
    print("Datos ya existen, se omite el seed.")
else:
    print("Sembrando datos de ejemplo...")

    admin = User(name="Administrador", email="admin@onel.com", role="admin",
                 phone="3101234567", city="Puerto Caicedo", address="Cabildo Yanacona")
    admin.set_password("admin123")
    admin.save()

    cliente = User(name="María Cliente", email="cliente@onel.com", role="customer",
                   phone="3119876543", city="Mocoa", address="Calle 5 #4-3")
    cliente.set_password("cliente123")
    cliente.save()

    cats = {}
    for name, slug, desc in [
        ("Cestería", "cesteria", "Cestos y canastos tejidos a mano"),
        ("Tejidos", "tejidos", "Mochilas y textiles tradicionales"),
        ("Cerámica", "ceramica", "Piezas de barro y arcilla"),
        ("Joyería", "joyeria", "Accesorios artesanales en chaquira"),
    ]:
        cats[slug] = Category.objects.create(name=name, slug=slug, description=desc)

    artesanos = {}
    for name, slug, spec, bio in [
        ("Rosa Anacona", "rosa-anacona", "Cestería", "Maestra tejedora con 30 años de experiencia."),
        ("Juan Jajoy", "juan-jajoy", "Cerámica", "Alfarero tradicional del pueblo Yanacona."),
        ("Luz Quinayás", "luz-quinayas", "Tejidos", "Especialista en mochilas de lana virgen."),
    ]:
        artesanos[slug] = Artisan.objects.create(name=name, slug=slug, specialty=spec, bio=bio, active=True)

    productos = [
        ("Canasto Tradicional", "canasto-tradicional", 45000, 12, "cesteria", "rosa-anacona", True),
        ("Mochila Yanacona", "mochila-yanacona", 120000, 8, "tejidos", "luz-quinayas", True),
        ("Vasija de Barro", "vasija-de-barro", 65000, 5, "ceramica", "juan-jajoy", True),
        ("Collar de Chaquira", "collar-de-chaquira", 35000, 20, "joyeria", "rosa-anacona", False),
        ("Individual Tejido", "individual-tejido", 25000, 30, "cesteria", "rosa-anacona", False),
        ("Olla de Arcilla", "olla-de-arcilla", 80000, 4, "ceramica", "juan-jajoy", True),
    ]
    for name, slug, price, stock, cat, art, feat in productos:
        Product.objects.create(
            name=name, slug=slug, price=price, stock=stock,
            category=cats[cat], artisan=artesanos[art],
            featured=feat, active=True,
            description=f"{name} hecho a mano por artesanos del pueblo Yanacona.",
        )

    Contact.objects.create(name="Pedro López", email="pedro@mail.com",
                           phone="3001112233", message="¿Hacen envíos a Bogotá?")

    print("Seed completado.")
    print("  Admin:   admin@onel.com / admin123")
    print("  Cliente: cliente@onel.com / cliente123")

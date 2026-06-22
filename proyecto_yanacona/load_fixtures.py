import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_yanacona.settings')
django.setup()

from store.models import Product, Category, Artisan, User
from django.core.files.images import ImageFile
from django.conf import settings
import random

# Crear categorías si no existen
categories_data = [
    {'name': 'Cestería', 'slug': 'cesteria', 'description': 'Productos de cestería tradicional'},
    {'name': 'Cerámica', 'slug': 'ceramica', 'description': 'Cerámica tradicional Yanacona'},
    {'name': 'Tejido', 'slug': 'tejido', 'description': 'Tejidos artesanales'},
    {'name': 'Joyería', 'slug': 'joyeria', 'description': 'Joyería artesanal'},
    {'name': 'Madera', 'slug': 'madera', 'description': 'Trabajos en madera'},
]

for cat_data in categories_data:
    Category.objects.get_or_create(slug=cat_data['slug'], defaults=cat_data)

print("✅ Categorías creadas")

# Crear artesanos si no existen
artisans_data = [
    {'name': 'María Lucumí', 'slug': 'maria-lucumi', 'specialty': 'Cestería', 'bio': 'Artesana con 20 años de experiencia en cestería tradicional.', 'active': True},
    {'name': 'Luis Yalanda', 'slug': 'luis-yalanda', 'specialty': 'Cerámica', 'bio': 'Maestro ceramista, heredero de técnicas ancestrales.', 'active': True},
    {'name': 'Rosa Pillimue', 'slug': 'rosa-pillimue', 'specialty': 'Tejido', 'bio': 'Tejedora experta en diseños tradicionales Yanacona.', 'active': True},
    {'name': 'Ana Waira', 'slug': 'ana-waira', 'specialty': 'Joyería', 'bio': 'Creadora de joyería con materiales naturales del Putumayo.', 'active': True},
    {'name': 'Carlos Taita', 'slug': 'carlos-taita', 'specialty': 'Madera', 'bio': 'Tallador de madera con técnicas ancestrales.', 'active': True},
]

for art_data in artisans_data:
    Artisan.objects.get_or_create(slug=art_data['slug'], defaults=art_data)

print("✅ Artesanos creados")

# Crear productos de ejemplo
products_data = [
    {'name': 'Bolso Tejido Yanacona', 'slug': 'bolso-tejido-yanacona', 'description': 'Bolso tejido a mano con fibras naturales del Putumayo. Diseño tradicional Yanacona con colores vibrantes.', 'price': 120000, 'stock': 8, 'category_slug': 'cesteria', 'artisan_slug': 'maria-lucumi', 'active': True, 'featured': True},
    {'name': 'Cuenco Cerámico Tradicional', 'slug': 'cuenco-ceramico-tradicional', 'description': 'Cuenco de cerámica hecho a mano con técnicas ancestrales. Pintado con pigmentos naturales.', 'price': 85000, 'stock': 12, 'category_slug': 'ceramica', 'artisan_slug': 'luis-yalanda', 'active': True, 'featured': True},
    {'name': 'Tapiz Yanacona', 'slug': 'tapiz-yanacona', 'description': 'Tapiz tejido en telar tradicional con lana de oveja y tintes naturales.', 'price': 150000, 'stock': 5, 'category_slug': 'tejido', 'artisan_slug': 'rosa-pillimue', 'active': True, 'featured': True},
    {'name': 'Collar de Semillas', 'slug': 'collar-semillas', 'description': 'Collar artesanal elaborado con semillas naturales de la región amazónica.', 'price': 45000, 'stock': 20, 'category_slug': 'joyeria', 'artisan_slug': 'ana-waira', 'active': True, 'featured': False},
    {'name': 'Máscara Tallada en Madera', 'slug': 'mascara-madera', 'description': 'Máscara tradicional tallada en madera de ceiba con técnicas ancestrales.', 'price': 180000, 'stock': 3, 'category_slug': 'madera', 'artisan_slug': 'carlos-taita', 'active': True, 'featured': True},
    {'name': 'Canasta de Fibra Natural', 'slug': 'canasta-fibra-natural', 'description': 'Canasta tejida con fibras de chambira recolectadas de forma sostenible.', 'price': 95000, 'stock': 15, 'category_slug': 'cesteria', 'artisan_slug': 'maria-lucumi', 'active': True, 'featured': False},
    {'name': 'Jarrón Cerámico Pintado', 'slug': 'jarron-ceramico', 'description': 'Jarrón de cerámica con pinturas tradicionales que representan la naturaleza.', 'price': 110000, 'stock': 7, 'category_slug': 'ceramica', 'artisan_slug': 'luis-yalanda', 'active': True, 'featured': False},
    {'name': 'Chal Tejido a Mano', 'slug': 'chal-tejido', 'description': 'Chal suave tejido a mano con lana de alpaca y diseños geométricos.', 'price': 135000, 'stock': 10, 'category_slug': 'tejido', 'artisan_slug': 'rosa-pillimue', 'active': True, 'featured': False},
    {'name': 'Aretes de Tagua', 'slug': 'aretes-tagua', 'description': 'Aretes elaborados con tagua (marfil vegetal) tallado a mano.', 'price': 35000, 'stock': 25, 'category_slug': 'joyeria', 'artisan_slug': 'ana-waira', 'active': True, 'featured': False},
    {'name': 'Bowl de Madera Tallada', 'slug': 'bowl-madera', 'description': 'Bowl decorativo tallado en madera de palo sangre con acabado natural.', 'price': 75000, 'stock': 6, 'category_slug': 'madera', 'artisan_slug': 'carlos-taita', 'active': True, 'featured': False},
]

for prod_data in products_data:
    category = Category.objects.filter(slug=prod_data['category_slug']).first()
    artisan = Artisan.objects.filter(slug=prod_data['artisan_slug']).first()

    if category and artisan:
        prod_defaults = {
            'description': prod_data['description'],
            'price': prod_data['price'],
            'stock': prod_data['stock'],
            'category': category,
            'artisan': artisan,
            'active': prod_data['active'],
            'featured': prod_data['featured'],
        }
        Product.objects.get_or_create(slug=prod_data['slug'], defaults=prod_defaults)

print("✅ Productos creados")
print(f"
📊 Total en base de datos:")
print(f"   Categorías: {Category.objects.count()}")
print(f"   Artesanos: {Artisan.objects.count()}")
print(f"   Productos: {Product.objects.count()}")

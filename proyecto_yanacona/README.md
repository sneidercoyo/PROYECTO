# O'NEL Artesanías — E-Commerce Django

E-commerce para el Cabildo Yanacona de Puerto Caicedo, Putumayo.

## ⚠️ DIFERENCIA IMPORTANTE

- **Panel Admin Django** (`/admin/`) — Para gestionar la tienda (productos, órdenes, usuarios)
- **Login de la Web** (`/login/`) — Para clientes comprar en la tienda

Son dos sistemas separados.

## Requisitos

- Python 3.10+
- MySQL 8.0+

## Instalación Rápida

```bash
# 1. Descomprimir y entrar
cd proyecto_yanacona

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Crear superusuario de Django (para /admin/)
python manage.py createsuperuser
# Usuario: admin
# Email: admin@onel.com
# Contraseña: admin123

# 6. Verificar base de datos
python manage.py inspectdb

# 7. Iniciar servidor
python manage.py runserver
```

## Usuarios Pre-creados (Base de Datos)

Los siguientes usuarios ya están en tu base de datos MySQL:

| Usuario | Contraseña | Rol | Uso |
|---------|-----------|-----|-----|
| **ESNEIDER** | `123` | Cliente | Login en la web (`/login/`) |
| **admin@onel.com** | `admin123` | Admin | Login en la web (`/login/`) |
| **cliente@demo.com** | `password` | Cliente | Login en la web (`/login/`) |

## Accesos

| URL | Descripción | Credenciales |
|-----|-------------|--------------|
| `http://localhost:8000/` | Tienda O'NEL | — |
| `http://localhost:8000/admin/` | Panel Admin Django | El que creaste con `createsuperuser` |
| `http://localhost:8000/login/` | Login Clientes | ESNEIDER / 123 |

## Panel Admin Django — Estilizado

El panel de administración tiene los colores de la página:
- Header con gradiente marrón
- Breadcrumbs arcoíris
- Botones con gradiente multicolor
- Login con logo y estilo de la tienda

## Estructura

```
proyecto_yanacona/
├── manage.py
├── requirements.txt
├── proyecto_yanacona/          # Configuración Django
│   ├── settings.py             # MySQL (root / Esneider#1)
│   ├── urls.py
│   └── ...
├── store/                       # App principal
│   ├── models.py               # Tablas con managed=False
│   ├── admin.py                # Panel admin configurado
│   ├── views.py                # Vistas de la tienda
│   └── ...
├── templates/
│   ├── base.html               # Layout principal
│   ├── store/                  # Templates de la tienda
│   └── admin/                  # Templates del admin personalizado
│       ├── base_site.html      # Estilo del admin
│       └── login.html          # Login del admin estilizado
├── static/
│   ├── css/style.css           # Estilos de la tienda
│   ├── js/main.js              # JavaScript
│   └── images/                 # Logo e imágenes
└── usuarios.sql                # Script SQL de usuarios
```

## Características

- Catálogo de productos con filtros y búsqueda
- Carrito de compras persistente
- Checkout con datos de envío
- Perfil de usuario con historial de órdenes
- Panel de administración estilizado
- Diseño responsive con tema artesanal

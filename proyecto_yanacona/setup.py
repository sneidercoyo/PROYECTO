#!/usr/bin/env python
"""
SCRIPT DE CONFIGURACIÓN — O'NEL Artesanías
Ejecutar después de descomprimir el ZIP
"""

import os
import sys

print("=" * 50)
print("CONFIGURACIÓN O'NEL ARTESANIAS")
print("=" * 50)

# 1. Verificar entorno virtual
print("\n[1/4] Verificando entorno virtual...")
if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
    print("✅ Entorno virtual activado")
else:
    print("⚠️  Activa el entorno virtual primero:")
    print("   Windows: venv\Scripts\activate")
    print("   Linux/Mac: source venv/bin/activate")
    sys.exit(1)

# 2. Instalar dependencias
print("\n[2/4] Instalando dependencias...")
os.system("pip install -r requirements.txt")

# 3. Crear superusuario Django
print("\n[3/4] Creando superusuario de Django...")
print("   Ejecuta: python manage.py createsuperuser")
print("   Usuario sugerido: admin")
print("   Email: admin@onel.com")
print("   Contraseña: admin123")

# 4. Instrucciones para usuarios de la web
print("\n[4/4] Usuarios de la web (ya creados en la base de datos):")
print("   👤 ESNEIDER / 123 (cliente)")
print("   👤 admin@onel.com / admin123 (administrador)")
print("   👤 cliente@demo.com / password (demo)")

print("\n" + "=" * 50)
print("Para iniciar el servidor:")
print("   python manage.py runserver")
print("=" * 50)

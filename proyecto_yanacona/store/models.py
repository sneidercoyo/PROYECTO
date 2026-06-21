from django.db import models
from django.contrib.auth.hashers import make_password, check_password as django_check_password


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Descripción")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'categories'
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['name']
        managed = False

    def __str__(self):
        return self.name


class Artisan(models.Model):
    name = models.CharField(max_length=150, verbose_name="Nombre")
    slug = models.SlugField(max_length=150, unique=True, verbose_name="Slug")
    bio = models.TextField(blank=True, verbose_name="Biografía")
    specialty = models.CharField(max_length=100, verbose_name="Especialidad")
    image = models.ImageField(upload_to='artisans/', blank=True, verbose_name="Imagen")
    active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'artisans'
        verbose_name = "Artesano"
        verbose_name_plural = "Artesanos"
        ordering = ['name']
        managed = False

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Descripción")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock")
    image = models.ImageField(upload_to='products/', blank=True, verbose_name="Imagen")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Categoría")
    artisan = models.ForeignKey(Artisan, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Artesano")
    featured = models.BooleanField(default=False, verbose_name="Destacado")
    active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['-created_at']
        managed = False

    def __str__(self):
        return self.name

    def formatted_price(self):
        return f"${self.price:,.0f}"


class User(models.Model):
    ROLE_CHOICES = [
        ('customer', 'Cliente'),
        ('admin', 'Administrador'),
    ]
    name = models.CharField(max_length=150, verbose_name="Nombre")
    email = models.EmailField(max_length=150, unique=True, verbose_name="Correo")
    password = models.CharField(max_length=255, verbose_name="Contraseña")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    address = models.TextField(blank=True, verbose_name="Dirección")
    city = models.CharField(max_length=100, blank=True, verbose_name="Ciudad")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer', verbose_name="Rol")
    active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['-created_at']
        managed = False

    def __str__(self):
        return self.name

    def set_password(self, raw_password):
        import bcrypt
        hashed = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt())
        self.password = hashed.decode('utf-8').replace('$2b$', '$2y$')

    def check_password(self, raw_password):
        import bcrypt
        try:
            hashed = self.password.replace('$2y$', '$2b$')
            return bcrypt.checkpw(raw_password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False

    def is_admin(self):
        return self.role == 'admin'


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('processing', 'En proceso'),
        ('shipped', 'Enviado'),
        ('delivered', 'Entregado'),
        ('cancelled', 'Cancelado'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuario")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Estado")
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total")
    shipping_name = models.CharField(max_length=150, blank=True, verbose_name="Nombre de envío")
    shipping_address = models.TextField(blank=True, verbose_name="Dirección de envío")
    shipping_city = models.CharField(max_length=100, blank=True, verbose_name="Ciudad de envío")
    shipping_phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono de envío")
    notes = models.TextField(blank=True, verbose_name="Notas")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'
        verbose_name = "Orden"
        verbose_name_plural = "Órdenes"
        ordering = ['-created_at']
        managed = False

    def __str__(self):
        return f"Orden #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Orden")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Producto")
    product_name = models.CharField(max_length=200, verbose_name="Nombre del producto")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    quantity = models.PositiveIntegerField(verbose_name="Cantidad")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal")

    class Meta:
        db_table = 'order_items'
        verbose_name = "Item de Orden"
        verbose_name_plural = "Items de Orden"
        managed = False

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"


class Contact(models.Model):
    name = models.CharField(max_length=150, verbose_name="Nombre")
    email = models.EmailField(max_length=150, verbose_name="Correo")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    message = models.TextField(verbose_name="Mensaje")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="Leído el")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'contacts'
        verbose_name = "Mensaje de Contacto"
        verbose_name_plural = "Mensajes de Contacto"
        ordering = ['-created_at']
        managed = True  # <-- CAMBIO: Django gestiona esta tabla

    def __str__(self):
        return f"Mensaje de {self.name}"


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Producto")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Cantidad")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cart_items'
        verbose_name = "Item de Carrito"
        verbose_name_plural = "Items de Carrito"
        unique_together = ('user', 'product')
        ordering = ['-created_at']
        managed = True  # <-- CAMBIO: Django gestiona esta tabla

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def subtotal(self):
        return self.product.price * self.quantity

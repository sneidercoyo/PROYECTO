from django.urls import path
from . import views

urlpatterns = [
    # Publicas
    path('', views.home, name='home'),
    path('tienda/', views.shop, name='shop'),
    path('producto/<slug:slug>/', views.product_detail, name='product_detail'),
    path('artesanos/', views.artisans, name='artisans'),
    path('artesano/<slug:slug>/', views.artisan_detail, name='artisan_detail'),
    path('nosotros/', views.about, name='about'),
    path('contacto/', views.contact, name='contact'),

    # Auth
    path('login/', views.login_view, name='login'),
    path('registro/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.profile, name='profile'),

    # Carrito
    path('carrito/', views.cart, name='cart'),
    path('carrito/agregar/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('carrito/actualizar/<int:item_id>/', views.update_cart, name='update_cart'),
    path('carrito/eliminar/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Checkout
    path('checkout/', views.checkout, name='checkout'),

    # Panel Administrador
    path('administrador/', views.admin_dashboard, name='admin_dashboard'),
    path('administrador/pedidos/', views.admin_orders, name='admin_orders'),
    path('administrador/pedidos/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('administrador/productos/', views.admin_products, name='admin_products'),
    path('administrador/productos/nuevo/', views.admin_add_product, name='admin_add_product'),
    path('administrador/productos/editar/<int:product_id>/', views.admin_edit_product, name='admin_edit_product'),
    path('administrador/productos/eliminar/<int:product_id>/', views.admin_delete_product, name='admin_delete_product'),
    path('administrador/categorias/', views.admin_categories, name='admin_categories'),
    path('administrador/categorias/nueva/', views.admin_add_category, name='admin_add_category'),
    path('administrador/categorias/editar/<int:category_id>/', views.admin_edit_category, name='admin_edit_category'),
    path('administrador/categorias/eliminar/<int:category_id>/', views.admin_delete_category, name='admin_delete_category'),
    path('administrador/artesanos/', views.admin_artisans, name='admin_artisans'),
    path('administrador/artesanos/nuevo/', views.admin_add_artisan, name='admin_add_artisan'),
    path('administrador/artesanos/editar/<int:artisan_id>/', views.admin_edit_artisan, name='admin_edit_artisan'),
    path('administrador/usuarios/', views.admin_users, name='admin_users'),
    path('administrador/usuarios/editar/<int:user_id>/', views.admin_edit_user, name='admin_edit_user'),
    path('administrador/mensajes/', views.admin_contacts, name='admin_contacts'),
    path('administrador/mensajes/<int:contact_id>/', views.admin_contact_detail, name='admin_contact_detail'),

    # Panel Artesano - COMPLETO
    path('artesano-panel/', views.artisan_dashboard, name='artisan_dashboard'),
    path('artesano-panel/perfil/', views.artisan_profile, name='artisan_profile'),
    path('artesano-panel/perfil/editar/', views.artisan_edit_profile, name='artisan_edit_profile'),
    path('artesano-panel/productos/', views.artisan_products, name='artisan_products'),
    path('artesano-panel/productos/nuevo/', views.artisan_add_product, name='artisan_add_product'),
    path('artesano-panel/productos/editar/<int:product_id>/', views.artisan_edit_product, name='artisan_edit_product'),
    path('artesano-panel/productos/eliminar/<int:product_id>/', views.artisan_delete_product, name='artisan_delete_product'),
    path('artesano-panel/productos/<int:product_id>/toggle/', views.artisan_toggle_product, name='artisan_toggle_product'),
    path('artesano-panel/pedidos/', views.artisan_orders, name='artisan_orders'),
    path('artesano-panel/pedidos/<int:order_id>/', views.artisan_order_detail, name='artisan_order_detail'),
    path('artesano-panel/estadisticas/', views.artisan_stats, name='artisan_stats'),
    path('artesano-panel/stock/', views.artisan_stock, name='artisan_stock'),
]

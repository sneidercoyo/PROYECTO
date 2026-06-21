from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tienda/', views.shop, name='shop'),
    path('producto/<slug:slug>/', views.product_detail, name='product_detail'),
    path('artesanos/', views.artisans, name='artisans'),
    path('artesano/<slug:slug>/', views.artisan_detail, name='artisan_detail'),
    path('nosotros/', views.about, name='about'),
    path('contacto/', views.contact, name='contact'),
    path('login/', views.login_view, name='login'),
    path('registro/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.profile, name='profile'),
    path('carrito/', views.cart, name='cart'),
    path('carrito/agregar/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('carrito/actualizar/<int:item_id>/', views.update_cart, name='update_cart'),
    path('carrito/eliminar/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),

    # Panel de Administrador
    path('panel/', views.admin_dashboard, name='admin_dashboard'),
    path('panel/productos/', views.admin_products, name='admin_products'),
    path('panel/productos/nuevo/', views.admin_add_product, name='admin_add_product'),
    path('panel/productos/<int:product_id>/editar/', views.admin_edit_product, name='admin_edit_product'),
    path('panel/artesanos/', views.admin_artisans, name='admin_artisans'),
    path('panel/artesanos/nuevo/', views.admin_add_artisan, name='admin_add_artisan'),
    path('panel/artesanos/<int:artisan_id>/editar/', views.admin_edit_artisan, name='admin_edit_artisan'),
    path('panel/categorias/', views.admin_categories, name='admin_categories'),
    path('panel/categorias/nueva/', views.admin_add_category, name='admin_add_category'),
    path('panel/categorias/<int:category_id>/editar/', views.admin_edit_category, name='admin_edit_category'),
    path('panel/pedidos/', views.admin_orders, name='admin_orders'),
    path('panel/pedidos/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('panel/usuarios/', views.admin_users, name='admin_users'),
    path('panel/usuarios/<int:user_id>/editar/', views.admin_edit_user, name='admin_edit_user'),
    path('panel/mensajes/', views.admin_contacts, name='admin_contacts'),
    path('panel/mensajes/<int:contact_id>/', views.admin_contact_detail, name='admin_contact_detail'),

    # Panel de Artesano
    path('panel-artesano/', views.artisan_dashboard, name='artisan_dashboard'),
    path('panel-artesano/productos/', views.artisan_products, name='artisan_products'),
    path('panel-artesano/productos/nuevo/', views.artisan_add_product, name='artisan_add_product'),
    path('panel-artesano/productos/<int:product_id>/editar/', views.artisan_edit_product, name='artisan_edit_product'),
    path('panel-artesano/pedidos/', views.artisan_orders, name='artisan_orders'),
    path('panel-artesano/pedidos/<int:order_id>/', views.artisan_order_detail, name='artisan_order_detail'),
]

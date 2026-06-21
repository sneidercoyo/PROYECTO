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
]

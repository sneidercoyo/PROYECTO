from django.contrib import admin
from .models import Category, Artisan, Product, User, Order, OrderItem, Contact, CartItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Artisan)
class ArtisanAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialty', 'active', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('active', 'specialty')
    search_fields = ('name', 'bio')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category', 'artisan', 'featured', 'active')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('category', 'featured', 'active')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock', 'featured', 'active')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'role', 'active', 'created_at')
    list_filter = ('role', 'active')
    search_fields = ('name', 'email')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'price', 'quantity', 'subtotal')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total', 'created_at')
    list_filter = ('status',)
    search_fields = ('shipping_name', 'shipping_phone')
    inlines = [OrderItemInline]
    list_editable = ('status',)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'read_at', 'created_at')
    search_fields = ('name', 'email', 'message')
    list_filter = ('read_at',)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'created_at')
    list_filter = ('user',)

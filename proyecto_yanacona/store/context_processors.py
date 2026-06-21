from .models import Category, CartItem


def cart_context(request):
    user_id = request.session.get('user_id')
    cart_count = 0
    if user_id:
        cart_count = CartItem.objects.filter(user_id=user_id).count()
    return {'cart_count': cart_count}


def categories_context(request):
    return {'all_categories': Category.objects.all()}

def admin_edit_category(request, category_id):
    user = require_admin(request)
    if not user:
        messages.error(request, "Acceso restringido a administradores.")
        return redirect('login')

    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        category.name = request.POST.get('name', category.name)
        category.slug = request.POST.get('slug', category.slug)
        category.description = request.POST.get('description', '')
        category.save()
        messages.success(request, f"Categoría '{category.name}' actualizada.")
        return redirect('admin_categories')

    return render(request, 'store/admin_edit_category.html', {'category': category})

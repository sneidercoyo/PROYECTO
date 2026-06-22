def admin_add_artisan(request):
    user = require_admin(request)
    if not user:
        messages.error(request, "Acceso restringido a administradores.")
        return redirect('login')

    if request.method == 'POST':
        # Datos del usuario
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')
        city = request.POST.get('city', '')

        # Datos del artesano
        slug = request.POST.get('slug') or slugify(name)
        slug = unique_slug(Artisan, slug)
        bio = request.POST.get('bio', '')
        specialty = request.POST.get('specialty', '')
        active = request.POST.get('active') == 'on'

        # Validar que el email no exista
        if User.objects.filter(email=email).exists():
            messages.error(request, "El correo ya está registrado.")
            return redirect('admin_add_artisan')

        # Crear el usuario (artesano)
        new_user = User.objects.create(
            name=name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            role='artisan'  # Rol de artesano
        )
        new_user.set_password(password)
        new_user.save()

        # Crear el perfil de artesano vinculado al usuario
        artisan = Artisan.objects.create(
            name=name,
            slug=slug,
            bio=bio,
            specialty=specialty,
            active=active
        )

        messages.success(request, f"Artesano '{name}' creado exitosamente! Puede iniciar sesión con: {email}")
        return redirect('admin_artisans')

    return render(request, 'store/admin_add_artisan.html')

// O'NEL Artesanías — JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts
    const alerts = document.querySelectorAll('.alert-exact');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'all 0.5s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-20px)';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // Quantity selector
    const quantityInputs = document.querySelectorAll('.quantity-selector input');
    quantityInputs.forEach(input => {
        const min = parseInt(input.min) || 1;
        const max = parseInt(input.max) || 99;
        input.addEventListener('change', function() {
            let val = parseInt(this.value);
            if (val < min) this.value = min;
            if (val > max) this.value = max;
        });
    });

    // Wishlist toggle
    const wishlistBtns = document.querySelectorAll('.product-wishlist');
    wishlistBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const icon = this.querySelector('i');
            if (icon.classList.contains('bi-heart')) {
                icon.classList.remove('bi-heart');
                icon.classList.add('bi-heart-fill');
                this.style.background = '#E74C3C';
                this.style.color = 'white';
                this.style.borderColor = '#E74C3C';
            } else {
                icon.classList.remove('bi-heart-fill');
                icon.classList.add('bi-heart');
                this.style.background = 'white';
                this.style.color = '#E74C3C';
                this.style.borderColor = '#E8DDD0';
            }
        });
    });

    // Mobile menu
    const mobileToggle = document.querySelector('.mobile-toggle');
    const navMenu = document.querySelector('.nav-menu');
    if (mobileToggle && navMenu) {
        mobileToggle.addEventListener('click', function() {
            navMenu.classList.toggle('mobile-open');
            const icon = this.querySelector('i');
            if (navMenu.classList.contains('mobile-open')) {
                icon.classList.remove('bi-list');
                icon.classList.add('bi-x-lg');
            } else {
                icon.classList.remove('bi-x-lg');
                icon.classList.add('bi-list');
            }
        });
    }
});

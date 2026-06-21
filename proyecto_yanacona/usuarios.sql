-- ============================================
-- USUARIOS PARA O'NEL ARTESANIAS
-- ============================================

USE onel_artesanias;

-- Usuario ESNEIDER para la web (rol: customer)
-- Contraseña: 123 (hasheada con bcrypt)
INSERT INTO users (name, email, password, phone, address, city, role, active, created_at) VALUES
('ESNEIDER', 'esneider@onel.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '3101234567', 'Puerto Caicedo', 'Putumayo', 'customer', 1, NOW())
ON DUPLICATE KEY UPDATE name='ESNEIDER', password='$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi';

-- Superusuario para Django Admin (rol: admin)
-- Usuario: admin / Contraseña: admin123
INSERT INTO users (name, email, password, role, active, created_at) VALUES
('Administrador', 'admin@onel.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'admin', 1, NOW())
ON DUPLICATE KEY UPDATE name='Administrador', password='$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi';

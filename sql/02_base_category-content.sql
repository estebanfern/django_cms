-- Inserción de datos en la tabla `category`
INSERT INTO category (name, description, is_active, is_moderated, price, date_create, type)
VALUES
('Tecnología', 'Categoría sobre tecnología y gadgets', TRUE, TRUE, 49.99, NOW(), 'Pago'),
('Educación', 'Categoría de recursos educativos gratuitos', TRUE, TRUE, NULL, NOW(), 'Publico'),
('Entretenimiento', 'Categoría de contenido para suscriptores', TRUE, TRUE, NULL, NOW(), 'Suscriptor');

-- Inserción de datos en la tabla `content` usando PostgreSQL
INSERT INTO content (title, summary, category_id, autor_id, is_active, date_create, date_expire, state)
VALUES
('Introducción a la IA', 'Un resumen sobre los fundamentos de la inteligencia artificial', 1, 1, TRUE, NOW(), NOW() + INTERVAL '1 year', 'Publicado'),
('Guía de Estudio para Exámenes', 'Consejos y recursos para preparar exámenes eficientemente', 2, 1, TRUE, NOW(), NOW() + INTERVAL '1 year', 'Revisión')

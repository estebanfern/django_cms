-- Inserción de datos en la tabla `category`
INSERT INTO category (name, description, is_active, is_moderated, price, date_create, type)
VALUES
('Tecnología', 'Categoría sobre tecnología y gadgets', TRUE, TRUE, 49.99, NOW(), 'Pago'),  -- No vacía
('Educación', 'Categoría de recursos educativos gratuitos', TRUE, TRUE, NULL, NOW(), 'Publico'),  -- No vacía
('Entretenimiento', 'Categoría de contenido para suscriptores', TRUE, TRUE, NULL, NOW(), 'Suscriptor'),  -- Vacía
('Salud', 'Categoría sobre salud y bienestar', TRUE, TRUE, NULL, NOW(), 'Publico'),  -- Vacía
('Negocios', 'Categoría enfocada en el mundo empresarial', TRUE, TRUE, 29.99, NOW(), 'Pago'),  -- Vacía
('Cocina', 'Categoría de recetas y consejos de cocina', TRUE, TRUE, NULL, NOW(), 'Publico'),  -- No vacía
('Deportes', 'Categoría sobre deportes y actividades físicas', TRUE, TRUE, 19.99, NOW(), 'Pago'),  -- No vacía
('Viajes', 'Categoría de guías y consejos para viajar', TRUE, TRUE, NULL, NOW(), 'Suscriptor'),  -- Vacía
('Arte', 'Categoría sobre arte y cultura', TRUE, TRUE, NULL, NOW(), 'Publico'),  -- No vacía
('Ciencia', 'Categoría de artículos científicos y avances', TRUE, TRUE, 39.99, NOW(), 'Pago');  -- No vacía

-- Inserción de datos en la tabla `content`
INSERT INTO content (title, summary, category_id, autor_id, is_active, date_create, date_expire, state)
VALUES
('Introducción a la IA', 'Un resumen sobre los fundamentos de la inteligencia artificial', 1, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', 'Publicado'),
('Guía de Estudio para Exámenes', 'Consejos y recursos para preparar exámenes eficientemente', 2, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', 'Revisión'),
('Últimos Gadgets de 2024', 'Revisión de los gadgets más innovadores del año', 1, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', 'Publicado'),
('Recetas Fáciles para el Día a Día', 'Platos sencillos y rápidos para tu día a día', 2, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', 'Publicado'),
('Beneficios del Yoga', 'Cómo el yoga puede mejorar tu salud física y mental', 3, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', 'Publicado'),
('Estrategias de Negociación', 'Aprende técnicas efectivas para negociar en el ámbito empresarial', 5, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', 'A publicar'),
('Rutinas de Ejercicio en Casa', 'Entrenamientos efectivos para realizar desde casa', 5, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', 'Revisión'),
('Destinos Exóticos para Viajar', 'Explora los destinos más exóticos del mundo', 5, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', 'Publicado'),
('Historia del Arte Moderno', 'Un recorrido por el arte moderno y sus principales exponentes', 5, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', 'A publicar'),
('Avances en Biotecnología', 'Últimos avances y descubrimientos en biotecnología', 10, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', 'Publicado');

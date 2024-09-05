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

-- Inserción de datos en la tabla `content` con los estados ajustados
INSERT INTO content (title, summary, category_id, autor_id, is_active, date_create, date_expire, state)
VALUES
-- Contenidos existentes con estados ajustados
('Introducción a la IA', 'Un resumen sobre los fundamentos de la inteligencia artificial', 1, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', 'publish'),
('Guía de Estudio para Exámenes', 'Consejos y recursos para preparar exámenes eficientemente', 2, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', 'revision'),
('Últimos Gadgets de 2024', 'Revisión de los gadgets más innovadores del año', 1, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', 'publish'),
('Recetas Fáciles para el Día a Día', 'Platos sencillos y rápidos para tu día a día', 2, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', 'publish'),
('Beneficios del Yoga', 'Cómo el yoga puede mejorar tu salud física y mental', 3, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', 'publish'),
('Estrategias de Negociación', 'Aprende técnicas efectivas para negociar en el ámbito empresarial', 5, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', 'to_publish'),
('Rutinas de Ejercicio en Casa', 'Entrenamientos efectivos para realizar desde casa', 5, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', 'revision'),
('Destinos Exóticos para Viajar', 'Explora los destinos más exóticos del mundo', 5, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', 'publish'),
('Historia del Arte Moderno', 'Un recorrido por el arte moderno y sus principales exponentes', 5, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', 'to_publish'),
('Avances en Biotecnología', 'Últimos avances y descubrimientos en biotecnología', 10, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', 'publish'),
('Fundamentos de Programación', 'Introducción a los conceptos básicos de programación', 1, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', 'draft'),
('Cómo Meditar', 'Guía paso a paso para empezar a meditar', 3, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', 'revision'),
('El Impacto de la Inteligencia Artificial en la Medicina', 'Explorando cómo la IA está cambiando la medicina moderna', 10, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', 'to_publish'),
('Tips de Fotografía para Principiantes', 'Consejos básicos para mejorar tus fotos', 4, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', 'publish'),
('Nutrición y Salud', 'Cómo una buena nutrición puede cambiar tu vida', 3, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', 'inactive'),
('Aprende a Tocar la Guitarra', 'Guía para principiantes para tocar guitarra', 7, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', 'draft'),
('Cocina Internacional', 'Descubre recetas de diferentes partes del mundo', 6, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', 'publish'),
('Mindfulness en el Trabajo', 'Cómo aplicar mindfulness en tu vida profesional', 8, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', 'to_publish'),
('Historia de la Música Clásica', 'Desde Bach hasta Beethoven, una historia completa', 9, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', 'revision'),
('Desarrollo de Apps Móviles', 'Todo lo que necesitas saber para empezar a desarrollar apps', 1, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', 'draft');

-- Inserción de datos en la tabla `category`
INSERT INTO category (name, description, is_active, is_moderated, price, date_create, type)
VALUES
('Tecnología', 'Categoría sobre tecnología y gadgets', TRUE, TRUE, 49.99, NOW(), 'Pago'),
('Educación', 'Categoría de recursos educativos gratuitos', TRUE, TRUE, NULL, NOW(), 'Publico'),
('Entretenimiento', 'Categoría de contenido para suscriptores', TRUE, TRUE, NULL, NOW(), 'Suscriptor'),
('Salud', 'Categoría sobre salud y bienestar', TRUE, TRUE, NULL, NOW(), 'Publico'),  -- Vacía
('Negocios', 'Categoría enfocada en el mundo empresarial', TRUE, TRUE, 29.99, NOW(), 'Pago'),
('Cocina', 'Categoría de recetas y consejos de cocina', TRUE, TRUE, NULL, NOW(), 'Publico'),
('Deportes', 'Categoría sobre deportes y actividades físicas', TRUE, TRUE, 19.99, NOW(), 'Pago'),
('Viajes', 'Categoría de guías y consejos para viajar', TRUE, TRUE, NULL, NOW(), 'Suscriptor'),
('Arte', 'Categoría sobre arte y cultura', TRUE, TRUE, NULL, NOW(), 'Publico'),  -- No vacía
('Ciencia', 'Categoría de artículos científicos y avances', TRUE, TRUE, 39.99, NOW(), 'Pago'),
('No Moderada', 'Categoría no moderada', TRUE, FALSE, NULL, NOW(), 'Publico');

-- Inserción de datos en la tabla `content` con los nuevos campos ajustados
INSERT INTO content (
    title, summary, category_id, autor_id, is_active, date_create, date_expire, date_published, content, attachment, state
)
VALUES
-- Contenidos existentes con estados ajustados y nuevos campos
('Introducción a la IA', 'Un resumen sobre los fundamentos de la inteligencia artificial', 1, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', NULL, '<p>Contenido detallado sobre IA.</p>', NULL, 'publish'),
('Guía de Estudio para Exámenes', 'Consejos y recursos para preparar exámenes eficientemente', 2, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', NULL, '<p>Guía completa para exámenes.</p>', NULL, 'revision'),
('Últimos Gadgets de 2024', 'Revisión de los gadgets más innovadores del año', 1, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', NULL, '<p>Revisión de los gadgets más innovadores de 2024.</p>', NULL, 'publish'),
('Recetas Fáciles para el Día a Día', 'Platos sencillos y rápidos para tu día a día', 2, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', NULL, '<p>Recetas fáciles para cada día.</p>', NULL, 'publish'),
('Beneficios del Yoga', 'Cómo el yoga puede mejorar tu salud física y mental', 3, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', NULL, '<p>Beneficios del yoga explicados.</p>', NULL, 'publish'),
('Estrategias de Negociación', 'Aprende técnicas efectivas para negociar en el ámbito empresarial', 5, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', NULL, '<p>Estrategias para una negociación exitosa.</p>', NULL, 'to_publish'),
('Rutinas de Ejercicio en Casa', 'Entrenamientos efectivos para realizar desde casa', 5, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', NULL, '<p>Rutinas de ejercicio para casa.</p>', NULL, 'revision'),
('Destinos Exóticos para Viajar', 'Explora los destinos más exóticos del mundo', 5, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', NULL, '<p>Guía para destinos exóticos.</p>', NULL, 'publish'),
('Historia del Arte Moderno', 'Un recorrido por el arte moderno y sus principales exponentes', 5, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', NULL, '<p>Historia completa del arte moderno.</p>', NULL, 'to_publish'),
('Avances en Biotecnología', 'Últimos avances y descubrimientos en biotecnología', 10, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', NULL, '<p>Avances recientes en biotecnología.</p>', NULL, 'publish'),
('Fundamentos de Programación', 'Introducción a los conceptos básicos de programación', 1, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', NULL, '<p>Fundamentos de la programación.</p>', NULL, 'draft'),
('Cómo Meditar', 'Guía paso a paso para empezar a meditar', 3, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', NULL, '<p>Guía completa sobre meditación.</p>', NULL, 'revision'),
('El Impacto de la Inteligencia Artificial en la Medicina', 'Explorando cómo la IA está cambiando la medicina moderna', 10, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', NULL, '<p>IA en medicina moderna.</p>', NULL, 'to_publish'),
('Tips de Fotografía para Principiantes', 'Consejos básicos para mejorar tus fotos', 4, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', NULL, '<p>Consejos básicos de fotografía.</p>', NULL, 'publish'),
('Nutrición y Salud', 'Cómo una buena nutrición puede cambiar tu vida', 3, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', NULL, '<p>Importancia de la nutrición.</p>', NULL, 'inactive'),
('Aprende a Tocar la Guitarra', 'Guía para principiantes para tocar guitarra', 7, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', NULL, '<p>Guía para tocar guitarra.</p>', NULL, 'draft'),
('Cocina Internacional', 'Descubre recetas de diferentes partes del mundo', 6, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', NULL, '<p>Recetas internacionales.</p>', NULL, 'publish'),
('Mindfulness en el Trabajo', 'Cómo aplicar mindfulness en tu vida profesional', 8, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', NULL, '<p>Mindfulness en el entorno laboral.</p>', NULL, 'to_publish'),
('Historia de la Música Clásica', 'Desde Bach hasta Beethoven, una historia completa', 9, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', NULL, '<p>Historia de la música clásica.</p>', NULL, 'revision'),
('Desarrollo de Apps Móviles', 'Todo lo que necesitas saber para empezar a desarrollar apps', 1, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', NULL, '<p>Desarrollo de aplicaciones móviles.</p>', NULL, 'draft'),
('Contenido Expirado','Expirado' ,1, 2, TRUE, NOW(), NOW(), NULL, '<p>Contenido expirado.</p>', NULL, 'publish'),
('Contenido no moderado 1','No moderado' ,11, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', NULL, '<p>Contenido expirado.</p>', NULL, 'draft'),
('Contenido no moderado 2','No moderado' ,11, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', NULL, '<p>Contenido expirado.</p>', NULL, 'draft'),
('Contenido no moderado 3','No moderado' ,11, 2, TRUE, NOW(), NOW() + INTERVAL '1 year', NULL, '<p>Contenido expirado.</p>', NULL, 'draft');

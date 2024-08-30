--Creación de Roles
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM public.auth_group WHERE name = 'Suscriptor') THEN
        INSERT INTO public.auth_group (name) VALUES ('Suscriptor');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM public.auth_group WHERE name = 'Autor') THEN
        INSERT INTO public.auth_group (name) VALUES ('Autor');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM public.auth_group WHERE name = 'Editor') THEN
        INSERT INTO public.auth_group (name) VALUES ('Editor');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM public.auth_group WHERE name = 'Publicador') THEN
        INSERT INTO public.auth_group (name) VALUES ('Publicador');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM public.auth_group WHERE name = 'Administrador') THEN
        INSERT INTO public.auth_group (name) VALUES ('Administrador');
    END IF;
END $$;

--Adjudicación de permsos
DO $$
BEGIN
	DELETE FROM public.auth_group_permissions;
	--crear contenido a autor
	INSERT INTO public.auth_group_permissions (group_id, permission_id) VALUES (
		(SELECT id FROM public.auth_group WHERE name = 'Autor'),
		(SELECT id FROM public.auth_permission WHERE codename = 'create_content')
	);

	--editar contenido a editor
	INSERT INTO public.auth_group_permissions (group_id, permission_id) VALUES (
		(SELECT id FROM public.auth_group WHERE name = 'Editor'),
		(SELECT id FROM public.auth_permission WHERE codename = 'edit_content')
	);

	--publicar contenido a publicador
	INSERT INTO public.auth_group_permissions (group_id, permission_id) VALUES (
		(SELECT id FROM public.auth_group WHERE name = 'Publicador'),
		(SELECT id FROM public.auth_permission WHERE codename = 'publish_content')
	);

	--crear roles a administrador
	INSERT INTO public.auth_group_permissions (group_id, permission_id) VALUES (
		(SELECT id FROM public.auth_group WHERE name = 'Administrador'),
		(SELECT id FROM public.auth_permission WHERE codename = 'create_roles')
	);

	--ver roles a administrador
	INSERT INTO public.auth_group_permissions (group_id, permission_id) VALUES (
		(SELECT id FROM public.auth_group WHERE name = 'Administrador'),
		(SELECT id FROM public.auth_permission WHERE codename = 'view_roles')
	);

	--editar roles a administrador
	INSERT INTO public.auth_group_permissions (group_id, permission_id) VALUES (
		(SELECT id FROM public.auth_group WHERE name = 'Administrador'),
		(SELECT id FROM public.auth_permission WHERE codename = 'edit_roles')
	);

	--eliminar roles a administrador
	INSERT INTO public.auth_group_permissions (group_id, permission_id) VALUES (
		(SELECT id FROM public.auth_group WHERE name = 'Administrador'),
		(SELECT id FROM public.auth_permission WHERE codename = 'delete_roles')
	);

	--asignar roles a administrador
	INSERT INTO public.auth_group_permissions (group_id, permission_id) VALUES (
		(SELECT id FROM public.auth_group WHERE name = 'Administrador'),
		(SELECT id FROM public.auth_permission WHERE codename = 'assign_roles')
	);

	--quitar roles a administrador
	INSERT INTO public.auth_group_permissions (group_id, permission_id) VALUES (
		(SELECT id FROM public.auth_group WHERE name = 'Administrador'),
		(SELECT id FROM public.auth_permission WHERE codename = 'remove_roles')
	);

	--ver usuarios a administrador
	INSERT INTO public.auth_group_permissions (group_id, permission_id) VALUES (
		(SELECT id FROM public.auth_group WHERE name = 'Administrador'),
		(SELECT id FROM public.auth_permission WHERE codename = 'view_users')
	);

	--bloquear usuarios a administrador
	INSERT INTO public.auth_group_permissions (group_id, permission_id) VALUES (
		(SELECT id FROM public.auth_group WHERE name = 'Administrador'),
		(SELECT id FROM public.auth_permission WHERE codename = 'block_users')
	);

	--desbloquear usuarios a administrador
	INSERT INTO public.auth_group_permissions (group_id, permission_id) VALUES (
		(SELECT id FROM public.auth_group WHERE name = 'Administrador'),
		(SELECT id FROM public.auth_permission WHERE codename = 'unblock_users')
	);

	--Verificar en el futuro
	--comment_post
	--react_to_post
	--report_post
	--create_users
	--reset_passwords

END $$;

--Creación de usuarios de prueba
DO $$
BEGIN
	--
	-- La contraseña por defecto es: hola
	--

	--Suscriptor
	INSERT INTO public.app_customuser (password, email, name, photo, is_active, is_staff, date_joined, about, is_superuser)
	VALUES ('pbkdf2_sha256$870000$FGoSCplr3LwAJGHvtT2Nck$gnDoOSio6SeB3ryqZ7OQ4blsoMHm9+Fj2SezR2B1r04=', 'suscriptor@mail.com',
	'Suscriptor González', 'profile_pics/perfil.png', true, false, CURRENT_TIMESTAMP, 'Soy un suscriptor', false);
	--Autor
	INSERT INTO public.app_customuser (password, email, name, photo, is_active, is_staff, date_joined, about, is_superuser)
	VALUES ('pbkdf2_sha256$870000$FGoSCplr3LwAJGHvtT2Nck$gnDoOSio6SeB3ryqZ7OQ4blsoMHm9+Fj2SezR2B1r04=', 'autor@mail.com',
	'Autor Perez', 'profile_pics/perfil.png', true, false, CURRENT_TIMESTAMP, 'Soy un autor', false);
	--Editor
	INSERT INTO public.app_customuser (password, email, name, photo, is_active, is_staff, date_joined, about, is_superuser)
	VALUES ('pbkdf2_sha256$870000$FGoSCplr3LwAJGHvtT2Nck$gnDoOSio6SeB3ryqZ7OQ4blsoMHm9+Fj2SezR2B1r04=', 'editor@mail.com',
	'Editor Rodriguez', 'profile_pics/perfil.png', true, false, CURRENT_TIMESTAMP, 'Soy un editor', false);
	--Publicador
	INSERT INTO public.app_customuser (password, email, name, photo, is_active, is_staff, date_joined, about, is_superuser)
	VALUES ('pbkdf2_sha256$870000$FGoSCplr3LwAJGHvtT2Nck$gnDoOSio6SeB3ryqZ7OQ4blsoMHm9+Fj2SezR2B1r04=', 'publicador@mail.com',
	'Publicador Gómez', 'profile_pics/perfil.png', true, false, CURRENT_TIMESTAMP, 'Soy un publicador', false);
	--Administrador
	INSERT INTO public.app_customuser (password, email, name, photo, is_active, is_staff, date_joined, about, is_superuser)
	VALUES ('pbkdf2_sha256$870000$FGoSCplr3LwAJGHvtT2Nck$gnDoOSio6SeB3ryqZ7OQ4blsoMHm9+Fj2SezR2B1r04=', 'administrador@mail.com',
	'Administrador Cartes', 'profile_pics/perfil.png', true, false, CURRENT_TIMESTAMP, 'Soy un administrador', false);
END $$;

--Relación entre usuarios base y roles
DO $$
BEGIN
	INSERT INTO public.app_customuser_user_permissions (customuser_id, permission_id) VALUES(
		(SELECT id FROM public.app_customuser WHERE email = 'suscriptor@mail.com'),
		(SELECT id FROM auth_group WHERE name = 'Suscriptor')
	);

	INSERT INTO public.app_customuser_user_permissions (customuser_id, permission_id) VALUES(
		(SELECT id FROM public.app_customuser WHERE email = 'autor@mail.com'),
		(SELECT id FROM auth_group WHERE name = 'Autor')
	);

	INSERT INTO public.app_customuser_user_permissions (customuser_id, permission_id) VALUES(
		(SELECT id FROM public.app_customuser WHERE email = 'editor@mail.com'),
		(SELECT id FROM auth_group WHERE name = 'Editor')
	);

	INSERT INTO public.app_customuser_user_permissions (customuser_id, permission_id) VALUES(
		(SELECT id FROM public.app_customuser WHERE email = 'publicador@mail.com'),
		(SELECT id FROM auth_group WHERE name = 'Publicador')
	);

	INSERT INTO public.app_customuser_user_permissions (customuser_id, permission_id) VALUES(
		(SELECT id FROM public.app_customuser WHERE email = 'administrador@mail.com'),
		(SELECT id FROM auth_group WHERE name = 'Administrador')
	);
END $$;

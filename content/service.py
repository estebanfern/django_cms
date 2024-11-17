

def validate_permission_kanban(user, content, newState, oldState):
    """
    Valida si un usuario tiene permiso para cambiar el estado de un contenido en un flujo de trabajo tipo Kanban.

    Esta función asegura que las transiciones de estado de un contenido sean válidas de acuerdo con las reglas del negocio.

    :param user: Usuario que intenta realizar la acción.
    :type user: User
    :param content: Contenido cuyo estado se está modificando.
    :type content: Content
    :param newState: El nuevo estado al que se desea cambiar.
    :type newState: str
    :param oldState: El estado actual del contenido.
    :type oldState: str

    :return: Diccionario con el estado de la validación y un mensaje descriptivo.
    :rtype: dict

    :raises KeyError: Si el `newState` o el `oldState` no son válidos dentro del flujo de estados predefinido.

    Flujo de Estados:
        - draft:
            - name: "Borrador"
            - next: ["revision", "publish"]
            - prev: []
        - revision:
            - name: "Edición"
            - next: ["to_publish"]
            - prev: ["draft"]
        - to_publish:
            - name: "A publicar"
            - next: ["publish"]
            - prev: ["revision"]
        - publish:
            - name: "Publicado"
            - next: ["inactive"]
            - prev: []
        - inactive:
            - name: "Inactivo"
            - next: []
            - prev: ["publish"]
    """
    stateFlow = {
        'draft': {
            'name': 'Borrador',
            'next': ['revision', 'publish'],
            'prev': [],
        },
        'revision': {
            'name': 'Edicion',
            'next': ['to_publish'],
            'prev': ['draft'],
        },
        'to_publish': {
            'name': 'A publicar',
            'next': ['publish'],
            'prev': ['revision'],
        },
        'publish': {
            'name': 'Publicado',
            'next': ['inactive'],
            'prev': [],
        },
        'inactive': {
            'name': 'Inactivo',
            'next': [],
            'prev': ['publish'],
        },
    }
    
    # Verificar si el estado es válido
    if newState not in stateFlow[content.state]['next'] and newState not in stateFlow[content.state]['prev'] and newState != oldState:
        # el mensaje quiero que sea que no es posible cambiar de estado de oldState a newState
        return {'status': 'error', 'message': f'No es posible cambiar de {stateFlow[oldState]["name"]} a {stateFlow[newState]["name"]}.'}

    # Verificar los permisos del usuario
    if newState == 'draft' and not user.has_perm('app.edit_content'):
        return {'status': 'error', 'message': 'No tienes permiso para cambiar el estado.'}

    if newState == 'revision' and not user.has_perm('app.create_content') and not user.has_perm('app.publish_content'):
        return {'status': 'error', 'message': 'No tienes permiso para cambiar el estado.'}

    if newState == 'to_publish' and not user.has_perm('app.edit_content'):
        return {'status': 'error', 'message': 'No tienes permiso para cambiar el estado.'}
    if newState == 'publish' and not user.has_perm('app.publish_content') and not user.has_perm('app.create_content') and not user.has_perm('app.edit_is_active'):
        return {'status': 'error', 'message': 'No tienes permiso para cambiar el estado.'}

    if newState == 'inactive' and not user.has_perm('app.edit_is_active') and not user.has_perm('app.create_content'):
        return {'status': 'error', 'message': 'No tienes permiso para cambiar el estado.'}

    # Restricciones adicionales para cambios de estados subiendo el flujo de estados
    if newState == 'publish' and oldState == 'draft' and content.category.is_moderated and user.has_perm('app.create_content'):
        return {'status': 'error', 'message': 'No se puede publicar un contenido de categoría moderada desde el estado de Borrador.'}

    if newState == 'publish' and oldState == 'draft' and not user.has_perm('app.create_content'):
        return {'status': 'error', 'message': 'No tienes permiso para cambiar el estado.'}

    if newState == 'publish' and oldState == 'to_publish' and not user.has_perm('app.publish_content'):
        return {'status': 'error', 'message': 'No tienes permiso para cambiar el estado.'}

    if newState == 'revision' and oldState == 'draft' and not user.has_perm('app.create_content'):
        return {'status': 'error', 'message': 'No tienes permiso para cambiar el estado.'}

    if newState == 'revision' and oldState == 'draft' and user.has_perm('app.create_content') and not content.autor == user:
        return {'status': 'error', 'message': 'No puedes cambiar al estado Edicion de un contenido que no creaste.'}

    if newState == 'inactive' and oldState == 'publish' and user.has_perm('app.create_content') and not user.has_perm('app.edit_is_active') and not content.autor == user:
        return {'status': 'error', 'message': 'No puedes cambiar al estado Inactivo de un contenido que no creaste.'}

    if newState == 'publish' and oldState == 'draft' and user.has_perm('app.create_content') and not content.autor == user and not content.category.is_moderated:
        return {'status': 'error', 'message': 'No puedes cambiar al estado Publicado de un contenido que no creaste.'}

    # Restricciones adicionales para cambios de estados bajando el flujo de estados
    if newState == 'draft' and oldState == 'revision' and not user.has_perm('app.edit_content'):
        return {'status': 'error', 'message': 'No tienes permiso para cambiar el estado.'}

    if newState == 'revision' and oldState == 'to_publish' and not user.has_perm('app.publish_content'):
        return {'status': 'error', 'message': 'No tienes permiso para cambiar el estado.'}

    if newState == 'publish' and oldState == 'inactive' and not user.has_perm('app.edit_is_active') and not user.has_perm('app.create_content'):
        return {'status': 'error', 'message': 'No tienes permiso para cambiar el estado.'}

    return {'status': 'success', 'message': 'Permisos validados correctamente.'}






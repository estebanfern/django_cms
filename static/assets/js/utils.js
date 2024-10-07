modal = {
    info : function(options) {
        let defaults = {
            title: '<i class="bi bi-info-circle text-primary"></i> Información',
            centerVertical: true,
            size: 'large',
            buttons: {
                ok: {
                    label: 'Ok', 
                    className: 'btn btn-success'
                }
            }
        }
        var settings = $.extend({}, defaults, options);
        bootbox.dialog(settings)
    },
    success : function(options) {
        let defaults = {
            title: '<i class="bi bi-check-circle text-success"></i> Resultado exitoso',
            centerVertical: true,
            buttons: {
                ok: {
                    label: 'Ok', 
                    className: 'btn btn-success'
                }
            }
        }
        var settings = $.extend({}, defaults, options);
        bootbox.dialog(settings)
    },
    error : function(options) {
        let defaults = {
            title: '<i class="bi bi-exclamation-octagon text-danger"></i> Ocurrió un error inesperado',
            centerVertical: true,
            buttons: {
                ok: {
                    label: 'Ok', 
                    className: 'btn btn-secondary'
                }
            }
        }
        var settings = $.extend({}, defaults, options);
        bootbox.dialog(settings)
    },
    warning : function(options) {
        let defaults = {
            title: '<i class="bi bi-exclamation-triangle text-warning"></i> Alerta',
            centerVertical: true,
            buttons: {
                ok: {
                    label: 'Ok', 
                    className: 'btn btn-secondary'
                }
            }
        }
        var settings = $.extend({}, defaults, options);
        bootbox.dialog(settings)
    }
}

function redirectWithParams(element, url, param, value=null) {
    // Obtener el valor del parámetro del elemento si no se pasa un valor
    if (!value) {
        value = element.attributes[`${param}-value`].value;
    }
    // Obtener los parámetros existentes de la URL actual
    const urlParams = new URLSearchParams(window.location.search);
    // Añadir o modificar el parámetro
    urlParams.set(param, value);
    // Redireccionar con los parámetros actualizados
    window.location.href = `${url}?${urlParams.toString()}`;
}

function deleteParam(url, ...params) {
    // Obtener los parámetros existentes de la URL actual
    const urlParams = new URLSearchParams(window.location.search);
    // Eliminar el parámetro
    params.forEach( param => {
        urlParams.delete(param);    // Redireccionar con los parámetros actualizados
    })

    if (url !== null) {
        window.location.href = `${url}?${urlParams.toString()}`;
    } else {
        const newUrl = `${window.location.pathname}?${urlParams.toString()}`;
        history.replaceState(null, '', newUrl);
    }
}

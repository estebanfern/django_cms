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

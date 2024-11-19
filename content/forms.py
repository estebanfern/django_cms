import datetime
from django import forms
from .models import Content
from .models import Report

class ContentForm(forms.ModelForm):
    """
    Formulario para la creación y edición de contenidos.

    Permite gestionar los campos asociados al modelo `Content`, aplicando reglas y comportamientos
    específicos según el estado del formulario (creación o edición).

    :attribute change_reason: Campo opcional para especificar la razón de edición.
    :type change_reason: CharField
    """

    change_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'required':'required'}),
        label='Razón de edición'
    )

    class Meta:
        """
        Configuración interna del formulario.

        :attribute model: Modelo asociado al formulario (`Content`).
        :type model: Model
        :attribute fields: Campos del modelo incluidos en el formulario.
        :type fields: list
        :attribute widgets: Widgets personalizados para los campos, ajustando la apariencia y el comportamiento.
        :type widgets: dict
        """

        model = Content
        fields = ['title', 'summary', 'category', 'date_published', 'date_expire', 'content', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),  # Campo de texto con clase Bootstrap
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': '4', 'maxlength' : '255'}),  # Asegura que ocupe toda la línea
            'category': forms.Select(attrs={'class': 'form-select'}),  # Campo select con clase Bootstrap
            'date_published': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control',
                    'min': (datetime.datetime.now() + datetime.timedelta(days=1)).replace(hour=7, minute=0).strftime('%Y-%m-%dT%H:%M'),
                    'max': '2026-12-31T23:00',
                }
            ),
            'date_expire': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control',
                    'min': (datetime.datetime.now() + datetime.timedelta(days=1)).replace(hour=7, minute=0).strftime('%Y-%m-%dT%H:%M'),
                    'max': '2026-12-31T23:00',
                }
            ),
        
        }
    def __init__(self, *args, **kwargs):
        """
        Inicializa el formulario y ajusta los campos según si el formulario está en modo de creación o edición.

        Lógica:
            - En modo edición:
                - Si el contenido no está en estado `borrador`, desactiva campos específicos.
                - Si está en estado `borrador`, ajusta los campos para permitir la edición completa.
            - En modo creación, aplica la configuración inicial a los campos.

        :param args: Argumentos posicionales.
        :type args: list
        :param kwargs: Argumentos nombrados, como la instancia del contenido.
        :type kwargs: dict
        """

        super(ContentForm, self).__init__(*args, **kwargs)
            # Verifica si el formulario está en modo de edición o creación
        if self.instance.pk:
            if self.instance.state != Content.StateChoices.draft:
                # En modo de edición por editor
                for field in self.fields.values():
                    field.required = False

                self.fields['date_published'].widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'readonly': 'readonly'})
                self.fields['date_expire'].widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'readonly': 'readonly'})
                self.fields['title'].widget.attrs['disabled'] = 'disabled'
                self.fields['summary'].widget.attrs['disabled'] = 'disabled'
                self.fields['category'].widget.attrs['disabled'] = 'disabled'
                self.fields['date_published'].widget.attrs['disabled'] = 'disabled'
                self.fields['date_expire'].widget.attrs['disabled'] = 'disabled'
                self.fields['tags'].widget.attrs['disabled'] = 'disabled'
                self.fields['tags'].widget.attrs['class'] = 'form-control'
            else:
                # En modo edición por autor
                self.fields['tags'].widget.attrs['class'] = 'form-control'
                self.fields['date_published'].widget = forms.TextInput(
                    attrs={
                        'type': 'datetime-local',
                        'class': 'form-control',
                        'min': (datetime.datetime.now() + datetime.timedelta(days=1)).replace(hour=7, minute=0).strftime('%Y-%m-%dT%H:%M'),
                        'max': '2026-12-31T23:00',
                    }
                )
                self.fields['date_expire'].widget = forms.TextInput(
                    attrs={
                        'type': 'datetime-local',
                        'class': 'form-control',
                        'min': (datetime.datetime.now() + datetime.timedelta(days=1)).replace(hour=7, minute=0).strftime('%Y-%m-%dT%H:%M'),
                        'max': '2026-12-31T23:00',
                    }
                )
        else:
            # En modo de creación
            # Se hace algo?
            self.fields['tags'].widget.attrs['class'] = 'form-control'



class ReportForm(forms.ModelForm):
    """
    Formulario para crear un reporte de contenido.

    Permite capturar los datos necesarios para reportar un contenido, incluyendo opciones
    personalizadas según si el usuario está autenticado.

    Widgets:
        - Personalizan los campos del formulario con clases CSS para facilitar la integración con frameworks de frontend.
    """

    class Meta:
        """
        Configuración interna del formulario.

        :attribute model: Modelo asociado al formulario (`Report`).
        :type model: Model
        :attribute fields: Campos incluidos en el formulario.
        :type fields: list
        :attribute widgets: Widgets personalizados para los campos del formulario.
        :type widgets: dict
        """

        model = Report
        fields = ['name', 'email', 'reason', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'reason': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }
        email = forms.EmailField(
        error_messages={'invalid': 'Introduzca una dirección de correo electrónico válida.'}
    )

    def __init__(self, *args, **kwargs):
        """
        Inicializa el formulario, ajustando los campos según si el usuario está autenticado.

        - Si el usuario está autenticado:
            - Rellena automáticamente los campos `name` y `email`.
            - Oculta los campos de `name` y `email`.
        - Si el usuario no está autenticado:
            - Hace que los campos `name` y `email` sean obligatorios.

        :param args: Argumentos posicionales.
        :type args: list
        :param kwargs: Argumentos nombrados, incluyendo el usuario autenticado.
        :type kwargs: dict
        """

        user = kwargs.pop('user', None)
        super(ReportForm, self).__init__(*args, **kwargs)

        self.fields['reason'].choices = [('', 'Seleccione un motivo')] + list(self.fields['reason'].choices[1:])

        # Si el usuario está autenticado, llenamos automáticamente nombre y email
        if user and user.is_authenticated:
            self.fields['name'].initial = user.name
            self.fields['email'].initial = user.email
            self.fields['name'].widget.attrs['hidden'] = 'hidden'  
            self.fields['email'].widget.attrs['hidden'] = 'hidden'  
        else:
            # Si es un visitante, hacemos que estos campos sean obligatorios
            self.fields['name'].required = True
            self.fields['email'].required = True


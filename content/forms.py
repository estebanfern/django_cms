import datetime
from django import forms
from .models import Content
from .models import Report

class ContentForm(forms.ModelForm):
    """
    Formulario para la creación y edición de contenido.

    Hereda de:
        - forms.ModelForm: Utiliza un formulario basado en el modelo 'Content'.

    Atributos:
        change_reason (CharField): Campo opcional para especificar la razón de edición, presentado como un área de texto.

    Meta:
        - model: El modelo asociado al formulario es 'Content'.
        - fields: Lista de campos del modelo que se incluyen en el formulario.
        - widgets: Personaliza la apariencia y el comportamiento de los campos del formulario con clases CSS y otros atributos.

    Métodos:
        __init__: Inicializa el formulario y ajusta los campos según si el formulario está en modo de creación o edición.
    """

    change_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'required':'required'}),
        label='Razón de edición'
    )

    class Meta:
        """
        Configuración interna del formulario.

        Atributos:
            model (Model): Define el modelo asociado al formulario, que en este caso es 'Content'.
            fields (list): Lista de campos del modelo que se incluirán en el formulario ('title', 'summary', 'category', 'date_published', 'date_expire', 'content', 'tags').
            widgets (dict): Define los widgets personalizados para los campos del formulario, aplicando clases CSS como 'form-control' y ajustando atributos como el tipo de entrada y los rangos de fechas para los campos de fechas.
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
            - Llama al método '__init__' de la clase padre para inicializar el formulario.
            - Verifica si el formulario está en modo de edición (instancia existente) o creación (nueva instancia).
            - Si está en modo de edición:
                - Si el contenido no está en estado 'borrador', desactiva los campos para evitar cambios no permitidos.
                - Si el contenido está en estado 'borrador', ajusta los campos relevantes para permitir la edición completa.
            - En ambos modos, asegura que el campo 'tags' tenga la clase CSS 'form-control'.

        Parámetros:
            *args: Argumentos posicionales.
            **kwargs: Argumentos nombrados.

        Retorna:
            None
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

    Campos:
        name (CharField): Nombre de quien reporta. Oculto y completado automáticamente si el usuario está autenticado.
        email (EmailField): Correo electrónico de quien reporta. Oculto y completado automáticamente si el usuario está autenticado.
        reason (ChoiceField): Motivo del reporte, con una lista desplegable de opciones.
        description (TextField): Descripción opcional del motivo del reporte.

    Widgets:
        Se personalizan los widgets para agregar clases CSS a los campos, facilitando la integración con un framework de frontend.

    Métodos:
        __init__(user): Inicializa el formulario, completando los campos de nombre y email si el usuario está autenticado.
                        Si el usuario no está autenticado, los campos de nombre y correo son obligatorios.
                        Además, oculta los campos de nombre y email para usuarios autenticados.
    """


    class Meta:
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


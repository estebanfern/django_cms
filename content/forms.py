import datetime
from django import forms
from .models import Content

class ContentForm(forms.ModelForm):
    change_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'required':'required'}),
        label='Razón de edición'
    )

    class Meta:
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
                    }
                )
                self.fields['date_expire'].widget = forms.TextInput(
                    attrs={
                        'type': 'datetime-local',
                        'class': 'form-control',
                    }
                )
        else:
            # En modo de creación
            # Se hace algo?
            self.fields['tags'].widget.attrs['class'] = 'form-control'

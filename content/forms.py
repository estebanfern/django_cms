from django import forms
from .models import Content

class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ['title', 'summary', 'category', 'date_published', 'content', 'attachment']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),  # Campo de texto con clase Bootstrap
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': '4', 'maxlength' : '255'}),  # Asegura que ocupe toda la línea
            'category': forms.Select(attrs={'class': 'form-select'}),  # Campo select con clase Bootstrap
            'date_published': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control', 'multiple':'True'}),  # Campo de archivo con clase Bootstrap
        }
    def __init__(self, *args, **kwargs):
        super(ContentForm, self).__init__(*args, **kwargs)
            # Verifica si el formulario está en modo de edición o creación
        if self.instance.pk:
            if self.instance.state != Content.StateChoices.draft:
                # En modo de edición
                self.fields['category'].required = False
                self.fields['category'].widget.attrs['disabled'] = 'disabled'
                self.fields['date_published'].widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'readonly': 'readonly'})
        else:
            # En modo de creación
            self.fields['date_published'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})

from django import forms
from .models import Content

class ContentForm(forms.ModelForm):
    change_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        label='Razón de edición'
    )

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
                for field in self.fields.values():
                    field.required = False

                self.fields['date_published'].widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'readonly': 'readonly'})
                self.fields['title'].widget.attrs['disabled'] = 'disabled'
                self.fields['summary'].widget.attrs['disabled'] = 'disabled'
                self.fields['category'].widget.attrs['disabled'] = 'disabled'
                self.fields['date_published'].widget.attrs['disabled'] = 'disabled'
        else:
            # En modo de creación
            self.fields['date_published'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})

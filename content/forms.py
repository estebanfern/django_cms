from django import forms
from .models import Content

class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ['title', 'summary', 'category', 'date_published', 'content', 'attachment']
        widgets = {
            'summary': forms.Textarea(attrs={'style': 'display: block; width: 100%;'}),  # Asegura que ocupe toda la línea
            #'date_published': forms.DateInput(attrs={'type': 'date', 'style': 'display: block; width: 100%;'}),
        }
    def __init__(self, *args, **kwargs):
        super(ContentForm, self).__init__(*args, **kwargs)
            # Verifica si el formulario está en modo de edición o creación
        if self.instance.pk:
            if self.instance.state != Content.StateChoices.draft:
                # En modo de edición
                self.fields['category'].required = False
                self.fields['category'].widget.attrs['disabled'] = 'disabled'
        else:
            # En modo de creación
            self.fields['date_published'].widget = forms.DateInput(attrs={'type': 'date'})

        
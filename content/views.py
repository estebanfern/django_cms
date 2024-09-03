from django.shortcuts import redirect, render

# Create your views here.
from django.utils import timezone 
from django.views.generic import CreateView, UpdateView
from .models import Content
from .forms import ContentForm

class ContentCreateView(CreateView):
    model = Content
    form_class = ContentForm
    template_name = 'content_form.html'
    success_url = 'home' # a donde te vas a ir
    def form_valid(self, form):
        action = self.request.POST.get('action')
        content = form.save(commit=False)

        content.autor = self.request.user

        if action == 'save_draft':
            content.is_active = False
            content.date_create = timezone.now()
            content.date_expire = None
            content.state = Content.StateChoices.draft
        elif action == 'send_for_revision':
            content.is_active = False
            content.date_create = timezone.now()
            content.date_expire = None
            content.state = Content.StateChoices.revision
            
        content.save()
        return redirect(self.success_url)

# no uso aun
class ContentUpdateView(UpdateView):
    model = Content
    form_class = ContentForm
    template_name = 'content_form.html'
    success_url = 'home'  # donde ir

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        
        # Verificar el grupo del usuario y ajustar el formulario
        if user.get_groups_string() == 'Editor':
            # Solo lectura para los campos específicos si el usuario es un Autor
            form.fields['title'].widget.attrs['readonly'] = True
            form.fields['summary'].widget.attrs['readonly'] = True
            form.fields['category'].widget.attrs['readonly'] = True
            form.fields['date_published'].widget.attrs['readonly'] = True

        elif user.get_groups_string() == 'Publicador':
            # Solo lectura para todos los campos si el usuario es un Publicador
            for field in form.fields:
                form.fields[field].widget.attrs['readonly'] = True

        return form
    
    def form_valid(self, form):
        user = self.request.user
        action = self.request.POST.get('action')


        # Recupera el objeto original desde la base de datos
        content = self.get_object()



        if user.get_groups_string() == 'Autor':
            # Solo actualizar los campos que vienen del formulario
            form_data = form.cleaned_data
            for field in form_data:
                setattr(content, field, form_data[field])

            # Cambiar el estado basado en la acción
            if action == 'send_for_revision':
                content.state = Content.StateChoices.revision
        else:

            content.category = self.get_object().category
            
            if user.get_groups_string() == 'Editor':

                # Solo actualiza el campo 'content' desde el formulario
                content.content = form.cleaned_data['content']

                if action == 'send_to_draft':
                    content.state = Content.StateChoices.draft
                elif action == 'send_to_publish':
                    content.state = Content.StateChoices.to_publish


            elif user.get_groups_string() == 'Publicador':
                if action == 'send_for_revision':
                    content.state = Content.StateChoices.revision
                elif action == 'publish':
                    content.is_active = True
                    content.date_expire = None #este se debe cambiaaaaaaaar
                    content.state = Content.StateChoices.publish
            
        content.save()
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        print("Form is invalid")  # Depuración
        print(form.errors)  # Mostrar errores en el formulario
        return super().form_invalid(form)
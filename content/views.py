from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy

# Create your views here.
from django.utils import timezone 
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Content
from .forms import ContentForm
from django.core.exceptions import PermissionDenied

class ContentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Content
    form_class = ContentForm
    template_name = 'content/content_form.html'
    success_url = 'home' # a donde ir despues
    cancel_url = 'home' # ir cuando se cancela
    permission_required = 'app.create_content'
    
    def form_valid(self, form):
        content = form.save(commit=False)
        content.autor = self.request.user
        content.is_active = True
        content.date_create = timezone.now()
        content.date_expire = None
        content.state = Content.StateChoices.draft
        content.save()
        return redirect(self.success_url)
        
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
        
        


class ContentUpdateView(LoginRequiredMixin, UpdateView):
    model = Content
    form_class = ContentForm
    template_name = 'content/content_form.html'
    success_url = 'home'  # donde ir despues

    # Lista de permisos
    required_permissions = ['app.create_content', 'app.edit_content']

    def dispatch(self, request, *args, **kwargs):
        # Verifica si el usuario tiene al menos uno de los permisos requeridos
        if not any(request.user.has_perm(perm) for perm in self.required_permissions):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

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

            
        content.save()
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        print(form.errors)  # Mostrar errores en el formulario
        return super().form_invalid(form)


def view_content(request, id):
    content = get_object_or_404(Content, id=id)
    return render(request, 'content/view.html', {"content" : content})

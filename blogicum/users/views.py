from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .forms import RegistrationForm


class RegistrationView(CreateView):
    form_class = RegistrationForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('blog:index')
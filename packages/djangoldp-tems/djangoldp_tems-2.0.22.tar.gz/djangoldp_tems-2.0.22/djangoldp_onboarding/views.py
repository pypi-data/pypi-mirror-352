from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import ParticipantRegistrationForm
from .models import RegisterParticipant


class OrganisationCreateView(CreateView):
    model = RegisterParticipant
    form_class = ParticipantRegistrationForm
    template_name = "onboarding_form.html"
    success_url = reverse_lazy("onboarding-success")

    def form_valid(self, form):
      response = super().form_valid(form)
      response.status_code = 303
      return response

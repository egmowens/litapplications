from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from litapplications.committees.models.committees import Committee

from .data_ingest import ingest_file
from .forms import DataIngestForm


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['your_committees'] = Committee.objects.filter(
            owner=self.request.user)
        context['lonely_committees'] = Committee.objects.filter(
            owner=None)
        return context



class DataIngestView(LoginRequiredMixin, FormView):
    form_class = DataIngestForm
    template_name = 'data_ingest.html'
    success_url = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_superuser:
            messages.add_message(request, messages.INFO,
                'Sorry; only superusers can access this page.')
            return HttpResponseRedirect(reverse_lazy('home'))
        return super(DataIngestView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('file_field')
        if form.is_valid():
            for f in files:
                ingest_file(request, f)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

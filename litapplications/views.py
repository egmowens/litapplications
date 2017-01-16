from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from litapplications.committees.models.committees import Committee
from litapplications.committees.views import CommitteeCreateView

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
        if not (self.request.user.is_superuser or
                self.request.user.groups.filter(name='Chairs')):
            messages.add_message(request, messages.INFO,
                'Sorry; you need additional permissions to access that page.')
            return HttpResponseRedirect(reverse_lazy('home'))
        return super(DataIngestView, self).dispatch(request, *args, **kwargs)


    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('file_field')
        new_committees = []

        if form.is_valid():
            for f in files:
                resp = ingest_file(request, f)
                for warning in resp.warnings:
                    messages.add_message(request, messages.WARNING, warning)

                if resp.new_committees:
                    new_committees.extend(resp.new_committees)

            if new_committees:
                unique_new_comms = list(set(new_committees))
                return_resp = CommitteeCreateView()
                return_resp.new_committees = unique_new_comms
                return_resp.request = request
                return return_resp.get(request)
            else:
                return self.form_valid(form)
        else:
            return self.form_invalid(form)

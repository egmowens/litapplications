from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from litapplications.candidates.models import Candidate, Appointment

from .models import Committee

class CommitteeListView(LoginRequiredMixin, ListView):
    model = Committee

    def get_context_data(self, **kwargs):
        context = super(CommitteeListView, self).get_context_data(**kwargs)
        context['your_committees'] = self.get_queryset().filter(
            owner=self.request.user)
        return context



class CommitteeDetailView(LoginRequiredMixin, DetailView):
    model = Committee

    def get_context_data(self, **kwargs):
        context = super(CommitteeDetailView, self).get_context_data(**kwargs)
        obj = self.get_object()
        context['applicants'] = Candidate.objects.filter(
            appointments__status=Appointment.APPLICANT,
            appointments__committee=obj)

        context['potential'] = Candidate.objects.filter(
            appointments__status=Appointment.POTENTIAL,
            appointments__committee=obj)

        context['recommended'] = Candidate.objects.filter(
            appointments__status=Appointment.RECOMMENDED,
            appointments__committee=obj)

        context['accepted'] = Candidate.objects.filter(
            appointments__status=Appointment.ACCEPTED,
            appointments__committee=obj)

        context['not_recommended'] = Candidate.objects.filter(
            appointments__status=Appointment.NOPE,
            appointments__committee=obj)

        context['declined'] = Candidate.objects.filter(
            appointments__status=Appointment.DECLINED,
            appointments__committee=obj)
        return context



class CommitteeUpdateNotesView(LoginRequiredMixin, UpdateView):
    model = Candidate
    fields = ['notes']

    def form_valid(self, form):
        return super(CommitteeUpdateNotesView, self).form_valid(form)

    def get_success_url(self):
        return self.get_object().get_absolute_url()

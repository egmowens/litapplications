from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .models import Candidate

class CandidateListView(LoginRequiredMixin, ListView):
    model = Candidate

    def get_context_data(self, **kwargs):
        context = super(CandidateListView, self).get_context_data(**kwargs)
        context['unreviewed'] = Candidate.objects.filter(
            potential_comms__isnull=True,
            review_complete=False)

        context['in_process'] = Candidate.objects.filter(
            potential_comms__isnull=False,
            review_complete=False)

        context['reviewed'] = Candidate.objects.filter(
            review_complete=True)

        return context

class CandidateDetailView(LoginRequiredMixin, DetailView):
    model = Candidate

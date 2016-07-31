from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

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

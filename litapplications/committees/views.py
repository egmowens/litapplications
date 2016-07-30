from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .models import Committee

class CommitteeListView(LoginRequiredMixin, ListView):
    model = Committee



class CommitteeDetailView(LoginRequiredMixin, DetailView):
    model = Committee

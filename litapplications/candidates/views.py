from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .models import Candidate

class CandidateListView(LoginRequiredMixin, ListView):
    model = Candidate



class CandidateDetailView(LoginRequiredMixin, DetailView):
    model = Candidate

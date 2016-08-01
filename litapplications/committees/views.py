from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from litapplications.candidates.models import Candidate, Appointment

from .forms import UpdateNotesForm, UpdateNumbersForm
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

        context['candidates'] = Candidate.objects.filter(
            appointments__committee=obj)

        # For constructing the dropdown in the batch editing form.
        # We exclude ACCEPTED and DECLINED because committee members can't
        # set those - they rely on the VP having sent a letter and the applicant
        # having responded.
        context['status_choices'] = [choice for choice
            in Appointment.STATUS_CHOICES
            if choice[0] not in [Appointment.ACCEPTED, Appointment.DECLINED]]

        context['notes_form'] = UpdateNotesForm(instance=self.get_object())
        context['numbers_form'] = UpdateNumbersForm(instance=self.get_object())

        return context



class CommitteeUpdateNotesView(LoginRequiredMixin, UpdateView):
    model = Committee
    fields = ['notes']

    def form_invalid(self, form):
        response = super(CommitteeUpdateNotesView, self).form_invalid(form)
        for error in form.errors.values():
            messages.add_message(self.request, messages.WARNING,
                error.as_data()[0][0]) # just the message, no formatting

        return HttpResponseRedirect(self.get_success_url())


    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS,
            'Update successful. Thank you for working on appointments today!')
        return super(CommitteeUpdateNotesView, self).form_valid(form)


    def get_success_url(self):
        return self.get_object().get_absolute_url()



class CommitteeUpdateNumbersView(LoginRequiredMixin, UpdateView):
    model = Committee
    fields = ['min_appointees', 'max_appointees']

    def form_invalid(self, form):
        super(CommitteeUpdateNumbersView, self).form_invalid(form)

        for error in form.errors.values():
            messages.add_message(self.request, messages.WARNING,
                error.as_data()[0][0]) # just the message, no formatting

        return HttpResponseRedirect(self.get_success_url())


    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS,
            'Update successful. Thank you for working on appointments today!')
        return super(CommitteeUpdateNumbersView, self).form_valid(form)


    def get_success_url(self):
        return self.get_object().get_absolute_url()

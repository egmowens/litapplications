import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from litapplications.committees.models import Committee

from .forms import UpdateNotesForm
from .models import Candidate, Appointment

logger = logging.getLogger(__name__)


class CandidateListView(LoginRequiredMixin, ListView):
    model = Candidate

    def get_context_data(self, **kwargs):
        context = super(CandidateListView, self).get_context_data(**kwargs)
        context['unfinished'] = Candidate.objects.filter(
            appointments__status__in=[
                Appointment.APPLICANT,
                Appointment.POTENTIAL]
            ).distinct()

        context['pending'] = Candidate.objects.filter(
            appointments__status__in=[
                Appointment.RECOMMENDED]
            ).distinct()

        context['done'] = Candidate.objects.exclude(
            appointments__status__in=[
                Appointment.APPLICANT,
                Appointment.POTENTIAL,
                Appointment.RECOMMENDED]
            ).exclude(appointments=None).distinct()

        return context



class CandidateDetailView(LoginRequiredMixin, DetailView):
    model = Candidate

    def get_context_data(self, **kwargs):
        context = super(CandidateDetailView, self).get_context_data(**kwargs)
        context['notes_form'] = UpdateNotesForm(instance=self.get_object())

        obj = self.get_object()
        context['committees'] = Committee.objects.filter(
            appointments__candidate=obj,
            appointments__status__in=[
                Appointment.APPLICANT,
                Appointment.POTENTIAL,
                Appointment.RECOMMENDED
            ]).distinct()
        context['other_committees'] = Committee.objects.exclude(
            appointments__candidate=obj).distinct()
        return context



class UpdateNotesView(LoginRequiredMixin, UpdateView):
    model = Candidate
    fields = ['notes']

    def get_success_url(self):
        return self.get_object().get_absolute_url()



class UpdateStatusView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        try:
            committee = Committee.objects.get(pk=self.kwargs['pk'])
        except Committee.DoesNotExist:
            # ValueError will be raised if the status cannot be cast to int.
            logger.exception('Tried to update status for nonexistent committee')
            return HttpResponseBadRequest()

        try:
            assert 'candidates' in request.POST
        except AssertionError:
            messages.add_message(request, messages.WARNING,
                'Please select one or more candidates in order to set their '
                'status.')

            return HttpResponseRedirect(reverse_lazy(
                'committees:detail', args=[committee.pk]))

        try:
            assert 'batch_status' in request.POST

            status = request.POST['batch_status']
            assert status in [Appointment.APPLICANT,
                              Appointment.POTENTIAL,
                              Appointment.RECOMMENDED,
                              Appointment.NOPE,
                              Appointment.ACCEPTED,
                              Appointment.DECLINED]
        except (AssertionError, ValueError):
            # ValueError will be raised if the status cannot be cast to int.
            logger.exception('Did not find valid data for batch editing')
            return HttpResponseBadRequest()

        for candidate_pk in request.POST.getlist('candidates'):
            try:
                candidate = Candidate.objects.get(pk=candidate_pk)
            except Candidate.DoesNotExist:
                logger.exception('Could not find app with posted pk {pk}; '
                    'continuing through remaining apps'.format(pk=candidate_pk))
                continue

            try:
                appointments = Appointment.objects.filter(
                    candidate=candidate, committee=committee)
                assert len(appointments) == 1
                appointment = appointments[0]
                appointment.status = status
                appointment.save()
            except:
                logger.exception('Could not find appointment for candidate '
                    '{candidate} and committee {committee}; status not '
                    'set'.format(candidate=candidate, committee=committee))
                return HttpResponseBadRequest()

        messages.add_message(request, messages.SUCCESS,
            'Update successful. Thank you for working on appointments today!')

        return HttpResponseRedirect(reverse_lazy(
            'committees:detail', args=[committee.pk]))



class UpdateAppointmentsView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        try:
            candidate = Candidate.objects.get(pk=self.kwargs['pk'])
        except Candidate.DoesNotExist:
            # ValueError will be raised if the status cannot be cast to int.
            logger.exception('Tried to update appointments for nonexistent candidate')
            return HttpResponseBadRequest()

        try:
            assert 'committees' in request.POST
        except AssertionError:
            messages.add_message(request, messages.WARNING,
                'Please select one or more committees.')

            return HttpResponseRedirect(reverse_lazy(
                'candidates:detail', args=[candidate.pk]))

        for committee_pk in request.POST.getlist('committees'):
            try:
                committee = Committee.objects.get(pk=committee_pk)
            except Committee.DoesNotExist:
                logger.exception('Could not find committee with posted pk {pk};'
                    ' continuing through remaining pks'.format(pk=committee_pk))
                continue

            appointment = Appointment()
            appointment.candidate = candidate
            appointment.committee = committee
            appointment.status = Appointment.APPLICANT
            appointment.locally_proposed = True
            appointment.save()

        messages.add_message(request, messages.SUCCESS,
            'Update successful. Thank you for working on appointments today!')

        return HttpResponseRedirect(reverse_lazy(
            'candidates:detail', args=[candidate.pk]))

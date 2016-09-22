from guardian.core import ObjectPermissionChecker
import logging

from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.views.generic.base import View, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic.list import ListView

from litapplications.candidates.models import Note
from litapplications.committees.models.committees import Committee
from litapplications.committees.models.units import (Unit,
                                                NOTE__CAN_MAKE_CANDIDATE_NOTE,
                                                NOTE__CAN_MAKE_PRIVILEGED_NOTE)

from .forms import UpdateNoteForm, UpdateLibraryTypeForm, CreateNoteForm
from .models import Candidate, Appointment

logger = logging.getLogger(__name__)


# This code has to live somewhere. Can't live in models.py, because the
# app registry isn't ready yet. Groups: the worst. And the permission-setting
# needs to happen in the admin for now, because everything is awful.
chairs, created = Group.objects.get_or_create(name='Chairs')


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

        context['library_key'] = \
            [(libtype[1], Candidate.LIBRARY_TYPE_IMAGES[libtype[0]])
                for libtype in Candidate.LIBRARY_TYPE_CHOICES]

        return context



class CandidateDetailView(LoginRequiredMixin, DetailView):
    model = Candidate

    def get_context_data(self, **kwargs):
        context = super(CandidateDetailView, self).get_context_data(**kwargs)
        notes = Note.objects.filter(candidate=self.get_object(),
            privileged=False)
        special_notes = Note.objects.filter(candidate=self.get_object(),
            privileged=True)
        checker = ObjectPermissionChecker(self.request.user)

        notes_forms = []
        for note in notes:
            if checker.has_perm(NOTE__CAN_MAKE_CANDIDATE_NOTE, note.unit):
                update_form = UpdateNoteForm(instance=note)
                update_form.fields['text'].label = 'Note for {unit}'.format(
                    unit=note.unit)
                notes_forms.append(update_form)

        unnoted_units = []
        for unit in Unit.objects.all():
            if (checker.has_perm(NOTE__CAN_MAKE_CANDIDATE_NOTE, unit)
                and not notes.filter(unit=unit)):

                unnoted_units.append(unit.pk)

        special_notes_forms = []
        for note in special_notes:
            if checker.has_perm(NOTE__CAN_MAKE_PRIVILEGED_NOTE, note.unit):
                update_form = UpdateNoteForm(instance=note)
                update_form.fields['text'].label = 'Note for {unit}'.format(
                    unit=note.unit)
                special_notes_forms.append(update_form)

        context['notes_forms'] = notes_forms

        if unnoted_units:
            create_form = CreateNoteForm(
                initial={'candidate': self.get_object()})
            create_form.fields['unit'].queryset = Unit.objects.filter(
                pk__in=unnoted_units)
            create_form.fields['candidate'].widget = forms.HiddenInput()
            context['create_form'] = create_form

        obj = self.get_object()
        context['committees'] = Committee.objects.filter(
            appointments__candidate=obj,
            appointments__status__in=[
                Appointment.APPLICANT,
                Appointment.POTENTIAL,
                Appointment.RECOMMENDED,
                Appointment.SENT
            ]).distinct()
        context['other_committees'] = Committee.objects.exclude(
            appointments__candidate=obj).distinct()
        context['appointments'] = Committee.objects.filter(
                appointments__candidate=obj,
                appointments__status=Appointment.ACCEPTED
            ).distinct()

        context['libtype_form'] = UpdateLibraryTypeForm(
            instance=self.get_object())

        return context



class UpdateNoteView(LoginRequiredMixin, UpdateView):
    model = Note
    fields = ['text']

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS,
            'Note updated.')
        return self.get_object().candidate.get_absolute_url()



class CreateNoteView(LoginRequiredMixin, CreateView):
    model = Note
    fields = ['text', 'unit', 'candidate']

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS,
            'Note created.')
        return self.object.candidate.get_absolute_url()



class UpdateLibraryTypeView(LoginRequiredMixin, UpdateView):
    model = Candidate
    fields = ['library_type']

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS,
            'Library type updated.')
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

        settable_statuses = Appointment.settable_statuses(
                request.user, committee.unit)

        try:
            assert 'batch_status' in request.POST

            status = request.POST['batch_status']
            assert status in settable_statuses
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
                if appointment.status in settable_statuses:
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



class AppointmentsView(LoginRequiredMixin, TemplateView):
    template_name = 'candidates/appointments.html'

    def get_context_data(self, **kwargs):
        context = super(AppointmentsView, self).get_context_data(**kwargs)
        context['recommended'] = Appointment.objects.filter(
            status=Appointment.RECOMMENDED).order_by('candidate')
        context['accepted'] = Appointment.objects.filter(
            status=Appointment.ACCEPTED).order_by('candidate')
        context['declined'] = Appointment.objects.filter(
            status=Appointment.DECLINED).order_by('candidate')

        context['status_choices'] = ['----',
                                     Appointment.SENT,
                                     Appointment.ACCEPTED,
                                     Appointment.DECLINED]
        return context


    def post(self, request, *args, **kwargs):
        print request.POST

        for key, value in request.POST.items():
            if key.startswith('appointment'):
                pk = key[12:]

                try:
                    appointment = Appointment.objects.get(pk=pk)
                except Appointment.DoesNotExist:
                    logger.exception('Could not find appointment #{pk}'.format(
                        pk=pk))
                    continue

                try:
                    assert value in ['----',
                                     Appointment.SENT,
                                     Appointment.DECLINED,
                                     Appointment.ACCEPTED]
                except AssertionError:
                    logger.exception('Received bad status {status}'.format(
                        status=value))

                if value == '----':
                    continue

                appointment.status = value
                appointment.save()

        messages.add_message(request, messages.INFO, 'Updated! Thank you for '
            'working on appointments today.')
        return HttpResponseRedirect(reverse_lazy('candidates:appointments'))

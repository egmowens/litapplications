import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.forms import modelformset_factory
from django.forms.widgets import TextInput, Select
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.views.generic.base import View, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from litapplications.candidates.models import Candidate, Appointment
from litapplications.committees.models.units import get_privileged_units

from .forms import UpdateNotesForm, UpdateNumbersForm, CommitteeCreateForm
from .models.committees import Committee

logger = logging.getLogger(__name__)


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
            # We need to make sure to remove all the appointments removed by
            # the default manager - they aren't removed when we filter the
            # Candidate queryset!
            appointments__in=Appointment.objects.all(),
            appointments__status=Appointment.APPLICANT,
            appointments__committee=obj).distinct()

        context['potential'] = Candidate.objects.filter(
            appointments__in=Appointment.objects.all(),
            appointments__status=Appointment.POTENTIAL,
            appointments__committee=obj).distinct()

        context['recommended'] = Candidate.objects.filter(
            appointments__in=Appointment.objects.all(),
            appointments__status=Appointment.RECOMMENDED,
            appointments__committee=obj).distinct()

        context['sent'] = Candidate.objects.filter(
            appointments__in=Appointment.objects.all(),
            appointments__status=Appointment.SENT,
            appointments__committee=obj).distinct()

        context['accepted'] = Candidate.objects.filter(
            appointments__in=Appointment.objects.all(),
            appointments__status=Appointment.ACCEPTED,
            appointments__committee=obj).distinct()

        context['not_recommended'] = Candidate.objects.filter(
            appointments__in=Appointment.objects.all(),
            appointments__status=Appointment.NOPE,
            appointments__committee=obj).distinct()

        context['declined'] = Candidate.objects.filter(
            appointments__in=Appointment.objects.all(),
            appointments__status=Appointment.DECLINED,
            appointments__committee=obj).distinct()

        context['candidates'] = Candidate.objects.filter(
            appointments__in=Appointment.objects.all(),
            appointments__committee=obj).distinct()

        # For constructing the dropdown in the batch editing form.
        context['status_choices'] = [choice for choice
            in Appointment.STATUS_CHOICES
            if choice[0]
            in Appointment.settable_statuses(self.request.user, obj.unit)]

        context['notes_form'] = UpdateNotesForm(instance=self.get_object())
        context['numbers_form'] = UpdateNumbersForm(instance=self.get_object())

        return context



class UpdateNotesView(LoginRequiredMixin, UpdateView):
    model = Committee
    fields = ['notes']

    def form_invalid(self, form):
        response = super(UpdateNotesView, self).form_invalid(form)
        for error in form.errors.values():
            messages.add_message(self.request, messages.WARNING,
                error.as_data()[0][0]) # just the message, no formatting

        return HttpResponseRedirect(self.get_success_url())


    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS,
            'Update successful. Thank you for working on appointments today!')
        return super(UpdateNotesView, self).form_valid(form)


    def get_success_url(self):
        return self.get_object().get_absolute_url()



class UpdateNumbersView(LoginRequiredMixin, UpdateView):
    model = Committee
    fields = ['min_appointees', 'max_appointees']

    def form_invalid(self, form):
        super(UpdateNumbersView, self).form_invalid(form)

        for error in form.errors.values():
            messages.add_message(self.request, messages.WARNING,
                error.as_data()[0][0]) # just the message, no formatting

        return HttpResponseRedirect(self.get_success_url())


    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS,
            'Update successful. Thank you for working on appointments today!')
        return super(UpdateNumbersView, self).form_valid(form)


    def get_success_url(self):
        return self.get_object().get_absolute_url()



class UpdateOwnerView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        try:
            committee = Committee.objects.get(pk=self.kwargs['pk'])
        except Committee.DoesNotExist:
            # ValueError will be raised if the status cannot be cast to int.
            logger.exception('Tried to update status for nonexistent committee')
            return HttpResponseBadRequest()

        committee.owner = request.user
        committee.save()

        messages.add_message(request, messages.SUCCESS,
            'You now own {committee}. Thank you for working on appointments '
            'today!'.format(committee=committee))

        return HttpResponseRedirect(reverse_lazy('committees:list'))



class CommitteeCreateView(LoginRequiredMixin, TemplateView):
    new_committees = None
    template_name = 'committees/committee_multiple_form.html'

    def dispatch(self, request, *args, **kwargs):
        if not (self.request.user.is_superuser or
                self.request.user.groups.filter(name='Chairs')):
            messages.add_message(request, messages.INFO,
                'Sorry; you need additional permissions to access that page.')
            return HttpResponseRedirect(reverse_lazy('home'))
        return super(CommitteeCreateView, self).dispatch(
            request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super(CommitteeCreateView, self).get_context_data(**kwargs)
        privileged_units = get_privileged_units(self.request.user)
        unit_choices = [(unit.id, unit) for unit in privileged_units]

        if self.new_committees:
            CommitteeFormSet = modelformset_factory(Committee,
                form=CommitteeCreateForm,
                widgets={'short_code': TextInput(attrs={'readonly': True}),
                         'unit': Select(choices=unit_choices)
                        },
                extra=len(self.new_committees))
            initial_data = [{'short_code': short_code}
                            for short_code in self.new_committees]
            formset = CommitteeFormSet(
                        initial=initial_data,
                        queryset=Committee.objects.none())
            form_count = formset.total_form_count()
            context['formset'] = formset
        else:
            form = CommitteeCreateForm()
            form_count = 1
            context['form'] = form

        context['form_count'] = form_count # Used to pluralize header.

        return context


    def post(self, request, *args, **kwargs):
        CommitteeFormSet = modelformset_factory(Committee,
            form=CommitteeCreateForm)

        if 'form-TOTAL_FORMS' in request.POST:
            # It had a management form, so it was a formset; use formset logic.
            formset = CommitteeFormSet(request.POST)

            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS,
                    'Committee(s) created. You should reimport your data files'
                    'if you were trying to import potential appointments to '
                    'those committees.')
                return HttpResponseRedirect(reverse_lazy('data_ingest'))
            else:
                return self.render_to_response(
                    self.get_context_data(formset=formset))
        else:
            form = CommitteeCreateForm(request.POST)

            if form.is_valid():
                form.save()
                messages.add_message(request, messages.SUCCESS,
                    'Committee created. You should reimport your data files'
                    'if you were trying to import potential appointments to '
                    'those committees.')
                return HttpResponseRedirect(reverse_lazy('data_ingest'))
            else:
                return self.render_to_response(
                    self.get_context_data(form=form))

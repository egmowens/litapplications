from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView

from litapplications.committees.models import Committee


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['your_committees'] = Committee.objects.filter(
            owner=self.request.user)
        context['lonely_committees'] = Committee.objects.filter(
            owner=None)
        return context

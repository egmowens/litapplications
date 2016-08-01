from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.CandidateListView.as_view(), name='list'),
    url(r'^(?P<pk>\d+)/$', views.CandidateDetailView.as_view(), name='detail'),
    url(r'^(?P<pk>\d+)/update/notes/$', views.CandidateUpdateNotesView.as_view(),
        name='update_notes'),
    url(r'^(?P<pk>\d+)/update/status/$', views.UpdateStatusView.as_view(),
        name='update_status'),
]

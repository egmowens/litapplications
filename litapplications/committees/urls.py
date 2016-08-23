from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.CommitteeListView.as_view(), name='list'),
    url(r'^(?P<pk>\d+)/$', views.CommitteeDetailView.as_view(), name='detail'),
    url(r'^(?P<pk>\d+)/update/notes/$', views.UpdateNotesView.as_view(),
        name='update_notes'),
    url(r'^(?P<pk>\d+)/update/numbers/$', views.UpdateNumbersView.as_view(),
        name='update_numbers'),
    url(r'^(?P<pk>\d+)/update/owner/$', views.UpdateOwnerView.as_view(),
        name='update_owner'),
]

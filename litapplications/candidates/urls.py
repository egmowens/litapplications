from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.CandidateListView.as_view(), name='list'),
    url(r'^(?P<pk>\d+)/$', views.CandidateDetailView.as_view(), name='detail'),
    url(r'^(?P<pk>\d+)/update/note/$', views.UpdateNoteView.as_view(),
        name='update_note'),
    url(r'^create/note/$', views.CreateNoteView.as_view(),
        name='create_note'),
    url(r'^(?P<pk>\d+)/update/status/$', views.UpdateStatusView.as_view(),
        name='update_status'),
    url(r'^(?P<pk>\d+)/update/appointments/$', views.UpdateAppointmentsView.as_view(),
        name='update_appointments'),
    url(r'^(?P<pk>\d+)/update/libtype/$', views.UpdateLibraryTypeView.as_view(),
        name='update_libtype'),
    url(r'^appointments/', views.AppointmentsView.as_view(), name='appointments'),
]

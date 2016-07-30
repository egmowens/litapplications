from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.CandidateListView.as_view(), name='list'),
    url(r'^(?P<pk>\d+)/', views.CandidateDetailView.as_view(), name='detail'),
    url(r'^update/(?P<pk>\d+)/notes/', views.CandidateUpdateNotesView.as_view(),
        name='update_notes'),
]

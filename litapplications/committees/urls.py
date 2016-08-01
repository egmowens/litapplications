from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.CommitteeListView.as_view(), name='list'),
    url(r'^(?P<pk>\d+)/', views.CommitteeDetailView.as_view(), name='detail'),
    url(r'^update/(?P<pk>\d+)/notes/', views.CommitteeUpdateNotesView.as_view(),
        name='update_notes'),
]

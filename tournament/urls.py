from django.conf.urls import url, include
from django.contrib.auth.views import password_change, password_change_done

from . import views

app_name = "tournament"

urlpatterns = [
    url(r'^accounts/password/change/$', password_change, {'post_change_redirect' : '/accounts/password/change/done/'},name="password_change"),
    url(r'^accounts/password/change/done/$',password_change_done),
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout_view/$', views.logout_view, name='logout_view'),
    url(r'^read_in_values/$', views.read_in_values, name='read_in_values'),
    url(r'^update_bracket/$', views.update_bracket, name='update_bracket'),
    url(r'^all_probs/(?P<mode>[-\w]+)/$', views.all_probs, name='all_probs'),
    url(r'^all_probs_Kaggle/$', views.all_probs_Kaggle, name='all_probs_Kaggle'),
    url(r'^tournament_probs/$', views.tournament_probs, name='tournament_probs'),
    url(r'^tournament_probs_download/$', views.tournament_probs_download, name='tournament_probs_download'),
    url(r'^(?P<coefficient_id>[0-9]+)/$', views.update_coefficient, name='update_coefficient'),
]

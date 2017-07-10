from django.conf.urls import url, include
from . import views

ajax_patterns = [
    url(r'^modify', views.ajax_conf_modify, name='modify'),
]

urlpatterns = [
    url(r'^ajax/', include(ajax_patterns, namespace='ajax')),
    url(r'^rule', views.rule_conf, name='rule'),
]
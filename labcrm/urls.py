from django.conf.urls import url, include
from labcrm import views


ajax_urls = [
    url(r'^preview', views.ajax_preview, name='preview')
]


urlpatterns = [
    url(r'^ajax/', include(ajax_urls, namespace='ajax')),
    url(r'^users', views.user_list, name='list'),
    url(r'^detail', views.user_detail, name='detail'),
    url(r'^conf', views.ques_conf, name='conf'),
    url(r'^fill', views.ques_fill, name='fill'),
    url(r'^add', views.ques_add, name='add'),
]

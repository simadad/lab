from django.conf.urls import url, include
from labcrm import views


ajax_urls = [
    url(r'^preview', views.ajax_conf_preview, name='preview'),
    # url(r'^modify', views.ajax_detail_modify, name='modify'),
    url(r'^add', views.ajax_conf_add, name='add'),
    url(r'^del', views.ajax_user_del, name='del'),
]


urlpatterns = [
    url(r'^ajax/', include(ajax_urls, namespace='ajax')),
    url(r'^users', views.user_list, name='list'),
    url(r'^detail/(?P<new_id>.*)$', views.user_detail, name='detail2'),
    url(r'^detail', views.user_detail, name='detail'),
    url(r'^paper', views.paper_display, name='paper'),
    url(r'^conf', views.ques_conf, name='conf'),
    url(r'^fill/(?P<data_key>[\s\S]*)$', views.ques_fill, name='fill'),
    url(r'^fill', views.ques_fill, name='fill2'),
    url(r'^class', views.link_to_class, name='class'),
]

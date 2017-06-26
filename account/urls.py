from django.conf.urls import url, include
from .views import register, log_in

urlpatterns = [
    url(r'^register', register, name='register'),
    url(r'^login', log_in, name='login'),
]

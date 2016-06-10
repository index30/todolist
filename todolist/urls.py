from django.conf.urls import url
from . import views
from .views import *
from django.conf import settings
import django.contrib.auth.views

urlpatterns = [
    url(r'^$',views.top,name='top'),
    url(r'^task/$',views.index,name='index'),
    url(r'^task/(?P<task_id>[0-9]+)/$',views.task_content,name='task'),
    url(r'^task/create/$',views.create,name='create'),
    url(r'^register/$',views.register,name='register'),
    url(r'^login/$',django.contrib.auth.views.login,{'template_name':'todolist/signin.html'},name='signin'),
    url(r'^logout/$',views.signout,name='signout'),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.STATIC_ROOT,
    }
    ),
]


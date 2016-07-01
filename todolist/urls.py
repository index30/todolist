from django.conf.urls import url
from . import views
from .views import *
from django.conf import settings
import django.contrib.auth.views

urlpatterns = [
    url(r'^$',views.top,name='top'),
    url(r'^task/$',views.index,name='index'),
    url(r'^task/$',views.task_done,name='task_done'),
    url(r'^task/(?P<tasks_id>(\d+,)+)/$',views.select_delete,name='select_delete'),
    url(r'^task/(?P<task_id>\d+)/$',views.task_content,name='task'),
    url(r'^task/create/$',views.create,name='create'),
    url(r'^register/$',views.register,name='register'),
    url(r'^login/$',django.contrib.auth.views.login,{'template_name':'todolist/signin.html'},name='signin'),
    url(r'^logout/$',views.signout,name='signout'),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.STATIC_ROOT,
    }
    ),
]


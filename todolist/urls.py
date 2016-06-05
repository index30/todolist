from django.conf.urls import url
from . import views
import django.contrib.auth.views

urlpatterns = [
    url(r'^$',views.top,name='top'),
    url(r'^detail/$',views.index,name='index'),
    url(r'^detail/(?P<task_id>[0-9]+)/$',views.task_content,name='detail'),
    url(r'^detail/(?P<task_id>[0-9]+)/delete$',views.delete_task,name='delete'),
    url(r'^make/$',views.make_task,name='make'),
    url(r'^register/$',views.register,name='register'),
    url(r'^login/$',django.contrib.auth.views.login,{'template_name':'todolist/signin.html'},name='signin'),
    url(r'^logout/$',views.signout,name='signout')
]

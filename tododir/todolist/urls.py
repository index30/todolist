from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$',views.top,name='top'),
    url(r'^detail/$',views.index,name='index'),
    url(r'^detail/(?P<task_id>[0-9]+)/$',views.task_content,name='detail'),
    url(r'^detail/(?P<task_id>[0-9]+)/delete$',views.delete_task,name='delete'),
    url(r'^make/$',views.make_task,name='make'),
]

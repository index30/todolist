from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$',views.index,name='index'),
    #url(r'^todolist/(?P<id>[0-9]+)/$',views.task_content,name='detail'),
]

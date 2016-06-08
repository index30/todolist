import json
from django.shortcuts import render,redirect,get_object_or_404,render_to_response
from django.core.context_processors import csrf
from django.template import RequestContext
from django.contrib.auth import authenticate,login,logout,models
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404

from .models import Task
from django.contrib.auth.models import User

import datetime

from django.views.decorators.http import require_GET

from django.views.generic import View

def top(request):
    return render_to_response('todolist/top.html',RequestContext(request,{}))

@login_required
def index(request):
    task_list = Task.objects.filter(user=request.user)
    context = {
        'task_list':task_list
    }
    return render_to_response('todolist/index.html',RequestContext(request,context))

@login_required
def task_content(request, task_id):
    if request.method == "GET":
        task_num = int(task_id)
        task_content = Task.objects.get(id=task_id)
        task_context = {
            'task_content':task_content
        }
        return render_to_response('todolist/task.html',RequestContext(request,task_context))
    elif request.method == "DELETE":
        # d_task = get_object_or_404(Task,pk=task_id)
        try:
            d_task = Task.objects.get(id=task_id)
            # 削除する
            d_task.delete()
            return HttpResponse(json.dumps({"status": "OK"}), content_type='application/json')
        except Task.DoesNotExist:
            return HttpResponse(json.dumps({"status": "404"}), content_type='application/json')

@login_required
def create(request):
    try:
        m_title = request.POST['title']
        m_text = request.POST['text']
        m_done = False
        m_created_at = datetime.datetime.now()
        m_updated_at = datetime.datetime.now()
        m_finished_at = request.POST['finish']
        m_user = request.user
        
    except (KeyError,Task.DoesNotExist):
        return render_to_response('todolist/create.html',RequestContext(request,{}))
    else:
        Task(title=m_title,text=m_text,done=m_done,created_at=m_created_at,updated_at=m_updated_at,finished_at=m_finished_at,user=m_user).save()
    return redirect('index')

def register(request):
    try:
        u_name=request.POST['user_name']
        u_email=request.POST['email']
        u_pass=request.POST['password']
    except (KeyError,User.DoesNotExist):
        return render_to_response('todolist/make_user.html',RequestContext(request,{}))
    else:
        User.objects.create_user(u_name,u_email,u_pass).save()
    return redirect('top')

def signout(request):
    logout(request)
    return redirect('top')

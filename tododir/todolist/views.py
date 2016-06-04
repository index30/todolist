from django.shortcuts import render,redirect,get_object_or_404,render_to_response
from django.core.context_processors import csrf
from django.template import RequestContext
from django.contrib.auth import authenticate,login,logout,models
from django.contrib.auth.decorators import login_required

from .models import Task
from django.contrib.auth.models import User

import datetime

from .forms import NewUserCreationForm as UserCreationForm
from django.views.decorators.http import require_GET

def top(request):
    return render_to_response('todolist/top.html',RequestContext(request,{}))

@login_required
def index(request):
    task_list = Task.objects.filter(user=request.user)
    context = {
        'task_list':task_list
    }
    return render(request, 'todolist/index.html', context)

@login_required
def task_content(request, task_id):
    task_num = int(task_id)
    task_content = Task.objects.get(id=task_id)
    task_context = {
        'task_content':task_content
    }
    return render(request, 'todolist/detail.html',task_context)

@login_required
def make_task(request):
    try:
        m_title = request.POST['title']
        m_text = request.POST['text']
        m_done = False
        m_created_at = datetime.datetime.now()
        m_updated_at = datetime.datetime.now()
        m_finished_at = request.POST['finish']
        m_user = request.user
        
    except (KeyError,Task.DoesNotExist):
        return render(request,'todolist/make.html')
    else:
        Task(title=m_title,text=m_text,done=m_done,created_at=m_created_at,updated_at=m_updated_at,finished_at=m_finished_at,user=m_user).save()
    return redirect('index')

@login_required
def delete_task(request,task_id):
    d_task = get_object_or_404(Task,pk=task_id)
    print(d_task)
    d_task.delete()
    return redirect('index')

def register(request):
    try:
        u_name=request.POST['user_name']
        u_email=request.POST['email']
        u_pass=request.POST['password']
    except (KeyError,User.DoesNotExist):
        return render(request,'todolist/make_user.html')
    else:
        User.objects.create_user(u_name,u_email,u_pass).save()
    return redirect('top')

def signout(request):
    logout(request)
    return redirect('top')

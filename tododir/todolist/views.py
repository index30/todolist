from django.shortcuts import render,redirect,get_object_or_404,render_to_response
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required

from .models import Task
from .models import User

import datetime

from .forms import NewUserCreationForm as UserCreationForm
from django.views.decorators.http import require_GET

def top(request):
    return render(request, 'todolist/top.html')

@login_required
def index(request):
    task_list = Task.objects.all()
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
    except (KeyError,Task.DoesNotExist):
        return render(request,'todolist/make.html')
    else:
        #Task t
        #t.m_title = 
        Task(title=m_title,text=m_text,done=m_done,created_at=m_created_at,updated_at=m_updated_at,finished_at=m_finished_at).save()
    return redirect('index')

@login_required
def delete_task(request,task_id):
    d_task = get_object_or_404(Task,pk=task_id)
    print(d_task)
    d_task.delete()
    return redirect('index')

#@require_GET
#def to_register(request):
#    form = UserCreationForm()
#    c = {'form': form}
#    c.update(csrf(request))
#    print('toregi')
#    return render_to_response('todolist/make_user.html', c)

def register(request):
    try:
        u_name=request.POST['user_name']
        u_email=request.POST['email']
        u_pass=request.POST['password']
    except (KeyError,Task.DoesNotExist):
        return render(request,'todolist/make_user.html')
    else:
        User(name=u_name,email=u_email,password=u_pass).save()
    return redirect('top')

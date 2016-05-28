from django.shortcuts import render,redirect,get_object_or_404
from .models import Task

import datetime

def top(request):
    return render(request, 'todolist/top.html')

def index(request):
    task_list = Task.objects.all()
    context = {
        'task_list':task_list
    }
    return render(request, 'todolist/index.html', context)

def task_content(request, task_id):
    task_num = int(task_id)
    task_content = Task.objects.get(id=task_id)
    task_context = {
        'task_content':task_content
    }
    return render(request, 'todolist/detail.html',task_context)

def make_task(request):
    try:
        id=4
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

def delete_task(request,task_id):
    d_task = get_object_or_404(Task,pk=task_id)
    print(d_task)
    d_task.delete()
    return redirect('index')

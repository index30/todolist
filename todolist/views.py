import json
import sys
import re
import datetime
from .models import Task
from dateutil.relativedelta import relativedelta
from django.http import HttpResponse, Http404, QueryDict
from django.shortcuts import render,redirect,get_object_or_404,render_to_response
from django.template.context_processors import csrf
from django.template import RequestContext
from django.contrib.auth import authenticate,login,logout,models
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_GET
from django.views.generic import View

def top(request):
    '''
    if request.user.is_authenticated:
        task_list = Task.objects.filter(user=request.user)
        context = {
            'task_list':task_list
        }
    else:
        context=''
'''
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
        task_content = Task.objects.get(id=task_id)
        task_info = {
            'task_content':task_content
        }
        return render_to_response('todolist/task.html',RequestContext(request,task_info))
    elif request.method == "DELETE":
        # d_task = get_object_or_404(Task,pk=task_id)
        try:
            del_task = Task.objects.get(id=task_id)
            # 削除する
            del_task.delete()
            return HttpResponse(json.dumps({"status": "OK"}), content_type='application/json')
        except Task.DoesNotExist:
            return HttpResponse(json.dumps({"status": "404"}), content_type='application/json')

@login_required
def select_chk_or_del(request,tasks_id):
    if request.method == "DELETE":
        try:
            task_list = list(map(int,tasks_id[:-1].split(",")))
        except(KeyError):
            return redirect('index')
        else:
            [Task.objects.get(id=t).delete() for t in task_list]
            #for tip in task_list:
            #    Task.objects.get(id=tip).delete()
            return HttpResponse(json.dumps({"status": "OK"}), content_type='application/json')
    elif request.method == "GET":
        print("test")
        try:
            task_id = list(map(int,tasks_id[:-1].split(",")))
            emp = []
            for task_num in task_id:
                task_content = Task.objects.get(id=task_num)
                emp.append(task_content)
        except(KeyError,Task.DoesNotExist):
            return redirect('top')
        else:
            for tip in emp:
                if tip.done == False:
                    tip.done = True
                else:
                    tip.done = False
                tip.save()
            task_list = Task.objects.filter(user=request.user)
            context = {
                'task_list':task_list
            }
            return HttpResponse(json.dumps({"status": "OK"}), content_type='application/json')
    
@login_required
def create(request):
    try:
        new_title = request.POST['title']
        new_text = request.POST['text']
        new_done = False
        new_created_at = datetime.datetime.now()
        new_updated_at = datetime.datetime.now()
        tdatatime = request.POST['finish']
        new_user = request.user
    except (KeyError,Task.DoesNotExist):
        return render_to_response('todolist/create.html',RequestContext(request,{}))
    else:
        pattern = "(20)[0-9]{2}\-[0-9]{1,2}\-[0-9]{1,2}[T](0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]"
        matchOB = re.match(pattern,tdatatime)
        if matchOB:
            new_finished_at = datetime.datetime.strptime(tdatatime, '%Y-%m-%dT%H:%M')
            if new_title and new_text and new_created_at < new_finished_at and new_finished_at < (new_created_at + relativedelta(years=80)):
                Task(title=new_title,text=new_text,done=new_done,created_at=new_created_at,updated_at=new_updated_at,finished_at=new_finished_at,user=new_user).save()
                return redirect('index')
            else:
                error_mes = True
                return render_to_response('todolist/create.html',RequestContext(request,error_mes))
        else:
            error_mes = True
            return render_to_response('todolist/create.html',RequestContext(request,error_mes))
        
def register(request):
    if not request.user.is_authenticated():
        try:
            new_name=request.POST['user_name']
            new_email=request.POST['email']
            new_pass=request.POST['password']
            conf_pass=request.POST['confirm']
        except (KeyError,User.DoesNotExist):
            return render_to_response('todolist/make_user.html',RequestContext(request,{}))
        else:
            if new_pass == conf_pass:
                User.objects.create_user(new_name,new_email,new_pass).save()
                return redirect('signin')
            else:
                error_mes = True
                return render_to_response('todolist/make_user.html',RequestContext(request,error_mes))
    else:
        return redirect('signin')

@login_required
def signout(request):
    logout(request)
    return redirect('top')

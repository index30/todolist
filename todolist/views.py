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
#    if request.user.is_authenticated:
#        task_list = Task.objects.filter(user=request.user)
#        context = {
#            'task_list':task_list
#        }
#    else:
#        context=''
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
def task_done(request,task_id):
    try:
        task_num = int(task_id)
        #task_num = request.POST['chkbox']
        task_content = Task.objects.get(id=task_num)
        print(task_content)
        if(task_content.done == False):
            task_content.done = True
        else:
            task_content.done = False
        task_content.save()
        task_list = Task.objects.filter(user=request.user)
        context = {
            'task_list':task_list
        }
        return render_to_response('todolist/index.html',RequestContext(request,context))
    except(KeyError,Task.DoesNotExist):
        return redirect('top')
    
@login_required
def select_delete(request,tasks_id):
    if request.method == "DELETE":
        try:
            data = tasks_id
            task_list = list(map(int,data[:-1].split(",")))
        except(KeyError):
            return redirect('index')
        else:
            #Task.objects.filter(id=task_list).delete()
            for tip in task_list:
                Task.objects.get(id=tip).delete()
            return HttpResponse(json.dumps({"status": "OK"}), content_type='application/json')
    else:
        return redirect('index')
    
@login_required
def create(request):
    try:
        m_title = request.POST['title']
        m_text = request.POST['text']
        m_done = False
        m_created_at = datetime.datetime.now()
        m_updated_at = datetime.datetime.now()
        #strをdatetimeに変換出来ない
        tdatatime = request.POST['finish']
        m_user = request.user
    except (KeyError,Task.DoesNotExist):
        return render_to_response('todolist/create.html',RequestContext(request,{}))
    else:
        pattern = "(20)[0-9]{2}\-[0-9]{1,2}\-[0-9]{1,2}[T](0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]"
        matchOB = re.match(pattern,tdatatime)
        if matchOB:
            m_finished_at = datetime.datetime.strptime(tdatatime, '%Y-%m-%dT%H:%M')
            if m_title and m_text and m_created_at < m_finished_at and m_finished_at < (m_created_at + relativedelta(years=80)):
                Task(title=m_title,text=m_text,done=m_done,created_at=m_created_at,updated_at=m_updated_at,finished_at=m_finished_at,user=m_user).save()
                return redirect('index')
            else:
                error_mes = True
                return render_to_response('todolist/create.html',RequestContext(request,error_mes))
        else:
            error_mes = True
            return render_to_response('todolist/create.html',RequestContext(request,error_mes))
        
def register(request):
    #login中はloginに飛ぶ
    if not request.user.is_authenticated():
        try:
            u_name=request.POST['user_name']
            u_email=request.POST['email']
            u_pass=request.POST['password']
            c_pass=request.POST['confirm']
        except (KeyError,User.DoesNotExist):
            return render_to_response('todolist/make_user.html',RequestContext(request,{}))
        else:
            if u_pass == c_pass:
                User.objects.create_user(u_name,u_email,u_pass).save()
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

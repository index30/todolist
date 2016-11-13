import json
import sys
import re
import datetime
import requests
from collections import OrderedDict
from django.db import IntegrityError
from .models import Task
from .common import Common
from django.conf import settings
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
    if request.user.is_authenticated():
        task_list = Task.objects.filter(user=request.user, done=False)
        context = {
            'task_list': task_list,
            'number': task_list.count()
        }
    else:
        context = {
            'error_mes': "ログイン/ユーザー登録して下さい"
        }
    return render_to_response('todolist/top.html', RequestContext(request,
                                                                  context))


@login_required
def index(request):
    task_list = Task.objects.filter(user=request.user)
    context = {
        'task_list': task_list
    }
    return render_to_response('todolist/index.html',
                              RequestContext(request, context))


@login_required
def task_content(request, task_id):
    if request.method == "GET":
        task_info = Common.get_task(request,task_id)
        if len(task_info) > 0:
            return render_to_response('todolist/task.html',
                                      RequestContext(request, task_info))
        else:
            return redirect('top')
    elif request.method == "DELETE":
        Common.delete_task(request,task_id)


@login_required
def select_chk_or_del(request, tasks_id):
    if request.method == "DELETE":
        try:
            task_list = list(map(int, tasks_id[:-1].split(",")))
        except(KeyError):
            return redirect('index')
        else:
            for t in task_list:
                del_task = Task.objects.get(id=t)
                if del_task.user.username == request.user.username:
                    del_task.delete()
            # [Task.objects.get(id=t).delete() for t in task_list]
            # for tip in task_list:
            #    Task.objects.get(id=tip).delete()
            return HttpResponse(json.dumps({"status": "OK"}),
                                content_type='application/json')
    elif request.method == "GET":
        print("test")
        try:
            task_id = list(map(int, tasks_id[:-1].split(",")))
            emp = []
            for task_num in task_id:
                task_content = Task.objects.get(id=task_num)
                emp.append(task_content)
        except(KeyError, Task.DoesNotExist):
            return redirect('top')
        else:
            for tip in emp:
                if not tip.done:
                    tip.done = True
                else:
                    tip.done = False
                tip.save()
            # task_list = Task.objects.filter(user=request.user)
            # context = {
            #    'task_list': task_list
            # }
            return HttpResponse(json.dumps({"status": "OK"}),
                                content_type='application/json')


def make_tab(line):
    print("test")
    n_line = line.split(' ')
    n_line[1] = n_line[1][:-3]
    new_line = "T".join(n_line)
    print(new_line)
    return new_line


@login_required
def create(request):
    try:
        new_title = request.POST['title']
        new_text = request.POST['text']
        new_done = False
        new_created_at = datetime.datetime.now()
        new_updated_at = datetime.datetime.now()
        tdatatime = request.POST['finish']
        now_user = request.user
    except (KeyError, Task.DoesNotExist):
        return render_to_response('todolist/create.html',
                                  RequestContext(request, {}))
    else:
        pattern = "(20)[0-9]{2}\-[0-9]{1,2}\-[0-9]{1,2}[T](0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]"
        
        tdata = make_tab(tdatatime)
        matchOB = re.match(pattern, tdata)
        if matchOB:
            new_finished_at = datetime.datetime.strptime(tdata,
                                                         '%Y-%m-%dT%H:%M')
            if new_title and new_text:
                if len(new_title) < 50 and len(new_text) < 1000:
                    if new_created_at < new_finished_at and new_finished_at < (new_created_at + relativedelta(years=80)):
                        Task(title=new_title, text=new_text, done=new_done,
                             created_at=new_created_at, updated_at=new_updated_at,
                             finished_at=new_finished_at, user=now_user).save()
                        return redirect('index')
                    else:
                        b_error = True
                        error_mes = "過去のタスクを作成する事は出来ません."
                        content = {
                            'message': error_mes,
                            'b_error': b_error
                        }
                        return render_to_response('todolist/create.html',
                                                  RequestContext(request,
                                                                 content))
                elif len(new_title) >= 50:
                    b_error = True
                    error_mes = "タイトルが長過ぎます.50文字以内にして下さい"
                    content = {
                        'message': error_mes,
                        'b_error': b_error
                    }
                    return render_to_response('todolist/create.html',
                                              RequestContext(request,
                                                             content))
                else:
                    b_error = True
                    error_mes = "タスクの内容が長過ぎます.1000文字以内にして下さい"
                    content = {
                        'message': error_mes,
                        'b_error': b_error
                    }
                    return render_to_response('todolist/create.html',
                                              RequestContext(request,
                                                             content))
            else:
                b_error = True
                error_mes = "タイトルかタスクの内容が空欄です."
                content = {
                    'message': error_mes,
                    'b_error': b_error
                }
                return render_to_response('todolist/create.html',
                                          RequestContext(request, content))
        else:
            b_error = True
            error_mes = "Deadlineの入力形式が異なっています."
            content = {
                'message': error_mes,
                'b_error': b_error
            }
            return render_to_response('todolist/create.html',
                                      RequestContext(request, content))


def auth_captcha(request):

        # 開発環境などではFalseにしておく
    if not settings.CAPTCHA:
        return True

    captcha = request.POST.get("g-recaptcha-response", "")
    if captcha:
        origin_url = "https://www.google.com/recaptcha/api/siteverify?secret={}&response={}"
        url = origin_url.format(
            settings.CAPTCHA_SECRETKEY, captcha)
        res = requests.get(url)

        #  認証成功ならTrue、失敗ならFalse
        if res.json().get("success", ""):
            return True

    return False


def register(request):
    if not request.user.is_authenticated():
        try:
            new_name = request.POST['user_name']
            new_email = request.POST['email']
            new_pass = request.POST['password']
            conf_pass = request.POST['confirm']
        except (KeyError, User.DoesNotExist):
            return render_to_response('todolist/make_user.html',
                                      RequestContext(request, {}))
        else:
            if auth_captcha(request):
                if new_pass == conf_pass:
                    user = authenticate(username=new_name, password=new_pass)
                    if user is None:
                        try:
                            User.objects.create_user(new_name,
                                                     new_email,
                                                     new_pass).save()
                        except(IntegrityError):
                            b_error = True
                            error_mes = "appleなど,単純な名前は避けて下さい"
                            content = {
                                'message': error_mes,
                                'b_error': b_error
                            }
                            return render_to_response(
                                'todolist/make_user.html',
                                RequestContext(request, content))
                        else:
                            return redirect('signin')
                    else:
                        b_error = True
                        error_mes = "そのユーザーは既に存在します"
                        content = {
                            'message': error_mes,
                            'b_error': b_error
                        }
                        return render_to_response('todolist/make_user.html',
                                                  RequestContext(request,
                                                                 content))
                else:
                    b_error = True
                    error_mes = "パスワードが異なっています"
                    content = {
                        'message': error_mes,
                        'b_error': b_error
                    }
                    return render_to_response('todolist/make_user.html',
                                              RequestContext(request, content))
            else:
                b_error = True
                error_mes = "チェックを入れて下さい"
                content = {
                    'message': error_mes,
                    'b_error': b_error
                }
                return render_to_response('todolist/make_user.html',
                                          RequestContext(request, content))
    else:
        return redirect('signin')


@login_required
def signout(request):
    logout(request)
    return redirect('top')

def render_json_response(request, data, status=None):
    """response を JSON で返却"""
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    callback = request.GET.get('callback')
    if not callback:
        callback = request.POST.get('callback')  # POSTでJSONPの場合
        if callback:
            json_str = "%s(%s)" % (callback, json_str)
            response = HttpResponse(json_str, content_type='application/javascript; charset=UTF-8', status=status)
        else:
            response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=status)
        return response
        

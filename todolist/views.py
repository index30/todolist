import json
import sys
import re
from datetime import datetime
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
        if Common.delete_task(request,task_id):
            return HttpResponse(json.dumps({"status": "OK"}),
                                content_type='application/json')
        else:
            return HttpResponse(json.dumps({"status": "404"}),
                                content_type='application/json')

@login_required
def select_chk_or_del(request, tasks_id):
    if request.method == "DELETE":
        try:
            task_list = list(map(int, tasks_id[:-1].split(",")))
        except(KeyError):
            return redirect('index')
        #本来ならCommon.delete_taskを用いたいが、500
        for t in task_list:
            Common.delete_task(request,t)
        return HttpResponse(json.dumps({"status": "OK"}),
                            content_type='application/json')

    elif request.method == "GET":
        try:
            task_id = list(map(int, tasks_id[:-1].split(",")))
            emp = []
            for task_num in task_id:
                task_content = Task.objects.get(id=task_num)
                emp.append(task_content)
        except(KeyError, Task.DoesNotExist):
            return redirect('top')
        for tip in emp:
            if not tip.done:
                tip.done = True
            else:
                tip.done = False
            tip.save()
        return HttpResponse(json.dumps({"status": "OK"}),
                            content_type='application/json')


def make_tab(line):
    n_line = line.split(' ')
    n_line[1] = n_line[1][:-3]
    new_line = "T".join(n_line)
    return new_line


@login_required
def create(request):
    content = {'message': "", 'b_error': True}
    response = lambda content: render_to_response('todolist/create.html',
                                                  RequestContext(request, content))
    if request.method == "GET":
        return response({})

    new_title = request.POST.get('title')
    new_text = request.POST.get('text')
    new_done = False
    new_created_at = datetime.now()
    new_updated_at = datetime.now()
    tdatetime = request.POST.get('finish')
    now_user = request.user

    try:
        new_finished_at = datetime.strptime(tdatetime, '%Y-%m-%d %H:%M:%S')

        if not new_title or not new_text:
            content.update({'message': "タイトルかタスクの内容が空欄です."})
            return response(content)

        if len(new_title) > 50 or len(new_text) > 1000:
            message = "タイトルが長すぎます.50文字以内にして下さい" if len(new_title) > 50 else \
                      "タスクの内容が長過ぎます.1000文字以内にして下さい"
            content.update({'message': message})
            return response(content)

        if new_created_at >= new_finished_at or \
           new_finished_at > (new_created_at + relativedelta(years=80)):
            content.update({'message': "過去のタスクを作成する事は出来ません."})
            return response(content)

        Task(title=new_title, text=new_text, done=new_done,
             created_at=new_created_at, updated_at=new_updated_at,
             finished_at=new_finished_at, user=now_user).save()
        return redirect('index')
    except ValueError:
        content.update({'message': "Deadlineの入力形式が異なっています."})
        return response(content)


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
    

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

def render_json_response(request, data, status=None):
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

def api_content(request, task_id):
    if request.method == "GET":
        tasks = Common.get_task(request,task_id)
        print(tasks)
        print(len(tasks))
        if len(tasks) > 0:
            task_info = tasks['task_content']
            task = []
            task_dict = OrderedDict([
                ('id', task_info.id),
                ('title', task_info.title),
                ('text', task_info.text),
                ('done', task_info.done)
#                ('finished_at', task_info.finished_at)
            ])
            task.append(task_dict)
            data = OrderedDict([('tasks', task)])
            return render_json_response(request, data)
        else:
            return render_json_response(request, tasks)
    elif request.method == "DELETE":
        Common.delete_task(request,task_id)

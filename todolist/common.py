import json
import sys
import re
import datetime
import requests
from collections import OrderedDict
from django.db import IntegrityError
from .models import Task
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

class Common:
    def get_task(request,task_id):
        try:
            task_content = Task.objects.get(id=task_id)
        except(KeyError, Task.DoesNotExist):
            task = {}
            return task
        if task_content.user.username == request.user.username:
            task = {
                'task_content': task_content
            }
            return task
        else:
            task = {}
            return task
        
        
    def delete_task(request,task_id):
        # d_task = get_object_or_404(Task,pk=task_id)
        try:
            del_task = Task.objects.get(id=task_id)
            # 削除する
            if del_task.user.username == request.user.username:
                del_task.delete()
            return True
        except Task.DoesNotExist:
            return False



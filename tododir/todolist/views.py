from django.shortcuts import render

from .models import Task

def index(request):
    task_list = Task.objects.all()
    context = {
        'task_list':task_list
    }
    return render(request, 'todolist/index.html', context)

'''
def task_content(request, task_id="1"):
    task_num = int(task_id)
    task_content = Task.objects.filter(id=task_id)
    task_context = {
        'task_content':task_content
    }
    return render(request, 'todolist/detail.html',context)
'''

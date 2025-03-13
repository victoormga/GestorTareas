from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.utils import timezone
from .forms import TaskForm
from .models import Task

# Home
def home(request):
    return render(request, 'tasks/home.html')

#Sign Up
def signup(request):

    if request.method == 'GET':
        return render(request, 'tasks/signup.html', {
        'form': UserCreationForm
    })
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                #Registro del usuario
                user = User.objects.create_user(
                username=request.POST['username'],
                password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                return render(request, 'tasks/signup.html', {
                    'form': UserCreationForm,
                    'error': 'User already exists'
                    })
        return render(request, 'tasks/signup.html', {
            'form': UserCreationForm,
            'error': 'Passwords do not match'
        })
    
def tasks(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True) # Muestra según el usuario y según si está completada, por la fecha

    return render(request, 'tasks/tasks.html', {'tasks': tasks})

def create_task(request):
    
    if request.method == 'GET':
        return render(request, 'tasks/create_task.html', {
            'form': TaskForm
        })
    else: 
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'tasks/create_task.html', {
                'form': TaskForm,
                'error': 'Please privide vailda data'
            })

def task_detail(request, task_id):
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'tasks/task_detail.html', {'task': task, 'form': form})
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'tasks/task_detail.html', {'task': task, 'form': form, 
                'error': 'Error updating task'})

def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')

def log_out(request):
    logout(request)
    return redirect('home')

def log_in(request):
    if request.method == 'GET' :
        return render(request, 'tasks/login.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST
            ['password'])
        if user is None:
            return render(request, 'tasks/login.html', {
                'form': AuthenticationForm,
                'error': 'Username or password is incorrect'
            })
        else:
            login(request, user)
            return redirect('tasks')

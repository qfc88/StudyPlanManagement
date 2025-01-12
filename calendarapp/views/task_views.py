from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.generic import View


from calendarapp.models import Task
from calendarapp.forms import TaskForm

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'calendarapp/task_form.html'
    success_url = reverse_lazy('calendarapp:all_tasks')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'calendarapp/task_form.html'
    success_url = reverse_lazy('calendarapp:all_tasks')

class TaskDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        Task.objects.filter(pk=pk, user=request.user).delete()
        return JsonResponse({'status': 'success'})

@login_required
def complete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.user == task.user:
        task.is_completed = True
        task.save()
    return redirect('calendarapp:all_tasks')
@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    if request.method == 'POST':
        task.delete()
        return redirect('calendarapp:all_tasks')
        
    return render(request, 'calendarapp/task_confirm_delete.html', {'task': task})
@login_required
def modify_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'message': 'Task updated successfully'})
            return redirect('calendarapp:all_tasks')
    else:
        form = TaskForm(instance=task)
    
    return render(request, 'calendarapp/modify_task.html', {'form': form})
from django.shortcuts import render

def log_view(request):
    return render(request, 'django_realtime_logs/logs.html')

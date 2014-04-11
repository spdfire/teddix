from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.core.context_processors import csrf

def base_view(request):
    if not request.user.is_authenticated():
        return redirect('/users/login/?next=%s' % request.path)
    else:
        return render(request, 'base.html')

def login(request, *args, **kwargs):
    if request.method == 'POST':
        if not request.POST.get('remember_me', None):
            request.session.set_expiry(1209600) # 2 weeks
    return auth_views.login(request, *args, **kwargs)


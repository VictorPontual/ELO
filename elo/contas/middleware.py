from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse


class AdminOnlyAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user and user.is_authenticated and not (user.is_staff or user.is_superuser):
            if request.path != reverse('logout'):
                logout(request)
                messages.error(request, 'Acesso permitido apenas para contas administrativas.')
                return redirect('login')

        return self.get_response(request)

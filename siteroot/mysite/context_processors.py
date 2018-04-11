def login_modal(request):
    return {
        'login_form': LoginForm(),
    }
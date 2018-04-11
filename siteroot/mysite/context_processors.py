from mysite.forms import LoginForm

def login_modal(request):
    return {
        'login_form': LoginForm(),
    }
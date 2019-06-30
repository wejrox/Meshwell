from mysite.forms import LoginForm


def login_modal(request):
    '''
    Generates a login form and returns it.
    '''
    return {
        'login_form': LoginForm(),
    }
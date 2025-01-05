from bottle import request, redirect


def authenticate(func):
    def wrapper(*args, **kwargs):
        authenticated = True
        session = request.environ.get('beaker.session')
        if not session.get('Logged-In') or not session['Logged-In']:
            authenticated = False
            session['Logged-In'] = False
            session.save()
        elif not session.get('User-Agent') or session['User-Agent'] != request.get_header('User-Agent'):
            session.delete()
            authenticated = False
        if not authenticated:
            return redirect('/login')
        return func(*args, **kwargs)
    return wrapper

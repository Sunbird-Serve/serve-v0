from functools import wraps
from django.shortcuts import render,redirect



def GuardianLogin(function):
  @wraps(function)
  def wrap(request, *args, **kwargs):
    if 'guardian' in request.session:
        if request.session['guardian']:
            return function(request, *args, **kwargs)
        else:
            return redirect('/')
    else:
        return redirect('/')
  return wrap

def StudentLogin(function):
  @wraps(function)
  def wrap(request, *args, **kwargs):
    if 'student' in request.session:
        if request.session['student']:
            return function(request, *args, **kwargs)
        else:
            return redirect('/student/student_dashboard')
    else:
        return redirect('/student/student_dashboard')
  return wrap
from django.shortcuts import render, render_to_response
import httplib2
import json
from django.core.context_processors import csrf
import math
from django.http import HttpResponse
httplib2.debuglevel = 5


# Create your views here.
def _get_session(view):
    def wrapper(r, *args, **kwargs):
        h = httplib2.Http(".cache")
        resp, content = h.request("http://127.0.0.1:8003/sesser/checksession/", 'GET',
                                  headers={'Cookie': r.META['HTTP_COOKIE']})
        print 'SESSION: %s' % content
        session = json.loads(content) if resp.status == 200 else None
        return view(r, session=session, *args, **kwargs)
    return wrapper

def _auth_required(view):
    def wrapper(r, *args, **kwargs):
        session = kwargs.get('session')
        if session is None:
            print 'Not authed'
            return HttpResponse('Not authed', status=403)
        else:
            return view(r, *args, **kwargs)
    return wrapper

@_get_session
def index(request, session=None):
    return render_to_response('base.html', {'title': 'index', 'session': session})

@_get_session
def logout(request, session=None):
    h = httplib2.Http(".cache")
    resp, content = h.request("http://127.0.0.1:8003/sesser/logout/", 'GET',
                              headers={'Cookie': request.META['HTTP_COOKIE']})
    resp = render_to_response('logout.html', {'session': session})
    print 'LOGOUT: %s' % content
    resp['refresh'] = '1'
    return resp

@_get_session
def register(request, session=None):
    if request.POST:
        h = httplib2.Http(".cache")
        credentials = {}
        credentials['login'] = request.POST['login']
        credentials['password'] = request.POST['password']
        credentials['age'] = request.POST['age']
        credentials['email'] = request.POST['email']
        credentials['name'] = request.POST['name']
        credentials['phone'] = request.POST['phone']

        resp, content = h.request("http://127.0.0.1:8003/sesser/register/", 'POST', body=json.dumps(credentials))
        print 'REGISTER: %s' % content
        if resp.status == 201:
            return render_to_response('register_success.html', {'session': session})
        else:
            return render_to_response('register_fail.html', {'session': session})
    else:
        ctx = {'session': session}
        ctx.update(csrf(request))
        return render_to_response('register.html', ctx)

@_get_session
def login(request, session=None):
    if request.POST:
        h = httplib2.Http(".cache")
        credentials = {}
        credentials['login'] = request.POST['login']
        credentials['password'] = request.POST['password']

        resp, content = h.request("http://127.0.0.1:8003/sesser/login/", 'POST', body=json.dumps(credentials))
        print 'LOGIN: %s' % content
        answer = render_to_response('base.html', {'session': session})
        if resp.status == 200:
            answer['set-cookie'] = resp['set-cookie']
        answer['refresh'] = '1'
        return answer

    else:
        ctx = {}
        ctx.update(csrf(request))
        ctx.update({'session': session})
        return render_to_response('login.html', ctx)

@_get_session
def places(request, page_id=1, session=None):
    page_id = int(page_id)
    h = httplib2.Http(".cache")
    resp, content = h.request("http://localhost:8001/places_back/place/?page=%s" % page_id, 'GET')
    print "READ_PLACES: %s" % content
    data = json.loads(content)
    ctx = {'title': 'index',
           'data': data,
           'page_id': page_id,
           'session': session,
           'prev_page': "/meetings/places/watch/{0}".format(int(page_id) - 1) if page_id > 1 else None,
           'next_page': '/meetings/places/watch/{0}'.format(int(page_id) + 1) if page_id < math.ceil(data['total_obj'] / 5.0) else None,
           'total_page': math.ceil(data['total_obj'] / 5.0)}
    ctx.update(csrf(request))
    return render_to_response('places.html', ctx)

@_get_session
def place_add(request, session=None):
    if request.POST:
        h = httplib2.Http(".cache")
        data = {'name': request.POST['title'],
                'x_coord': request.POST['x_coord'],
                'y_coord': request.POST['y_coord']}
        resp, content = h.request("http://localhost:8001/places_back/place/", 'POST', body=json.dumps(data))
        print "ADD_PLACES: %s" % content
    return render_to_response('base.html', {'session': session})

@_get_session
def place_edit(request, session=None):
    if request.POST:
        h = httplib2.Http(".cache")
        data = {}
        if len(request.POST['title']) > 0:
            data['name'] = request.POST['title']
        if len(request.POST['x_coord']) > 0:
            data['x_coord'] = request.POST['x_coord']
        if len(request.POST['y_coord']) > 0:
            data['y_coord'] = request.POST['y_coord']
        resp, content = h.request("http://localhost:8001/places_back/place/%s/" % request.POST['place_id'], 'PUT', body=json.dumps(data))
        print "EDIT_PLACES: %s" % content
    return render_to_response('base.html', {'session': session})

def _get_all_places():
    h = httplib2.Http(".cache")
    resp, content = h.request("http://localhost:8001/places_back/place/", 'GET')
    places = json.loads(content)
    print "GET_ALL_PLACES: %s" % content
    return places['obj']

def _add_places_name(plans, places):
    for plan in plans:
        for place in places:
            if plan['place_id'] == place['id']:
                plan['place_title'] = place['name']


@_get_session
@_auth_required
def plans(request, page_id=1, session=None):
    places = _get_all_places()

    page_id = int(page_id)
    h = httplib2.Http(".cache")
    resp, content = h.request("http://localhost:8002/plans_back/user/%s/plan/?page=%s" % (session['id'], page_id), 'GET')
    print "READ_PLANS: %s" % content
    plans = json.loads(content)
    _add_places_name(plans['obj'], places)
    ctx = {'title': 'index',
           'data': plans,
           'page_id': page_id,
           'session': session,
           'places': places,
           'prev_page': "/meetings/plans/watch/{0}".format(int(page_id) - 1) if page_id > 1 else None,
           'next_page': '/meetings/plans/watch/{0}'.format(int(page_id) + 1) if page_id < math.ceil(plans['total_obj'] / 5.0) else None,
           'total_page': math.ceil(plans['total_obj'] / 5.0)}
    ctx.update(csrf(request))
    return render_to_response('plans.html', ctx)

@_get_session
@_auth_required
def plans_add(request, session):
    if request.POST:
        h = httplib2.Http(".cache")
        call_url = "http://localhost:8002/plans_back/user/%s/plan/" % session['id']
        data = json.dumps({'title': request.POST['title'],
                'user_id': session['id'],
                'date': request.POST['date'],
                'place_id': request.POST['place_id'],
                'body': request.POST['body']})
        resp, content = h.request(call_url, 'POST', body=data)
        print "ADD_PLANS: %s" % content
    return render_to_response('base.html', {'session': session})

@_get_session
@_auth_required
def plans_edit(request, session):
    if request.POST:
        h = httplib2.Http(".cache")
        data = {}
        if len(request.POST['title']) > 0:
            data['title'] = request.POST['title']
        if len(request.POST['date']) > 0:
            data['date'] = request.POST['date']
        if len(request.POST['place_id']) > 0:
            data['place_id'] = request.POST['place_id']
        if len(request.POST['body']) > 0:
            data['body'] = request.POST['body']
        resp, content = h.request("http://localhost:8002/plans_back/user/%s/plan/%s/" % (session['id'],
                                                                                         request.POST['plan_id']),
                                  'PUT', body=json.dumps(data))
        print "EDIT_PLANS: %s" % content
    return render_to_response('base.html', {'session': session})

@_get_session
@_auth_required
def plans_delete(request, session):
    if request.POST:
        h = httplib2.Http(".cache")
        resp, content = h.request("http://localhost:8002/plans_back/user/%s/plan/%s/" % (session['id'],
                                                                                         request.POST['plan_id']),
                                  'DELETE')
        print "DELETE _PLANS: %s" % content
    return render_to_response('base.html', {'session': session})

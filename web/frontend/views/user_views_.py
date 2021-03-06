__author__ = 'Omer Aslan'

import http.client
import urllib.parse
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib import auth

from api.models import User
from api.views import file


def registration_view(request):
    if request.user.is_authenticated():
        return redirect("../homepage")
    else:
        if request.method == "POST":
            name = request.POST['name']
            surname = request.POST['surname']
            email = request.POST['email']
            password = request.POST['password']
            username = request.POST['username']
            params = urllib.parse.urlencode(
                {'name': name,
                 'surname': surname,
                 'email': email,
                 'password': password,
                 'username': username,
                 })
            headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "application/json"}
            connection = http.client.HTTPConnection('127.0.0.1', 8000)
            connection.request("POST", "/api/register/", params, headers)
            registration_response = connection.getresponse()
            registration_data_json = registration_response.read()
            registration_data = json.loads(registration_data_json.decode("utf-8"))
            if registration_data["status"] == "success":
                return render(request, "login.html", {"registration": True})
            else:
                return render(request, "register.html",
                              {"error": True, "error_message": registration_data["message"]})
        else:
            return render(request, "register.html")



def login_view(request):
    if request.user.is_authenticated():
        return redirect("../homepage")
    else:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            params = urllib.parse.urlencode({'username': username, 'password': password})
            headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "application/json"}
            connection = http.client.HTTPConnection('127.0.0.1',8000)
            connection.request("POST", "/api/login/", params, headers)
            login_response = connection.getresponse()
            login_data_json = login_response.read()
            login_data = json.loads(login_data_json.decode("utf-8"))
            user = None
            if login_data['status'] == "success":
                user = authenticate(username=username, password=password)
                login(request, user)
                return redirect("../homepage")
            if user is None:
                return render(request, "./login.html")
            return redirect("../homepage")
        else:
            return render(request, "./login.html")

def forgot_password_view(request):
    if request.user.is_authenticated():
        return redirect("../homepage")
    else:
        return render(request, "./forgot_password.html")

def get_events(user):
    params = urllib.parse.urlencode({'username': user.username})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "application/json"}
    connection = http.client.HTTPConnection('127.0.0.1', 8000)
    connection.request("POST", "/api/get_owned_events/", params, headers)
    event_list_response = connection.getresponse()
    event_list_json_data = event_list_response.read()
    event_list_data = json.loads(event_list_json_data.decode("utf-8"))
    event_list = event_list_data["events"]
    return event_list

def get_event_requests(user):
    params = urllib.parse.urlencode({'username': user.username})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "application/json"}
    connection = http.client.HTTPConnection('127.0.0.1', 8000)
    connection.request("POST", "/api/get_event_requests/", params, headers)
    friend_request_response = connection.getresponse()
    friend_request_json_data = friend_request_response.read()
    friend_request_data = json.loads(friend_request_json_data.decode("utf-8"))
    friend_request_list = friend_request_data["events_requests"]
    return friend_request_list

def profile(request, username):
    user = None
    if request.user.is_authenticated():
    #It will be replaced by web service when it runs
        user = get_object_or_404(User, username=username)
        events = get_events(user)
        friend_request_list = get_friend_requests(user)
        event_request_list = get_event_requests(user)
        friends_count = get_friends_count(user)
        friends_request_count = len(friend_request_list)
        events_count = len(event_request_list)
        context = {'user': user, 'username': request.user.username, 'events': events,'friend_request': friend_request_list,
                   'event_request': event_request_list,
                   'friends_count': friends_count,
                   'friend_request_count': friends_request_count,
                   'event_request_count': events_count,
                   }
        return render(request, 'profile.html', context)
    else:
        return redirect("http://127.0.0.1:8000/login/")

def get_event(event_id):
    params = urllib.parse.urlencode({'event': event_id})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "application/json"}
    connection = http.client.HTTPConnection('127.0.0.1', 8000)
    connection.request("POST", "/api/get_event/", params, headers)
    friend_request_response = connection.getresponse()
    friend_request_json_data = friend_request_response.read()
    friend_request_data = json.loads(friend_request_json_data.decode("utf-8"))
    friend_request_list = friend_request_data["event"]
    return friend_request_list

def events(request, username, event_id):
    user = None
    if request.user.is_authenticated():
    #It will be replaced by web service when it runs
        user = get_object_or_404(User, username=username)

        friend_request_list = get_friend_requests(user)
        event_request_list = get_event_requests(user)
        friends_count = get_friends_count(user)
        friends_request_count = len(friend_request_list)
        events_count = len(event_request_list)
        event = get_event(event_id)
        context = {'user': user, 'username': request.user.username,'friend_request': friend_request_list,
                   'event_request': event_request_list,
                   'friends_count': friends_count,
                   'friend_request_count': friends_request_count,
                   'event_request_count': events_count,
                   'event': event}
        return render(request, 'events.html', context)
    else:
        return redirect("http://127.0.0.1:8000/login/")


def get_friend_requests(user):
    params = urllib.parse.urlencode({'username': user.username})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "application/json"}
    connection = http.client.HTTPConnection('127.0.0.1', 8000)
    connection.request("POST", "/api/get_friend_requests/", params, headers)
    friend_request_response = connection.getresponse()
    friend_request_json_data = friend_request_response.read()
    friend_request_data = json.loads(friend_request_json_data.decode("utf-8"))
    friend_request_list = friend_request_data["senders"]
    return friend_request_list


def get_owned_groups(request):
    params = urllib.parse.urlencode({'username': request.user.username})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "application/json"}
    connection = http.client.HTTPConnection('127.0.0.1', 8000)
    connection.request("POST", "/api/get_owned_groups/", params, headers)
    event_list_response = connection.getresponse()
    event_list_json_data = event_list_response.read()
    event_list_data = json.loads(event_list_json_data.decode("utf-8"))
    event_list = event_list_data["groups"]
    return event_list

def get_participant_groups(request):
    params = urllib.parse.urlencode({'username': request.user.username})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "application/json"}
    connection = http.client.HTTPConnection('127.0.0.1', 8000)
    connection.request("POST", "/api/get_participant_groups/", params, headers)
    event_list_response = connection.getresponse()
    event_list_json_data = event_list_response.read()
    event_list_data = json.loads(event_list_json_data.decode("utf-8"))
    event_list = event_list_data["groups"]
    return event_list


def groups(request, username):
    user = None
    if request.user.is_authenticated():
        groups = get_owned_groups(request)
        participantgroups = get_participant_groups(request)
    #It will be replaced by web service when it runs
        user = get_object_or_404(User, username=username)
        context = {'user': user, 'username': request.user.username, 'owned_groups': groups, 'groups': participantgroups}
        return render(request, 'groups.html', context)
    else:
        return redirect("http://127.0.0.1:8000/login/")

def g1(request, username, group_id):
    user = None
    if request.user.is_authenticated():
    #It will be replaced by web service when it runs
        user = get_object_or_404(User, username=username)
        context = {'user': user, 'username': request.user.username}
        return render(request, 'g1.html', context)
    else:
        return redirect("http://127.0.0.1:8000/login/")

def g2(request, username):
    user = None
    if request.user.is_authenticated():
    #It will be replaced by web service when it runs
        user = get_object_or_404(User, username=username)
        context = {'user': user, 'username': request.user.username}
        return render(request, 'g2.html', context)
    else:
        return redirect("http://127.0.0.1:8000/login/")

def g3(request, username):
    user = None
    if request.user.is_authenticated():
    #It will be replaced by web service when it runs
        user = get_object_or_404(User, username=username)
        context = {'user': user, 'username': request.user.username}
        return render(request, 'g3.html', context)
    else:
        return redirect("http://127.0.0.1:8000/login/")

def edit(request, username):
    if request.user.is_authenticated():
        if request.method == "POST":
            user = request.user
            name = request.POST["name"]
            surname = request.POST["surname"]
            new_password = request.POST["new_password"]
            new_password2 = request.POST["new_password2"]
            currentPassword = request.POST["currentPassword"]
            params = urllib.parse.urlencode(
                {'name': name, 'surname': surname, 'username': username, 'new_password': new_password,
                 'new_password2': new_password2, 'currentPassword': currentPassword})
            headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "application/json"}
            connection = http.client.HTTPConnection('127.0.0.1', 8000)
            url = "/api/profile/%s/edit/" % username
            connection.request("POST", url, params, headers)
            edit_response = connection.getresponse()
            edit_data_json = edit_response.read()
            edit_data = json.loads(edit_data_json.decode("utf-8"))
            if edit_data["status"] == "success":
                context = {'user': user, 'username': user.username, 'error': False, 'success': True}
            else:
                context = {'user': user, 'username': user.username, 'error': True, 'success': False}
            return render(request, 'profile_edit.html', context)
        else:
            user = request.user
            context = {'user': user, 'error': False, 'success': False}
            return render(request, 'profile_edit.html', context)
    else:
        return redirect("login")


def search_user(request):
    if request.user.is_authenticated():
        if request.method == "POST":
            username = request.POST['username']
            if username == "":
                 return redirect("../homepage")
            params = urllib.parse.urlencode({"username" : request.user.username})
            headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "application/json"}
            connection = http.client.HTTPConnection('127.0.0.1', 8000)
            connection.request("POST", "/api/search/"+username+"/", params, headers)
            search_response = connection.getresponse()
            search_data_json = search_response.read()
            search_data = json.loads(search_data_json.decode("utf-8"))
            friends_count = get_friends_count(request.user)
            if 'users' in search_data:
                user_list = []
                for user in search_data['users']:
                    user_list.append(get_object_or_404(User, username=user['username']))
                context = {'search_field': username, 'users': user_list,
                           'count': user_list.count(0), 'friends_count': friends_count}
            else:
                context = {'search_field': username, 'count': 0, 'friends_count': friends_count}
            user = None
            if search_data['status'] == "success":
                return render(request, "search.html", context)
            print("There is no user like that!")
        else:
            print("Use post method!")
            return redirect("login")
    else:
        print("Please login to system")
        return render(request, "./login.html")


def add_friend(request, username):
    if request.user.is_authenticated():
        if request.method == "POST":
            if search_user(request, username):
                User.friend_list.append(search_user(request, username))
            else:
                print("There is no user like that")
                return None
        else:
            print("Please use POST method!")
    else:
        return render(request, "./login.html")

def delete_friend(request, username):
    if request.user.is_authenticated():
        if request.method == "POST":
            if search_user(request, username):
                User.friend_list.remove(search_user(request, username))
            else:
                print("That user is not on your friend list")
                return None
        else:
            print("Please use POST method!")
    else:
        return render(request, "./login.html")


def friends_view(request, username):
    if request.user.is_authenticated():
        user = request.user
        params = urllib.parse.urlencode({'username': username})
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "application/json"}
        connection = http.client.HTTPConnection('127.0.0.1', 8000)
        connection.request("POST", "/api/get_friends/", params, headers)
        friend_list_response = connection.getresponse()
        friend_list_json_data = friend_list_response.read()
        friend_list_data = json.loads(friend_list_json_data.decode("utf-8"))
        friend_list = friend_list_data["friends"]
        context = {'user': user, 'username': username, 'friend_list': friend_list, 'friends_count': len(friend_list)}
        return render(request, "friends.html", context)
    else:
        return redirect("http://127.0.0.1:8000/login/")

def logout(request):
    responseJSON = {}
    auth.logout(request)
    responseJSON["message"] = "You logout successfully"
    responseJSON["status"] = "success"
    file.create_file(request, responseJSON, "logout", request.method)
    return redirect("../login")

def notifications_view(request):
    user = None
    if request.user.is_authenticated():
        #It will be replaced by web service when it runs
        user = request.user
        context = {'user': user, 'username': user.username}
        return render(request, 'notifications.html', context)
    else:
        return redirect("http://127.0.0.1:8000/login/")


def get_friends_count(user):
    params = urllib.parse.urlencode({'username': user.username})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "application/json"}
    connection = http.client.HTTPConnection('127.0.0.1', 8000)
    connection.request("POST", "/api/get_friends/", params, headers)
    friend_list_response = connection.getresponse()
    friend_list_json_data = friend_list_response.read()
    friend_list_data = json.loads(friend_list_json_data.decode("utf-8"))
    friend_list = friend_list_data["friends"]

    return len(friend_list)

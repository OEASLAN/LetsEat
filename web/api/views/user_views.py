__author__ = 'Hakan Uyumaz & Burak Atalay & Omer Aslan'


import os
import json
from random import randint

from django.contrib.auth import authenticate, login
from django.contrib import auth
from django.http import HttpResponse
from django.template.defaultfilters import slugify
from django.core.mail import EmailMessage

from ..forms import UserCreationForm, UserUpdateForm
from ..models import User
from ..views import file




responseJSON = {}





def is_POST(request):
    if request.method != "POST":
        fail_response(responseJSON)
        responseJSON["message"] = "No request found."
        return False
    return True


def success_response(responseJSON):
    responseJSON["status"] = "success"


def fail_response(responseJSON):
    responseJSON["status"] = "failed"


def send_password_mail(user):
    subject = "Your Let's Eat Account Password"
    body = """Hello {0} {1},
Thank you for signing up for Let's Eat.
To login to Let's Eat you can use following password:
{2}
Best Regards,
Let's Eat Team
            """.format(user.name, user.surname, user.password)

    mail = EmailMessage(subject, body, "Let's Eat <hakanuyumaz@hotmail.com>", to=[user.email])
    mail.send(fail_silently=False)


def registration_view(request):
    responseJSON = {}
    if is_POST(request):
        form = UserCreationForm(request.POST)

        if form.errors:
            fail_response(responseJSON)
            responseJSON["message"] = "Errors occurred."
            return HttpResponse(json.dumps(responseJSON), content_type="application/json")

        user = form.save(commit=False)
        user.is_active = True
        user.save()

        success_response(responseJSON)
        responseJSON["message"] = "Successfully registered."

    file.create_file(request, responseJSON, "registration_view", request.method)
    return HttpResponse(json.dumps(responseJSON), content_type="application/json")


def registration_from_facebook(request):
    responseJSON = {}
    if is_POST(request):
        request_copy = request.POST.copy()
        name = request.POST["name"]
        surname = request.POST["surname"]
        email = request.POST["email"]
        facebook_id = request.POST["facebook_id"]
        if User.objects.filter(facebook_id=facebook_id).count() > 0:
            login_with_facebook(request)
            user = User.objects.filter(facebook_id=facebook_id)[0]
            login(request, authenticate(username=user.username, password=user.password))
        else:
            request_copy["username"] = get_available_username(name, surname)
            request_copy["password"] = get_random_password()
            request_copy["facebook_id"] = facebook_id
            form = UserCreationForm(request_copy)

            if form.errors:
                fail_response(responseJSON)
                responseJSON["message"] = "Errors occurred."
                return HttpResponse(json.dumps(responseJSON), content_type="application/json")

            user = form.save(commit=False)
            user.is_active = True
            user.save()
            user.facebook_id = facebook_id
            user.save()
            #send_password_mail(user)

            user_ = authenticate(username=request_copy["username"], password=request_copy["password"])
            login(request, user_)
            responseJSON["message"] = "Successfully registered from facebook."

        success_response(responseJSON)

    file.create_file(request, responseJSON, "registration_from_facebook", request.method)
    return HttpResponse(json.dumps(responseJSON), content_type="application/json")


def login_with_facebook(request):
    responseJSON = {}
    if is_POST(request):
        facebook_id = request.POST["facebook_id"]
        users = User.objects.filter(facebook_id=facebook_id)
        if users.count() > 0:
            user = users[0]
            success_response(responseJSON)
            responseJSON["user"] = create_user_JSON(user)
        else:
            fail_response(responseJSON)
            responseJSON["message"] = "No user found with given id"

    file.create_file(request, responseJSON, "login_with_facebook", request.method)
    return HttpResponse(json.dumps(responseJSON), content_type="application/json")


def get_available_username(name, surname):
    if User.objects.filter(username=normalized_username(name + " " + surname)).count() > 0:
        surname = surname + "-" + str(randint(0,500))
        return get_available_username(name, surname)
    else:
        return normalized_username(name + " " + surname)


def normalized_username(title):
    title = slugify(title)
    title = title.replace("-",".")
    return title


def get_random_password():
    password = User.objects.make_random_password()
    #mail will be sent.
    return password


def create_user_JSON(user):
    user_container = {}
    user_container["username"] = user.username
    user_container["name"] = user.name
    user_container["surname"] = user.surname
    user_container["email"] = user.email
    return user_container


def login_view(request):
    responseJSON = {}

    if is_POST(request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
                login(request, user)
                success_response(responseJSON)

                responseJSON["container"] = create_user_JSON(user)
                responseJSON["message"] = "Successfully logged in"
                print(responseJSON["status"])
        else:
            fail_response(responseJSON)
            responseJSON["message"] = "User credentials are not correct."


    file.create_file(request, responseJSON, "login_view", request.method)
    return HttpResponse(json.dumps(responseJSON, ensure_ascii=False).encode('utf8'),
                            content_type="application/json")


def user_profile(request):
    responseJSON = {}
    success_response(responseJSON)
    responseJSON["container"] = create_user_JSON(request.user)
    file.create_file(request, responseJSON, "user_profile", request.method)
    return HttpResponse(json.dumps(responseJSON, ensure_ascii=False).encode('utf8'),
                        content_type="application/json")


def profile(request, username):
    responseJSON = {}
    user = User.objects.get(username=username)
    responseJSON["status"] = "success"
    responseJSON["container"] = {}
    responseJSON["container"]["username"] = user.username
    responseJSON["container"]["name"] = user.name
    responseJSON["container"]["surname"] = user.surname
    responseJSON["container"]["email"] = user.email
    file.create_file(request, responseJSON, "profile", request.method)
    return HttpResponse(json.dumps(responseJSON, ensure_ascii=False).encode('utf8'),
                            content_type="application/json")


def logout(request):
    responseJSON = {}
    auth.logout(request)
    success_response(responseJSON)
    file.create_file("", responseJSON, "logout", request.method)
    return HttpResponse(json.dumps(responseJSON, ensure_ascii=False).encode('utf8'),
                            content_type="application/json")


def edit(request, username):
    responseJSON = {}
    if is_POST(request):
        user = User.objects.get(username=username)
        form = UserUpdateForm(request.POST, instance=user)
        new_password = request.POST["newPassword"]
        new_password2 = request.POST["newPassword2"]
        current_password = request.POST["currentPassword"]
        if user.check_password(current_password):
            if form.errors:
                print(form.errors)
                fail_response(responseJSON)
                responseJSON["message"] = "Form errors occurred."
            else:
                user = form.save(commit=False)
                if new_password != "" and new_password == new_password2:
                    print("Password changed")
                    user.set_password(new_password)
                user.is_active = True
                user.save()
                success_response(responseJSON)
                responseJSON["message"] = "Successfully updated."
        else:
            fail_response(responseJSON)
            responseJSON["message"] = "Current password is invalid."

    file.create_file(request, responseJSON, "edit", request.method)
    return HttpResponse(json.dumps(responseJSON), content_type="application/json")


def test(request):
    return HttpResponse("Successful")


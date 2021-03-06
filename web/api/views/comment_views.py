__author__ = 'Hakan Uyumaz'

import json

from django.http import HttpResponse

from ..models import User, Event, Comment

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


def create_user_JSON(user):
    userJSON = {}
    userJSON["username"] = user.username
    userJSON["name"] = user.name
    userJSON["surname"] = user.surname
    userJSON["email"] = user.email
    return userJSON


def create_comment_JSON(comment):
    commentJSON = {}
    commentJSON["id"] = comment.id
    commentJSON["owner"] = create_user_JSON(comment.owner)
    commentJSON["time"] = str(comment.time)
    commentJSON["likes"] = []
    for like in comment.likes.all():
        commentJSON["likes"].append(create_user_JSON(like))
    commentJSON["comments"] = []
    sub_comments = Comment.objects.filter(comment=comment)
    for sub_comment in sub_comments:
        commentJSON["comments"].append(create_comment_JSON(sub_comment))
    commentJSON["content"] = comment.content
    return commentJSON


def comment_on_event(request):
    responseJSON = {}

    if is_POST(request):
        event_id = request.POST["event"]
        username = request.POST["username"]
        content = request.POST["content"]
        event = Event.objects.filter(pk=event_id)[0]
        user = User.objects.filter(username=username)[0]
        if event is None:
            fail_response(responseJSON)
            responseJSON["message"] = "Event not found."
            file.create_file(request, responseJSON, "comment_on_event", request.method)
            return HttpResponse(json.dumps(responseJSON))
        if user is None:
            fail_response(responseJSON)
            responseJSON["message"] = "User not found."
            file.create_file(request, responseJSON, "comment_on_event", request.method)
            return HttpResponse(json.dumps(responseJSON))
        comment = Comment(event=event, owner=user, content=content, is_event_comment=True)
        comment.save()
        success_response(responseJSON)
        responseJSON["message"] = "Comment created."
        responseJSON["comment"] = create_comment_JSON(comment)

    file.create_file(request, responseJSON, "comment_on_event", request.method)
    return HttpResponse(json.dumps(responseJSON))


def comment_on_comment(request):
    responseJSON = {}

    if is_POST(request):
        comment_id = request.POST["comment"]
        username = request.POST["username"]
        content = request.POST["content"]
        comment = Comment.objects.filter(pk=comment_id)[0]
        user = User.objects.filter(username=username)[0]
        if comment is None:
            fail_response(responseJSON)
            responseJSON["message"] = "Comment not found."
            return HttpResponse(json.dumps(responseJSON))
        if user is None:
            fail_response(responseJSON)
            responseJSON["message"] = "User not found."
            return HttpResponse(json.dumps(responseJSON))
        new_comment = Comment(comment=comment, owner=user, content=content, is_event_comment=False)
        new_comment.save()
        success_response(responseJSON)
        responseJSON["message"] = "Comment created."
        responseJSON["comment"] = create_comment_JSON(new_comment)
    return HttpResponse(json.dumps(responseJSON))


def like_comment(request):
    responseJSON = {}

    if is_POST(request):
        comment_id = request.POST["comment"]
        username = request.POST["username"]
        comment = Comment.objects.filter(pk=comment_id)[0]
        user = User.objects.filter(username=username)[0]
        if comment is None:
            fail_response(responseJSON)
            responseJSON["message"] = "Comment not found."
            return HttpResponse(json.dumps(responseJSON))
        if user is None:
            fail_response(responseJSON)
            responseJSON["message"] = "User not found."
            return HttpResponse(json.dumps(responseJSON))
        comment.likes.add(user)
        comment.save()
        success_response(responseJSON)
        responseJSON["message"] = "Comment updated."
        responseJSON["comment"] = create_comment_JSON(comment)
    return HttpResponse(json.dumps(responseJSON))


def get_comment(request):
    responseJSON = {}

    if is_POST(request):
        comment_id = request.POST["comment"]
        comment = Comment.objects.filter(pk=comment_id)[0]
        if comment is None:
            fail_response(responseJSON)
            responseJSON["message"] = "Comment not found."
            return HttpResponse(json.dumps(responseJSON))
        success_response(responseJSON)
        responseJSON["message"] = "Comment found."
        responseJSON["comment"] = create_comment_JSON(comment)
    return HttpResponse(json.dumps(responseJSON))
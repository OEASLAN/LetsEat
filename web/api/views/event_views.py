__author__ = 'Hakan Uyumaz'

import json

from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from ..forms import EventCreationForm
from ..models import User, Restaurant, Event


def create_event(request):
    responseJSON = {}
    if request.method == "POST":
        owner_id = request.POST["owner"]
        restaurant_id = request.POST["restaurant"]
        owner = get_object_or_404(User, pk=owner_id)
        restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
        form = EventCreationForm(request.POST)
        type = Event.TYPE_LABELS.get(request.POST["type"], None)
        if form.errors or not type:
            responseJSON["status"] = "failed"
            responseJSON["message"] = "Errors occurred."
            return HttpResponse(json.dumps(responseJSON), content_type="application/json")
        event = form.save(commit=False)
        event.owner = owner
        event.participants.add(owner)
        event.restaurant = restaurant
        if request.POST["joinable"] == 1:
            event.joinable = True
        else:
            event.joinable = False
        event.type = type
        event.save()
        responseJSON["status"] = "success"
        responseJSON["message"] = "Successfully registered."
    else:
        responseJSON["status"] = "failed"
        responseJSON["message"] = "No request found."
    return HttpResponse(json.dumps(responseJSON), content_type="application/json")


def invite_event(request):
    responseJSON = {}
    if request.method == "POST":
        event = get_object_or_404(Event, pk=request.POST["event"])
        participant = get_object_or_404(User, username=request.POST["participant"])
        event.participants.add(participant)
        event.save()
        responseJSON["status"] = "success"
        responseJSON["message"] = "Participant added."
    else:
        responseJSON["status"] = "failed"
        responseJSON["message"] = "No request found."
    return HttpResponse(json.dumps(responseJSON), content_type="application/json")
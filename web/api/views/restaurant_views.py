__author__ = 'Hakan Uyumaz'

import json

from django.http import HttpResponse

from ..models import Restaurant
from ..forms import RestaurantCreationForm
from ..views import file

responseJSON = {}


def is_POST(request):
    if request.method != "POST":
        fail_response()
        responseJSON["message"] = "No request found."
        return False
    return True


def success_response(responseJSON):
    responseJSON["status"] = "success"


def fail_response(responseJSON):
    responseJSON["status"] = "failed"


def create_restaurant(request):
    responseJSON = {}
    if is_POST(request):
        restaurant = RestaurantCreationForm(request.POST)
        if restaurant.errors or not type:
            responseJSON["status"] = "failed"
            responseJSON["message"] = "Errors occurred."
            return HttpResponse(json.dumps(responseJSON), content_type="application/json")
        restaurant.save()
        responseJSON["status"] = "success"
        responseJSON["message"] = "Successfully registered."
    file.create_file(request, responseJSON, "create_restaurant", request.method)
    return HttpResponse(json.dumps(responseJSON), content_type="application/json")


def create_restaurant_JSON(restaurant):
    restaurantJSON = {}
    restaurantJSON["name"] = restaurant.name
    return restaurantJSON


def create_restaurants_json(responseJSON):
    responseJSON["restaurants"] = []
    for restaurant in Restaurant.objects.all():
        responseJSON["restaurants"].append(create_restaurant_JSON(restaurant))


def get_restaurant_list(request):
    responseJSON = {}
    create_restaurants_json(responseJSON)
    success_response(responseJSON)
    responseJSON["message"] = "Successfully returned."
    file.create_file(request, responseJSON, "get_restaurant_list", request.method)
    return HttpResponse(json.dumps(responseJSON), content_type="application/json")

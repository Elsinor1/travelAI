from django.shortcuts import render
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse, Http404, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.core.serializers import serialize
from django.core.paginator import Paginator

import json
import datetime

# from django.core.serializers import serialize

from rest_framework.views import APIView
from rest_framework.response import Response

from amadeus import Client, ResponseError, Location

from travel.serializers import (
    AirportSerializer,
    TravelProfileSerializer,
    TravelOfferSerializer,
)
from travel.utils.helpers import get_matches, get_airport, get_travel_offer
from travel.models import (
    City_autocomplete,
    User,
    City,
    Airport,
    Travel_profile,
    Vacation_type,
    Travel_offer,
    ActivityPreference,
    DiningPreference,
)


# Setting up Amadeus client
amadeus = Client()


# Create your views here.
def index(request):
    offers = Travel_offer.objects.all()

    offers = list(offers)

    # Set the pagination
    paginator = Paginator(offers, 10)  # Show 10 posts per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    print(f"Displaying index offers page {page_number if page_number else 0}")

    return render(request, "travel/index.html", {"offers": page_obj})


def register_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")

        # Ensure password matches confirmation
        password = request.POST.get("password")
        confirmation = request.POST.get("confirmation")
        if password != confirmation:
            return render(
                request, "travel/register.html", {"message": "Passwords must match"}
            )

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request, "travel/register.html", {"message": "Username already taken"}
            )

        login(request, user)
        print("Logged in")
        return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, "travel/register.html")


def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        print(user)
        if not user:
            return render(
                request,
                "travel/login.html",
                {"message": "Incorrect username and password combination"},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, "travel/login.html")


@login_required
def logout_user(request):
    logout(request)
    return render(request, "travel/index.html")


@login_required
def custom_trip(request):
    """Displays page for custom trip generation and display"""
    # GET request
    if request.method == "GET":
        travel_profiles = Travel_profile.objects.filter(owner=request.user)
        travel_offers = Travel_offer.objects.filter(travel_profile__owner=request.user)
        return render(
            request,
            "travel/custom_trip.html",
            {
                "travel_profiles": travel_profiles,
                "travel_offers": travel_offers,
            },
        )
    else:
        return Http404("Only GET requests are possible")


def travel_offer(request):
    """Gets single travel offer"""
    travel_profile_id = request.GET.get("travel_profile_id")
    if not travel_profile_id:
        return HttpResponse("Travel profile must be defined in URL")
    last_destination_id = request.GET.get("last_destination_id")
    if not last_destination_id:
        last_destination_id = 0
    travel_date_str = request.GET.get("travel_date")
    return_date_str = request.GET.get("return_date")
    try:
        if travel_date_str:
            travel_date = datetime.date.fromisoformat(travel_date_str)
        else:
            travel_date = datetime.date.today() + datetime.timedelta(weeks=1)
        if return_date_str:
            return_date = datetime.date.fromisoformat(return_date_str)
        else:
            return_date = datetime.date.today() + datetime.timedelta(weeks=1, days=3)
    except ValueError:
        return HttpResponse("Travel date and return date must be in ISO 8601 format")

    try:
        travel_profile = Travel_profile.objects.get(id=travel_profile_id)
    except Travel_profile.DoesNotExist:
        return Http404("Profile does not exist")

    print(f"Getting travel offer for {travel_profile}")
    # Get travel offers for profile
    offer = get_travel_offer(
        travel_profile=travel_profile,
        last_destination_id=last_destination_id,
        flight_date=travel_date,
        return_date=return_date,
    )

    return render(request, "travel/display_offer.html", {"traveloffer": offer})


def display_offer(request, offer_id):
    """Displays single travel offer"""
    if not offer_id:
        return HttpResponse(
            "Travel offer ID must be defined in URL, example: display_offer/1"
        )

    try:
        offer = Travel_offer.objects.get(id=offer_id)
    except Exception as e:
        return HttpResponse(
            f"No records found under travel offer ID = {offer_id}, raised exception: {e}"
        )

    return render(request, "travel/display_offer.html", {"offer": offer})


@login_required
def travel_profile(request):
    """Displays travel profile form throughprofiles are added or edited"""
    # Initial data
    travel_profiles = Travel_profile.objects.filter(owner=request.user)
    travel_profiles_json = json.dumps(
        TravelProfileSerializer(travel_profiles, many=True).data
    )
    initial_data = {
        "profiles": travel_profiles,
        "profiles_json": travel_profiles_json,
        "vacation_types": Vacation_type.objects.all(),
        "activity_preferences": ActivityPreference.objects.all(),
        "dining_preferences": DiningPreference.objects.all(),
    }
    # Render form
    return render(request, "travel/travel_profile.html", initial_data)


# API's
@login_required
def get_travel_offers_api(request):
    """For travel profile id from GET request gets existing travel offers from DB"""
    travel_profile_id = request.GET.get("travel_profile_id")
    if not travel_profile_id:
        print(
            f"get_travel_offers has failed to find travel_profile, travel_profile_id is: {travel_profile_id}"
        )
        return JsonResponse(
            {"message": "travel_profile_id has to be passed in GET request"}
        )

    travel_offers = Travel_offer.objects.filter(travel_profile__id=travel_profile_id)
    travel_offers_serialized = TravelOfferSerializer(travel_offers, many=True)
    print("get_travel_offers_api got:", travel_offers_serialized.data)
    return JsonResponse(travel_offers_serialized.data, safe=False)


@login_required
def get_new_offer_api(request):
    """For travel profile id from GET request creates new travel offer"""
    print("getting offer")
    travel_profile_id = request.GET.get("travel_profile_id")
    if not travel_profile_id:
        print(
            f"get_new_offer has failed to find travel_profile_id, travel_profile_id is: {travel_profile_id}"
        )
        return {"message": "travel_profile_id has to be passed in GET request"}

    try:
        travel_profile = Travel_profile.objects.get(id=travel_profile_id)
    except Travel_profile.DoesNotExist:
        return Http404("Profile does not exist")

    travel_date_str = request.GET.get("travel_date")
    return_date_str = request.GET.get("return_date")
    try:
        if travel_date_str:
            travel_date = datetime.date.fromisoformat(travel_date_str)
        else:
            travel_date = datetime.date.today() + datetime.timedelta(weeks=1)
        if return_date_str:
            return_date = datetime.date.fromisoformat(return_date_str)
        else:
            return_date = datetime.date.today() + datetime.timedelta(weeks=1, days=3)
    except ValueError:
        return HttpResponse("Travel date and return date must be in ISO 8601 format")

    print(f"Getting travel offer for {travel_profile}")
    # Get travel offers for profile
    offer = get_travel_offer(
        travel_profile=travel_profile,
        flight_date=travel_date,
        return_date=return_date,
    )
    serialized_offer = TravelOfferSerializer(offer).data
    print(f"get_new_offer_api got {serialized_offer}")
    return JsonResponse(serialized_offer, safe=False)


@method_decorator(login_required, name="dispatch")
class UpdateProfileView(APIView):
    """API for profile update and creation"""

    def post(
        self,
        request,
    ):
        travel_profile = request.POST["travelProfileId"]
        adult_amount = int(request.POST["adultAmount"])
        childer_amount = int(request.POST["childrenAmount"])
        vacation_type = request.POST.get("vacationType")
        dining_preference = request.POST.get("diningPreference")
        activity_preference = request.POST.get("activityPreference")
        city = request.POST["location"]
        airport_selection = request.POST.getlist("airportSelect")

        print(f"Travel Profile: {travel_profile}")
        print(f"Number of Adults: {adult_amount}")
        print(f"Number of Children: {childer_amount}")
        print(f"Vacation Type: {vacation_type}")
        print(f"Selected Airport: {airport_selection}")
        print(f"Location: {city}")

        # Get Autocomplete_city
        city_autocomplete = City_autocomplete.objects.filter(name=city)
        # If query is successful, pick the first result
        if city_autocomplete:
            city_autocomplete = city_autocomplete[0]
            new_city = City.objects.get(code="n/a")
        # If not succesfull, create new City instead
        else:
            city_autocomplete = City_autocomplete.objects.get(code="n/a")
            new_city = City.objects.create(
                code=city[:10] if len(city) > 10 else city,
                name=city,
            )

        # Query form data from DB
        dining_preference_query = DiningPreference.objects.get(name=dining_preference)
        activity_preference_query = ActivityPreference.objects.get(
            name=activity_preference
        )
        vacation_type_query = Vacation_type.objects.get(name=vacation_type)
        preffered_airports_query = Airport.objects.filter(name__in=airport_selection)

        # Creation of new profile
        if travel_profile == "new":
            user_profile = Travel_profile.objects.create(
                owner=request.user,
                city=new_city,
                autocomplete_city=city_autocomplete,
                adults=adult_amount,
                children=childer_amount,
                vacation_type=vacation_type_query,
                dining_preference=dining_preference_query,
                activity_preference=activity_preference_query,
            )
            user_profile.preffered_airports.set(preffered_airports_query)
            user_profile.save()
            print(f"Travel profile created {user_profile.name}")
            message = "Profile sucessfully created"

        # Update of existing profile
        else:
            user_profile = Travel_profile.objects.get(
                owner=request.user, id=travel_profile
            )
            # Check the profile exists
            if not user_profile:
                return Http404(
                    f"User profile with name {travel_profile} does not exist"
                )

            # Update current object
            if user_profile.adults != adult_amount:
                user_profile.adults = adult_amount
            if user_profile.children != childer_amount:
                user_profile.children = childer_amount
            if user_profile.vacation_type != vacation_type_query:
                user_profile.vacation_type = vacation_type_query
            if user_profile.city != new_city:
                user_profile.city = new_city
            if user_profile.dining_preference != dining_preference_query:
                user_profile.dining_preference = dining_preference_query
            if user_profile.activity_preference != activity_preference_query:
                user_profile.activity_preference = activity_preference_query
            if user_profile.autocomplete_city != city_autocomplete:
                user_profile.autocomplete_city = city_autocomplete
            if user_profile.preffered_airports != preffered_airports_query:
                user_profile.preffered_airports.set(preffered_airports_query)
            user_profile.save()
            message = "Profile succesfully updated"
            print(f"Travel profile{user_profile} updated successfully")

        serializer = TravelProfileSerializer(user_profile)
        profile_json = json.dumps({"message": message, "profile_data": serializer.data})
        return JsonResponse(profile_json, safe=False)


@login_required
def location_autocomplete(request) -> JsonResponse:
    """Returns autocomplete suggestions based on DB query of given input letters in GET request"""
    try:
        letters: str = request.GET.get("letters")
        letters = letters.capitalize()
        matches: dict = get_matches(letters)
        # print(f"Autocomplete matches: {str(matches)}")
        return JsonResponse(matches, safe=False)
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error: {e}")
        return Http404


class NearestAirportsView(APIView):
    """Returns json of nearest airports based on location data given in GET request"""

    def post(self, request, *args, **kwargs):
        # Get user info
        profile = request.data.get("profile")

        # Get location info
        longitude = float(request.data.get("longitude"))
        latitude = float(request.data.get("latitude"))
        req_amount = int(request.data.get("req_amount", 5))
        max_distance = float(request.data.get("max_distance", 1000))

        print(
            f"Fetching nearest airports with parameters: longitude={longitude}, latitude={latitude}, req. amount={req_amount}, max distance={max_distance}"
        )

        # Amadeus API
        # Getting airports in a 500km radius from the given location
        response = amadeus.reference_data.locations.airports.get(
            longitude=longitude, latitude=latitude
        )

        nearest_airports = []

        try:
            for index, airport_data in enumerate(response.data):
                # If the request amount has been reached
                if index == req_amount:
                    break

                # DISTANCE UNIT IMPLEMENTATION TBD

                # If distance > max_distance, go to the next
                distance = airport_data["distance"]["value"]
                if distance > max_distance:
                    continue

                # Get airport from DB
                airport = get_airport(airport_data)
                nearest_airports.append(airport)

        except AttributeError as e:
            print("Attribute error when looping over airport_data", e)

        # Serialize the list of Airport objects to JSON
        serializer = AirportSerializer(nearest_airports, many=True)
        serialized_airports = serializer.data

        return Response({"nearest_airports": serialized_airports}, status=200)

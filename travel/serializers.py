from rest_framework import serializers
from .models import (
    Airport,
    Travel_profile,
    Travel_offer,
    Vacation_type,
    City,
    City_autocomplete,
    DiningPreference,
    ActivityPreference,
    Itinerary_image,
    Flight_route,
)


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = "__all__"


class VacationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacation_type
        fields = ("id", "name")


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ("id", "name")


class CityAutocompleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = City_autocomplete
        fields = ("id", "name")


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name")


class DiningPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiningPreference
        fields = ("id", "name")


class ActivityPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityPreference
        fields = ("id", "name")


class TravelProfileSerializer(serializers.ModelSerializer):
    preffered_airports = AirportSerializer(many=True)
    vacation_type = VacationTypeSerializer()
    city = CitySerializer()
    autocomplete_city = CityAutocompleteSerializer()
    dining_preference = DiningPreferenceSerializer()
    activity_preference = ActivityPreferenceSerializer()

    class Meta:
        model = Travel_profile
        fields = "__all__"


class ItineraryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Itinerary_image()
        fields = "__all__"


class FlightRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight_route()
        fields = "__all__"


class TravelOfferSerializer(serializers.ModelSerializer):
    image = ItineraryImageSerializer(many=True)
    origin_airport = AirportSerializer()
    destination_airport = AirportSerializer()
    return_routes = FlightRouteSerializer(many=True)
    departure_routes = FlightRouteSerializer(many=True)

    class Meta:
        model = Travel_offer()
        fields = "__all__"

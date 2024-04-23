from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model


class User(AbstractUser):
    def __str__(self):
        return f"User {self.id} {self.username}"


class Location(models.Model):
    """Geo location of a city or a vilage"""

    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return f"Location ({self.latitude}, {self.longitude})"


class Region(models.Model):
    """Region - SEASI, ASIA, NAMER, EUROP"""

    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.code


class Country(models.Model):
    """Country"""

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100, unique=True)
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE, related_name="countries"
    )

    def __str__(self):
        return self.name


class City_autocomplete(models.Model):
    """City table for autocompletion purpose"""

    name = models.CharField(max_length=100)
    alt_names = models.CharField(max_length=100)
    timezone_id = models.CharField(max_length=50)
    population = models.IntegerField()
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return self.name


class City(models.Model):
    """City for Airports and destinations"""

    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="city"
    )
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name="cities"
    )

    def __str__(self):
        return self.name


class Vacation_type(models.Model):
    """Type of vacation, e.g. Beach Relax or Adventure"""

    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Airport(models.Model):
    """Airport"""

    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="airports")
    name = models.CharField(max_length=20)
    detailed_name = models.CharField(max_length=100)
    iata_code = models.CharField(max_length=5, unique=True)

    def __str__(self):
        return f" {self.city} airport {self.name}"

    def label(self):
        return self.city.name if self.city.name else self.name


class Possible_destination(models.Model):
    """Possible origin destination pairs"""

    origin = models.ManyToManyField(Airport, related_name="origin_for")
    destination = models.ManyToManyField(
        Airport, default=0, related_name="destination_for"
    )


class ActivityPreference(models.Model):
    """Activity preference used in travel profile, e.g. 'Highly active' or 'Laid back'"""

    name = models.CharField(max_length=50)
    description = models.CharField(max_length=300)

    def __str__(self):
        return f"Activity preference: {self.name}: {self.description}"


class DiningPreference(models.Model):
    """Dining preference used in travel profile, e.g. 'Fine Dining' or 'Street food or Local'"""

    name = models.CharField(max_length=50)
    description = models.CharField(max_length=300)

    def __str__(self):
        return f"Dining preference: {self.name}: {self.description}"


class Travel_profile(models.Model):
    """Travel profile containing user vacation preferences and preffered airports"""

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="travel_profiles"
    )
    autocomplete_city = models.ForeignKey(
        City_autocomplete,
        on_delete=models.CASCADE,
        blank=True,
        related_name="travel_profiles",
    )
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, blank=True, related_name="travel_profiles"
    )
    name = models.CharField(max_length=50)
    adults = models.IntegerField()
    children = models.IntegerField()
    vacation_type = models.ForeignKey(
        Vacation_type, on_delete=models.CASCADE, default=1
    )
    preffered_airports = models.ManyToManyField(Airport, related_name="preffered_by")
    activity_preference = models.ForeignKey(
        ActivityPreference, on_delete=models.SET_DEFAULT, default=1
    )
    dining_preference = models.ForeignKey(
        DiningPreference, on_delete=models.SET_DEFAULT, default=1
    )

    def __str__(self):
        return f"Travel profile {self.id} of {self.owner.username}, vacation type: {self.vacation_type}, airports: {len(list(self.preffered_airports.all()))}"

    def description(self):
        """Returns full description of the profile"""
        if self.adults == 1:
            description = f"{self.vacation_type} for {self.adults} adult"
        else:
            description = f"{self.vacation_type} for {self.adults} adults"
        if self.children == 1:
            description += f", {self.children} child"
        elif self.children > 1:
            description += f", {self.children} children"
        return description

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        print("Travel profile saved")


class Airport_relevance(models.Model):
    """Defines how an airport is relevant to a travel profile"""

    profile = models.ForeignKey(
        Travel_profile, on_delete=models.CASCADE, related_name="relevant_airports"
    )
    airport = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="relevant_for"
    )
    relevance = models.DecimalField(max_digits=7, decimal_places=5)
    distance = models.DecimalField(max_digits=4, decimal_places=2)
    distance_unit = models.CharField(max_length=3)


class Suitable_airport(models.Model):
    """Defines how an airport is suitable for a vacation type, suitability is number 1-10, 10 means an airport is the most suitable for given vacation type"""

    airport = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="suitable_for"
    )
    vacation = models.ForeignKey(
        Vacation_type, on_delete=models.CASCADE, related_name="suitable"
    )
    suitability = models.IntegerField()

    @staticmethod
    def get_suitability(airport: Airport, vacation_type: Vacation_type) -> int:
        """Calculates suitability for given airport and vacation type"""
        from travel.utils.AI_helpers import get_suitability_from_ai

        suitability = get_suitability_from_ai(airport.city.name, vacation_type.name)
        try:
            suitability = int(suitability)
        except ValueError:
            print(f"get_suitability was unable to change {suitability} to an integer.")
            return None
        return suitability

    @staticmethod
    def set_all_suitabilities(airport: Airport) -> None:
        """
        For given Aiport object sets suitability for each existing vacation type"""
        vacation_types = Vacation_type.objects.all()
        for vacation_type in vacation_types:
            suitability = Suitable_airport.get_suitability(airport, vacation_type)
            Suitable_airport.objects.create(
                airport=airport, vacation=vacation_type, suitability=suitability
            )


class Profile_destination(models.Model):
    """Defines fitting destinations for a travel profile and origin airport"""

    travel_profile = models.ForeignKey(
        Travel_profile, on_delete=models.CASCADE, related_name="profile_destinations"
    )
    origin_airport = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="profile_origin_airports"
    )
    destination_airport = models.ForeignKey(
        Airport,
        default=0,
        on_delete=models.CASCADE,
        related_name="profile_destination_airports",
    )


class Airline(models.Model):
    """Airport code, name and logo url"""

    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=3)
    logo = models.CharField(max_length=200)

    def __str__(self):
        return self.name


# class Flight_util:
#     """Support class for Single flight"""

#     def get_identifier(self):
#         """Returns a string describing a single flight"""
#         return f"{self.origin}->{self.destination}_on_{str(self.departure_date)}"


class Single_flight(models.Model):
    """Information about a flight, origin, destination, departure date, arrival date, price, carrier, identifier"""

    origin = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="departures"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="arrivals"
    )
    departure_date = models.DateField()
    arrival_date = models.DateField()
    price = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    carrier = models.ForeignKey(
        Airline, on_delete=models.CASCADE, related_name="flights"
    )
    # Identifier is set automatically after instance save
    identifier = models.CharField(max_length=100, unique=True, null=True, blank=True)

    # Override the save function to calculate the identifier before saving
    def save(self, *args, **kwargs):
        """Creates a string describing a single flight"""
        self.identifier = (
            f"{self.origin}->{self.destination}_on_{str(self.departure_date)}"
        )
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Single flight {self.origin} to {self.destination}"


class Flight_route(models.Model):
    """Flight route combines multiple single flights"""

    origin = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="departure_routes"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="arrival_routes"
    )
    departure_date = models.DateField()
    arrival_date = models.DateField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    flights = models.ManyToManyField(Single_flight, related_name="routes")
    identifier = models.CharField(max_length=100, unique=True, null=True, blank=True)

    # Override the save function to calculate the identifier before saving
    def save(self, *args, **kwargs):
        self.identifier = f"{self.origin}->{self.destination}_on_{str(self.departure_date)}_arriving_{self.arrival_date}"
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Flight route {self.id} {self.origin} to {self.destination}"


class Accomodation(models.Model):
    """Accomodation information - !!currently only DUMMY!!"""

    name = models.CharField(
        max_length=100,
    )
    description = models.CharField(
        max_length=1000,
    )


class Itinerary_image(models.Model):
    """Image name, url and description of image used in itinerary"""

    name = models.CharField(max_length=50, null=True, blank=True)
    url = models.CharField(max_length=500)
    description = models.CharField(max_length=200, null=True, blank=True)


class Travel_offer(models.Model):
    """Defines all information about travel offer such as origin, destination, flight routes, itinerary, accomodation and images"""

    travel_profile = models.ForeignKey(
        Travel_profile,
        on_delete=models.SET(1),
        related_name="travel_offers",
    )
    origin_airport = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="origin_in_travel_offers"
    )
    destination_airport = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="destination_in_travel_offers"
    )
    departure_routes = models.ManyToManyField(
        Flight_route, related_name="travel_offers_departing"
    )
    return_routes = models.ManyToManyField(
        Flight_route, related_name="travel_offers_returning"
    )

    itinerary = models.JSONField(blank=True, null=True, default=dict())
    accomodation = models.ManyToManyField(Accomodation, related_name="travel_offers")
    image = models.ManyToManyField(Itinerary_image, related_name="in_offers")

    def __str__(self):
        return f"Travel Offer ID: {self.id}, from {self.origin_airport.name} to {self.destination_airport.name}, total departure routes{len(self.departure_routes.all())}, total arrival routes {len(self.return_routes.all())}"

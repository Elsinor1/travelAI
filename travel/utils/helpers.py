"""Helper functions"""

from travel.models import (
    City_autocomplete,
    Airport,
    Airport_relevance,
    Region,
    Country,
    City,
    Location,
    Travel_profile,
    Airline,
    Single_flight,
    Flight_route,
    Vacation_type,
    Possible_destination,
    Profile_destination,
    Suitable_airport,
    Accomodation,
    Travel_offer,
    Itinerary_image,
)
from amadeus import ResponseError, Client
import amadeus

from django.core.serializers import serialize
from django.db import IntegrityError
from decimal import Decimal

from datetime import date, timedelta, datetime
from typing import List
from dotenv import load_dotenv

from travel.utils.trip_advisor import get_image_url_from_description
from travel.utils.AI_helpers import get_itinerary


def get_matches(letters: str) -> list:
    """Returns 5 cities that begins with given string, ordered by biggest population"""
    matches = City_autocomplete.objects.filter(
        name__startswith=letters.capitalize()
    ).order_by("-population")[:5]
    # matches_list = queryset_to_values(queryset=matches.values(), columns=("name", "longitude", "latitude"))
    matches_list = list(matches.values())
    # print("get matches -> dict:" ,matches_list)

    if not matches_list:
        matches_list = []
    return matches_list


def get_airport_data(iata_code: str) -> dict:
    """Get information about airport, city and country based on airport's iata_code"""
    
    # Amadeus API key
    load_dotenv()

    amadeus_client = Client()
    try:
        response = amadeus_client.reference_data.locations.get(
            keyword=iata_code, subType=amadeus.Location.AIRPORT
        )
    except ResponseError as e:
        print(
            f"get_airport_data could not fetch airport data for iata code: {iata_code} due to:",
            e,
        )
        return {}
    if not response:
        print(f"get_airport_data fetched no airport data for iata code: {iata_code}")
        return {}

    try:
        # If data exist, return data dict
        return response.data[0]
    except Exception as e:
        print(
            f"get_airport_data got error when returning response.data[0] for iata code: {iata_code}",
            e,
        )
        print(f"response data: {response.data} ")
        return {}


def get_airport(airport_data: dict = None, iata_code: str = None) -> Airport:
    """Gets Airport object from DB, if does not exist, create it
    Takes two optional parameters, if only iata_code given, uses get_airport_data"""
    # If airport data is not available, get data through Amadeus API using iata_code
    if not airport_data and not iata_code:
        return None

    if not iata_code:
        iata_code = airport_data["iataCode"]

    # Get the airport from DB
    try:
        airport = Airport.objects.get(iata_code=iata_code)
    # If aiport does not exists, create new
    except Airport.DoesNotExist:
        # Get airporty data if no airport data given
        if not airport_data:
            airport_data = get_airport_data(iata_code)
            # If no data was retrieved, return None
            if not airport_data:
                return None
        # Prepare city information
        detailed_name = airport_data["detailedName"]
        name = airport_data["name"]
        city = get_city(airport_data)
        print(f"Creating new airport {name} in {city.name}, iata_code: {iata_code}")

        # Create new City object
        airport = Airport.objects.create(
            city=city,
            name=name,
            detailed_name=detailed_name,
            iata_code=iata_code,
        )
        print(f"Airport {airport} created")

    return airport


def get_city(airport_data: dict) -> City:
    """Gets City object from DB, if does not exist, create it from airport_data dict"""
    try:
        city = City.objects.get(code=airport_data["address"]["cityCode"])
    # If city does not exists, save it to DB
    except City.DoesNotExist:
        # Get city data
        code = airport_data["address"]["cityCode"]
        name = airport_data["address"]["cityName"]
        print(f"Creating new city {name}, code: {code}")

        location = Location.objects.create(
            longitude=airport_data["geoCode"]["longitude"],
            latitude=airport_data["geoCode"]["latitude"],
        )

        # Create new city record
        city = City.objects.create(
            code=code, name=name, location=location, country=get_country(airport_data)
        )
        print(f"City {city.name} created")
    return city


def get_country(airport_data: dict) -> Country:
    """Gets County object from DB, if does not exist, create it from airport_data dict"""
    try:
        country = Country.objects.get(code=airport_data["address"]["countryCode"])
    except Country.DoesNotExist:
        # If region does not exists, save it to DB
        country_name = airport_data["address"]["countryName"]
        country_code = airport_data["address"]["countryCode"]
        print(f"Creating new country {country_name}, code: {country_code}")

        country = Country.objects.create(
            name=country_name,
            code=country_code,
            region=get_region(airport_data),
        )
        print(f"Country {country.name} created")
    return country


def get_region(airport_data: dict) -> Region:
    """Gets Region object from DB, if does not exist, create it from airport_data dict"""
    try:
        region = Region.objects.get(code=airport_data["address"]["regionCode"])
    except Region.DoesNotExist:
        region_code: str = airport_data["address"]["regionCode"]
        print(f"Creating new region with region_code: {region_code}")

        region = Region.objects.create(code=region_code)

        print(f"Region {region.code} created")
    return region


def get_destinations_from_api(origin_iata: str) -> List[Airport]:
    """Gets possible destinations for origin airport iata using Amadeus API
    Returns list of Airport objects"""
    # Amadeus API key
    load_dotenv()
    amadeus = Client()

    print(f"Getting flight destinations from Amadeus API for origin: {origin_iata}")
    try:
        response = amadeus.shopping.flight_destinations.get(origin=origin_iata)
    except ResponseError as e:
        print(
            f"Amadeus API was unable to find destinations for origin: {origin_iata}, due to {e}"
        )
        return []
    response_data = response.data
    print(f"get_destinations_from_api function got this: {response_data}")
    destinations = []
    for destination in response_data:
        # Get Airport object
        new_dest = get_airport(iata_code=destination["destination"])
        # If new destination has airport object
        if isinstance(new_dest, Airport):
            destinations.append(new_dest)

    print(
        f"get_destinations_from_api got {len(destinations)} destinations from Amadeus API"
    )
    return destinations


def get_destinations(origin_airport: Airport) -> List[Airport]:
    """For given origin airport iata code loads possible destinations for from"""
    # Get possible destinations from DB
    destinations = Possible_destination.objects.filter(origin=origin_airport)
    print(f"get_destinations got {len(list(destinations))} destinations from DB")
    # If not destinations found, get them from API
    if not destinations:
        destinations = get_destinations_from_api(origin_iata=origin_airport.iata_code)
    return destinations


def sort_destinations_sort_function(
    origin_destination: tuple, vacation_type: Vacation_type
) -> int:
    """Sort function for sort_destinations_by_suitability"""
    destination = origin_destination[1]
    try:
        suitable_airport = Suitable_airport.objects.get(
            airport=destination, vacation=vacation_type
        )
    except Suitable_airport.DoesNotExist:
        Suitable_airport.set_all_suitabilities(airport=destination)
        suitable_airport = Suitable_airport.objects.get(
            airport=destination, vacation=vacation_type
        )
    print(
        f"Suitability for {suitable_airport.airport} is {suitable_airport.suitability}"
    )
    return suitable_airport.suitability


def sort_destinations_by_suitability(
    origin_destinations: list, vacation_type: Vacation_type
) -> List[Airport]:
    """Sorts list of tuples (origin_irtport: destination_airport) based on suitability of destination for given vacation type"""

    origin_destinations.sort(
        reverse=True,
        key=lambda o_d: sort_destinations_sort_function(o_d, vacation_type),
    )
    print(f"List {origin_destinations} was sorted by suitability")

    return origin_destinations


def set_profile_destinations(travel_profile: Travel_profile) -> int:
    """Sets travel profile's destination airports"""

    print(f"Getting offers for {travel_profile}")
    origin_airports: list = travel_profile.preffered_airports.all()

    origin_destinations: list = []  # List of (origin:destiantion) tuples
    for origin_airport in origin_airports:
        # Apending possible destination airports
        destinations = get_destinations(origin_airport)
        for destination in destinations:
            origin_destinations.append((origin_airport, destination))

    # Get single Vacation type, !!!! Bugged with multiple vacation types !!!!
    vacation_type = travel_profile.vacation_type
    # Sort destinations by suitability for vacation type
    origin_destinations = sort_destinations_by_suitability(
        origin_destinations=origin_destinations, vacation_type=vacation_type
    )
    # Saving origin and destinations to the DB
    for origin_destination in origin_destinations:
        Profile_destination.objects.create(
            travel_profile=travel_profile,
            origin_airport=origin_destination[0],
            destination_airport=origin_destination[1],
        )
    print(
        f"{len(origin_destinations)} origin-destinatino pairs were added to Profile: {travel_profile}"
    )
    return len(origin_destinations)


def get_acomodation(destination: City, vacation_type: Vacation_type) -> Accomodation:
    """Gets suitable accomodation from DB or creates new"""
    # !!This is DUMMY function!!
    try:
        accomodation = Accomodation.objects.get(name="Test Accomodation")
    except Accomodation.DoesNotExist:
        accomodation = Accomodation.objects.create(
            name="Test Accomodation", description="Test Description"
        )
    return accomodation


def get_travel_offer(
    travel_profile: Travel_profile,
    destination_id: int = -1,
    flight_date: date = date.today() + timedelta(weeks=1),
    return_date: date = date.today() + timedelta(weeks=1, days=3),
    adults: int = 1,
) -> Travel_offer:
    """For given travel profile, get's the destination from Possible_destinations and returns Travel offer,
    destination_id parameter is arbitrary, if not given, next unused destination will be used
    """

    # If destination_id was given as a parameter
    if destination_id >= 0:
        # Get destination Airport based on destination ID
        try:
            offer_destination: Airport = Airport.objects.get(destination_id)
            offer_origin: Airport = travel_profile.preffered_airports.get()
        except Airport.DoesNotExist:
            print(
                "get_travel_offer got wrong destination_id, it does not correspond to any Airport's ID"
            )
            return None
    # THe destination Airport was not given as parameter
    else:
        # Gets unused destinations
        unused_profile_destinations = travel_profile.profile_destinations.exclude(
            destination_airport__id__in=travel_profile.travel_offers.values_list(
                "destination_airport__id", flat=True
            )
        )
        if unused_profile_destinations:
            offer_destination = unused_profile_destinations[0].destination_airport
            offer_origin = unused_profile_destinations[0].origin_airport
        else:
            print("get_travel_offer could not find a destination")
            return None

    # Get Flight routes
    departure_routes = FlightClass.get_flight_routes(
        origin_airport=offer_origin,
        destination_airport=offer_destination,
        departure_date=flight_date,
        adults=adults,
        route_amount=10,
    )

    return_routes = FlightClass.get_flight_routes(
        origin_airport=offer_destination,
        destination_airport=offer_origin,
        departure_date=return_date,
        adults=adults,
        route_amount=10,
    )

    # Gets travel offer accomodation
    accomodation = get_acomodation(
        destination=offer_destination,
        vacation_type=travel_profile.vacation_type,
    )

    # Get itinerary dcitionary from AI
    itinerary = get_itinerary(
        travel_profile=travel_profile,
        city=offer_destination.city,
        duration=(flight_date - return_date).days,
    )

    if itinerary:
        itinerary_images = []
        # Add highlight image for each day to itinerary dict
        for day in itinerary["Days"].values():
            # Get image info from itinerary dict
            image_name = day["Highlight_image"]["Image_name"]
            location_category = day["Highlight_image"]["Location_category"]
            # Get image Object
            image = get_image_url_from_description(
                description=image_name,
                category=location_category,
                image_size="large",
                source="Expert, Management",
            )
            if image:
                itinerary_images.append(image)
    else:
        itinerary = ""

    try:
        travel_offer = Travel_offer.objects.create(
            travel_profile=travel_profile,
            origin_airport=offer_origin,
            destination_airport=offer_destination,
            itinerary=itinerary,
        )
        # Add multiple objects from query using unpacking *
        travel_offer.departure_routes.add(*departure_routes)
        travel_offer.return_routes.add(*return_routes)
        travel_offer.image.add(*itinerary_images)
        travel_offer.accomodation.add(accomodation)
    except Exception as e:
        print(
            f"Travel offer for {travel_profile} for destination {offer_destination} could not be created due to {e}"
        )
        return None
    print(
        f"Travel offer for {travel_profile} for destination {offer_destination} was created"
    )
    return travel_offer


class FlightClass:
    """Class for handling flight data"""
    def __init__(self):
        # Amadeus API key
        load_dotenv()
        self.amadeus = Client()

    def get_flight_airport(self, iata_code: str) -> Airport:
        """Returns Airport object based on given iata code"""
        airport = Airport.objects.get(iata_code=iata_code)
        if not airport:
            response = self.amadeus.reference_data.locations.get(
                keyword=iata_code, subType=Location.AIRPORT
            )
            if response:
                airport_data = response.data
            else:
                print("get_flight_airport could not get airport data due to", response)
                return None
            airport = get_airport(airport_data)
        return airport

    @staticmethod
    def get_airline_logo(carrier_code):
        """Returns url string of carrier logo image based on given carrier_logo string"""
        return "https://s1.apideeplink.com/images/airlines/" + carrier_code + ".png"

    @staticmethod
    def get_airline(carrier_code: str) -> Airline:
        """Returns Airline object based on given carrier_code string"""
        # Get the Airline from DB
        try:
            airline = Airline.objects.get(code=carrier_code)
        # If not exists, create new
        except Airline.DoesNotExist:
            airline = Airline.objects.create(
                code=carrier_code,
                name=carrier_code,
                logo=FlightClass.get_airline_logo(carrier_code),
            )
        return airline

    @staticmethod
    def get_date_from_date_string(date_string: str) -> datetime:
        """Creates datetime object from given date_string in this format: "%Y-%m-%dT%H:%M:%S"""
        datetime_object = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
        return datetime_object

    @classmethod
    def get_flight(cls, single_flight_data: dict) -> Single_flight:
        """
        Creates a flight in a DB using dict of Amadeus flight data, if it already exists, gets it from DB
        """

        # Prepare flight data
        origin = get_airport(iata_code=single_flight_data["departure"]["iataCode"])
        destination = get_airport(iata_code=single_flight_data["arrival"]["iataCode"])
        departure_date = cls.get_date_from_date_string(
            single_flight_data["departure"]["at"]
        )

        arrival_date = cls.get_date_from_date_string(
            single_flight_data["arrival"]["at"]
        )
        try:
            carrier = cls.get_airline(single_flight_data["operating"]["carrierCode"])
        except KeyError:
            carrier = cls.get_airline(single_flight_data["carrierCode"])
        print(
            f"Get flight gets flight from {origin} to {destination} on {departure_date} arriving {arrival_date}, carrier {carrier}"
        )
        try:
            # Create flight in DB
            route_flight = Single_flight.objects.create(
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                arrival_date=arrival_date,
                carrier=carrier,
            )
            print(f"{route_flight} was created")

        # The record already exists, get it from DB
        except IntegrityError:
            route_flights = Single_flight.objects.filter(
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                arrival_date=arrival_date,
                carrier=carrier,
            )
            if route_flights:
                route_flight = route_flights[0]
            else:
                print(f"No flight found in DB from {origin} to {destination}")
                return None
        except Exception as e:
            print("Flight could not be created due to: ", e)
            return None
        return route_flight

    @classmethod
    def get_flight_routes(
        cls,
        origin_airport: Airport,
        destination_airport: Airport,
        departure_date: datetime,
        adults: int = 1,
        route_amount: int = 5,
    ) -> List[Flight_route]:
        """Gets a list of flight routes for given flight data using amadeus API"""

        # Settting of request data
        origin_iata = origin_airport.iata_code
        destination_iata = destination_airport.iata_code

        kwargs = {
            "originLocationCode": origin_iata,
            "destinationLocationCode": destination_iata,
            "departureDate": departure_date,
            "adults": adults,
        }
        print(f"Fetching flight from Amadeus API, {kwargs}")

        # Getting flights from Amadeus API
        try:
            response = cls.amadeus.shopping.flight_offers_search.get(**kwargs)

        except ResponseError as e:
            print("Exception occured", e)
            return None

        # Check we get some response data
        if not response.data:
            print("Response with no data")
            return None

        # Setup returned list variable
        flight_routes = []

        # For every flight route
        for index, flight_data in enumerate(response.data):

            # Check if the route amount limit has been reached
            if index >= route_amount - 1:
                break

            # Extracting route information
            departure_date = cls.get_date_from_date_string(
                flight_data["itineraries"][0]["segments"][0]["departure"]["at"]
            )

            arrival_date = cls.get_date_from_date_string(
                flight_data["itineraries"][0]["segments"][-1]["arrival"]["at"]
            )

            price = flight_data["price"]["total"]
            flights = []

            # For each single flight in flight route
            for flight in flight_data["itineraries"][0]["segments"]:
                # Get flight
                route_flight = cls.get_flight(flight)
                if route_flight:
                    flights.append(route_flight)

            print(
                f"Creating flight route from {origin_airport} to {destination_airport} at {departure_date} arriving {arrival_date} price: {price}"
            )

            # Create new flight route
            try:
                new_route = Flight_route.objects.create(
                    origin=origin_airport,
                    destination=destination_airport,
                    departure_date=departure_date,
                    arrival_date=arrival_date,
                    price=price,
                )
                print(f"{new_route} was created")
                # Add flights to flight route
                new_route.flights.add(*flights)
            # If already exists, get it from DB
            except IntegrityError:
                new_route = Flight_route.objects.filter(
                    origin=origin_airport,
                    destination=destination_airport,
                    departure_date=departure_date,
                    arrival_date=arrival_date,
                    price=price,
                )
                # Getting errors when using get query, changed to filter with [0]
                if new_route:
                    new_route = new_route[0]
                else:
                    continue

            # If not already in offers append route to flight offers
            if not new_route in flight_routes:
                flight_routes.append(new_route)

        # Sort flight routes by ascending price
        sorted_routes = sorted(flight_routes, key=lambda x: Decimal(x.price))
        print(sorted_routes)
        # Limit the amount of routes returned
        sorted_routes = sorted_routes[:route_amount]
        return sorted_routes

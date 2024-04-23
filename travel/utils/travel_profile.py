from travel.models import (
    Travel_profile,
    Suitable_airport,
    Airport,
    Profile_destination,
)

from typing import List


class TravelProfileClass:
    def __init__(self, travel_profile: Travel_profile) -> None:
        self.profile = travel_profile
        self.suitable_airports = []

    def get(self):
        """
        Returns list of suitable airports
        """
        return self.suitable_airports

    def query_destinations(self, amount: int = 100, suitability: int = 5) -> list:
        """
        Generates list of airport suitabilites that match trip purpose and have suitablity score > given suitability
        saved to instance
        """
        # Get all preffered vacation types for given profile
        vacation_types = self.travel_profile.vacation_types.all()
        suitable_airports: List[Airport] = []
        # For each type get all suitable airports
        for type in vacation_types:
            # Airport suitability object that matches vacation type and suitability >5
            airports = Suitable_airport.objects.filter(
                vacation=type, suitability__gte=suitability
            )
            suitable_airports.append(airports)
        print(
            f"Generating list of suitable airports of length: {len(suitable_airports)}"
        )
        # Saving list to the class object
        self.suitable_airports = suitable_airports
        return suitable_airports

    def sort_destinations(self) -> None:
        """
        Sorts the instance's airport suitability based on suitablity and proximity
        """

        suitable_airports = self.suitable_airports

        # Ensure the list exists
        if not suitable_airports:
            return AttributeError("Suitalbe airports need to be generated first")

        # Sort airports based on suitability and proximity
        suitable_airports.order_by("-suitability")

        self.suitable_airports = suitable_airports
        print("Airport list has been sorted")
        return

    def save_destinations(self) -> None:
        """
        Saves given airport querry to DB table Travel_destinations under given travel profile
        """
        for airport in self.suitable_airports:
            Profile_destination.objects.create(self.travel_profile, airport.airport)
        print(f"Saving destinations: {self.suitable_airports}")

    def remove_destinations(self, destinations: Profile_destination = None) -> None:
        """
        Removes Profile_destination records from DB,
        If 'destinations' argument is omitted, delete all Profile_destinations for given profile
        """
        if destinations:
            destinations.delte()
            print(f"{len(list(destinations))} Profile_desitnation(s) removed")
        else:
            destinations = Profile_destination.objects.filter(
                travel_profile=self.profile
            )
            destinations.delete()
            print(f"{len(list(destinations))} Profile_desitnation(s) removed")

from travel.models import Airport, Vacation_type, Airport_suitability
import random


class AirportClass:
    @classmethod
    def set_all_suitabilities(cls, airport: Airport):
        """
        For given Aiport object sets suitability for each existing vacation type"""
        vacation_types = Vacation_type.objects.all()
        for type in vacation_types:
            suitability = cls.get_suitability(airport, type)
            Airport_suitability.create(
                airport=airport, vacation=type, suitability=suitability
            )

    @classmethod
    def get_suitability(cls, airport: Airport, vacation_type: Vacation_type) -> int:
        """Calculates suitability for given airport and vacation type"""
        # Actual suitability TBD
        return random.randint(1, 10)


if __name__ == "__main__":
    airports = Airport.objects.all()
    for airport in airports:
        AirportClass.set_all_suitabilities(airport=airport)

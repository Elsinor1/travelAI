from django.contrib import admin
from .models import (
    Location,
    Travel_profile,
    Region,
    Country,
    City_autocomplete,
    City,
    Airport,
    Airport_relevance,
    Airline,
    Single_flight,
    Vacation_type,
    Flight_route,
    Travel_offer,
    ActivityPreference,
    DiningPreference,
    User,
)

admin.site.register(User)
admin.site.register(Location)
admin.site.register(Travel_profile)
admin.site.register(Region)
admin.site.register(Country)
admin.site.register(City_autocomplete)
admin.site.register(City)
admin.site.register(Airport)
admin.site.register(Airport_relevance)
admin.site.register(Airline)
admin.site.register(Single_flight)
admin.site.register(Flight_route)
admin.site.register(Vacation_type)
admin.site.register(Travel_offer)
admin.site.register(ActivityPreference)
admin.site.register(DiningPreference)

from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register_user, name="register"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("custom_trip/", views.custom_trip, name="custom_trip"),
    # URL pattern example travel_offer/?travel_profile_id=1&last_destination_id=1&travel_date=2024-03-11&return_date=2024-04-11
    path(
        "travel_offer/",
        views.travel_offer,
        name="travel_offer",
    ),
    # URL display_offer/1
    path("display_offer/<int:offer_id>", views.display_offer, name="display_offer"),
    path("travel_profile/", views.travel_profile, name="travel_profile"),
    #
    # API paths
    path("get_travel_offers", views.get_travel_offers_api, name="get_travep_offers"),
    path("get_new_offer", views.get_new_offer_api, name="get_new_offer"),
    path("update_profile/", views.UpdateProfileView.as_view(), name="update_profile"),
    path(
        "location_autocomplete/",
        views.location_autocomplete,
        name="location_autocomplete",
    ),
    path(
        "nearest_airport/", views.NearestAirportsView.as_view(), name="nearest_airports"
    ),
]

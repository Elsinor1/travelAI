from django.db.models.signals import post_save
from django.dispatch import receiver

from travel.models import Travel_profile, Airport, Suitable_airport
from travel.utils.helpers import set_profile_destinations


@receiver(signal=post_save, sender=Travel_profile)
def save_travel_profile_receiver(sender, instance, created, **kwargs) -> None:
    """Reciever for travel profile save, when saved sets profile destinations"""
    print("Receiver save_travel_profile_receiver activated")
    set_profile_destinations(instance)
    return


@receiver(post_save, sender=Airport)
def save_airport_reciever(sender, instance, **kwargs):
    """Reciever for airport save, when saved sets all suitabilites for vacation types"""
    print("Receiver save_airport_receiver activated")
    Suitable_airport.set_all_suitabilities(instance)

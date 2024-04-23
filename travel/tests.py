from travel.utils.trip_advisor import get_trip_adv_location_id, get_image
from travel.utils.AI_helpers import get_suitability_from_ai
from travel.utils.helpers import get_destinations_from_api
import pytest


# TRIP ADVISOR TESTS
@pytest.mark.parametrize(
    "location_name, category, language, expected_location_id",
    [
        ("Spilberk castle", "attractions", "en", "277575"),
        ("", "attractions", "en", None),
    ],
)
@pytest.mark.integration
def test_get_trip_adv_location_id(
    location_name, category, language, expected_location_id
):
    location_id = get_trip_adv_location_id(location_name, category, language)
    assert location_id == expected_location_id


@pytest.mark.parametrize(
    "location_id, image_size, source, expected_type",
    [
        ("277575", "original", "Traveler", str),
        ("bad_id", "original", "Traveler", type(None)),
    ],
)
@pytest.mark.integration
def test_get_image(location_id, image_size, source, expected_type):
    image_url = get_image(location_id=location_id, image_size=image_size, source=source)
    assert type(image_url) == expected_type
    if type(image_url) == str:
        assert len(image_url) >= 0


# AI HELPERS TESTS


@pytest.mark.integration
def test_get_suitability_from_ai():
    s = get_suitability_from_ai(city="Paris", vacation_type="City tour")
    assert s in range(0, 11)


# AMADEUS TESTS


@pytest.mark.integration
@pytest.mark.django_db
def test_get_destinations_from_api_integration():
    # Provide a real origin IATA code for testing
    origin_iata = "MAD"  # or any other valid IATA code
    destinations = get_destinations_from_api(origin_iata)

    # Assert that destinations is not empty and contains valid data
    assert destinations
    assert all(dest.iata_code for dest in destinations)

import requests
from dotenv import load_dotenv

from travel.models import Itinerary_image


def get_trip_adv_location_id(
    location_name: str, category: str = "attractions", language: str = "en"
) -> str:
    """
    Gets Trip advisor's location_id of given location location_name.
    parameters: location_name - string - Name or descritpion of the locatioin
                category: string - Filters result set based on property type. Valid options are "hotels", "attractions", "restaurants", and "geos"
                language - string, The language in which to return results (e.g. "en" for English or "es" for Spanish) from the list of our Supported Languages.
    """
    
    # Trip Advisor API key
    load_dotenv()

    query = location_name.replace(" ", "%20")
    url = f"https://api.content.tripadvisor.com/api/v1/location/search?key={key}&searchQuery={query}&category={category}&language={language}"

    headers = {"accept": "application/json"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        location_id = response.json()["data"][0]["location_id"]
        print(
            f"get_trip_adv_location_id got location id {location_id} for {location_name}"
        )
        return location_id
    else:
        print(
            f"get_trip_adv_location_id could not get location_id for {location_name}. Response got: {response.status_code}"
        )
        return None


def get_image(location_id: str, image_size: str = "original", source: str = "") -> str:
    """
    Gets img url from Trip advisor API based on location id.
    parameters: location_id - Trip Advisor id of the location
                image_size - string, options: thumbnail, small, medium, large, original
                source - string, A comma-separated list of allowed photo sources. Allowed values are 'Expert', 'Management', 'Traveler'. If not specified, allow photos from all sources.
    """
    # Trip Advisor API key
    load_dotenv()
    
    language = "en"
    photos_amount = "1"
    url = f"https://api.content.tripadvisor.com/api/v1/location/{location_id}/photos?key={key}&language={language}&limit={photos_amount}"

    if source:
        url += f"&source={source}"

    headers = {"accept": "application/json"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        url = response.json()["data"][0]["images"][image_size]["url"]
        return url
    else:
        print(
            f"get_image was unable to fetch image of {location_id}. Got response {response.status_code}."
        )
        return None


def get_image_url_from_description(
    description: str,
    category: str = "attractions",
    language: str = "en",
    image_size: str = "original",
    source: str = "",
) -> Itinerary_image:
    """
    Gets Trip advisor's location_id of given location location_name.
    parameters: description - string - Name or descritpion of the locatioin
                category: string - Filters result set based on property type. Valid options are "hotels", "attractions", "restaurants", and "geos"
                language - string, The language in which to return results (e.g. "en" for English or "es" for Spanish) from the list of our Supported Languages.
                image_size - string, options: thumbnail, small, medium, large, original
                source - string, A comma-separated list of allowed photo sources. Allowed values are 'Expert', 'Management', 'Traveler'. If not specified, allow photos from all sources.
    """
    location = get_trip_adv_location_id(
        location_name=description, category=category, language=language
    )
    image_url = get_image(location_id=location, image_size=image_size, source=source)
    if image_url:
        image = Itinerary_image.objects.create(name=description, url=image_url)
        print(
            f"get_image_url_from_description was got image {image.url} for {description}"
        )
        return image
    else:
        print(
            f"get_image_url_from_description was unable to get image for {description}"
        )
        return None

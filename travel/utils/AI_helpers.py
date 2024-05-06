from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

import re

import json

from travel.models import City, Travel_profile
from travel.utils.trip_advisor import get_trip_adv_location_id, get_image


def get_itinerary(
    travel_profile: Travel_profile,
    city: City,
    duration: int,
) -> str:
    """For given parameters generate a string of itinerary for each day.
    Returns a string in a JSON format"""

    prompt_text = """
      You are local guide in {city}, write an itinerary for {duration} day vacation with theme: {vacation_type}. Participants: {adults} adults and {children} children. 

      Level of activity should be {activity_preference} is described by {activity_description}.
      Dining preference is {dining_preference} described by: {dining_description}.
      
      Your itinerary should be detailed, highlighting key attractions, dining options with recomended restaurant, and activities for each day. Recommend only restautants or pubs favoured by local peaople. For restaurants, attach a link to the menu, for other activities, link website of the activity. For each attraction or restaurant add a cost estimate. 
      
      Write a funny short tip at the end. 
      
      Keep the text easy to understand even for a non native english speaker.
      
      For each day choose a main attraction of the day and write a attraction name and city to the highlight_image section under image_name, make sure image is different for each day.  Also add "location_category" that fits best to the highlighed attraction. Keep location name in the name of the image - for example: Spilberk Castle Brno. Add it to highlight_image section, choose from these valid options: "attractions", "restaurants", and "geos" (for natural sites)
      Make sure all activities are relevant for given conditions. On top add a catching label and a short description of the trip about 80 letters long. 
      Output will be structured in table like structure. Format output as a string of structured in json format as shown in example, make sure the json format is correct, keep dict key same as in example: 
      
      Example of one day trip:
            
      ( 
        "Label": "Brno Sojourn",
        "Description": "Dive into Brno's past at Spilberk Castle and Brno City Museum, relish in diverse culinary delights, unwind in picturesque parks, and embrace the city's vibrant nightlife.",
        "Days": (
            "Day_1": (
                "Activities": [
                    (
                        "Name": "Visit to Spilberk Castle",
                        "Description": "Walk through its historical halls, dungeons, and enjoy the panoramic view of the city from the top.",
                        "Entrance_fee": "240 CZK"
                    ),
                    (
                        "Name": "Lunch at Pavillon restaurant",
                        "Description": "Enjoy Czech cuisine with a modern twist.",
                        "Price_range": "200 to 400 CZK"
                    ),
                    (
                        "Name": "Visit to Brno City Museum",
                        "Description": "Get a deeper understanding of the city's history.",
                        "Entrance_fee": "150 CZK"
                    ),
                    (
                        "Name": "Stroll through Luzanky Park",
                        "Description": "Enjoy the beautiful park, which is free of charge."
                    ),
                    (
                        "Name": "Dinner at Borgo Agnese",
                        "Description": "Offers a wide range of Italian dishes.",
                        "Price_range": "300 to 600 CZK"
                    ),
                    (
                        "Name": "Night walk around city center",
                        "Description": "Explore the charming streets. Don't forget to try a traditional Czech beer at one of the local pubs."
                    )
                ],
                "Funny_tip": "Don't be surprised if you start pronouncing 'Brno' as 'br-no' after a few drinks! 😉",
                "Highlight_image": (
                    "Image_name": "Spilberk castle Brno",
                    "Location_category": "attractions"
                )
            )
        )
    )
    """
    prompt = ChatPromptTemplate.from_template(prompt_text)
    # api_key =
    api_key = "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"
    model = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=api_key)
    output_parser = StrOutputParser()

    chain = prompt | model | output_parser

    itinerary = chain.invoke(
        {
            "city": city,
            "duration": duration,
            "vacation_type": travel_profile.vacation_type.name,
            "adults": travel_profile.adults,
            "children": travel_profile.children,
            "activity_preference": travel_profile.activity_preference.name,
            "activity_description": travel_profile.activity_preference.description,
            "dining_preference": travel_profile.dining_preference.name,
            "dining_description": travel_profile.dining_preference.description,
        }
    )

    print("Itinerary generated successfuly")
    print(itinerary)
    try:
        itinerary_dict = json.loads(itinerary)
    except Exception as e:
        print(f"Get itinerary was unable to change format to dict due to {e}")
        try:
            itinerary_dict = json.loads(correct_json(itinerary, e))
        except Exception as e:
            print(f"Get itinerary was unable to change format to dict due to {e}")
            return None

    return itinerary_dict


def correct_json(json_str: str, error_message: str) -> str:
    prompt_text = """
      There's an error I need you to fix, error is on json: {json_str} error is: {error_message}"""
    prompt = ChatPromptTemplate.from_template(prompt_text)
    # api_key =
    api_key = "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"
    model = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=api_key)
    output_parser = StrOutputParser()

    chain = prompt | model | output_parser

    correct_json = chain.invoke({"json_str": json_str, "error_message": error_message})
    print(f"Json needed correction due to {error_message}")
    return correct_json


def get_suitability_from_ai(
    city: str,
    vacation_type: str,
) -> int:
    """For given parameters generate suitability mark -an int in range from 1-10. 1 means not suitable, 10 means totally suitable
    Returns int"""

    prompt_text = """
      In the scale from 1 to 10, mark how city: {city} is for tourists and visitors suitable for this purpose {vacation_type}. Judge based on possible activities for this purpose near this city. Return only single number from 1 to 10. 
    """
    prompt = ChatPromptTemplate.from_template(prompt_text)
    # api_key =
    api_key = "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"
    model = ChatOpenAI(model="gpt-4-turbo", openai_api_key=api_key)
    output_parser = StrOutputParser()

    chain = prompt | model | output_parser

    suitability = chain.invoke({"city": city, "vacation_type": vacation_type})

    try:
        suitability = int(suitability)
    except Exception as e:
        int_search = re.search(r"\d*", suitability)
        if int_search.groups():
            suitability = int(int_search.groups()[0])
        else:
            print(
                f"get_suitability_from_ai was unable to generate suitability, generated suitability is: {suitability}"
            )
            return 0

    print(f"Suitability for {vacation_type} in {city} generated successfuly")
    print(suitability)

    return suitability

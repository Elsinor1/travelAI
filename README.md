# Avivi - AI travel agency

### This web application was made as a final project for CS50W course provided by Harvard University.

## Description

**Avivi** is a web application that generates travel offers tailored to users' preferences. After completing a user's travel profile form setting up vacation preferebces and requirements, the application then creates custom travel offers that fit the user's preferences, including recommending suitable destinations.

Avivi connects to the _Amadeus API_ to fetch real-time flight offers with prices and availability. It also recommends a three-day itinerary, which includes sightseeing, activities, and dining recommendations generated using the _ChatGPT API_. Itinerary is complemented with beautiful images retrieved from the _Trip Advisor API_. All retrieved or generated data is stored in Django ORM models using an _SQLite_ database.

## Distinctiveness and Complexity

Avivi is unique due to its integration with external APIs. It connects to the Amadeus, ChatGPT, and Trip Advisor APIs. I utilizes django templates as well as API's used for frontend fetching without reloading the page using vanilla javascript. For APIs django and django rest framework is used. It's complexity exceeds previous projects due to it's scale (more than 1500 lines of code and 22 ORM models) and also utilization of previously unused libraries such as Django Rest Framework, Amadeus, Langchain and pytest.

Key features of the application that demonstrate distinctiveness and complexity:

- Nearest airport search: When filling out the travel profile form, after entering the user's location, an autocomplete is triggered. A call to the application API searches the city database for the closest match, then it shows suggestions for autocomplete. Once the user confirms the autocompleted location, another API call is triggered to search for the nearest airports based on the location's latitude and longitude.

- Itinerary creation: LangChain templating is used to generate custom prompts for the ChatGPT API. It includes the destination, user's preferences and requirements, and an example of how the returned string should look. The ChatGPT API then returns a model itinerary for three days in a JSON format. However, ChatGPT is prone to leaving some quotes or commas. To solve this, I created error handling that uses another ChatGPT API call, feeding the incorrect JSON string and the error message describing the issue. This creates a sufficiently working combination of AI agents.

- Setting up destination's suitability: After an Airport DB record is created, reciever triggers setting up of Airport's suitablity for all vacation types, such as "Beach Relax" or "City Tour". Suitability is a integer from 1-10. Another ChatGPT API call is used for obtaining this evaluation.

- Getting beatiful images: Every itinerary should be ideally described visually with beatiful images, for this purpose generated itinerary includes a description of an image. Using this description, an image URL is fetched from Trip Advisor API.

#### How to run the application:

In order to run this application you need access APIs therefore you need to setup all environment variables in .env file.
OPENAI_API_KEY = ""
AMADEUS_CLIENT_ID=  ""
AMADEUS_CLIENT_SECRET = ""
TRIP_ADVISOR_API = ""

Furthermore it is necessary to use my sqlite DB for autocomplete to work properly.

### Application contents

#### travel/urls.py

8 django view endpoints and 5 API endpoints

#### travel/models.py

22 custom django ORM models, storing information about locations and user travel preferences.

#### travel/serializers.py

11 serializers for query data serialization used in API views

#### travel/tests.py

Includes integration tests for APIs:

- test_get_trip_adv_location_id, test_get_image - tests connection to Trip Advisor API
- test_get_suitability_from_ai - tests connection to ChatGPT API
- test_get_destinations_from_api_integration - tests connection to Amadeus API

#### travel/utils/AI_helpers.py

Includes helper functions connecting to ChatGPT API.

- get_itinerary - For given parameters generate a string of itinerary for each day. Returns a string of itinerary data in a JSON format.
- get_suitability_from_ai - Values how given location is suitable for given vacation type. Returns an 1-10 int.
- correct_json - Corrects json format if the format is incorrect. For example when dash or semicolon is missing.

#### travel/utils/helpers.py

Contains core helper functions used for data query, creation and manipulation. Among the most important belong these functions:

- get_matches - Returns 5 cities that begins with given string, ordered by biggest population. Used for autocompletion of location input.
- get_travel_offer - For given travel profile, gets the destination from Possible_destinations and returns Travel offer. Destination_id parameter is arbitrary; if not given, next unused destination will be used.
- get_flight_routes - Gets a list of flight routes for given flight data using Amadeus API. A flight route is composed of individual flights, if the flight offer has multiple stops.

#### travel/helpers/recievers.py

Recievers are used when travel_profile or airport models are created or updated. They trigger actions after each save. I used recievers instead of overwriting the safe methods to avoid circular references.

- save_travel_profile_receiver - Reciever for travel profile save, when saved sets profile destinations
- save_airport_reciever - Reciever for airport save, when saved sets all suitabilites for vacation types

#### travel/helpers/trip_advisor.py

Contains functions linked to Trip Advisor API. They are used for finding photos fitting to the locations or objects used in a vacation's itinerary.

#### travel/static/travel/customTrip.js

Javascript functions linked to displaying or generating custom offers.

#### travel/static/travel/travelForm.js

Javascript functions linked to the travel profile form.

- AutocompleteModule - Module for autocompletion of location input.
- NearestAirportsModule - Module for fetching and displaying of nearest airports to location given in travel profile form.
- other functions for displaying and validating of a travel form.

#### travel/static/travel/styles.css

CSS and SCSS styling

#### travel/static/travel/templates

All HTML templates used for django templating

### Application navigation

#### Index page,

Shows various travel offers made by all users.

### Your offers

Displays travel offers generated by the user. User can also filtered by travel profile. By clicking on "Generate new offer" button user can create new travel offer.

### Display offer

After clicking on offer name in one of the previously mentioned pages, full travel offer is displayed. It includes three day itinerary with recommendations for activities or dining. Also displayes images describing the offer. On bottom can user see display of flight tickets recommended for this offer.

### Travel profile

After clicking on "Add or edit profiles" on the Your offers page you can access travel profile. Choose between "New" or "Edit" to prefill the form. Fill your preferences and location. When inputting location, confirm it in suggestions dropdown. After confirmation nearest airports are displayed. After completing a profile, you are redirected to "your offers" page.

### Finally, I would like to extend my heartfelt thanks to Brian Yu from Harvard University for teaching this incredible course. It was a pleasure to complete the course, and I'll always cherish this memorable chapter of my life.

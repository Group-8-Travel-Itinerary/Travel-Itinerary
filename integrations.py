# Description: This file contains the integrations with external APIs
# Imports the necessary modules and libraries
import logging
import requests
import json
import openai
import yaml
from datetime import datetime, timedelta
from flask import session  
from flask import flash



# Load the API keys from the config file
credentials = yaml.load(open('config.yaml'), Loader=yaml.FullLoader)
pexels_api_key = credentials['pexels']['api_key']
openai.api_key = credentials['openai']['api_key']
weather_api_key = credentials['weather']['api_key']
flight_api_key = credentials['flights']['api_key']

# Function to get the data from the Google Places API
def google_places():
    return "WIP"




# Function for sending quiz answers to GPT API
def send_quiz_to_gpt(message, OptionalCustomQuiz=None):
    # Get GPT quiz instructions
    if OptionalCustomQuiz is None:
        quiz_instructions = load_gpt_instructions('gpt_instructions/quiz_instructions.txt')
    else:
        quiz_instructions = OptionalCustomQuiz

    # Create the request body
    request_body = {
        "model": "gpt-4o",  # Ensure this is the correct model name
        "messages": [
            {"role": "system", "content": f"Here is the travel personality quiz that was given to the user: {quiz_instructions}"},
            {"role": "user", "content": f"Based on the following user responses to the travel personality quiz: {message}\n"
                                         "Please provide a summary of the user's travel personality and suggest three travel destinations in the following JSON format:\n"
                                         "{\n"
                                         '  "summary": "User\'s travel personality summary",\n'
                                         '  "destinations": [\n'
                                         '    {\n'
                                         '      "name": "Destination Name",\n'
                                         '      "description": "A brief description of the destination.",\n'
                                         '      "budgetRating": "Budget rating (e.g., $$ - Moderate, $$$ - Expensive, etc.)",\n'
                                         '      "weather": {\n'
                                         '        "season": "Season (e.g., Summer, Winter)",\n'
                                         '        "description": "Weather description for the selected season (e.g., warm, sunny)",\n'
                                         '        "averageTemperature": {\n'
                                         '          "min": "Minimum average temperature (°C or °F)",\n'
                                         '          "max": "Maximum average temperature (°C or °F)"\n'
                                         '        }\n'
                                         '      },\n'
                                         '      "activities": [\n'
                                         '        "Activity 1",\n'
                                         '        "Activity 2",\n'
                                         '        "Activity 3",\n'
                                         '        "Activity 4",\n'
                                         '        "Activity 5",\n'
                                         '        "Activity 6"\n'
                                         '      ],\n'
                                         '      "accommodation": [\n'
                                         '        "Place 1",\n'
                                         '        "Place 2",\n'
                                         '        "Place 3"\n'
                                         '      ],\n'
                                         '      "travelTips": [\n'
                                         '        "Tip 1",\n'
                                         '        "Tip 2"\n'
                                         '      ]\n'
                                         '    }\n'
                                         '  ]\n'
                                         '}'
            }
        ],
        "max_tokens": 10000
    }

    # Serialize the request body to JSON
    json_data = json.dumps(request_body)

    # Set the API URL
    url = "https://api.openai.com/v1/chat/completions"

    # Define your headers, including your API key
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"  # Ensure this is set in your environment or code
    }

    # Make the API call to the chat completions endpoint
    response = requests.post(url, headers=headers, data=json_data)

    # Check if the response is successful
    if response.status_code != 200:
        error_content = response.text
        return {"error": f"Error: {response.status_code}", "message": error_content}
    else:
        # Return the successful response data
        response_data = response.json()

        # Parse the content from the first choice to get the actual JSON
        content = response_data["choices"][0]["message"]["content"]

        # Remove the markdown code block markers (```json and ```) and parse the JSON
        if content.startswith("```json"):
            content = content[8:-3].strip()  # Remove the code block markers

        try:
            parsed_data = json.loads(content)
            print("Parsed API Response:", json.dumps(parsed_data, indent=2))
            return parsed_data  # Return the parsed data
        except json.JSONDecodeError as e:
            return {"error": "Failed to decode JSON", "details": str(e)}

def get_custom_quiz(prompt):
    model = "gpt-4o"  # Ensure the correct model name is used

    messages = [
        {"role": "system", "content": "You are an expert travel assistant."},
        {
            "role": "user",
            "content": f"""Create a personalized 10-question travel personality quiz for a user interested in: {prompt}. Format the response in JSON with the following structure:
            {{
                "quiz_title": "Travel Personality Quiz",
                "questions": [
                    {{
                        "question": "Question 1 text here",
                        "options": [
                            {{"option": "A", "text": "Option A text here"}},
                            {{"option": "B", "text": "Option B text here"}}
                        ],
                        "keyword": ["keyword"]
                    }},
                    // Continue for all 10 questions
                ]
            }}"""
        }
    ]

    request_body = {
        "model": model,
        "messages": messages,
        "max_tokens": 2000
    }

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"  # Ensure your API key is configured
    }

    response = requests.post(url, headers=headers, json=request_body)

    if response.status_code == 200:
        response_data = response.json()
        quiz_content = response_data["choices"][0]["message"]["content"]
        return quiz_content
    else:
        flash(f"Error fetching quiz: {response.text}", "error")
        return None
    
    
    
# Return gpt instruction for a specific step as string
def load_gpt_instructions(file_path):
 with open(file_path, 'r') as file:
    return file.read()

# Function to get data from a flights API to give an idea of the prices
def flights_api(base_city, cities, start_date, end_date):
    flight_data = {}
    
    for city in cities:
        # Get FreebaseID for the city
        freebase_id = get_freebase_id(city)
        base_freebase_id = get_freebase_id(base_city)
        
        # Flight API URL with parameters
        url = f"https://serpapi.com/search.json?engine=google_flights&departure_id={base_freebase_id}&arrival_id={freebase_id}&outbound_date={start_date}&return_date={end_date}&currency=GBP&api_key={flight_api_key}&hl=en"
        
        response = requests.get(url)
        if response.status_code != 200:
            error_content = response.text
            flight_data[city] = {"error": f"Error: {response.status_code}", "message": error_content}
            continue
        
        response_data = response.json()
        
        # Extracting useful information from the response
        try:
            best_flight = response_data['best_flights'][0]
            flights = best_flight['flights']
            layovers = best_flight.get('layovers', [])
            total_duration = best_flight['total_duration']
            carbon_emissions = best_flight['carbon_emissions']['this_flight']
            price = best_flight['price']
            airline_logo = best_flight['airline_logo']
            
            flight_info = {
                "flights": [],
                "layovers": layovers,
                "total_duration": total_duration,
                "carbon_emissions": carbon_emissions,
                "price": price,
                "airline_logo": airline_logo
            }
            
            for flight in flights:
                flight_info["flights"].append({
                    "departure_airport": flight['departure_airport']['name'],
                    "departure_time": flight['departure_airport']['time'],
                    "arrival_airport": flight['arrival_airport']['name'],
                    "arrival_time": flight['arrival_airport']['time'],
                    "duration": flight['duration'],
                    "airplane": flight['airplane'],
                    "airline": flight['airline'],
                    "airline_logo": flight['airline_logo'],
                    "travel_class": flight['travel_class'],
                    "flight_number": flight['flight_number'],
                    "legroom": flight['legroom'],
                    "extensions": flight['extensions']
                })
            
            flight_data[city] = flight_info
        except (IndexError, KeyError) as e:
            flight_data[city] = {"error": "No flight data found", "details": str(e)}
    
    return flight_data


# Function to get the weather data from an API
def weather_api(cities):
    weather_data = {}
    
    for city in cities:
        # Geolocation API to get Latitude and Longitude of the city
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&appid={weather_api_key}"
        response = requests.get(geo_url)
        
        if response.status_code != 200:
            error_content = response.text
            weather_data[city] = {"error": f"Error: {response.status_code}", "message": error_content}
            continue
        
        response_data = response.json()
        if not response_data:
            weather_data[city] = {"error": "No data found for the city"}
            continue
        
        lat = response_data[0]["lat"]
        lon = response_data[0]["lon"]

        # Once we have the latitude and longitude, we can use the One Call API to get the weather data
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={weather_api_key}&units=metric" 
        response = requests.get(weather_url)

        if response.status_code != 200:
            error_content = response.text
            weather_data[city] = {"error": f"Error: {response.status_code}", "message": error_content}
            continue

        response_data = response.json()

        # Extracting required fields
        coord = response_data["coord"]
        main = response_data["main"]
        weather = response_data["weather"][0]
        wind = response_data["wind"]
        sys = response_data["sys"]

        # Storing extracted data in weather_data
        weather_data[city] = {
            "latitude": coord["lat"],
            "longitude": coord["lon"],
            "temperature": main["temp"],
            "feels_like": main["feels_like"],
            "temp_min": main["temp_min"],
            "temp_max": main["temp_max"],
            "pressure": main["pressure"],
            "humidity": main["humidity"],
            "weather_description": weather["description"],
            "wind_speed": wind["speed"],
            "wind_deg": wind["deg"],
            "country": sys["country"],
            "sunrise": sys["sunrise"],
            "sunset": sys["sunset"]
        }
    
    return weather_data

def get_freebase_id(city_name):
    # Define the Wikidata API endpoint
    wikidata_url = 'https://www.wikidata.org/w/api.php'

    # Define the parameters for the API request
    params = {
        'action': 'wbsearchentities',
        'search': city_name,
        'language': 'en',
        'format': 'json'
    }

    # Make the API request
    response = requests.get(wikidata_url, params=params)
    data = response.json()

    # Check if the city was found
    if not data['search']:
        return None

    # Get the Wikidata entity ID for the city
    entity_id = data['search'][0]['id']

    # Define the parameters to get the entity data
    params = {
        'action': 'wbgetentities',
        'ids': entity_id,
        'props': 'claims',
        'format': 'json'
    }

    # Make the API request to get the entity data
    response = requests.get(wikidata_url, params=params)
    data = response.json()

    # Extract the Freebase ID (P646) from the entity data
    claims = data['entities'][entity_id]['claims']
    if 'P646' in claims:
        freebase_id = claims['P646'][0]['mainsnak']['datavalue']['value']
        return freebase_id

    return None

def pexels_images(query, per_page=10):
    # Function to get images from Pexels API
    url = "https://api.pexels.com/v1/search"
    headers = {
        "Authorization": pexels_api_key
    }
    params = {
        "query": query,
        "per_page": per_page
    }
    
    
    response = requests.get(url, headers=headers, params=params)
        
    if response.status_code != 200:
        error_content = response.text
        return {"error": f"Error: {response.status_code}", "message": error_content}
    else:
        response_data = response.json()
        photos = response_data.get("photos", [])
        image_urls = [photo["src"]["original"] for photo in photos]
        
        return image_urls

#not sure why this is here   
#print(weather_api(["New York", "Los Angeles", "Chicago"]))

#not sure why this is here 
#cities = ["New York", "Los Angeles", "Chicago"]
#start_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
#end_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')

#print(flights_api("Glasgow", cities, start_date, end_date))


def get_activities(destination, preferences):
    # Define the prompt for OpenAI to generate activities
    prompt = f"""
    You are a travel assistant. A user is planning a trip to {destination} and has specific preferences based on a travel quiz.
    Here are the preferences: {preferences}.
    
    Recommend a list of activities that align with these preferences. Format the response in JSON with the following structure:
    {{
        "destination": "{destination}",
        "activities": [
            {{
                "name": "Activity name here",
                "type": "Type (e.g., adventure, relaxation, cultural)",
                "description": "Brief description of the activity"
            }}
        ]
    }}
    Only include activities that directly match the user's preferences.
    """

    # Create the request body
    request_body = {
        "model": "gpt-4o",  # Ensure this is the correct model name
        "messages": [
            {"role": "system", "content": "You are a knowledgeable travel assistant."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500
    }

    # Serialize the request body to JSON
    json_data = json.dumps(request_body)

    # Set the API URL
    url = "https://api.openai.com/v1/chat/completions"

    # Define headers, including the API key
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"  # Ensure the API key is set in your environment or code
    }

    # Make the API call to the chat completions endpoint
    response = requests.post(url, headers=headers, data=json_data)

    # Check if the response is successful
    if response.status_code != 200:
        error_content = response.text
        logging.error(f"OpenAI API error: {error_content}")
        return {"error": f"Error: {response.status_code}", "message": error_content}
    else:
        # Process and parse the successful response
        response_data = response.json()
        content = response_data["choices"][0]["message"]["content"]

        # Clean up the content if needed and parse it as JSON
        if content.startswith("```json"):
            content = content[8:-3].strip()  # Remove the code block markers

        try:
            activities_data = json.loads(content)
            logging.info(f"Activities: {json.dumps(activities_data, indent=2)}")
            return activities_data
        except json.JSONDecodeError as e:
            logging.error("Failed to decode JSON response.")
            return {"error": "Failed to decode JSON", "details": str(e)}

def concat_preferences_for_activities():
    # Retrieve stored data from session
    if(session.get('initial_prompt', '')):
      initial_prompt = session.get('initial_prompt', '')
    
    # Check if 'custom_quiz' is available in the session; if not, load instructions
    if session.get('custom_quiz'):
        quiz = session.get('custom_quiz', '')
    else:
        quiz = load_gpt_instructions('gpt_instructions/quiz_instructions.txt')
    
    formatted_answers = session.get('formatted_answers', '')
    summary = session.get('summary', '')
    destinations = session.get('destinations', [])

    destination = session.get('destination', '')

    # Formulate the prompt with session data
    activities_prompt = (
        f"The user selected {destination} as their destination. "
        f"Here is the quiz they were given: {quiz}. "
        f"Their answers to the quiz: {formatted_answers}. "
        f"Summary of preferences: {summary}. "
        f"Here were the output suggestions for the destination. Use the provided destination to find activities that match {destinations}. "
        f"Based on this, suggest activities that align with these preferences. "
        f"Please format the activities in JSON format, with each activity containing a 'name', 'type', and 'description'."
    )

    # Return the prompt for use with OpenAI
    return activities_prompt


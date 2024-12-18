# Description: This file contains the integrations with external APIs
# Imports the necessary modules and libraries
import logging
import requests
import json
import openai
import yaml
from flask import session, flash

# Load the API keys from the config file
credentials = yaml.load(open('config.yaml'), Loader=yaml.FullLoader)
pexels_api_key = credentials['pexels']['api_key']
openai.api_key = credentials['openai']['api_key']
weather_api_key = credentials['weather']['api_key']
flight_api_key = credentials['flight']['api_key']
ip_api_key = credentials['geoip']['api_key']

def send_quiz_to_gpt(message, OptionalCustomQuiz=None):


    # Load GPT quiz instructions
    if OptionalCustomQuiz is None:
        quiz_instructions = load_gpt_instructions('gpt_instructions/quiz_instructions.txt')
    else:
        quiz_instructions = OptionalCustomQuiz

    # Get the initial prompt, handling cases where it might not exist
    initial_prompt = session.get('initial_prompt', None)
    if initial_prompt is None:
        initial_prompt_message = "The user did not provide an initial input."
    else:
        initial_prompt_message = f"The user's initial input is: {initial_prompt}."

    # Create the request body
    request_body = {
        "model": "gpt-4",  # Ensure this is the correct model name
        "messages": [
            {
                "role": "system",
                "content": f"Here is the travel personality quiz that was given to the user: {quiz_instructions}"
            },
            {
                "role": "user",
                "content": f"Based on the following user responses to the travel personality quiz: {message}\n"
                           f"{initial_prompt_message}\n"
                           "Summarize the user's travel personality and suggest three travel destinations in this format. "
                           "If the user's initial input is a city or a destination (e.g., Edinburgh), provide three specific areas or neighborhoods within that destination. "
                           "For example, if the user inputs 'Edinburgh,' suggest destinations like 'Edinburgh Old Town,' 'Edinburgh New Town,' and 'Edinburgh Leith.  ... please ensure the city is included in the destination name'\n\n"
                           "Use this JSON format:\n"
                           "{\n"
                           '  "summary": "User\'s travel personality summary",\n'
                           '  "destinations": [\n'
                           '    {\n'
                           '      "name": "Destination Name",\n'
                           '      "airport": "Airport Name closest to the destination",\n'
                           '      "description": "A brief description of the destination.",\n'
                           '      "activities": [\n'
                           '        "Activity 1",\n'
                           '        "Activity 2",\n'
                           '        "Activity 3"\n'
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
        "max_tokens": 5000  # Adjust based on your API limits
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

    # Parse the response data
    try:
        response_data = response.json()
        content = response_data["choices"][0]["message"]["content"]

        # Remove the markdown code block markers (if present)
        if content.startswith("```json"):
            content = content[8:-3].strip()

        # Parse the content into JSON
        parsed_data = json.loads(content)
        print("Parsed API Response:", json.dumps(parsed_data, indent=2))
        return parsed_data

    except (KeyError, json.JSONDecodeError) as e:
        return {"error": "Failed to decode response content", "details": str(e)}





def parse_response(content):
    try:
        lines = content.split('\n')
        result = {"summary": "", "destinations": []}
        current_destination = None

        for line in lines:
            if line.startswith("Summary:"):
                result["summary"] = line.replace("Summary:", "").strip()
            elif line.startswith("Destination"):
                if current_destination:  # Save the last destination
                    result["destinations"].append(current_destination)
                current_destination = {}
            elif line.startswith("Name:"):
                current_destination["name"] = line.replace("Name:", "").strip()
            elif line.startswith("Description:"):
                current_destination["description"] = line.replace("Description:", "").strip()
            elif line.startswith("Activities:"):
                current_destination["activities"] = line.replace("Activities:", "").strip().split('|')
            elif line.startswith("Accommodation:"):
                current_destination["accommodation"] = line.replace("Accommodation:", "").strip().split('|')
            elif line.startswith("Travel Tips:"):
                current_destination["travel_tips"] = line.replace("Travel Tips:", "").strip().split('|')

        if current_destination:  # Append the last destination
            result["destinations"].append(current_destination)

        return result
    except Exception as e:
        return {"error": f"Parsing failed: {str(e)}", "details": content}

def get_custom_quiz(prompt):
 
    model = "gpt-4"  # Use GPT-4 for enhanced capabilities

    # Construct the prompt
    instruction = (
        f"Create a personalized 10-question travel personality quiz with questions relevent to a user intrested in: {prompt}. "
        "Provide the quiz in the following format:\n"
        "Question 1: Question text here\n"
        "Options: A) Option A text here | B) Option B text here | C) Option C text here | D) Option D text here\n"
        "...\n"
        "Continue this pattern for all 10 questions."
    )

    # Prepare the request body
    request_body = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a quiz generator specializing in creating travel personality quizzes."},
            {"role": "user", "content": instruction}
        ],
        "max_tokens": 1500,  # Adjust for expected response length
        "temperature": 0.7,  # Controls randomness; adjust for more/less creative output
        "top_p": 1.0,        # Controls diversity via nucleus sampling
        "n": 1               # Number of completions to generate
    }

    # Define the API endpoint and headers
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"  # Ensure your API key is configured correctly
    }

    # Make the API request
    response = requests.post(url, headers=headers, json=request_body)

    if response.status_code == 200:
        try:
            response_data = response.json()
            quiz_content = response_data["choices"][0]["message"]["content"].strip()
            return parse_quiz_to_json(quiz_content)
        except (KeyError, json.JSONDecodeError) as e:
            print(f"Error parsing response: {str(e)}")  # Replace with appropriate logging
            return None
    else:
        error_message = f"Error fetching quiz: {response.text}"
        print(error_message)  # Replace with appropriate logging
        return None


def parse_quiz_to_json(quiz_content):
    lines = quiz_content.split('\n')
    questions = []
    current_question = {}

    for line in lines:
        if line.startswith("Question"):
            if current_question:
                questions.append(current_question)
            current_question = {
                "question": line.split(': ', 1)[1],
                "options": []
            }
        elif line.startswith("Options"):
            options = line.split(': ', 1)[1].split(' | ')
            for option in options:
                option_letter, option_text = option.split(') ', 1)
                current_question["options"].append({
                    "option": option_letter.strip(),
                    "text": option_text.strip(),
                    
                })

    if current_question:
        questions.append(current_question)

    quiz_json = {
        "questions": questions
    }

    return json.dumps(quiz_json, indent=2)
    
    
    
# Return gpt instruction for a specific step as string
def load_gpt_instructions(file_path):
 with open(file_path, 'r') as file:
    return file.read()

def get_activities(destination, preferences):
    # Define the prompt for OpenAI to generate activities
    prompt = (
        f"You are a travel assistant. A user is planning a trip to {destination} with preferences: {preferences}.\n"
        "Recommend at least five activities that align with these preferences. Provide the response in the following JSON format:\n"
        "{\n"
        '  "destination": "Destination Name",\n'
        '  "activities": [\n'
        '    {\n'
        '      "name": "Activity Name",\n'
        '      "type": "Type of Activity (e.g., adventure, relaxation, cultural)",\n'
        '      "description": "Brief description of the activity."\n'
        '    },\n'
        '    // Include at least five activities\n'
        '  ]\n'
        "}"
    )

    # Create the request body
    request_body = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a knowledgeable travel assistant."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500,  # Adjust based on expected response length
        "temperature": 0.5,  # Lower temperature for more deterministic output
        "top_p": 0.9,        # Adjust as needed
        "n": 1               # Number of completions to generate
    }

    # Set the API URL
    url = "https://api.openai.com/v1/chat/completions"

    # Define headers, including the API key
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"  # Ensure the API key is set in your environment or code
    }

    # Make the API call to the chat completions endpoint
    response = requests.post(url, headers=headers, json=request_body)

    # Check if the response is successful
    if response.status_code != 200:
        error_content = response.text
        logging.error(f"OpenAI API error: {error_content}")
        return {"error": f"Error: {response.status_code}", "message": error_content}
    else:
        # Process and parse the successful response
        response_data = response.json()
        content = response_data["choices"][0]["message"]["content"]
        print("Raw content received:", content)

        # Attempt to parse the content as JSON
        try:
            # Remove code block markers if present
            if content.startswith("```json"):
                content = content[8:-3].strip()
            activities_data = json.loads(content)
            logging.info(f"Activities: {json.dumps(activities_data, indent=2)}")
            return activities_data
        except json.JSONDecodeError:
            logging.error("Failed to decode JSON response.")
            return {"error": "Failed to decode JSON"}


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


def form_itinerary_prompt(destination, formatted_answers, quiz_instructions, itinerary_activities):
    # Basic prompt structure
    prompt = f"You are planning a travel itinerary for the destination: {destination}.\n\n"

    # Add quiz instructions if provided
    if quiz_instructions:
        prompt += f"Here are some quiz instructions for better customization:\n{quiz_instructions}\n\n"

    # Add answers from the user quiz
    prompt += "User preferences based on quiz:\n"
    for answer in formatted_answers:
        prompt += f"- {answer}\n"
    
    # Add details of each selected activity
    prompt += "\nThe selected activities for the itinerary include:\n"
    for activity in itinerary_activities:
        activity_details = (
            f"Activity Name: {activity.get('name')}\n"
            f"Type: {activity.get('type')}\n"
            f"Description: {activity.get('description')}\n"
        )
        prompt += f"\n{activity_details}"

    

    return prompt



def get_itinerary(prompt):
    model = "gpt-4o"  # Ensure the correct model name is used

    messages = [
        {"role": "system", "content": "You are an expert travel assistant."},
        {
            "role": "user",
            "content": f"""Based on the following prompt, create a detailed travel itinerary that includes a day-by-day schedule, with selected activities, and suggested accommodations for the destination:
            
            {prompt}
            
            Format the response in JSON with the following structure:
            {{
                "itinerary": [
                    {{
                        "day": "Day 1",
                        "activities": [
                            {{"time": "9:00 AM", "activity": "Visit a local attraction"}}, 
                            {{"time": "12:00 PM", "activity": "Lunch at a recommended restaurant"}}
                        ],
                        "accommodation": "Suggested accommodation for the night"
                    }},
                    // Continue for each day of the trip, adding activities and accommodations as needed
                ]
            }}
            """
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
        itinerary_content = response_data["choices"][0]["message"]["content"]
        if itinerary_content.startswith("```json"):
            itinerary_content = itinerary_content[8:-3].strip()  # Remove the code block markers
        return itinerary_content
    else:
        flash(f"Error fetching itinerary: {response.text}", "error")
        return None
    
# Non GPT API calls    

# Function to get data from a flights API to give an idea of the prices
def flights_api(request_city, destination_city, start_date, end_date):
    flight_data = {}
    
    # Get FreebaseID for the cities
    freebase_id = get_freebase_id(destination_city)
    base_freebase_id = get_freebase_id(request_city)
    
    # Flight API URL with parameters
    url = f"https://serpapi.com/search.json?engine=google_flights&departure_id={base_freebase_id}&arrival_id={freebase_id}&outbound_date={start_date}&return_date={end_date}&currency=GBP&api_key={flight_api_key}&hl=en"
    
    response = requests.get(url)
    
    if response.status_code != 200:
        error_content = response.text
        flight_data[destination_city] = {"error": f"Error: {response.status_code}", "message": error_content}
        return flight_data
    
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
        google_flights_url = response_data['search_metadata']['google_flights_url']
        
        flight_info = {
            "flights": [],
            "layovers": layovers,
            "total_duration": total_duration,
            "carbon_emissions": carbon_emissions,
            "price": price,
            "airline_logo": airline_logo,
            "google_flights_url": google_flights_url
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
        
        flight_data[destination_city] = flight_info
    except (IndexError, KeyError) as e:
        flight_data[destination_city] = {"error": "No flight data found", "details": str(e)}
    
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

def pexels_images(query, per_page):
    # Function to get landscape images from Pexels API
    url = "https://api.pexels.com/v1/search"
    headers = {
        "Authorization": pexels_api_key
    }
    params = {
        "query": query,
        "per_page": per_page,
        "orientation": "landscape"  # Ensure only landscape images are fetched
    }
    
    response = requests.get(url, headers=headers, params=params)
        
    if response.status_code != 200:
        error_content = response.text
        return {"error": f"Error: {response.status_code}", "message": error_content}
    else:
        response_data = response.json()
        photos = response_data.get("photos", [])
        image_urls = [photo["src"]["medium"] for photo in photos]
        
        return image_urls
    
def get_user_location():
    # Make a request to get the user's IP address
    response = requests.get('https://httpbin.org/ip')
    # Parse the JSON response and get the user's IP address
    user_ip = response.json()['origin']
    url = f'https://api.ipgeolocation.io/ipgeo?apiKey={ip_api_key}&ip={user_ip}'
    # Create a request to the URL
    response = requests.get(url)
    # Parse the JSON response
    json_data = response.json()
    # Find the city in the response
    city = json_data.get('city')
    # Store the city in the session
    return city
    
#set location and radius from getting chat gpt to output it when getting activities!!! this can reduce costs for api calls to google places 
def text_search_activities(query, api_key, location=None, radius=None):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        'query': query,
        'key': api_key,
        'fields': 'place_id,name,photos,formatted_address,rating,user_ratings_total'
    }
    if location:
        params['location'] = location
    if radius:
        params['radius'] = radius
    
    response = requests.get(url, params=params)
    return response.json()

#fixed above method making the below method obsolete to prevent extra costs
def get_activity_details(place_id, api_key):
    url = f"https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        'place_id': place_id,
        'key': api_key,
        'fields': 'website'
    }
    response = requests.get(url, params=params)
    return response.json()

def get_photo_url(photo_reference, api_key, max_width=400):
    return f"https://maps.googleapis.com/maps/api/place/photo?maxwidth={max_width}&photoreference={photo_reference}&key={api_key}"

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

    # Iterate through the search results to find a valid Freebase ID
    for result in data['search']:
        entity_id = result['id']

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
            if freebase_id:
                return freebase_id

    return None


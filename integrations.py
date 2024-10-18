# Description: This file contains the integrations with external APIs
# Imports the necessary modules and libraries
import requests
import json
import openai
import yaml

# Load the API keys from the config file
credentials = yaml.load(open('config.yaml'), Loader=yaml.FullLoader)
pexels_api_key = credentials['pexels']['api_key']

# Function to get the data from the Google Places API
def google_places():
    return "WIP"

# OpenAI API key
openai.api_key = ''

# Function for sending quiz answers to GPT API
def send_quiz_to_gpt(message):
    # Get GPT quiz instructions
    quiz_instructions = load_gpt_instructions('gpt_instructions/quiz_instructions.txt')

    # Create the request body
    request_body = {
        "model": "gpt-4o-mini",  # Ensure this is the correct model name
        "messages": [
            {"role": "system", "content": f"Here is the travel personality quiz that was given to the user: {quiz_instructions}"},
            {"role": "user", "content": f"Based on the following user responses to the travel personality quiz: {message}\n"
                                         "Please provide a summary of the user's travel personality and suggest three travel destinations in the following JSON format:\n"
                                         "{\"summary\": \"User's travel personality summary\", \"destinations\": [{\"name\": \"Destination Name\", \"activities\": [\"Activity 1\", \"Activity 2\"], \"accommodation\": [\"Place 1\", \"Place 2\"], \"travelTips\": [\"Tip 1\", \"Tip 2\"]}, ...]}."}
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
        "Authorization": f"Bearer {openai.api_key}"  # Use the defined API key variable
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
  


    
# Return gpt instruction for a specific step as string
def load_gpt_instructions(file_path):
 with open(file_path, 'r') as file:
    return file.read()

# Flight API key
flight_api_key = '4fd54c41dd6fc731d431e14ee573e56d'

# Function to get data from a flights API to give an idea of the prices
def flights():
    # Flight API URL
    url = "https://api.aviationstack.com"

    response = requests.get(url)
    if response.status_code != 200:
        error_content = response.text
        return {"error": f"Error: {response.status_code}", "message": error_content}
    else:
        response_data = response.json()
        return response_data

# Weather API key
weather_api_key = '5f27832dfc3b15ad2b12926ec704e8d7'

# Function to get the weather data from an API
def weather():
    # Geolocation Api to get Latitude and Longitude of the city

    for i in range(3):
        geo_url = "http://api.openweathermap.org/geo/1.0/direct?q=" & city(i) & "&appid=" & weather_api_key

        response = requests.get(geo_url)
        if response.status_code != 200:
            error_content = response.text
            return {"error": f"Error: {response.status_code}", "message": error_content}
        else:
            response_data = response.json()
            lat = response_data[0]["lat"]
            lon = response_data[0]["lon"]

        #Once we have the latitude and longitude, we can use the One Call API to get the weather data
        weather_url = f"http://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely&appid={weather_api_key}"
        response = requests.get(weather_url)

        if response.status_code != 200:
            error_content = response.text
            return {"error": f"Error: {response.status_code}", "message": error_content}
        
        else:
            response_data = response.json()
            return response_data

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
    
print(pexels_images("iceland"))
# Description: This file contains the integrations with external APIs
# Imports the necessary modules and libraries
import requests
import json
import openai
import yaml

# Load the API keys from the config file
credentials = yaml.load(open('config.yaml'), Loader=yaml.FullLoader)
pexels_api_key = credentials['pexels']['api_key']
openai.api_key = credentials['open_ai']['api_key']
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
def flights():
    return "WIP"

# Function to get the weather data from an API
def weather():
    return "WIP"

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


import requests

def fetch_animation_url(keyword):
    # Use LottieFiles' public API endpoint to search animations by keyword
    search_url = f"https://assets7.lottiefiles.com/api/v1/animations/search?search={keyword}&limit=1"

    response = requests.get(search_url)
    
    if response.status_code == 200:
        try:
            animation_data = response.json()
            # Check if the data contains any animations
            if animation_data.get("data"):
                # Extract the first animation's URL if available
                animation_url = animation_data["data"][0]["lottie_url"]
                return animation_url
            else:
                print(f"No animation found for keyword: {keyword}")
                return None
        except ValueError:
            print(f"Error parsing JSON response for keyword '{keyword}'")
            return None
    else:
        print(f"Error: Request to LottieFiles failed with status code {response.status_code}")
        return None

def get_quiz_animations(quiz_json):
    animations = {}
    
    quiz_data = json.loads(quiz_json)
    
    for question in quiz_data["questions"]:
        question_text = question["question"]
        keywords = question["keyword"]
        
        # Fetch animation URLs for each keyword
        animation_urls = []
        for keyword in keywords:
            url = fetch_animation_url(keyword)
            if url:
                animation_urls.append(url)
            else:
                print(f"No URL found for keyword: {keyword}")
        
        # Store the results in the animations dictionary
        animations[question_text] = animation_urls
        print(f"Question: {question_text} - Animation URLs: {animation_urls}")
    
    return animations
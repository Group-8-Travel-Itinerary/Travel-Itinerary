# Description: This file contains the integrations with external APIs
# Imports the necessary modules and libraries
import requests
import json
import openai

# Function to get the data from the Google Places API
def google_places():
    return "WIP"

# OpenAI API key
openai.api_key = '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'

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

# Function to get data from a flights API to give an idea of the prices
def flights():
    return "WIP"

# Function to get the weather data from an API
def weather():
    return "WIP"
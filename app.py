# Description: This file contains the code for the Flask app that will be used to run the web application.
# Imports the necessary modules and libraries
from pathlib import Path
from flask import Flask, render_template, request, url_for, flash, redirect, session
import time
from datetime import datetime, timedelta

import requests
import yaml
from integrations import concat_preferences_for_activities, form_itinerary_prompt, get_activities, get_activity_details, get_itinerary, get_photo_url, get_single_image, load_gpt_instructions, parse_response, send_quiz_to_gpt, pexels_images, get_custom_quiz, flights_api, text_search_activities, weather_api, get_user_location
import os
from flask_session import Session as FlaskSession
import logging
import json


# Set up logging
logging.basicConfig(level=logging.INFO)

# Creates a Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure Flask-Session
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'  # Use filesystem-based session storage
app.config['SESSION_FILE_DIR'] = './flask_session/'  # Directory to store session files
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
FlaskSession(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    #added as when closing and reloading the application the session from custom uiz from previous is still there preventing it from going to hardcoded quiz when doing /quiz but now i realised why you added the button to get to hard coded quiz where you added session clear. 
    session.clear() 
    if request.method == 'POST':
        # Get the destination input from the form
        initial_prompt = request.form.get('destinationInput')

        if initial_prompt:
            # Call get_custom_quiz with error handling
             start_time = time.time()  # Start timer
             custom_quiz = get_custom_quiz(initial_prompt)
             end_time = time.time()  # End timer

             # Calculate elapsed time
             elapsed_time = end_time - start_time
             print(f"custom quiz API call duration: {elapsed_time:.2f} seconds")

            
             if custom_quiz:
                session['custom_quiz'] = custom_quiz
                session['initial_prompt'] = initial_prompt
                return redirect(url_for('quiz'))  # Redirect to the quiz page
             else:
                flash('Error retrieving quiz. Please try again.', 'error')
                return redirect(url_for('index'))
        else:
            #if no initial prompt sent over than assume they want the default quiz 
            #add button in ui to give users option for basic quiz
            return redirect(url_for('quiz'))

    # For a GET request, just render the index page without any quiz
    return render_template('index.html')

@app.route('/reset-and-start-quiz', methods=['GET'])
def reset_and_start_quiz():
    # Clear session data
    session.clear()  
    # Redirect to the hardcoded quiz route
    return redirect(url_for('quiz'))  


# Route for the quiz page
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        # Process the user's answers to the quiz
        user_answers = [
    request.form.get('answer1') or '',
    request.form.get('answer2') or '',
    request.form.get('answer3') or '',
    request.form.get('answer4') or '',
    request.form.get('answer5') or '',
    request.form.get('answer6') or '',
    request.form.get('answer7') or '',
    request.form.get('answer8') or '',
    request.form.get('answer9') or '',
    request.form.get('answer10') or ''
]

        # Combine user answers into a single message or format as needed
        formatted_answers = ', '.join(user_answers)
        session['formatted_answers'] = formatted_answers
        
        # Call the method to send quiz answers to GPT
            # Measure API call duration
        start_time = time.time()  # Start timer
        gpt_response = send_quiz_to_gpt(formatted_answers)
        end_time = time.time()  # End timer

        # Calculate elapsed time
        elapsed_time = end_time - start_time
        print(f"GPT API call duration: {elapsed_time:.2f} seconds")


        # Check for 'error' key in gpt_response and handle accordingly
        if 'error' in gpt_response:
            logging.error(f"Error from GPT response: {gpt_response}")
            error_message = gpt_response.get('message', 'Unknown error from GPT API')
            return redirect(url_for('index'))

        gpt_response = parse_response(gpt_response)
        
        # Extract summary and destinations from the response
        summary = gpt_response.get('summary', 'No summary available')
        destinations = gpt_response.get('destinations', [])
        session['destinations'] = destinations
        session['summary'] = summary
        
        start_time = time.time()  # Start timer
        destination_images = {destination['name']: get_single_image(destination['name']) for destination in destinations}
        end_time = time.time()  # End timer

        # Calculate elapsed time
        elapsed_time = end_time - start_time
        print(f"images API call duration: {elapsed_time:.2f} seconds")

       # Create a dictionary for destination images
       

        # Render the response in a new template
        return render_template(
            'quiz_response.html',
            summary=summary,
            destinations=destinations,
            destination_images=destination_images
        )

    # Handle GET request by loading the quiz from session if available
    custom_quiz = session.get('custom_quiz')
    
    if custom_quiz:
        #print("Custom Quiz from session:", session.get('custom_quiz'))

        # If there is a custom quiz in the session, render it
        return render_template('quiz.html', quiz=custom_quiz)
    
    # Otherwise, load hard-coded quiz data from a JSON file
    # This won't work if the custom quiz already exists in the session
    quiz_data_file = Path('static/data/quiz_data.json')
    if quiz_data_file.exists():
        with open(quiz_data_file, 'r') as f:
            default_quiz = json.load(f)
    return render_template('quiz.html', quiz= default_quiz)

#sort out later for testing here now 
credentials = yaml.load(open('config.yaml'), Loader=yaml.FullLoader)
places_api_key = credentials['places']['api_key']

@app.route('/activities', methods=['GET', 'POST'])
def activities():
    if request.method == 'POST':
        # Handle POST request for selecting a destination
        selected_destination = request.form.get('selected_destination')
        session['destination'] = selected_destination

        # Retrieve the prompt based on session data
        prompt = concat_preferences_for_activities()
        
        start_time = time.time()  # Start timer
        activities_data = get_activities(selected_destination, prompt)
        end_time = time.time()  # End timer

        # Calculate elapsed time
        elapsed_time = end_time - start_time
        print(f"activities API call duration: {elapsed_time:.2f} seconds")
        # Get basic activity information (name, type, description) from get_activities
        
        session['activities'] = activities_data  # Store this in session for later access

        # Initialize detailed_activities_map as an empty dictionary
        session['detailed_activities_map'] = {}

        # Render the activities page with basic information
        return render_template(
            'activities.html', 
            destination=selected_destination, 
            activities=activities_data['activities'], 
            detailed_activities_map=session['detailed_activities_map']
        )

    elif request.method == 'GET':
        # Handle GET request when requesting more information about a specific activity
        activity_id = request.args.get('activity_id')
        destination = session.get('destination')
        activities_data = session.get('activities', {}).get('activities', [])

        # Initialize detailed_activities_map in the session if it doesn't exist
        if 'detailed_activities_map' not in session:
            session['detailed_activities_map'] = {}

        detailed_activities_map = session['detailed_activities_map']

        if activity_id:
            activity_id = int(activity_id)
            logging.debug(f"Fetching details for activity_id: {activity_id}")
            if activity_id not in detailed_activities_map:
                detailed_options = []
                try:
                    # Perform a search for the specific activity name
                    selected_activity = activities_data[activity_id]
                    activity_name = selected_activity['name']
                    search_results = text_search_activities(activity_name, places_api_key)

                    # Gather multiple detailed options for the activity
                    for result in search_results['results']:
                        place_id = result['place_id']
                        detailed_info = get_activity_details(place_id, places_api_key)

                        detailed_options.append({
                            "name": selected_activity["name"],
                            "type": selected_activity["type"],
                            "description": selected_activity["description"],
                            "address": result.get("formatted_address", "No address available"),
                            "rating": result.get("rating", "No rating available"),
                            "total_ratings": result.get("user_ratings_total", "No rating count"),
                            "photo_url": get_photo_url(result.get("photos", [{}])[0].get("photo_reference"), places_api_key),
                            "website": detailed_info.get("result", {}).get("website", "Website not available")
                        })

                    # Store the detailed options in the map with activity_id as the key
                    detailed_activities_map[activity_id] = detailed_options

                    # Update the session with the new detailed_activities_map
                    session['detailed_activities_map'] = detailed_activities_map

                except KeyError as e:
                    logging.error(f"KeyError: {e} - activities_data: {activities_data}")

        return render_template(
            'activities.html', 
            destination=destination, 
            activities=activities_data, 
            detailed_activities_map=detailed_activities_map
        )

@app.route('/itinerary', methods=['GET', 'POST'])
def itinerary():
    if request.method == 'POST':
        # Get list of selected activity IDs from the form
        selected_activities = request.form.getlist('selected_activities')
        # Convert selected activity IDs from string to integers
        selected_activity_ids = [int(activity_id) for activity_id in selected_activities]
        
        # Retrieve the activities from session
        activities_data = session.get('activities', {}).get('activities', [])

        # Check if selected_activity_ids are within the range of activities_data
        valid_activity_ids = [activity_id for activity_id in selected_activity_ids if 0 <= activity_id < len(activities_data)]
        if len(valid_activity_ids) != len(selected_activity_ids):
            flash('One or more selected activities are invalid.', 'error')
            return redirect(url_for('activities'))

        # Filter the activities based on selected IDs
        itinerary_activities = [activities_data[activity_id] for activity_id in valid_activity_ids]

        # Formulate prompt for itinerary using all session data and activities selected
        OptionalCustomQuiz = session.get('custom_quiz')
        if OptionalCustomQuiz is None:
            quiz_instructions = load_gpt_instructions('gpt_instructions/quiz_instructions.txt')
        else:
            quiz_instructions = OptionalCustomQuiz
        
        formatted_answers = session.get('formatted_answers')
        destination = session.get('destination')
        
        # Check if city is defined in the session, if not, find the user location using the IP address
        if 'city' not in session:
            session['city'] = get_user_location()
        city = session['city']

        prompt = form_itinerary_prompt(destination, formatted_answers, quiz_instructions, itinerary_activities)

        itinerary = get_itinerary(prompt)
        
        # Ensure itinerary is parsed as JSON
        try:
            itinerary = json.loads(itinerary)
        except json.JSONDecodeError as e:
            flash ('Error parsing itinerary JSON', 'error')
            return redirect(url_for('index'))
        # Place the itenerary variable inside the intenerary key
        itinerary = itinerary['itinerary']
        
        # API Calls for Flights, Images and Weather

        # Call the Pexels API function to get images
        images = pexels_images(destination)
        
       # Generate the dates for the next week starting from today formatted in YYYY-MM-DD
        start_date = datetime.now().date().strftime('%Y-%m-%d')
        end_date = (datetime.now().date() + timedelta(days=7)).strftime('%Y-%m-%d')
        # Strip anything after the , in the destination to get the city name for flights
        flight_destination = destination.split(',')[0]
        # Call the Flights API function to get flight information
        flights = flights_api(city, flight_destination, start_date, end_date)
        
        # Extract the flight details from the response
        flight_details = []
        for destination, flight_info in flights.items():
            if 'flights' in flight_info:
                # Iterate over the flights list to extract the flight details
                for flight in flight_info['flights']:
                    # Append the flight details to the flight_details list
                    flight_details.append({
                        'departure_airport': flight['departure_airport'],
                        'arrival_airport': flight['arrival_airport'],
                        'airline': flight['airline'],
                        'airline_logo': flight['airline_logo'],
                        'price': flight_info['price'],
                        'layovers': [{'name': layover['name'], 'duration': layover['duration']} for layover in flight_info['layovers']],
                        'google_flights_url': flight_info['google_flights_url']
                    })
            else:
                flight_details.append({
                    'error': flight_info.get('error', 'No flight data found'),
                    'details': flight_info.get('details', '')
                })
        
        # Call the Weather API function to get weather information
        weather = weather_api([destination])
        
        print(f'Flights: {flights}')
        print(f"Weather: {weather}")
        
        # Combine the data and render a new template
        return render_template('result.html', itinerary=itinerary, flights=flight_details, images=images, weather=weather, destination=destination)
    return redirect(url_for('index', info='Please enter a destination to view your itinerary.'))

@app.route('/destinations')
def destinations():
    return render_template('destinations.html')

@app.route('/result')
def result():
    return render_template('result.html')

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
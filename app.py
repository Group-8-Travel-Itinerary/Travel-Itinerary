# Description: This file contains the code for the Flask app that will be used to run the web application.
# Imports the necessary modules and libraries
from flask import Flask, render_template, request, url_for, flash, redirect, session
from datetime import datetime, timedelta

import requests
import yaml
from integrations import concat_preferences_for_activities, form_itinerary_prompt, get_activities, get_activity_details, get_itinerary, get_photo_url, load_gpt_instructions, send_quiz_to_gpt, pexels_images, get_custom_quiz, flights_api, text_search_activities, weather_api
import os
import logging


# Set up logging
logging.basicConfig(level=logging.INFO)

# Creates a Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the destination input from the form
        initial_prompt = request.form.get('destinationInput')

        if initial_prompt:
            
            #move this flights stuff to itinerary later on
            #base_city = session.get('base_city')
            #destination = ["New York", "Los Angeles", "Chicago"]
            #start_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            #end_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
            #print(flights_api(base_city, destination, start_date, end_date))
            
            breakpoint()
            # Call get_custom_quiz with error handling
            custom_quiz = get_custom_quiz(initial_prompt)
            if custom_quiz:
                session['custom_quiz'] = custom_quiz
                session['initial_prompt'] = initial_prompt
                print(custom_quiz)  # This should now print the quiz data
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
        gpt_response = send_quiz_to_gpt(formatted_answers)

        # Check for 'error' key in gpt_response and handle accordingly
        if 'error' in gpt_response:
            logging.error(f"Error from GPT response: {gpt_response}")
            error_message = gpt_response.get('message', 'Unknown error from GPT API')
            return redirect(url_for('index'))

        # Extract summary and destinations from the response
        summary = gpt_response.get('summary', 'No summary available')
        destinations = gpt_response.get('destinations', [])
        session['destinations'] = destinations
        session['summary'] = summary

        # Render the response in a new template
        return render_template('quiz_response.html', summary=summary, destinations=destinations)

    # Handle GET request by loading the quiz from session if available
    custom_quiz = session.get('custom_quiz')
    
    if custom_quiz:
        # If there is a custom quiz in the session, render it
        return render_template('quiz.html', quiz=custom_quiz)
    
    # Otherwise, load a basic quiz template or default quiz data
    return render_template('quiz.html')

@app.route('/itinerary', methods=['GET', 'POST'])
def itinerary():
    if request.method == 'POST':
       
        
        # Get list of selected activity IDs from the form
        selected_activities = request.form.getlist('selected_activities')
        # Convert selected activity IDs from string to integers
        selected_activity_ids = [int(activity_id) for activity_id in selected_activities]
        
        # Retrieve the activities from session
        activities_data = session.get('activities', {}).get('activities', [])

        # Filter the activities based on selected IDs
        itinerary_activities = [activities_data[activity_id] for activity_id in selected_activity_ids]

        #formulate prompt for itineray using all session data and activities selected
        OptionalCustomQuiz = session.get('custom_quiz')
        if OptionalCustomQuiz is None:
         quiz_instructions = load_gpt_instructions('gpt_instructions/quiz_instructions.txt')
        else:
         quiz_instructions = OptionalCustomQuiz
        
        formatted_answers = session['formatted_answers']
        destination = session['destination']

        prompt = form_itinerary_prompt(destination, formatted_answers, quiz_instructions, itinerary_activities)



        itinerary = get_itinerary(prompt)

        # Call the Pexels API function to get images
        #images = pexels_images(destination)
        
        # Call the Flights API function to get flight information
        #flights = flights_api()
        # WIP: Awaiting implementation of the flights_api function
        
        # Call the Weather API function to get weather information
        #weather = weather_api(destination)
        # WIP: Awaiting implementation of the weather_api function
        
        # Combine the data and render a new template
        #return render_template('itinerary.html', images=images, flights=flights, weather=weather)
        return render_template('itinerary.html', itinerary=itinerary)
    return redirect(url_for('index', info='Please enter a destination to view your itenary.'))

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

        # Get basic activity information (name, type, description) from get_activities
        activities_data = get_activities(selected_destination, prompt)
        session['activities'] = activities_data  # Store this in session for later access

        # Initialize detailed_activities_map as an empty dictionary
        detailed_activities_map = {}

        # Render the activities page with basic information
        return render_template(
            'activities.html', 
            destination=selected_destination, 
            activities=activities_data['activities'], 
            detailed_activities_map=detailed_activities_map
        )

    elif request.method == 'GET':
        # Handle GET request when requesting more information about a specific activity
        activity_id = request.args.get('activity_id')
        destination = session.get('destination')
        activities_data = session.get('activities', {}).get('activities', [])
        
        # Initialize detailed_activities_map as an empty dictionary
        detailed_activities_map = {}

        if activity_id:
            # Find the specific activity by ID
            activity_id = int(activity_id)
            selected_activity = activities_data[activity_id] if activity_id < len(activities_data) else None

            if selected_activity:
                # Perform a search for the specific activity name
                activity_name = selected_activity['name']
                search_results = text_search_activities(activity_name, places_api_key)

                # Gather multiple detailed options for the activity
                detailed_options = []
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

                # Store the detailed options in a map with activity_id as the key
                detailed_activities_map[activity_id] = detailed_options

        return render_template(
            'activities.html', 
            destination=destination, 
            activities=activities_data, 
            detailed_activities_map=detailed_activities_map
        )





# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)






# Description: This file contains the code for the Flask app that will be used to run the web application.
# Imports the necessary modules and libraries
from flask import Flask, render_template, request, url_for, flash, redirect, session
from datetime import datetime, timedelta
from integrations import concat_preferences_for_activities, get_activities, send_quiz_to_gpt, pexels_images, get_custom_quiz, flights_api, weather_api
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

@app.route('/itenary', methods=['GET', 'POST'])
def itenary():
    if request.method == 'POST':
        # Get the destination input
        destination = ''
        
        # Call the Pexels API function to get images
        images = pexels_images(destination)
        
        # Call the Flights API function to get flight information
        flights = flights_api()
        # WIP: Awaiting implementation of the flights_api function
        
        # Call the Weather API function to get weather information
        weather = weather_api(destination)
        # WIP: Awaiting implementation of the weather_api function
        
        # Combine the data and render a new template
        return render_template('itenary.html', images=images, flights=flights, weather=weather)
    
    return redirect(url_for('index', info='Please enter a destination to view your itenary.'))


@app.route('/activities', methods=['POST'])
def activities():
    selected_destination = request.form.get('selected_destination')
    session['destination'] = selected_destination
    
    # Retrieve the prompt based on session data
    prompt = concat_preferences_for_activities()

    # Get activities based on the selected destination and prompt
    activities_data = get_activities(selected_destination, prompt)
    logging.info(f"Activities: {activities_data}")

    # Render the activities page with error handling
    return render_template('activities.html', destination=selected_destination, activities=activities_data)

@app.route('/destinations')
def destinations():
    return render_template('destinations.html')

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)




    # Print activities in JSON format using method 
#print(json.dumps(get_activities(destination, preferences), indent=4))

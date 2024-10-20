# Description: This file contains the code for the Flask app that will be used to run the web application.
# Imports the necessary modules and libraries
from flask import Flask, render_template, request, url_for, flash, redirect
from integrations import send_quiz_to_gpt, pexels_images, get_custom_quiz, flights_api, weather_api, login_db, register_db


# Creates a Flask app
app = Flask(__name__)

# Route for the index page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the destination input from the form
        destination = request.form.get('destinationInput')

        if destination:
            # Pass the destination to the get_custom_quiz method
            custom_quiz = get_custom_quiz(destination)

            # Print the result for testing (optional)
            print(custom_quiz)

            # Render the index page again but with the custom quiz result
            return render_template('quiz.html', custom_quiz=custom_quiz)

        else:
            # If no input was provided, flash an error message
            flash('Please enter a destination or select a suggestion.', 'error')
            return redirect(url_for('index'))

    # For a GET request, just render the index page without any quiz
    return render_template('index.html', quiz=None)

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        # Check if custom quiz data was passed along
        if 'custom_quiz' in request.form:
            custom_quiz = request.form['custom_quiz']
            
            # Render the quiz form with the custom questions
            return render_template('quiz.html', quiz=custom_quiz)
        
        # Otherwise, process the user's answers to the quiz
        user_answers = [
            request.form.get('answer1'),
            request.form.get('answer2'),
            request.form.get('answer3'),
            request.form.get('answer4'),
            request.form.get('answer5'),
            request.form.get('answer6'),
            request.form.get('answer7'),
            request.form.get('answer8'),
            request.form.get('answer9'),
            request.form.get('answer10')
        ]

        # Combine user answers into a single message or format as needed
        formatted_answers = ', '.join(user_answers)

        # Call the method to send quiz answers to GPT
        gpt_response = send_quiz_to_gpt(formatted_answers)

        # Extract summary and destinations from the response
        if 'error' in gpt_response:
            flash(gpt_response['message'], 'error')
            return redirect(url_for('index'))

        summary = gpt_response.get('summary')
        destinations = gpt_response.get('destinations', [])

        # Render the response in a new template or display it on the same page
        return render_template('quiz_response.html', summary=summary, destinations=destinations)

    # If no POST request, just render the quiz form (for GET request)
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

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get the username and password from the form
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the username and password are correct
        # WIP: Add a check for valid credentials
        if username == '' and password == '':
            # Redirect to the index page
            return redirect(url_for('index'))
        else:
            # Flash an error message if the credentials are incorrect
            flash('Invalid username or password. Please try again.', 'error')
            
@app.route('/logout')
def logout():
    # Redirect to the login page
    #  WIP: Add a logout functionality
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get the signup details from the form
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Check if the passwords match
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'error')
            return redirect(url_for('register'))

        # Check if the username is already taken
        # WIP: Add a check for existing usernames
        # WIP: Add a check for existing emails
        # WIP: Add a function for storing user data in a database

        # Register the user and redirect to the login page
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('.html')



# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
# Description: This file contains the code for the Flask app that will be used to run the web application.
# Imports the necessary modules and libraries
from flask import Flask, render_template, request, url_for, flash, redirect, session
import json
from bs4 import BeautifulSoup
import requests
from datetime import date, datetime
from integrations import openai
from integrations import send_quiz_to_gpt


# Creates a Flask app
app = Flask(__name__)

# Route for the index page
@app.route('/')
def index():
    # Return the index page
    return render_template('index.html')

# Quiz page test 
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        # Get user answers from the form
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
        formatted_answers = ', '.join(filter(None, user_answers))

        # Inside the quiz() function after calling send_quiz_to_gpt
        gpt_response = send_quiz_to_gpt(formatted_answers)

        # Extract summary and destinations from the response
        if 'error' in gpt_response:
            flash(gpt_response['message'], 'error')
            return redirect(url_for('index'))

        summary = gpt_response.get('summary')
        destinations = gpt_response.get('destinations', [])

        # Render the response in a new template or display it on the same page
        return render_template('quiz_response.html', summary=summary, destinations=destinations)

    return render_template('quiz.html')  # Render the quiz form on GET request

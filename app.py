# Description: This file contains the code for the Flask app that will be used to run the web application.
# Imports the necessary modules and libraries
from flask import Flask, render_template, request, url_for, flash, redirect, session
import json
from bs4 import BeautifulSoup
import requests
from datetime import date, datetime
from integrations import google_places, chat_gpt

# Creates a Flask app
app = Flask(__name__)

# Route for the index page
@app.route('/')
def index():
    # Return the index page
    return render_template('index.html')

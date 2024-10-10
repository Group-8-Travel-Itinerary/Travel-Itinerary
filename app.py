from flask import Flask, render_template, request, url_for, flash, redirect, session
import json
from bs4 import BeautifulSoup
import requests
from datetime import date, datetime

app = Flask(__name__)

@app.route('/')
def index():
    # Return the index page
    return render_template('index.html')

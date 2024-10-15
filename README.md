# Travel Itinerary Project

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Setting Up the Project](#setting-up-the-project)
- [Running the Project](#running-the-project)
- [Updating Dependencies](#updating-dependencies)
- [Instructions for Developers](#instructions-for-developers)
- [Contributing](#contributing)

## Overview
This project is a web application built with Flask that helps users plan and manage their travel itineraries. 

## Prerequisites
Before you begin, ensure you have the following installed:
- Python 3.x
- Git
- pip (Python package installer)

## Setting Up the Project

1. **Clone the Repository**:  
   If you haven't cloned the repository yet, use the following command:
   ```bash
   git clone https://github.com/Group-8-Travel-Itinerary/Travel-Itinerary.git
   cd Travel-Itinerary
   ```

2. **Pull the Latest Changes**:  
   Before creating a new branch, make sure to pull the latest changes from the main branch:
   ```bash
   git checkout main
   git pull origin main
   ```

3. **Create a New Branch**:  
   Create and switch to a new branch for your work:
   ```bash
   git checkout -b your-feature-branch-name
   ```

4. **Set Up a Virtual Environment**:  
   It's recommended to use a virtual environment to manage dependencies:
   ```bash
   python -m venv venv
   ```

5. **Activate the Virtual Environment**:
   - **Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

6. **Install Dependencies**:  
   Use the `requirements.txt` file to install the necessary packages:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Project

To run the Flask application, execute the following command:
```bash
flask run
```

Make sure your environment variable `FLASK_APP` is set correctly, typically to `app.py`:
- **macOS/Linux**:
  ```bash
  export FLASK_APP=app.py
  ```
- **Windows**:
  ```bash
  set FLASK_APP=app.py
  ```

## Updating Dependencies

When adding new dependencies or updating existing ones, follow these steps:

1. **Ensure `pipreqs` is Installed**:  
   Before running the update script, make sure `pipreqs` is installed. The script will attempt to install it for you, but if the installation fails, you may need to install it manually:
   ```bash
   pip install --user pipreqs
   ```

2. **Run the Update Script**:  
   To update `requirements.txt` based on your project imports, execute the following command:
   ```bash
   python update_requirements.py
   ```
   This will regenerate the `requirements.txt` file.

3. **Commit Your Changes**:  
   After updating `requirements.txt`, add and commit your changes:
   ```bash
   git add requirements.txt
   git commit -m "Update requirements.txt"
   ```

4. **Push Your Changes**:  
   Push your branch to the remote repository:
   ```bash
   git push origin your-feature-branch-name
   ```

# Description: This file contains the code for the Flask app that will be used to run the web application.
# Imports the necessary modules and libraries
from flask import Flask, render_template, request, url_for, flash, redirect, json
from integrations import send_quiz_to_gpt, pexels_images, get_custom_quiz, get_quiz_animations


# Creates a Flask app
app = Flask(__name__)

# Route for the index page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        destination = request.form.get('destinationInput')
        
        if destination:
            # Generate custom quiz and redirect to /quiz
            custom_quiz = get_custom_quiz(destination)
            
            if custom_quiz:
                # Pass the quiz to /quiz route by redirecting with JSON data
                return redirect(url_for('quiz', custom_quiz=json.dumps(custom_quiz)))
            else:
                flash("Could not generate quiz, please try again.", "error")
                return redirect(url_for('index'))
        
        flash('Please enter a destination or select a suggestion.', 'error')
        return redirect(url_for('index'))
    
    return render_template('index.html')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        # Handle user responses and generate output
        user_answers = [request.form.get(f'answer{i}') for i in range(1, 11)]
        formatted_answers = ', '.join(filter(None, user_answers))
        gpt_response = send_quiz_to_gpt(formatted_answers)

        if 'error' in gpt_response:
            flash(gpt_response['message'], 'error')
            return redirect(url_for('index'))

        return render_template('quiz_response.html', summary=gpt_response.get('summary'), destinations=gpt_response.get('destinations'))
    
    # If it's a GET request, retrieve the custom quiz data
    custom_quiz = request.args.get('custom_quiz')
    if custom_quiz:
        custom_quiz = json.loads(custom_quiz)
        animations = get_quiz_animations(custom_quiz)
        print("\n--- Quiz Animations ---")
        for question, urls in animations.items():
                print(f"Question: {question}")
                for url in urls:
                    print(f"   Animation URL: {url}")
        print("\n--- End of Animations ---\n")

        return render_template('quiz.html', quiz=custom_quiz, animations=animations)
    
    flash("No quiz data found.", "error")
    return redirect(url_for('index'))

@app.route('/pexels_test')
def pexels_test():
    # Call the Pexels API function to get images
    images = pexels_images('amsterdam in winter')

    # Render the images on a new template
    return render_template('pexels_test.html', images=images)

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request, jsonify, render_template, request, redirect, url_for, session
import json
import os
from flask_session import Session
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
load_dotenv()

# Load stories from data.json
def load_stories():
    with open('data.json', 'r') as file:
        return json.load(file)

@app.route('/')
def index():
    if 'story_index' not in session:
            session['story_index'] = 0  # Start at the first story
    
    data = load_stories()  # Load stories from JSON file
    stories = data['stories']

    # Check if there are more stories
    if session['story_index'] < len(stories):
        story_data = stories[session['story_index']]
        return render_template('index.html', story=story_data['story'], questions=story_data['questions'], story_id=story_data['id'])
    else:
        return render_template('end.html')  # Render an end page when done

@app.route('/submit', methods=['POST'])
def submit():
    # Retrieve the current story index
    story_index = session['story_index']
    
    # Load the existing responses
    responses_file = 'responses.json'
    if os.path.exists(responses_file):
        with open(responses_file, 'r') as file:
            responses_data = json.load(file)
    else:
        responses_data = {}

    # Collect user responses
    user_responses = {}
    questions = load_stories()['stories'][story_index]['questions']
    
    for i, question in enumerate(questions):
        user_responses[question] = {
            'response': request.form.get(f'response_{i + 1}'),
            'comment': request.form.get(f'comment_{i + 1}', '')
        }

    # Store the responses in the responses_data dictionary
    responses_data[f'story_{story_index}'] = user_responses
    
    # Write the updated responses to the JSON file
    with open(responses_file, 'w') as file:
        json.dump(responses_data, file, indent=4)

    # Increment the story index after answering questions
    session['story_index'] += 1
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)